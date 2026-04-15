from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import torch
from torch.utils.data import Dataset


def parse_species_set(value: object) -> set[int]:
    if isinstance(value, set):
        return {int(species_id) for species_id in value}
    if isinstance(value, (list, tuple)):
        return {int(species_id) for species_id in value}
    if not isinstance(value, str):
        return set()

    stripped = value.strip().strip("{}")
    if not stripped:
        return set()

    return {
        int(token.strip())
        for token in stripped.split(",")
        if token.strip()
    }


def load_metadata_frame(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if "species_set" not in frame.columns:
        raise ValueError(f"{path} does not contain a species_set column")
    frame = frame.copy()
    frame["species_set"] = frame["species_set"].apply(parse_species_set)
    return frame


def split_frame(
    frame: pd.DataFrame,
    *,
    source: str | None = None,
    subset: str | None = None,
) -> pd.DataFrame:
    result = frame
    if source is not None:
        result = result[result["source"] == source]
    if subset is not None:
        result = result[result["subset"] == subset]
    return result.reset_index(drop=True)


@dataclass
class SpeciesExample:
    survey_id: str
    x: torch.Tensor
    loc: torch.Tensor


class SpeciesSetDataset(Dataset[SpeciesExample]):
    def __init__(self, frame: pd.DataFrame, num_species: int):
        self.frame = frame.reset_index(drop=True).copy()
        if "species_set" not in self.frame.columns:
            raise ValueError("SpeciesSetDataset requires a species_set column")
        self.frame["species_set"] = self.frame["species_set"].apply(parse_species_set)
        self.num_species = num_species
        self.lat_column = "lat" if "lat" in self.frame.columns else "latitude" if "latitude" in self.frame.columns else None
        self.lon_column = "lon" if "lon" in self.frame.columns else "longitude" if "longitude" in self.frame.columns else None

    def __len__(self) -> int:
        return len(self.frame)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor | str]:
        row = self.frame.iloc[index]
        vector = torch.zeros(self.num_species, dtype=torch.float32)
        species = row["species_set"]
        if species:
            vector[list(species)] = 1.0
        location = torch.zeros(2, dtype=torch.float32)
        if self.lat_column is not None and self.lon_column is not None:
            lat_value = pd.to_numeric(row[self.lat_column], errors="coerce")
            lon_value = pd.to_numeric(row[self.lon_column], errors="coerce")
            if pd.notna(lat_value) and pd.notna(lon_value):
                location = torch.tensor([float(lat_value), float(lon_value)], dtype=torch.float32)
        return {
            "survey_id": str(row.get("survey_id", index)),
            "x": vector,
            "loc": location,
        }
