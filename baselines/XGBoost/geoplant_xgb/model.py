"""Model training and inference (XGBoost 3.x compatible)."""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from tqdm.auto import tqdm

from .config import ExperimentConfig


def _train_single_species(
    feature_array: np.ndarray, target_binary: np.ndarray, cfg: ExperimentConfig
) -> xgb.XGBClassifier:
    """Fit one :class:`xgboost.XGBClassifier` with early stopping for a single species.

    Notes:
        xgboost 3.x: set `early_stopping_rounds` on the estimator, and pass only
        `eval_set` to :meth:`XGBClassifier.fit` (no `callbacks`, no `verbose`).
    """
    model = xgb.XGBClassifier(
        **cfg.xgb_params, early_stopping_rounds=cfg.early_stopping_rounds
    )
    stratify_vec = target_binary if target_binary.sum() > 0 else None
    X_train, X_valid, y_train, y_valid = train_test_split(
        feature_array,
        target_binary,
        test_size=0.1,
        random_state=42,
        stratify=stratify_vec,
    )
    model.fit(X_train, y_train, eval_set=[(X_valid, y_valid)])
    return model


def train_ovr(
    train_features: pd.DataFrame,
    train_labels: pd.DataFrame,
    species_column_names: List[str],
    cfg: ExperimentConfig,
) -> Dict[str, xgb.XGBClassifier]:
    """Train one-vs-rest classifiers (binary XGBoost per species)."""
    models: Dict[str, xgb.XGBClassifier] = {}
    feature_array = train_features.values.astype(np.float32)
    for species_name in tqdm(
        species_column_names, desc="Training OVR models", leave=False
    ):
        target = train_labels[species_name].values.astype(np.int32)
        if target.max() == 0:
            continue  # skip species with no positives
        models[species_name] = _train_single_species(feature_array, target, cfg)
    return models


def predict_scores(
    models_by_species: Dict[str, xgb.XGBClassifier],
    features_matrix: pd.DataFrame,
    species_column_names: List[str],
) -> np.ndarray:
    """Predict class-1 probabilities for each species in `species_column_names` order."""
    scores = np.zeros(
        (len(features_matrix), len(species_column_names)), dtype=np.float32
    )
    X_values = features_matrix.values
    for j, species_name in enumerate(species_column_names):
        if species_name in models_by_species:
            scores[:, j] = models_by_species[species_name].predict_proba(X_values)[:, 1]
    return scores


def train_richness_estimator(
    train_features: pd.DataFrame,
    train_labels: pd.DataFrame,
    cfg: ExperimentConfig,
    nbins: int = 15,
) -> Tuple[xgb.XGBClassifier, np.ndarray, dict[int, float]]:
    """Train a multi-class classifier to predict per-sample richness bin.

    Returns:
        (classifier, bin_edges, bin_index_to_mean_richness)
    """
    richness = train_labels.sum(axis=1).values.astype(np.int32)
    quantiles = np.linspace(0, 1, nbins + 1)
    bin_edges = np.unique(np.quantile(richness, quantiles))
    bin_edges[0] = -0.5  # sentinel for digitize
    bins = np.digitize(richness, bin_edges[1:], right=True)
    bin_to_mean = {int(b): float(richness[bins == b].mean()) for b in np.unique(bins)}

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
    X_train, X_valid, y_train, y_valid = train_test_split(
        train_features.values, bins, test_size=0.1, random_state=42, stratify=bins
    )
    classifier.fit(X_train, y_train, eval_set=[(X_valid, y_valid)])
    return classifier, bin_edges, bin_to_mean


def estimate_topk(
    classifier: xgb.XGBClassifier,
    bin_edges: np.ndarray,
    bin_to_mean_richness: dict[int, float],
    features_matrix: pd.DataFrame,
    offset: int = 5,
) -> np.ndarray:
    """Predict Top‑K per sample as round(mean_richness_for_bin) + `offset` (clipped to [1, 5000])."""
    predicted_bins = classifier.predict(features_matrix.values)
    mean_richness = np.array(
        [bin_to_mean_richness.get(int(b), 0.0) for b in predicted_bins],
        dtype=np.float32,
    )
    return np.clip(np.rint(mean_richness).astype(int) + int(offset), 1, 5000)
