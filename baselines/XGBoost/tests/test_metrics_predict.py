from __future__ import annotations

import numpy as np
import pandas as pd

from geoplant_xgb.metrics import macro_auc, sample_f1_at_k, sample_recall_at_k
from geoplant_xgb.predict import export_predictions


class DummyModel:
    def __init__(self, positive_scores):
        self.positive_scores = np.asarray(positive_scores, dtype=float)

    def predict_proba(self, features):
        negatives = 1.0 - self.positive_scores
        return np.column_stack([negatives, self.positive_scores])


def test_metrics_return_expected_scores():
    y_true = np.array([[1, 0, 1], [0, 1, 0]], dtype=int)
    y_scores = np.array([[0.9, 0.1, 0.8], [0.2, 0.7, 0.1]], dtype=float)

    assert np.isclose(sample_f1_at_k(y_true, y_scores, 2), 5.0 / 6.0)
    assert sample_recall_at_k(y_true, y_scores, 2) == 1.0
    assert macro_auc(y_true, y_scores) == 1.0


def test_export_predictions_uses_sample_id_column():
    features = pd.DataFrame({"survey_id": [101, 102], "clim_bio1": [0.2, 0.5]})
    models = {
        "sp_10": DummyModel([0.9, 0.1]),
        "sp_11": DummyModel([0.2, 0.8]),
    }

    submission = export_predictions(
        models,
        features,
        ["sp_10", "sp_11"],
        topk_per_sample=np.array([1, 1]),
        sample_id_col="survey_id",
    )

    assert submission.to_dict(orient="records") == [
        {"surveyId": 101, "predictions": "10"},
        {"surveyId": 102, "predictions": "11"},
    ]
