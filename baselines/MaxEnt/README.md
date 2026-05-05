GeoPlant MaxEnt Baseline

A regularized maximum-entropy baseline for presence-absence species prediction using tabular GeoPlant predictors.

## Start Here

This baseline mirrors the XGBoost layout, but uses MaxEnt-style logistic models under the hood.
In practice, that means one-vs-rest regularized logistic regression for species scoring plus
an optional multiclass logistic richness estimator for per-sample Top-K selection.

# Runtime dependencies
pip install -r requirements.txt

# Package layout

geoplant_maxent/
  __init__.py
  config.py
  encoding.py
  io_csv.py
  data.py
  model.py
  metrics.py
  experiment.py
  predict.py
  evaluation.py
tests/
  test_io_csv.py
  test_data.py
  test_model_predict.py

# Quick start

```python
from geoplant_maxent import ExperimentConfig, PredictorPairSpec
from geoplant_maxent.io_csv import (
    load_metadata_csv,
    load_predictor_pairs,
    build_features_from_meta_and_predictors_pair,
)
from geoplant_maxent.data import (
    build_wide_labels_from_long_metadata,
    align_features_with_labels,
    select_top_species,
    split_features_by_group,
)
from geoplant_maxent.model import train_ovr, train_richness_estimator, estimate_topk
from geoplant_maxent.predict import export_predictions

cfg = ExperimentConfig(
    predictor_pairs=[
        PredictorPairSpec(
            name="bioclim",
            group="climatic",
            prefix="clim_",
            train_path=".../PA-train-bioclimatic.csv",
            test_path=".../PA-test-bioclimatic.csv",
        )
    ]
)

train_meta = load_metadata_csv(".../PA_metadata_train.csv")
test_meta = load_metadata_csv(".../PA_metadata_test.csv")
train_pred, test_pred = load_predictor_pairs(cfg.predictor_pairs)
train_features, test_features = build_features_from_meta_and_predictors_pair(
    cfg, train_meta, test_meta, train_pred, test_pred
)

train_labels_wide = build_wide_labels_from_long_metadata(train_meta)
train_feat_aligned, train_lab_aligned, species_cols = align_features_with_labels(
    train_features, train_labels_wide, cfg.sample_id_col
)

top_species = select_top_species(train_lab_aligned, species_cols, cfg)
groups = split_features_by_group(train_feat_aligned, cfg)
clim_cols = groups["climatic"]

models = train_ovr(
    train_feat_aligned[clim_cols],
    train_lab_aligned.set_index(cfg.sample_id_col),
    top_species,
    cfg,
)
richness_model, edges, bin_to_mean = train_richness_estimator(
    train_feat_aligned[clim_cols],
    train_lab_aligned.set_index(cfg.sample_id_col),
    cfg,
)
topk = estimate_topk(
    richness_model,
    edges,
    bin_to_mean,
    test_features[clim_cols],
    offset=cfg.richness_offset,
)
submission = export_predictions(
    models,
    test_features[[cfg.sample_id_col] + clim_cols],
    top_species,
    topk,
    cfg.sample_id_col,
)
```

## Notes

- This baseline is “MaxEnt-style” rather than a Java MaxEnt wrapper.
- It is designed to share the same GeoPlant CSV schema and evaluation flow as the XGBoost baseline.
- For many tabular baseline comparisons, this is a simpler and more transparent reference model.
