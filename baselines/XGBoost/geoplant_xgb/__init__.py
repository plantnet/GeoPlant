"""GeoPlant XGBoost baseline utilities."""

from .config import ExperimentConfig, PredictorPairSpec
from .data import (
    align_features_with_labels,
    build_wide_labels_from_long_metadata,
    select_top_species,
    split_features_by_group,
)
from .evaluation import lists_to_wide, parse_solution
from .experiment import run_all, run_one_ablation
from .io_csv import (
    build_features_from_meta_and_predictors_pair,
    load_metadata_csv,
    load_predictor_pairs,
)
from .metrics import macro_auc, sample_f1_at_k, sample_recall_at_k
from .model import (
    estimate_topk,
    predict_scores,
    train_ovr,
    train_richness_estimator,
)
from .predict import export_predictions

__all__ = [
    "ExperimentConfig",
    "PredictorPairSpec",
    "align_features_with_labels",
    "build_features_from_meta_and_predictors_pair",
    "build_wide_labels_from_long_metadata",
    "estimate_topk",
    "export_predictions",
    "lists_to_wide",
    "load_metadata_csv",
    "load_predictor_pairs",
    "macro_auc",
    "parse_solution",
    "predict_scores",
    "run_all",
    "run_one_ablation",
    "sample_f1_at_k",
    "sample_recall_at_k",
    "select_top_species",
    "split_features_by_group",
    "train_ovr",
    "train_richness_estimator",
]
