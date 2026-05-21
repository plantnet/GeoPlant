"""GeoPlant dataset downloader CLI."""

from __future__ import annotations

import argparse
import os
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias
from urllib.parse import quote

import requests
from tqdm import tqdm

try:
    from .config import LEGACY_RASTERS, METADATA, PRESENCE_ABSENCE, PRESENCE_ONLY, RASTERS, URL_STRUCT, VARIABLES
except ImportError:  # pragma: no cover - supports direct script execution
    from config import LEGACY_RASTERS, METADATA, PRESENCE_ABSENCE, PRESENCE_ONLY, RASTERS, URL_STRUCT, VARIABLES

ManifestEntry: TypeAlias = str | list[str]
FileGroups: TypeAlias = list[list[str]]
SatelliteModality: TypeAlias = str
SATELLITE_MODALITIES = ("sentinel2_jpeg", "sentinel2_tiff", "alphaearth")
ENVIRONMENTAL_VALUE_VARIABLES = ("elevation", "humanfootprint", "landcover", "soilgrids")
RASTER_VARIABLES = tuple(RASTERS)


@dataclass(frozen=True)
class DownloadResult:
    """Structured result for one requested file download.

    Attributes
    ----------
    file_path:
        Manifest-relative file path, or the local filename for skipped files.
    success:
        Whether the file was downloaded or already present.
    error:
        Error message captured for failed downloads.
    skipped:
        Whether the local file already existed with the expected size.
    """

    file_path: str
    success: bool
    error: str | None = None
    skipped: bool = False


@dataclass(frozen=True)
class ExtractResult:
    """Structured result for one requested archive extraction.

    Attributes
    ----------
    archive_path:
        Local path to the zip archive.
    output_dir:
        Directory where the archive was extracted.
    success:
        Whether extraction completed or was skipped.
    error:
        Error message captured for failed extractions.
    skipped:
        Whether extraction was skipped because the output directory already
        existed and ``overwrite`` was false.
    """

    archive_path: str
    output_dir: str
    success: bool
    error: str | None = None
    skipped: bool = False


def find_url(file_path: str) -> str:
    """Resolve a direct download URL from the published Seafile page."""
    response = requests.get(URL_STRUCT.format(quote(file_path, safe="/")), timeout=60)
    response.raise_for_status()
    match = re.search(r"rawPath: '([^']+)'", response.text)
    if match:
        return match.group(1).replace("\\u002D", "-") + "?raw=1"
    raise requests.exceptions.HTTPError(f"Failed to find url for {file_path}")


def check_if_file_complete(path: Path, response: requests.Response) -> bool:
    """Return True when a file should be downloaded or re-downloaded."""
    if path.exists():
        server_size = int(response.headers.get("Content-Length", 0))
        local_size = path.stat().st_size
        if server_size != local_size:
            return True
        print(f"{path} already downloaded and complete.")
        return False
    return True


def download_file(url: str, filename: Path) -> DownloadResult:
    """Download a file from a direct URL."""
    response = requests.get(url, timeout=60, stream=True)
    response.raise_for_status()
    if not check_if_file_complete(filename, response):
        return DownloadResult(file_path=str(filename), success=True, skipped=True)

    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    filename.parent.mkdir(parents=True, exist_ok=True)
    progress_bar = tqdm(total=total_size, unit="iB", unit_scale=True)
    try:
        with filename.open("wb") as file_handle:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file_handle.write(data)
    finally:
        progress_bar.close()

    if total_size not in (0, progress_bar.n):
        raise requests.exceptions.RequestException("Error: downloaded file size does not match server size.")
    return DownloadResult(file_path=str(filename), success=True)


def process_download(file_path: str, output_dir: str) -> DownloadResult:
    """Download one file and return a structured result."""
    url = None
    try:
        url = find_url(file_path)
        print(f"Downloading {url} ({file_path})")
        return download_file(url, Path(output_dir) / file_path)
    except requests.exceptions.RequestException as exc:
        error = str(exc) or exc.__class__.__name__
        if url:
            error = f"{error} [{url}]"
        print(f"Failed to download file {file_path}\n\t{error}")
        return DownloadResult(file_path=file_path, success=False, error=error)


def download_files(file_paths: list[str], output_dir: str | Path) -> list[DownloadResult]:
    """Download manifest paths into an output directory.

    This function is shared by the CLI and the ``GeoPlant`` Python API so both
    entrypoints preserve the same folder layout and error handling.
    """
    return [process_download(file_path, str(output_dir)) for file_path in file_paths]


def _safe_extract_zip(archive: zipfile.ZipFile, output_dir: Path) -> None:
    """Extract a zip archive while preventing writes outside ``output_dir``."""
    output_root = output_dir.resolve()
    for member in archive.infolist():
        target_path = (output_dir / member.filename).resolve()
        if output_root != target_path and output_root not in target_path.parents:
            raise ValueError(f"Unsafe path in zip archive: {member.filename}")
    archive.extractall(output_dir)


def extract_file(archive_path: str | Path, output_dir: str | Path | None = None, overwrite: bool = False) -> ExtractResult:
    """Extract one zip archive.

    By default the extraction directory is the archive path without its
    ``.zip`` suffix. Existing extraction directories are skipped unless
    ``overwrite`` is true.
    """
    archive_path = Path(archive_path)
    output_dir = Path(output_dir) if output_dir is not None else archive_path.with_suffix("")
    try:
        if output_dir.exists() and not overwrite:
            print(f"{output_dir} already exists; skipping extraction.")
            return ExtractResult(
                archive_path=str(archive_path),
                output_dir=str(output_dir),
                success=True,
                skipped=True,
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path) as archive:
            _safe_extract_zip(archive, output_dir)
        print(f"Extracted {archive_path} to {output_dir}.")
        return ExtractResult(archive_path=str(archive_path), output_dir=str(output_dir), success=True)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        error = str(exc) or exc.__class__.__name__
        print(f"Failed to extract file {archive_path}\n\t{error}")
        return ExtractResult(archive_path=str(archive_path), output_dir=str(output_dir), success=False, error=error)


def extract_files(file_paths: list[str], output_dir: str | Path, overwrite: bool = False) -> list[ExtractResult]:
    """Extract selected manifest zip paths from an output directory."""
    output_dir = Path(output_dir)
    archives = [output_dir / file_path for file_path in file_paths if file_path.endswith(".zip")]
    return [extract_file(archive_path, overwrite=overwrite) for archive_path in archives]


def multipart_extract_dir(archive_path: str | Path) -> Path:
    """Return the shared extraction directory for a multipart archive name."""
    archive_path = Path(archive_path)
    stem = archive_path.with_suffix("").name
    group_stem = re.sub(r"[-_.]part[-_.]?\d+$", "", stem, flags=re.IGNORECASE)
    if group_stem == stem:
        group_stem = re.sub(r"[-_.]\d{2,3}$", "", stem)
    if not group_stem:
        group_stem = stem
    return archive_path.with_name(group_stem)


def extract_downloaded_file_groups(
    file_groups: FileGroups,
    output_dir: str | Path,
    successful_files: set[str],
    overwrite: bool = False,
) -> list[ExtractResult]:
    """Extract zip groups only when every file in the group downloaded.

    Multipart datasets can be represented in the manifest as nested lists. All
    files in such a group must download successfully before any archive from
    that group is extracted.
    """
    output_dir = Path(output_dir)
    extract_results: list[ExtractResult] = []
    for file_group in file_groups:
        archives = [file_path for file_path in file_group if file_path.endswith(".zip")]
        if not archives:
            continue

        missing_files = [file_path for file_path in file_group if file_path not in successful_files]
        if missing_files:
            print(
                "Skipping extraction for grouped archive because not all files downloaded: "
                + ", ".join(missing_files)
            )
            continue

        if len(archives) == 1:
            extract_results.extend(extract_files(archives, output_dir, overwrite=overwrite))
            continue

        archive_paths = [output_dir / archive for archive in archives]
        shared_output_dir = multipart_extract_dir(archive_paths[0])
        if shared_output_dir.exists() and not overwrite:
            print(f"{shared_output_dir} already exists; skipping grouped extraction.")
            extract_results.extend(
                ExtractResult(
                    archive_path=str(archive_path),
                    output_dir=str(shared_output_dir),
                    success=True,
                    skipped=True,
                )
                for archive_path in archive_paths
            )
            continue

        for archive_path in archive_paths:
            extract_results.append(extract_file(archive_path, shared_output_dir, overwrite=True))
    return extract_results


def flatten_file_groups(file_groups: FileGroups) -> list[str]:
    """Return a flat list of manifest paths from grouped selections."""
    return [file_path for file_group in file_groups for file_path in file_group]


def file_groups_from_entries(entries: list[ManifestEntry]) -> FileGroups:
    """Normalize manifest entries into extraction-aware file groups."""
    file_groups: FileGroups = []
    for entry in entries:
        if isinstance(entry, str):
            file_groups.append([entry])
        else:
            file_groups.append(list(entry))
    return file_groups


def deduplicate_file_groups(file_groups: FileGroups) -> FileGroups:
    """Deduplicate manifest paths while preserving group order."""
    deduplicated: FileGroups = []
    seen = set()
    for file_group in file_groups:
        unique_group = []
        for file_path in file_group:
            if file_path not in seen:
                unique_group.append(file_path)
                seen.add(file_path)
        if unique_group:
            deduplicated.append(unique_group)
    return deduplicated


def files_for_variable(
    structure: dict, cubes: bool, variable: str, legacy: bool = False
) -> list[str]:
    """Return manifest paths for a given variable and storage format."""
    return flatten_file_groups(file_groups_for_variable(structure, cubes, variable, legacy))


def file_groups_for_variable(
    structure: dict, cubes: bool, variable: str, legacy: bool = False
) -> FileGroups:
    """Return grouped manifest paths for a given variable and storage format."""
    variable_entry = structure.get(variable)
    if not variable_entry:
        return []
    if cubes:
        return file_groups_from_entries(variable_entry.get("cubes", []))
    if legacy and variable_entry.get("legacy_csvs"):
        return file_groups_from_entries(variable_entry["legacy_csvs"])
    return file_groups_from_entries(variable_entry.get("csvs", variable_entry.get("not_cubes", [])))


def satellite_modality(file_path: str) -> SatelliteModality | None:
    """Return the satellite modality for a manifest path."""
    if "/Sentinel2Patches-jpeg/" in file_path:
        return "sentinel2_jpeg"
    if "/Sentinel2Patches-tiff/" in file_path:
        return "sentinel2_tiff"
    if "/AlphaEarth/" in file_path:
        return "alphaearth"
    return None


def filter_satellite_file_groups(
    file_groups: FileGroups,
    modalities: list[SatelliteModality],
) -> FileGroups:
    """Keep only satellite data file groups matching selected modalities."""
    allowed = set(modalities)
    return [
        file_group
        for file_group in file_groups
        if any(satellite_modality(file_path) in allowed for file_path in file_group)
    ]


def raster_file_groups_for_variable(variable: str, legacy: bool = False) -> FileGroups:
    """Return raster file groups for a variable.

    Current raster files are selected by default. Legacy raster files replace
    the current files for variables that define a legacy raster set.
    """
    if legacy:
        legacy_entries = LEGACY_RASTERS.get(variable)
        if legacy_entries:
            return file_groups_from_entries(legacy_entries)
    return file_groups_from_entries(RASTERS.get(variable, []))


def selected_sources(source: str) -> list[str]:
    """Return source subset keys."""
    if source == "both":
        return ["po", "pa"]
    return [source]


def selected_variables(selection: list[str] | None, allowed: tuple[str, ...]) -> list[str]:
    """Return selected variables, defaulting to every allowed variable."""
    if not selection:
        return list(allowed)
    unknown = sorted(set(selection).difference(allowed))
    if unknown:
        raise ValueError(f"Unsupported variables for this data type: {unknown}")
    return list(selection)


def selected_satellite_modalities_from_names(modalities: list[str] | None) -> list[SatelliteModality]:
    """Normalize selected satellite data modalities."""
    if not modalities:
        return list(SATELLITE_MODALITIES)
    normalized = [modality.replace("-", "_") for modality in modalities]
    unknown = sorted(set(normalized).difference(SATELLITE_MODALITIES))
    if unknown:
        raise ValueError(f"Unknown satellite modalities: {unknown}")
    return normalized


def build_download_args(
    *,
    metadata: bool = False,
    rasters: bool = False,
    environmental_values: bool = False,
    bioclim_values: bool = False,
    bioclim_cubes: bool = False,
    landsat_values: bool = False,
    landsat_cubes: bool = False,
    satellite_data: bool = False,
    legacy: bool = False,
    source: str = "both",
    variables: list[str] | None = None,
    satellite_modalities: list[str] | None = None,
) -> argparse.Namespace:
    """Build an ``argparse.Namespace`` from Python API selections."""
    if source not in {"po", "pa", "both"}:
        raise ValueError(f"Unknown source: {source}")
    selected_satellite_modalities_from_names(satellite_modalities)
    return argparse.Namespace(
        metadata=metadata,
        rasters=rasters,
        environmental_values=environmental_values,
        bioclim_values=bioclim_values,
        bioclim_cubes=bioclim_cubes,
        landsat_values=landsat_values,
        landsat_cubes=landsat_cubes,
        satellite_data=satellite_data,
        legacy=legacy,
        source=source,
        variables=variables,
        satellite_modalities=satellite_modalities,
    )


def resolve_requested_files(
    *,
    metadata: bool = False,
    rasters: bool = False,
    environmental_values: bool = False,
    bioclim_values: bool = False,
    bioclim_cubes: bool = False,
    landsat_values: bool = False,
    landsat_cubes: bool = False,
    satellite_data: bool = False,
    legacy: bool = False,
    source: str = "both",
    variables: list[str] | None = None,
    satellite_modalities: list[str] | None = None,
) -> list[str]:
    """Resolve manifest paths for a requested GeoPlant data subset."""
    args = build_download_args(
        metadata=metadata,
        rasters=rasters,
        environmental_values=environmental_values,
        bioclim_values=bioclim_values,
        bioclim_cubes=bioclim_cubes,
        landsat_values=landsat_values,
        landsat_cubes=landsat_cubes,
        satellite_data=satellite_data,
        legacy=legacy,
        source=source,
        variables=variables,
        satellite_modalities=satellite_modalities,
    )
    return collect_requested_files(args)


def resolve_requested_file_groups(
    *,
    metadata: bool = False,
    rasters: bool = False,
    environmental_values: bool = False,
    bioclim_values: bool = False,
    bioclim_cubes: bool = False,
    landsat_values: bool = False,
    landsat_cubes: bool = False,
    satellite_data: bool = False,
    legacy: bool = False,
    source: str = "both",
    variables: list[str] | None = None,
    satellite_modalities: list[str] | None = None,
) -> FileGroups:
    """Resolve extraction-aware manifest groups for a requested data subset."""
    args = build_download_args(
        metadata=metadata,
        rasters=rasters,
        environmental_values=environmental_values,
        bioclim_values=bioclim_values,
        bioclim_cubes=bioclim_cubes,
        landsat_values=landsat_values,
        landsat_cubes=landsat_cubes,
        satellite_data=satellite_data,
        legacy=legacy,
        source=source,
        variables=variables,
        satellite_modalities=satellite_modalities,
    )
    return collect_requested_file_groups(args)


def collect_requested_files(args: argparse.Namespace) -> list[str]:
    """Resolve requested files without downloading them."""
    return flatten_file_groups(collect_requested_file_groups(args))


def collect_requested_file_groups(args: argparse.Namespace) -> FileGroups:
    """Resolve requested file groups without downloading them."""
    requested_file_groups: FileGroups = []
    source_names = selected_sources(args.source)

    if args.metadata:
        for source_name in source_names:
            requested_file_groups.extend(file_groups_from_entries(METADATA[source_name]))

    if args.rasters:
        for variable in selected_variables(args.variables, RASTER_VARIABLES):
            requested_file_groups.extend(raster_file_groups_for_variable(variable, args.legacy))

    if args.environmental_values:
        for variable in selected_variables(args.variables, ENVIRONMENTAL_VALUE_VARIABLES):
            for source_name, structure in (("po", PRESENCE_ONLY), ("pa", PRESENCE_ABSENCE)):
                if source_name in source_names:
                    requested_file_groups.extend(file_groups_for_variable(structure, False, variable, args.legacy))

    if args.bioclim_values:
        for source_name, structure in (("po", PRESENCE_ONLY), ("pa", PRESENCE_ABSENCE)):
            if source_name in source_names:
                requested_file_groups.extend(file_groups_for_variable(structure, False, "climate"))

    if args.bioclim_cubes:
        for source_name, structure in (("po", PRESENCE_ONLY), ("pa", PRESENCE_ABSENCE)):
            if source_name in source_names:
                requested_file_groups.extend(file_groups_for_variable(structure, True, "climate"))

    if args.landsat_values:
        for source_name, structure in (("po", PRESENCE_ONLY), ("pa", PRESENCE_ABSENCE)):
            if source_name in source_names:
                requested_file_groups.extend(file_groups_for_variable(structure, False, "satellitetimeseries"))

    if args.landsat_cubes:
        for source_name, structure in (("po", PRESENCE_ONLY), ("pa", PRESENCE_ABSENCE)):
            if source_name in source_names:
                requested_file_groups.extend(file_groups_for_variable(structure, True, "satellitetimeseries"))

    if args.satellite_data:
        modalities = selected_satellite_modalities_from_names(
            getattr(args, "satellite_modalities", None) or getattr(args, "modalities", None)
        )
        for source_name, structure in (("po", PRESENCE_ONLY), ("pa", PRESENCE_ABSENCE)):
            if source_name in source_names:
                file_groups = file_groups_for_variable(structure, False, "satellitedata")
                requested_file_groups.extend(filter_satellite_file_groups(file_groups, modalities))

    return deduplicate_file_groups(requested_file_groups)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "GeoPlant Dataset Downloader.\n"
            "Download GeoPlant data by storage category."
        )
    )
    commands = parser.add_subparsers(dest="command", required=True)
    download = commands.add_parser("download", help="Download one GeoPlant data category.")
    download.set_defaults(
        metadata=False,
        rasters=False,
        environmental_values=False,
        bioclim_values=False,
        bioclim_cubes=False,
        landsat_values=False,
        landsat_cubes=False,
        satellite_data=False,
        legacy=False,
        extract=False,
        data="data",
        source="both",
        variables=None,
        modalities=None,
    )
    categories = download.add_subparsers(dest="category", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--data",
        default="data",
        help='Destination directory for downloaded files (default: "data").',
    )
    common.add_argument(
        "--extract",
        action="store_true",
        help="Extract selected zip archives after download.",
    )

    source_parent = argparse.ArgumentParser(add_help=False)
    source_parent.add_argument(
        "--source",
        choices=("po", "pa", "both"),
        default="both",
        help="Select presence-only, presence-absence, or both subsets.",
    )

    variables_parent = argparse.ArgumentParser(add_help=False)
    variables_parent.add_argument(
        "--variables",
        nargs="+",
        choices=VARIABLES,
        help=(
            "Filter variables for --rasters or --environmental-values. "
            "Defaults to every variable supported by the selected category."
        ),
    )

    legacy_parent = argparse.ArgumentParser(add_help=False)
    legacy_parent.add_argument(
        "--legacy",
        action="store_true",
        help="Use legacy files where available for rasters/environmental values.",
    )

    modalities_parent = argparse.ArgumentParser(add_help=False)
    modalities_parent.add_argument(
        "--modalities",
        nargs="+",
        choices=("sentinel2-jpeg", "sentinel2-tiff", "alphaearth"),
        help="Filter --satellite-data modalities. Defaults to all modalities.",
    )

    categories.add_parser("metadata", parents=[common, source_parent]).set_defaults(metadata=True)
    categories.add_parser("rasters", parents=[common, variables_parent, legacy_parent]).set_defaults(rasters=True)
    categories.add_parser(
        "environmental-values",
        parents=[common, source_parent, variables_parent, legacy_parent],
    ).set_defaults(environmental_values=True)

    bioclim = categories.add_parser("bioclim")
    bioclim_subcommands = bioclim.add_subparsers(dest="representation", required=True)
    bioclim_subcommands.add_parser("values", parents=[common, source_parent]).set_defaults(bioclim_values=True)
    bioclim_subcommands.add_parser("cubes", parents=[common, source_parent]).set_defaults(bioclim_cubes=True)

    landsat = categories.add_parser("landsat")
    landsat_subcommands = landsat.add_subparsers(dest="representation", required=True)
    landsat_subcommands.add_parser("values", parents=[common, source_parent]).set_defaults(landsat_values=True)
    landsat_subcommands.add_parser("cubes", parents=[common, source_parent]).set_defaults(landsat_cubes=True)

    categories.add_parser(
        "satellite-data",
        parents=[common, source_parent, modalities_parent],
    ).set_defaults(satellite_data=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    os.makedirs(args.data, exist_ok=True)

    try:
        requested_file_groups = collect_requested_file_groups(args)
    except ValueError as exc:
        parser.error(str(exc))

    requested_files = flatten_file_groups(requested_file_groups)
    if not requested_files:
        parser.error(
            "No files selected. Choose a data category such as "
            "`download metadata`, `download environmental-values`, or `download bioclim values`."
        )

    results = download_files(requested_files, args.data)
    successful_files = {
        file_path for file_path, result in zip(requested_files, results, strict=True) if result.success
    }
    extract_results = (
        extract_downloaded_file_groups(requested_file_groups, args.data, successful_files) if args.extract else []
    )
    failures = [result for result in results if not result.success]
    extract_failures = [result for result in extract_results if not result.success]
    skipped = [result for result in results if result.skipped]
    downloaded = [result for result in results if result.success and not result.skipped]

    print(
        f"Finished: {len(downloaded)} downloaded, {len(skipped)} skipped, "
        f"{len(failures)} failed, {len(extract_failures)} extraction failed."
    )
    return 1 if failures or extract_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
