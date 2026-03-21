"""Model training and inference helpers for MaxEnt-style baselines."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from tqdm.auto import tqdm

from .config import ExperimentConfig


def _make_binary_classifier(cfg: ExperimentConfig) -> LogisticRegression:
    params = dict(cfg.maxent_params)
    return LogisticRegression(**params)


def _make_multiclass_classifier(cfg: ExperimentConfig) -> LogisticRegression:
    params = dict(cfg.maxent_params)
    if params.get("solver") == "liblinear":
        params["solver"] = "lbfgs"
    params.pop("multi_class", None)
    return LogisticRegression(**params)


def _fit_standardized_model(
    model: LogisticRegression,
    feature_array: np.ndarray,
    targets: np.ndarray,
) -> dict[str, Any]:
    means = feature_array.mean(axis=0)
    stds = feature_array.std(axis=0)
    stds = np.where(stds == 0.0, 1.0, stds)
    X_scaled = (feature_array - means) / stds
    model.fit(X_scaled, targets)
    return {"model": model, "means": means, "stds": stds}


def _transform(features_matrix: pd.DataFrame, trained_object: dict[str, Any]) -> np.ndarray:
    feature_array = features_matrix.values.astype(np.float32)
    return (feature_array - trained_object["means"]) / trained_object["stds"]


class _ConstantPredictor:
    def __init__(self, value: int):
        self.value = int(value)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.full(X.shape[0], self.value, dtype=np.int32)


def train_ovr(
    train_features: pd.DataFrame,
    train_labels: pd.DataFrame,
    species_column_names: list[str],
    cfg: ExperimentConfig,
) -> Dict[str, dict[str, Any]]:
    """Train one-vs-rest MaxEnt classifiers for the selected species columns."""
    feature_array = train_features.values.astype(np.float32)
    models: Dict[str, dict[str, Any]] = {}
    for species_name in tqdm(species_column_names, desc="Training MaxEnt models", leave=False):
        target = train_labels[species_name].values.astype(np.int32)
        if target.max() == 0 or np.unique(target).size < 2:
            continue
        models[species_name] = _fit_standardized_model(
            _make_binary_classifier(cfg),
            feature_array,
            target,
        )
    return models


def predict_scores(
    models_by_species: Dict[str, dict[str, Any]],
    features_matrix: pd.DataFrame,
    species_column_names: list[str],
) -> np.ndarray:
    """Predict class-1 probabilities in the given species order."""
    scores = np.zeros((len(features_matrix), len(species_column_names)), dtype=np.float32)
    for index, species_name in enumerate(species_column_names):
        trained = models_by_species.get(species_name)
        if trained is None:
            continue
        feature_array = _transform(features_matrix, trained)
        scores[:, index] = trained["model"].predict_proba(feature_array)[:, 1]
    return scores


def train_richness_estimator(
    train_features: pd.DataFrame,
    train_labels: pd.DataFrame,
    cfg: ExperimentConfig,
    nbins: int | None = None,
) -> tuple[dict[str, Any], np.ndarray, dict[int, float]]:
    """Train a multiclass MaxEnt classifier that predicts sample richness bins."""
    richness = train_labels.sum(axis=1).values.astype(np.int32)
    effective_nbins = int(nbins or cfg.richness_nbins)
    quantiles = np.linspace(0, 1, effective_nbins + 1)
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
    if np.unique(bins).size < 2:
        means = train_features.values.astype(np.float32).mean(axis=0)
        stds = train_features.values.astype(np.float32).std(axis=0)
        stds = np.where(stds == 0.0, 1.0, stds)
        return {"model": _ConstantPredictor(int(bins[0])), "means": means, "stds": stds}, bin_edges, bin_to_mean
    trained = _fit_standardized_model(
        _make_multiclass_classifier(cfg),
        train_features.values.astype(np.float32),
        bins,
    )
    return trained, bin_edges, bin_to_mean


def estimate_topk(
    classifier: dict[str, Any],
    bin_edges: np.ndarray,
    bin_to_mean_richness: dict[int, float],
    features_matrix: pd.DataFrame,
    offset: int = 5,
) -> np.ndarray:
    """Predict a Top-K value per sample from the richness estimator."""
    del bin_edges
    feature_array = _transform(features_matrix, classifier)
    predicted_bins = classifier["model"].predict(feature_array)
    mean_richness = np.array(
        [bin_to_mean_richness.get(int(bin_index), 0.0) for bin_index in predicted_bins],
        dtype=np.float32,
    )
    return np.clip(np.rint(mean_richness).astype(int) + int(offset), 1, 5000)