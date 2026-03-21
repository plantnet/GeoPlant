from __future__ import annotations

import numpy as np
import pandas as pd

from geoplant_maxent.config import ExperimentConfig
from geoplant_maxent.model import estimate_topk, predict_scores, train_ovr, train_richness_estimator
from geoplant_maxent.predict import export_predictions


def test_train_predict_and_export_end_to_end():
    cfg = ExperimentConfig(
        maxent_params={
            "C": 1.0,
            "max_iter": 300,
            "solver": "liblinear",
            "class_weight": "balanced",
        },
        richness_nbins=3,
    )
    train_features = pd.DataFrame(
        {
            "clim_bio1": [0.0, 0.1, 1.0, 1.1, 2.0, 2.1],
            "clim_bio2": [0.0, 0.2, 1.0, 1.2, 2.0, 2.2],
        }
    )
    train_labels = pd.DataFrame(
        {
            "sp_10": [1, 1, 0, 0, 0, 0],
            "sp_11": [0, 0, 1, 1, 0, 0],
            "sp_12": [0, 0, 0, 0, 1, 1],
        }
    )
    test_features = pd.DataFrame(
        {
            "survey_id": [101, 102, 103],
            "clim_bio1": [0.05, 1.05, 2.05],
            "clim_bio2": [0.05, 1.05, 2.05],
        }
    )

    models = train_ovr(train_features, train_labels, ["sp_10", "sp_11", "sp_12"], cfg)
    scores = predict_scores(models, test_features.drop(columns=["survey_id"]), ["sp_10", "sp_11", "sp_12"])
    assert scores.shape == (3, 3)
    assert int(np.argmax(scores[0])) == 0
    assert int(np.argmax(scores[1])) == 1
    assert int(np.argmax(scores[2])) == 2

    richness_model, edges, bin_to_mean = train_richness_estimator(train_features, train_labels, cfg)
    topk = estimate_topk(
        richness_model,
        edges,
        bin_to_mean,
        test_features.drop(columns=["survey_id"]),
        offset=0,
    )
    assert topk.shape == (3,)
    submission = export_predictions(
        models,
        test_features,
        ["sp_10", "sp_11", "sp_12"],
        topk_per_sample=1,
        sample_id_col="survey_id",
    )
    assert submission.to_dict(orient="records") == [
        {"surveyId": 101, "predictions": "10"},
        {"surveyId": 102, "predictions": "11"},
        {"surveyId": 103, "predictions": "12"},
    ]
