GeoPlant XGBoost Baseline (Refactored)

A minimal, framework for presence–absence species prediction using XGBoost.

## Start Here

If you want a runnable example first, use `run_single_predictor_framework.ipynb`.
The notebook is kept as the reference walkthrough, while `geoplant_xgb/` contains
the reusable pipeline code that the notebook imports.

# Runtime dependencies
pip install -r requirements.txt

# (Optional) Docs extras: mkdocs + mkdocstrings
pip install -r requirements-docs.txt


# Package layout

geoplant_xgb/
  __init__.py
  config.py                 # ExperimentConfig, PredictorPairSpec
  encoding.py               # one_hot, to_numeric
  io_csv.py                 # load_metadata_csv, load_predictor_pairs, build_features_from_meta_and_predictors_pair
  data.py                   # build_wide_labels_from_long_metadata, align_features_with_labels, select_top_species, split_features_by_group
  model.py                  # train_ovr, predict_scores, train_richness_estimator, estimate_topk
  metrics.py                # sample_f1_at_k, sample_recall_at_k, macro_auc
  experiment.py             # run_one_ablation, run_all
  predict.py                # export_predictions
  evaluation.py             # parse_solution, lists_to_wide
docs/
  index.md, getting-started.md, data-schema.md, running-ablations.md, baseline-results.md
  api/*.md                 # mkdocstrings entrypoints
mkdocs.yml
requirements.txt
requirements-docs.txt


# Data schema (expected)

Train/Test metadata CSVs
	•	Required: surveyId
	•	Optional numeric: lat, lon, geoUncertaintyInM, areaInM2, year
	•	Optional categorical: country, region, taxonRank, county, disctrict
	•	Train‑only: speciesId (multiple rows per surveyId → presence–absence labels)

Predictor CSVs (per family)
	•	Separate TRAIN and TEST files, both with surveyId and numeric columns.
	•	Columns are prefixed on load (e.g., clim_*, soil_*, lc_*, hfp_*).

⸻

# Quick start

from geoplant_xgb import ExperimentConfig, PredictorPairSpec
from geoplant_xgb.io_csv import (
    load_metadata_csv,
    load_predictor_pairs,
    build_features_from_meta_and_predictors_pair,
)
from geoplant_xgb.data import (
    build_wide_labels_from_long_metadata,
    align_features_with_labels,
    split_features_by_group,
    select_top_species,
)
from geoplant_xgb.model import (
    train_ovr,
    train_richness_estimator,
    estimate_topk,
    predict_scores,
)
from geoplant_xgb.metrics import sample_f1_at_k, sample_recall_at_k, macro_auc

# 1) Configure a single predictor family (bioclim as example)
cfg = ExperimentConfig(
    predictor_pairs=[
        PredictorPairSpec(
            name="bioclim", group="climatic", prefix="clim_",
            train_path=".../PA-train-bioclimatic.csv",
            test_path=".../PA-test-bioclimatic.csv",
        )
    ]
)

# 2) Load metadata and predictors
train_meta = load_metadata_csv(".../train.csv", sample_id_col="surveyId")
test_meta  = load_metadata_csv(".../test.csv",  sample_id_col="surveyId")
train_pred_by_name, test_pred_by_name = load_predictor_pairs(cfg.predictor_pairs)

# 3) Build features
X_train, X_test = build_features_from_meta_and_predictors_pair(
    cfg, train_meta, test_meta, train_pred_by_name, test_pred_by_name
)

# 4) Build wide labels from long train metadata
Y_train_wide = build_wide_labels_from_long_metadata(
    train_meta, survey_id_column="surveyId", species_id_column="speciesId", species_prefix=cfg.species_prefix
)

# 5) Align by survey_id
X_train_aligned, Y_train_aligned, species_cols = align_features_with_labels(
    X_train, Y_train_wide, survey_id_column=cfg.sample_id_col
)

# 6) Pick a feature family and train OVR models
feature_groups = split_features_by_group(X_train_aligned, cfg)
clim_columns = feature_groups["climatic"]

top_species = select_top_species(Y_train_aligned, species_cols, cfg)
models = train_ovr(
    train_features=X_train_aligned[clim_columns],
    train_labels=Y_train_aligned.set_index(cfg.sample_id_col),
    species_column_names=top_species,
    cfg=cfg,
)

# 7) Per-sample Top‑K via richness estimator (or use cfg.fixed_top_k)
rich_clf, bin_edges, bin_to_mean = train_richness_estimator(
    train_features=X_train_aligned[clim_columns],
    train_labels=Y_train_aligned.set_index(cfg.sample_id_col),
    cfg=cfg
)
topk_per_sample = estimate_topk(rich_clf, bin_edges, bin_to_mean, X_test[clim_columns], offset=cfg.richness_offset)

# 8) Score test features
scores_test = predict_scores(models, X_test[clim_columns], top_species)

# (Optional) sanity scores on train (not a test estimate)
scores_train = predict_scores(models, X_train_aligned[clim_columns], top_species)
fs1 = sample_f1_at_k(Y_train_aligned[top_species].values.astype(int), scores_train, k=25)
rec = sample_recall_at_k(Y_train_aligned[top_species].values.astype(int), scores_train, k=25)
auc = macro_auc(Y_train_aligned[top_species].values.astype(int), scores_train)
print({"Fs1@25": fs1, "Recall@25": rec, "MacroAUC": auc})


⸻

Running ablations

Define ablations in ExperimentConfig.ablations and call run_all:

from geoplant_xgb.experiment import run_all

cfg.ablations = [
    ["climatic"],
    ["soilgrids"],
    ["climatic", "soilgrids"],
]

# Build a zero‑filled test label placeholder if you don't have ground truth
Y_test_placeholder = X_test[[cfg.sample_id_col]].copy()
for c in species_cols:
    Y_test_placeholder[c] = 0

results = run_all(
    experiment_config=cfg,
    train_features=X_train_aligned,
    train_labels=Y_train_aligned,
    test_features=X_test,                  # or aligned version if you merge labels
    test_labels=Y_test_placeholder,
    species_column_names=species_cols,
)
results.to_csv("xgb_ablation_results.csv", index=False)
print(results)

Expected results schema:

groups	n_features	n_species	AUC	Recall	Fs1	TopK
climatic	123	500	0.78	0.41	0.28	per‑sample
soilgrids	88	500	0.74	0.38	0.26	per‑sample
climatic+soilgrids	211	500	0.81	0.44	0.31	per‑sample

(Replace with your actual numbers.)

⸻

Export predictions

Use predict.export_predictions to emit [surveyId, predictions]:

from geoplant_xgb.predict import export_predictions

submission_df = export_predictions(
    models_by_species=models,
    features_matrix=X_test[clim_columns].assign(**{cfg.sample_id_col: X_test[cfg.sample_id_col]}),
    species_column_names=top_species,
    topk_per_sample=topk_per_sample,        # or cfg.fixed_top_k
    sample_id_col=cfg.sample_id_col,
)
submission_df.to_csv("submission_predictions.csv", index=False)


⸻

Build documentation (MkDocs)

pip install -r requirements-docs.txt
mkdocs serve     # http://127.0.0.1:8000
# mkdocs build   # static site in 'site/'

The API Reference pages under docs/api/*.md are generated from the package’s docstrings via mkdocstrings (Google‑style).

⸻

Design notes & conventions
	•	Descriptive names: prefer train_features_subset over Xtr, f1_score over fs1, etc.
	•	Early stopping: With XGBoost 3.x, pass early_stopping_rounds to the estimator constructor; call fit(eval_set=[...]) (no callbacks, no verbose).
	•	Feature families: Controlled by ExperimentConfig.group_prefixes. Adjust prefixes if your CSVs differ.
	•	Species scope: Filtered by top_species_n and min_pos_per_species. Tweak to balance coverage vs. speed.

⸻

Troubleshooting

TypeError: XGBClassifier.fit() got an unexpected keyword argument 'callbacks'
Use XGBoost ≥ 3.0 and set early_stopping_rounds on the estimator (the package already does this).

Misaligned shapes or empty species list
Check that you built wide labels correctly and aligned on survey_id (cfg.sample_id_col). Ensure speciesId exists in train metadata.

No features in a group
Verify your predictor CSV prefixes and group_prefixes. The loader prefixes numeric columns automatically (e.g., clim_*).

⸻

License

Specify your preferred license here (e.g., MIT).
