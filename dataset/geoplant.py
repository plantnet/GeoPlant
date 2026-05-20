"""Python access point for selecting and downloading GeoPlant data."""

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

Source = Literal["po", "pa", "both"]
VariableSelection = str | list[str]
SatelliteModalitySelection = str | list[str]


class GeoPlant:
    """Resolve and download GeoPlant files under one local data root."""

    def __init__(self, root: str | Path = "data") -> None:
        self.root = Path(root)

    def path(self, file_path: str | Path) -> Path:
        """Return the local path for a manifest-relative file."""
        return self.root / file_path

    def files(self, **kwargs) -> list[str]:
        """Return manifest paths selected by this request without downloading."""
        return resolve_requested_files(**self._normalize_request(kwargs))

    def file_groups(self, **kwargs) -> list[list[str]]:
        """Return extraction-aware manifest groups selected by this request."""
        return resolve_requested_file_groups(**self._normalize_request(kwargs))

    def download(self, *, extract: bool = False, overwrite: bool = False, **kwargs) -> list[DownloadResult]:
        """Download selected files into ``root``."""
        requested_file_groups = self.file_groups(**kwargs)
        requested_files = flatten_file_groups(requested_file_groups)
        if not requested_files:
            raise ValueError("No files selected. Specify at least one data category.")

        results = download_files(requested_files, self.root)
        if extract:
            successful_files = {
                file_path for file_path, result in zip(requested_files, results, strict=True) if result.success
            }
            extract_downloaded_file_groups(requested_file_groups, self.root, successful_files, overwrite=overwrite)
        return results

    def extract(self, *, overwrite: bool = False, **kwargs) -> list[ExtractResult]:
        """Extract selected local zip archives under ``root``."""
        requested_file_groups = self.file_groups(**kwargs)
        requested_files = flatten_file_groups(requested_file_groups)
        return extract_downloaded_file_groups(
            requested_file_groups,
            self.root,
            set(requested_files),
            overwrite=overwrite,
        )

    @staticmethod
    def _normalize_request(kwargs: dict) -> dict:
        """Validate friendly API arguments for downloader resolution."""
        request = {
            "metadata": bool(kwargs.pop("metadata", False)),
            "rasters": bool(kwargs.pop("rasters", False)),
            "environmental_values": bool(kwargs.pop("environmental_values", False)),
            "bioclim_values": bool(kwargs.pop("bioclim_values", False)),
            "bioclim_cubes": bool(kwargs.pop("bioclim_cubes", False)),
            "landsat_values": bool(kwargs.pop("landsat_values", False)),
            "landsat_cubes": bool(kwargs.pop("landsat_cubes", False)),
            "satellite_data": bool(kwargs.pop("satellite_data", False)),
            "legacy": bool(kwargs.pop("legacy", False)),
            "source": kwargs.pop("source", "both"),
            "variables": GeoPlant._normalize_variables(kwargs.pop("variables", None)),
            "satellite_modalities": GeoPlant._normalize_modalities(kwargs.pop("satellite_modalities", None)),
        }
        if kwargs:
            raise TypeError(f"Unknown GeoPlant request arguments: {sorted(kwargs)}")
        return request

    @staticmethod
    def _normalize_variables(variables: VariableSelection | None) -> list[str] | None:
        if variables is None:
            return None
        if variables == "all":
            return list(VARIABLES)
        if isinstance(variables, str):
            variables = [variables]
        unknown = sorted(set(variables).difference(VARIABLES))
        if unknown:
            raise ValueError(f"Unknown variables: {unknown}")
        return list(variables)

    @staticmethod
    def _normalize_modalities(modalities: SatelliteModalitySelection | None) -> list[str] | None:
        if modalities is None:
            return None
        if isinstance(modalities, str):
            modalities = [modalities]
        return [modality.replace("_", "-") for modality in modalities]
