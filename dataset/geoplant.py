"""Python access point for selecting and downloading GeoPlant data.

The :class:`GeoPlant` class is a small wrapper around the shared downloader
manifest. It keeps the local data root in one place while each ``files`` or
``download`` call declares the subset of data it needs. The underlying file
resolution and download code is the same as the command-line interface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from .config import VARIABLES
from .data_download import (
    DownloadResult,
    ExtractResult,
    download_files,
    extract_downloaded_file_groups,
    flatten_file_groups,
    resolve_requested_file_groups,
    resolve_requested_files,
)

Source = Literal["po", "pa"]
SourceSelection = Source | list[Source]
VariableSelection = str | list[str]


class GeoPlant:
    """Resolve and download GeoPlant files under one local data root.

    Parameters
    ----------
    root:
        Directory where downloaded files are stored. Paths from the Seafile
        manifest are preserved under this root.
    """

    def __init__(
        self,
        root: str | Path = "data",
    ) -> None:
        self.root = Path(root)

    def path(self, file_path: str | Path) -> Path:
        """Return the local path for a manifest-relative file.

        Parameters
        ----------
        file_path:
            Path as listed in the GeoPlant manifest, for example
            ``"PresenceAbsenceSurveys/PA_metadata_test_iid.csv"``.
        """
        return self.root / file_path

    def files(
        self,
        *,
        metadata: bool | SourceSelection = False,
        rasters: bool | VariableSelection = False,
        pre_extracted: bool = False,
        source: SourceSelection | None = None,
        sources: Source | list[Source] | None = None,
        variables: str | list[str] | None = None,
        cube: bool = False,
        cubes: bool = False,
        legacy: bool = False,
        legacy_rasters: bool = False,
    ) -> list[str]:
        """Return manifest paths selected by this request without downloading.

        Use this to inspect what would be downloaded before calling
        :meth:`download`.

        Examples
        --------
        ``files(metadata="pa")`` selects PA metadata files.
        ``files(source="pa", variables="climate", cubes=True)`` selects PA
        bioclimatic cube archives.
        ``legacy=True`` selects legacy v1 files for versioned rasters
        and raster-derived environmental values when available.
        """
        request = self._resolve_request(
            metadata=metadata,
            rasters=rasters,
            pre_extracted=pre_extracted,
            source=source,
            sources=sources,
            variables=variables,
            cube=cube,
            cubes=cubes,
            legacy=legacy,
            legacy_rasters=legacy_rasters,
        )
        return resolve_requested_files(
            metadata=request["metadata"],
            rasters=request["rasters"],
            pre_extracted=request["pre_extracted"],
            cube=request["cube"],
            legacy=request["legacy"],
            sources=request["sources"],
            variables=request["variables"],
        )

    def file_groups(
        self,
        *,
        metadata: bool | SourceSelection = False,
        rasters: bool | VariableSelection = False,
        pre_extracted: bool = False,
        source: SourceSelection | None = None,
        sources: Source | list[Source] | None = None,
        variables: str | list[str] | None = None,
        cube: bool = False,
        cubes: bool = False,
        legacy: bool = False,
        legacy_rasters: bool = False,
    ) -> list[list[str]]:
        """Return extraction-aware manifest groups selected by this request.

        Most files are returned as single-item groups. Multipart datasets are
        returned as one group containing all required files so callers can keep
        download and extraction behavior atomic.
        """
        request = self._resolve_request(
            metadata=metadata,
            rasters=rasters,
            pre_extracted=pre_extracted,
            source=source,
            sources=sources,
            variables=variables,
            cube=cube,
            cubes=cubes,
            legacy=legacy,
            legacy_rasters=legacy_rasters,
        )
        return resolve_requested_file_groups(
            metadata=request["metadata"],
            rasters=request["rasters"],
            pre_extracted=request["pre_extracted"],
            cube=request["cube"],
            legacy=request["legacy"],
            sources=request["sources"],
            variables=request["variables"],
        )

    def download(
        self,
        *,
        metadata: bool | SourceSelection = False,
        rasters: bool | VariableSelection = False,
        pre_extracted: bool = False,
        source: SourceSelection | None = None,
        sources: Source | list[Source] | None = None,
        variables: str | list[str] | None = None,
        cube: bool = False,
        cubes: bool = False,
        extract: bool = False,
        overwrite: bool = False,
        legacy: bool = False,
        legacy_rasters: bool = False,
    ) -> list[DownloadResult]:
        """Download the files selected by this request into ``root``.

        Examples
        --------
        ``download(metadata="pa")`` downloads PA metadata files.
        ``download(source="pa", variables="climate")`` downloads PA
        bioclimatic CSV values.
        ``download(source="pa", variables="climate", cubes=True)`` downloads
        PA bioclimatic cube archives. Set ``extract=True`` to extract selected
        zip archives after download.
        ``legacy=True`` selects legacy v1 files for versioned rasters
        and raster-derived environmental values when available.

        Returns
        -------
        list[DownloadResult]
            One result per selected manifest path, including skipped files and
            download failures. Network errors are captured in the result objects
            by the shared downloader.
        """
        requested_file_groups = self.file_groups(
            metadata=metadata,
            rasters=rasters,
            pre_extracted=pre_extracted,
            source=source,
            sources=sources,
            variables=variables,
            cube=cube,
            cubes=cubes,
            legacy=legacy,
            legacy_rasters=legacy_rasters,
        )
        requested_files = flatten_file_groups(requested_file_groups)
        if not requested_files:
            raise ValueError("No files selected. Specify metadata, rasters, variables, or cubes.")
        results = download_files(requested_files, self.root)
        if extract:
            successful_files = {
                file_path for file_path, result in zip(requested_files, results, strict=True) if result.success
            }
            extract_downloaded_file_groups(requested_file_groups, self.root, successful_files, overwrite=overwrite)
        return results

    def extract(
        self,
        *,
        metadata: bool | SourceSelection = False,
        rasters: bool | VariableSelection = False,
        pre_extracted: bool = False,
        source: SourceSelection | None = None,
        sources: Source | list[Source] | None = None,
        variables: str | list[str] | None = None,
        cube: bool = False,
        cubes: bool = False,
        overwrite: bool = False,
        legacy: bool = False,
        legacy_rasters: bool = False,
    ) -> list[ExtractResult]:
        """Extract selected local zip archives under ``root``.

        This does not download missing files. It resolves the same manifest
        selection as :meth:`files`, filters it to ``.zip`` archives, and keeps
        multipart archive groups in one shared extraction directory.
        """
        requested_file_groups = self.file_groups(
            metadata=metadata,
            rasters=rasters,
            pre_extracted=pre_extracted,
            source=source,
            sources=sources,
            variables=variables,
            cube=cube,
            cubes=cubes,
            legacy=legacy,
            legacy_rasters=legacy_rasters,
        )
        requested_files = flatten_file_groups(requested_file_groups)
        return extract_downloaded_file_groups(
            requested_file_groups,
            self.root,
            set(requested_files),
            overwrite=overwrite,
        )

    def _resolve_request(
        self,
        *,
        metadata: bool | SourceSelection,
        rasters: bool | VariableSelection,
        pre_extracted: bool,
        source: SourceSelection | None,
        sources: SourceSelection | None,
        variables: VariableSelection | None,
        cube: bool,
        cubes: bool,
        legacy: bool,
        legacy_rasters: bool,
    ) -> dict[str, bool | list[str] | None]:
        """Normalize friendly API selections into downloader flags."""
        selected_sources = self._combine_sources(source, sources)
        selected_variables = self._normalize_variables(variables)

        metadata_requested = bool(metadata)
        if isinstance(metadata, (str, list)):
            selected_sources = self._combine_sources(selected_sources, metadata)
            metadata_requested = True

        rasters_requested = bool(rasters)
        if isinstance(rasters, (str, list)):
            selected_variables = self._combine_variables(selected_variables, rasters)
            rasters_requested = True

        cube_requested = cube or cubes
        pre_extracted_requested = pre_extracted or cube_requested
        if selected_variables is not None and not metadata_requested and not rasters_requested:
            pre_extracted_requested = True

        return {
            "metadata": metadata_requested,
            "rasters": rasters_requested,
            "pre_extracted": pre_extracted_requested,
            "cube": cube_requested,
            "legacy": legacy or legacy_rasters,
            "sources": selected_sources,
            "variables": selected_variables,
        }

    @staticmethod
    def _combine_sources(
        first: SourceSelection | list[str] | None,
        second: SourceSelection | list[str] | None,
    ) -> list[str] | None:
        """Merge two compatible source selections."""
        first_sources = GeoPlant._normalize_sources(first)
        second_sources = GeoPlant._normalize_sources(second)
        if first_sources is None:
            return second_sources
        if second_sources is None:
            return first_sources
        combined = []
        for source in first_sources + second_sources:
            if source not in combined:
                combined.append(source)
        return combined

    @staticmethod
    def _normalize_sources(sources: SourceSelection | list[str] | None) -> list[str] | None:
        """Validate and normalize source selections for manifest resolution."""
        if sources is None:
            return None
        if isinstance(sources, str):
            sources = [sources]
        unknown_sources = sorted(set(sources).difference({"po", "pa"}))
        if unknown_sources:
            raise ValueError(f"Unknown sources: {unknown_sources}")
        return list(sources)

    @staticmethod
    def _combine_variables(
        first: list[str] | None,
        second: VariableSelection | list[str] | None,
    ) -> list[str] | None:
        """Merge two compatible variable selections."""
        second_variables = GeoPlant._normalize_variables(second)
        if first is None:
            return second_variables
        if second_variables is None:
            return first
        combined = []
        for variable in first + second_variables:
            if variable not in combined:
                combined.append(variable)
        return combined

    @staticmethod
    def _normalize_variables(variables: VariableSelection | list[str] | None) -> list[str] | None:
        """Validate and normalize variable selections for manifest resolution."""
        if variables is None:
            return None
        if variables == "all":
            return list(VARIABLES)
        if isinstance(variables, str):
            variables = [variables]
        unknown_variables = sorted(set(variables).difference(VARIABLES))
        if unknown_variables:
            raise ValueError(f"Unknown variables: {unknown_variables}")
        return list(variables)
