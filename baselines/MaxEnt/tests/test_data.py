from __future__ import annotations

import pandas as pd

from geoplant_maxent.config import ExperimentConfig
from geoplant_maxent.data import (
    align_features_with_labels,
    build_wide_labels_from_long_metadata,
    select_top_species,
    split_features_by_group,
)


def test_build_wide_labels_from_long_metadata_deduplicates_pairs():
    labels = build_wide_labels_from_long_metadata(
        pd.DataFrame({"surveyId": [1, 1, 1, 2], "speciesId": [10, 10, 11, 12]})
    )
    assert labels.columns.tolist() == ["survey_id", "sp_10", "sp_11", "sp_12"]
    assert labels.loc[0, "sp_10"] == 1
    assert labels.loc[0, "sp_11"] == 1


def test_align_features_with_labels_rejects_duplicate_survey_rows():
    features = pd.DataFrame({"survey_id": [1, 1], "lat": [0.1, 0.2]})
    labels = pd.DataFrame({"survey_id": [1], "sp_1": [1]})
    try:
        align_features_with_labels(features, labels)
    except ValueError as exc:
        assert "unique per survey" in str(exc)
    else:
        raise AssertionError("Expected align_features_with_labels to reject duplicate survey rows")


def test_select_top_species_and_split_features_by_group():
    cfg = ExperimentConfig(min_pos_per_species=2, top_species_n=1)
    labels = pd.DataFrame(
        {
            "survey_id": [1, 2, 3],
            "sp_10": [1, 1, 0],
            "sp_11": [1, 0, 0],
        }
    )
    features = pd.DataFrame(
        {
            "survey_id": [1, 2],
            "lat": [0.0, 1.0],
            "meta_country_FR": [1, 0],
            "clim_bio1": [5.0, 6.0],
        }
    )
    assert select_top_species(labels, ["sp_10", "sp_11"], cfg) == ["sp_10"]
    group_map = split_features_by_group(features, cfg)
    assert group_map["location"] == ["lat"]
    assert group_map["meta"] == ["meta_country_FR"]
    assert group_map["climatic"] == ["clim_bio1"]
