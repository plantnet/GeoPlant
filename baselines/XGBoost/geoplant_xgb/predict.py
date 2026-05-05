"""Prediction export helpers."""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from .model import predict_scores


def export_predictions(
    models_by_species: Dict[str, object],
    features_matrix: pd.DataFrame,
    species_column_names: list[str],
    topk_per_sample,
    sample_id_col: str,
) -> pd.DataFrame:
    """Export predictions as a surveyId/predictions table."""
    if sample_id_col not in features_matrix.columns:
        raise ValueError(f"`{sample_id_col}` missing in features_matrix")

    scoring_features = features_matrix.drop(columns=[sample_id_col])
    scores = predict_scores(models_by_species, scoring_features, species_column_names)
    if isinstance(topk_per_sample, int):
        k_values = np.full(scores.shape[0], int(topk_per_sample), dtype=int)
    else:
        k_values = np.asarray(topk_per_sample, dtype=int)
        if k_values.shape[0] != scores.shape[0]:
            raise ValueError("topk_per_sample length must match the number of samples")

    sorted_idx = np.argsort(-scores, axis=1)
    predictions = []
    for row_index in range(scores.shape[0]):
        k_value = max(1, min(int(k_values[row_index]), scores.shape[1]))
        selected = sorted_idx[row_index, :k_value]
        species_ids = [species_column_names[index].removeprefix("sp_") for index in selected]
        predictions.append(" ".join(species_ids))

    return pd.DataFrame(
        {
            "surveyId": features_matrix[sample_id_col].values,
            "predictions": predictions,
        }
    )
