"""Prediction export helpers."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from .model import predict_scores


def export_predictions(
    models_by_species: Dict[str, object],
    features_matrix: pd.DataFrame,
    species_column_names: List[str],
    topk_per_sample,
    sample_id_col: str,
) -> pd.DataFrame:
    """Export predictions as `[surveyId, predictions]` with space-separated species IDs."""
    scores = predict_scores(models_by_species, features_matrix, species_column_names)
    num_samples = scores.shape[0]
    if isinstance(topk_per_sample, int):
        k_arr = np.full(num_samples, int(topk_per_sample), dtype=int)
    else:
        k_arr = topk_per_sample.astype(int)
    sorted_idx = np.argsort(-scores, axis=1)
    lines = []
    for i in range(num_samples):
        k = max(1, min(k_arr[i], scores.shape[1]))
        idx = sorted_idx[i, :k]
        species_ids = [species_column_names[j].replace("sp_", "") for j in idx]
        lines.append(" ".join(species_ids))
    return pd.DataFrame(
        {"surveyId": features_matrix[sample_id_col].values, "predictions": lines}
    )
