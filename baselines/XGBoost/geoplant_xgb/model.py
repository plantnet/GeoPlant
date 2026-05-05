"""Model training and inference helpers."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm.auto import tqdm

from .config import ExperimentConfig


def _get_xgb():
    try:
        import xgboost as xgb
    except Exception as exc:  # pragma: no cover - depends on local native runtime
        raise RuntimeError(
            "xgboost could not be imported. Install a working XGBoost runtime "
            "before calling training helpers."
        ) from exc
    return xgb


def _train_single_species(
    feature_array: np.ndarray,
    target_binary: np.ndarray,
    cfg: ExperimentConfig,
) -> Any:
    """Fit one XGBoost classifier with early stopping for a single species."""
    xgb = _get_xgb()
    model = xgb.XGBClassifier(
        **cfg.xgb_params,
        early_stopping_rounds=cfg.early_stopping_rounds,
    )
    stratify = target_binary if np.unique(target_binary).size > 1 else None
    X_train, X_valid, y_train, y_valid = train_test_split(
        feature_array,
        target_binary,
        test_size=0.1,
        random_state=cfg.xgb_params.get("random_state", 42),
        stratify=stratify,
    )
    model.fit(X_train, y_train, eval_set=[(X_valid, y_valid)])
    return model


def train_ovr(
    train_features: pd.DataFrame,
    train_labels: pd.DataFrame,
    species_column_names: list[str],
    cfg: ExperimentConfig,
) -> Dict[str, Any]:
    """Train one-vs-rest classifiers for the selected species columns."""
    feature_array = train_features.values.astype(np.float32)
    models: Dict[str, Any] = {}
    for species_name in tqdm(species_column_names, desc="Training OVR models", leave=False):
        target = train_labels[species_name].values.astype(np.int32)
        if target.max() == 0:
            continue
        models[species_name] = _train_single_species(feature_array, target, cfg)
    return models


def predict_scores(
    models_by_species: Dict[str, Any],
    features_matrix: pd.DataFrame,
    species_column_names: list[str],
) -> np.ndarray:
    """Predict class-1 probabilities in the given species order."""
    scores = np.zeros((len(features_matrix), len(species_column_names)), dtype=np.float32)
    feature_array = features_matrix.values.astype(np.float32)
    for index, species_name in enumerate(species_column_names):
        model = models_by_species.get(species_name)
        if model is None:
            continue
        scores[:, index] = model.predict_proba(feature_array)[:, 1]
    return scores


def train_richness_estimator(
    train_features: pd.DataFrame,
    train_labels: pd.DataFrame,
    cfg: ExperimentConfig,
    nbins: int = 15,
) -> tuple[Any, np.ndarray, dict[int, float]]:
    """Train a multiclass classifier that predicts sample richness bins."""
    xgb = _get_xgb()
    richness = train_labels.sum(axis=1).values.astype(np.int32)
    quantiles = np.linspace(0, 1, nbins + 1)
    bin_edges = np.unique(np.quantile(richness, quantiles))
    if bin_edges.size < 2:
        bin_edges = np.array([-0.5, float(richness.max()) + 0.5], dtype=float)
        bins = np.zeros_like(richness)
    else:
        bin_edges[0] = -0.5
        bins = np.digitize(richness, bin_edges[1:], right=True)

    bin_to_mean = {
        int(bin_index): float(richness[bins == bin_index].mean())
        for bin_index in np.unique(bins)
    }

    classifier = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method=cfg.xgb_params.get("tree_method", "hist"),
        random_state=cfg.xgb_params.get("random_state", 42),
        n_jobs=cfg.xgb_params.get("n_jobs", 8),
        eval_metric="mlogloss",
        early_stopping_rounds=20,
    )
    stratify = bins if np.unique(bins).size > 1 else None
    X_train, X_valid, y_train, y_valid = train_test_split(
        train_features.values.astype(np.float32),
        bins,
        test_size=0.1,
        random_state=cfg.xgb_params.get("random_state", 42),
        stratify=stratify,
    )
    classifier.fit(X_train, y_train, eval_set=[(X_valid, y_valid)])
    return classifier, bin_edges, bin_to_mean


def estimate_topk(
    classifier: Any,
    bin_edges: np.ndarray,
    bin_to_mean_richness: dict[int, float],
    features_matrix: pd.DataFrame,
    offset: int = 5,
) -> np.ndarray:
    """Predict a Top-K value per sample from the richness estimator."""
    del bin_edges
    predicted_bins = classifier.predict(features_matrix.values.astype(np.float32))
    mean_richness = np.array(
        [bin_to_mean_richness.get(int(bin_index), 0.0) for bin_index in predicted_bins],
        dtype=np.float32,
    )
    return np.clip(np.rint(mean_richness).astype(int) + int(offset), 1, 5000)
