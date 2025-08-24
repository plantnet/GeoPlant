"""Configuration objects for GeoPlant XGBoost experiments.

The :class:`ExperimentConfig` defines schema hints, ablation groups, and model
hyperparameters. The :class:`PredictorPairSpec` describes a single predictor
family provided as **separate** train/test CSVs. Keep variable names descriptive
and avoid abbreviations to improve readability and maintainability.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PredictorPairSpec:
    """Descriptor of a predictor family given as separate TRAIN/TEST CSVs.

    Each CSV must contain a `surveyId` column and one or more **numeric** columns.
    Non-numeric columns are ignored during ingestion.

    Attributes:
        name: Logical identifier for this predictor family (e.g. "bioclim").
        group: Feature family name used in ablations (e.g. "climatic", "soilgrids").
        prefix: Prefix applied to all numeric columns from this family (e.g. "clim_").
        train_path: Path to the TRAIN CSV with `surveyId` and numeric columns.
        test_path: Path to the TEST CSV with `surveyId` and numeric columns.
    """

    name: str
    group: str
    prefix: str
    train_path: str
    test_path: str


@dataclass
class ExperimentConfig:
    """Experiment configuration and schema hints for GeoPlant baselines.

    Data schema:
        sample_id_col:
            Normalized name of the survey key inside the pipeline.
            Input CSVs use `surveyId`; we rename to this (default: "survey_id").
        species_prefix:
            Prefix for species columns in wide labels (default: "sp_").

    Predictors:
        predictor_pairs:
            List of :class:`PredictorPairSpec` describing per-family train/test CSVs.

    Feature families (ablation control):
        group_prefixes:
            Mapping family name → list of column prefixes. Columns with any listed
            prefix belong to that family.
        ablations:
            List of family combinations to evaluate (e.g., [["climatic"], ["climatic","soilgrids"]]).

    Modeling:
        xgb_params:
            Keyword arguments for :class:`xgboost.XGBClassifier` (compatible with xgboost 3.x).
        early_stopping_rounds:
            Early stopping patience set on the estimator.

    Selection:
        fixed_top_k:
            Constant Top‑K if `use_richness_estimator` is False.
        use_richness_estimator:
            If True, a classifier predicts per-sample richness bin → mapped to mean richness → +offset.
        richness_offset:
            Integer added to the estimated richness to form Top‑K.

    Species space:
        top_species_n:
            Keep the most frequent species up to this limit.
        min_pos_per_species:
            Drop species with fewer positives than this threshold.

    Misc:
        output_dir:
            Folder path for artifacts.

    Notes:
        - All functions accept and return **pandas DataFrames** with clear column names.
        - Avoid cryptic temporary names like `Xtr`, `Yte`. Use descriptive names.
    """

    # Schema
    sample_id_col: str = "survey_id"
    species_prefix: str = "sp_"
    # Predictors
    predictor_pairs: List[PredictorPairSpec] = field(default_factory=list)
    # Feature families → prefixes
    group_prefixes: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "location": ["lat", "lon", "elev", "loc_"],
            "climatic": ["clim_"],
            "soilgrids": ["soil_"],
            "landcover": ["lc_"],
            "humanfoot": ["hfp_"],
            "elevation": ["elev_"],
            "meta": ["meta_"],
        }
    )
    # Species space
    top_species_n: int = 500
    min_pos_per_species: int = 5
    # XGBoost params (3.x compatible)
    xgb_params: Dict = field(
        default_factory=lambda: dict(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            tree_method="hist",
            n_jobs=8,
            random_state=42,
            eval_metric="logloss",
            verbosity=0,
        )
    )
    early_stopping_rounds: int = 30
    # Top‑K selection
    fixed_top_k: int = 25
    use_richness_estimator: bool = True
    richness_offset: int = 5
    # Ablations
    ablations: List[List[str]] = field(default_factory=lambda: [["climatic"]])
    # Output
    output_dir: str = "outputs"
