
# Getting Started

The quickest entry point is `run_single_predictor_framework.ipynb`, which shows the
single-predictor workflow end to end. The package API below is the reusable layer
under that notebook.

Install runtime dependencies:

```bash
pip install -r requirements.txt
```

Install docs extras (optional):

```bash
pip install -r requirements-docs.txt
```

## Minimal example

```python
from geoplant_xgb import ExperimentConfig, PredictorPairSpec
from geoplant_xgb.io_csv import load_metadata_csv, load_predictor_pairs, build_features_from_meta_and_predictors_pair
from geoplant_xgb.data import build_wide_labels_from_long_metadata, align_features_with_labels, split_features_by_group, select_top_species
from geoplant_xgb.model import train_ovr, train_richness_estimator, estimate_topk, predict_scores
from geoplant_xgb.metrics import sample_f1_at_k, sample_recall_at_k, macro_auc

cfg = ExperimentConfig(predictor_pairs=[
    PredictorPairSpec(
        name="bioclim", group="climatic", prefix="clim_",
        train_path=".../PA-train-bioclimatic.csv",
        test_path=".../PA-test-bioclimatic.csv",
    )
])

train_meta = load_metadata_csv(".../train.csv", sample_id_col="surveyId")
test_meta  = load_metadata_csv(".../test.csv",  sample_id_col="surveyId")

train_pred, test_pred = load_predictor_pairs(cfg.predictor_pairs)
X_train, X_test = build_features_from_meta_and_predictors_pair(cfg, train_meta, test_meta, train_pred, test_pred)

Y_train_wide = build_wide_labels_from_long_metadata(train_meta, "surveyId", "speciesId", cfg.species_prefix)
X_train_aligned, Y_train_aligned, species_cols = align_features_with_labels(X_train, Y_train_wide, cfg.sample_id_col)

groups = split_features_by_group(X_train_aligned, cfg)
clim_cols = groups["climatic"]

models = train_ovr(X_train_aligned[clim_cols], Y_train_aligned.set_index(cfg.sample_id_col), species_cols, cfg)

# Per-sample Top‑K (or use cfg.fixed_top_k)
rich_clf, edges, b2m = train_richness_estimator(X_train_aligned[clim_cols], Y_train_aligned.set_index(cfg.sample_id_col), cfg)
topk = estimate_topk(rich_clf, edges, b2m, X_test[clim_cols], offset=cfg.richness_offset)
scores = predict_scores(models, X_test[clim_cols], species_cols)
```

See **Running Ablations** for end-to-end orchestration.
