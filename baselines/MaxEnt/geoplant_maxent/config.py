"""Configuration objects for GeoPlant MaxEnt experiments."""

from __future__ import annotations

from dataclasses import dataclass, field


DEFAULT_GROUP_PREFIXES = {
    "location": ["lat", "lon", "loc_", "elev_"],
    "climatic": ["clim_"],
    "soilgrids": ["soil_"],
    "landcover": ["lc_"],
    "humanfoot": ["hfp_"],
    "meta": ["meta_"],
}

DEFAULT_MAXENT_PARAMS = {
    "C": 1.0,
    "max_iter": 1000,
    "solver": "lbfgs",
    "class_weight": "balanced",
}

DEFAULT_METADATA_CATEGORICAL = [
    "country",
    "region",
    "taxonRank",
    "county",
    "district",
]
DEFAULT_METADATA_NUMERIC = ["geoUncertaintyInM", "areaInM2", "year"]
DEFAULT_METADATA_GEO = ["lat", "lon"]
DEFAULT_METADATA_ALIASES = {"disctrict": "district"}


@dataclass(frozen=True)
class PredictorPairSpec:
    """Descriptor of a predictor family provided as separate train/test CSVs."""

    name: str
    group: str
    prefix: str
    train_path: str
    test_path: str


@dataclass
class ExperimentConfig:
    """Experiment configuration and schema hints for GeoPlant MaxEnt baselines."""

    sample_id_col: str = "survey_id"
    source_sample_id_col: str = "surveyId"
    species_id_col: str = "speciesId"
    species_prefix: str = "sp_"
    predictor_pairs: list[PredictorPairSpec] = field(default_factory=list)
    group_prefixes: dict[str, list[str]] = field(
        default_factory=lambda: dict(DEFAULT_GROUP_PREFIXES)
    )
    metadata_categorical_columns: list[str] = field(
        default_factory=lambda: list(DEFAULT_METADATA_CATEGORICAL)
    )
    metadata_numeric_columns: list[str] = field(
        default_factory=lambda: list(DEFAULT_METADATA_NUMERIC)
    )
    metadata_geo_columns: list[str] = field(
        default_factory=lambda: list(DEFAULT_METADATA_GEO)
    )
    metadata_aliases: dict[str, str] = field(
        default_factory=lambda: dict(DEFAULT_METADATA_ALIASES)
    )
    top_species_n: int = 500
    min_pos_per_species: int = 5
    maxent_params: dict = field(default_factory=lambda: dict(DEFAULT_MAXENT_PARAMS))
    fixed_top_k: int = 25
    use_richness_estimator: bool = True
    richness_offset: int = 5
    richness_nbins: int = 15
    ablations: list[list[str]] = field(default_factory=lambda: [["climatic"]])
    output_dir: str = "outputs"
