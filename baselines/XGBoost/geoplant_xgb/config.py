"""Configuration objects for GeoPlant XGBoost experiments."""

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

DEFAULT_XGB_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "reg_lambda": 1.0,
    "tree_method": "hist",
    "n_jobs": 8,
    "random_state": 42,
    "eval_metric": "logloss",
    "verbosity": 0,
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
    """Experiment configuration and schema hints for GeoPlant baselines."""

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
    xgb_params: dict = field(default_factory=lambda: dict(DEFAULT_XGB_PARAMS))
    early_stopping_rounds: int = 30
    fixed_top_k: int = 25
    use_richness_estimator: bool = True
    richness_offset: int = 5
    ablations: list[list[str]] = field(default_factory=lambda: [["climatic"]])
    output_dir: str = "outputs"

