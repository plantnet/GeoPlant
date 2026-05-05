from __future__ import annotations

import pandas as pd

from geoplant_maxent.config import ExperimentConfig, PredictorPairSpec
from geoplant_maxent.io_csv import build_features_from_meta_and_predictors_pair, load_predictor_pairs


def test_build_features_collapses_long_metadata_and_aligns_one_hot_columns():
    cfg = ExperimentConfig()
    train_metadata = pd.DataFrame(
        {
            "surveyId": [1, 1, 2],
            "speciesId": [10, 11, 12],
            "lat": [45.1, 45.1, 46.2],
            "lon": [5.2, 5.2, 6.3],
            "country": ["France", "France", "Spain"],
            "disctrict": ["Ain", "Ain", "Navarre"],
            "year": [2020, 2020, 2021],
        }
    )
    test_metadata = pd.DataFrame(
        {
            "surveyId": [3],
            "lat": [47.3],
            "lon": [7.4],
            "country": ["Italy"],
            "district": ["Aosta"],
            "year": [2022],
        }
    )
    train_predictors = {"bioclim": pd.DataFrame({"surveyId": [1, 2], "clim_bio1": [0.1, 0.2]})}
    test_predictors = {"bioclim": pd.DataFrame({"surveyId": [3], "clim_bio1": [0.3]})}
    train_features, test_features = build_features_from_meta_and_predictors_pair(
        cfg,
        train_metadata,
        test_metadata,
        train_predictors,
        test_predictors,
    )
    assert train_features["survey_id"].tolist() == [1, 2]
    assert test_features["survey_id"].tolist() == [3]
    assert "meta_country_Italy" in train_features.columns
    assert "meta_district_Aosta" in test_features.columns


def test_load_predictor_pairs_keeps_numeric_columns_only(tmp_path):
    train_csv = tmp_path / "train.csv"
    test_csv = tmp_path / "test.csv"
    pd.DataFrame({"surveyId": [1, 2], "bio1": [1.0, 2.0], "label": ["wet", "dry"]}).to_csv(
        train_csv,
        index=False,
    )
    pd.DataFrame({"surveyId": [3], "bio1": [3.0], "label": ["dry"]}).to_csv(
        test_csv,
        index=False,
    )
    train_map, test_map = load_predictor_pairs(
        [
            PredictorPairSpec(
                name="bioclim",
                group="climatic",
                prefix="clim_",
                train_path=str(train_csv),
                test_path=str(test_csv),
            )
        ]
    )
    assert list(train_map["bioclim"].columns) == ["surveyId", "clim_bio1"]
    assert list(test_map["bioclim"].columns) == ["surveyId", "clim_bio1"]
