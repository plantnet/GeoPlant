"""GeoPlant dataset downloader CLI."""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path

import requests
from tqdm import tqdm

try:
    from .config import METADATA, PRESENCE_ABSENCE, PRESENCE_ONLY, RASTERS, URL_STRUCT, VARIABLES
except ImportError:  # pragma: no cover - supports direct script execution
    from config import METADATA, PRESENCE_ABSENCE, PRESENCE_ONLY, RASTERS, URL_STRUCT, VARIABLES


@dataclass(frozen=True)
class DownloadResult:
    file_path: str
    success: bool
    error: str | None = None
    skipped: bool = False


def find_url(file_path: str) -> str:
    """Resolve a direct download URL from the published Seafile page."""
    response = requests.get(URL_STRUCT.format(file_path), timeout=60)
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


def files_for_variable(structure: dict, cubes: bool, variable: str) -> list[str]:
    """Return manifest paths for a given variable and storage format."""
    variable_entry = structure.get(variable)
    if not variable_entry:
        return []
    if cubes:
        return list(variable_entry.get("cubes", []))
    return list(variable_entry.get("csvs", variable_entry.get("not_cubes", [])))


def selected_variables(args: argparse.Namespace) -> list[str]:
    """Return variables requested on the CLI."""
    if args.all_variables:
        return list(VARIABLES)
    return [variable for variable in VARIABLES if getattr(args, variable)]


def selected_sources(args: argparse.Namespace) -> list[str]:
    """Return requested source subsets using `po`/`pa` keys."""
    if args.presence_only and args.presence_absence:
        return ["po", "pa"]
    if args.presence_only:
        return ["po"]
    if args.presence_absence:
        return ["pa"]
    return ["po", "pa"]


def collect_requested_files(args: argparse.Namespace) -> list[str]:
    """Resolve requested files without downloading them."""
    requested_files: list[str] = []

    if args.metadata:
        for source_name in selected_sources(args):
            requested_files.extend(METADATA[source_name])

    if args.rasters:
        for variable in selected_variables(args):
            raster_path = RASTERS.get(variable)
            if raster_path:
                requested_files.append(raster_path)

    if args.pre_extracted:
        variables_to_download = selected_variables(args)
        if not variables_to_download:
            raise ValueError("`--pre-extracted` requires at least one variable flag or `--all-variables`.")
        source_names = selected_sources(args)
        for variable in variables_to_download:
            if "po" in source_names:
                requested_files.extend(files_for_variable(PRESENCE_ONLY, args.cube, variable))
            if "pa" in source_names:
                requested_files.extend(files_for_variable(PRESENCE_ABSENCE, args.cube, variable))

    deduplicated: list[str] = []
    seen = set()
    for file_path in requested_files:
        if file_path not in seen:
            deduplicated.append(file_path)
            seen.add(file_path)
    return deduplicated


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "GeoPlant Dataset Downloader.\n"
            "Download metadata, rasters, and pre-extracted GeoPlant modalities "
            "for presence-only and/or presence-absence subsets."
        )
    )
    parser.add_argument(
        "--data",
        default="data",
        help='Destination directory for downloaded files (default: "data").',
    )

    data_group = parser.add_argument_group("Data type")
    data_group.add_argument(
        "--metadata",
        action="store_true",
        help="Download metadata for the selected subsets. Defaults to both subsets if none is specified.",
    )
    data_group.add_argument(
        "--rasters",
        action="store_true",
        help="Download complete raster datasets for the selected variables.",
    )
    data_group.add_argument(
        "--pre-extracted",
        action="store_true",
        help="Download pre-extracted values or cube archives for the selected variables.",
    )
    data_group.add_argument(
        "--cube",
        action="store_true",
        help="Download cube files instead of CSV values when a cube version exists.",
    )

    source_group = parser.add_argument_group("Data sources")
    source_group.add_argument(
        "--presence-only",
        action="store_true",
        help="Select presence-only files.",
    )
    source_group.add_argument(
        "--presence-absence",
        action="store_true",
        help="Select presence-absence files.",
    )

    variable_group = parser.add_argument_group("Variables")
    for variable in VARIABLES:
        variable_group.add_argument(
            f"--{variable}",
            action="store_true",
            help=f'Download data related to "{variable}".',
        )
    variable_group.add_argument(
        "--all-variables",
        action="store_true",
        help="Select all variables.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    os.makedirs(args.data, exist_ok=True)

    try:
        requested_files = collect_requested_files(args)
    except ValueError as exc:
        parser.error(str(exc))

    if not requested_files:
        parser.error("No files selected. Choose at least one of `--metadata`, `--rasters`, or `--pre-extracted`.")

    results = [process_download(file_path, args.data) for file_path in requested_files]
    failures = [result for result in results if not result.success]
    skipped = [result for result in results if result.skipped]
    downloaded = [result for result in results if result.success and not result.skipped]

    print(f"Finished: {len(downloaded)} downloaded, {len(skipped)} skipped, {len(failures)} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
