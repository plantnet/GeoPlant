"""GeoPlant XGBoost baseline (clean API, rich docs).

This package provides a thin, well-documented framework to reproduce and extend
GeoPlant-style presence–absence baselines with XGBoost:

- **CSV ingestion** for *separate* train/test predictor files.
- **Metadata encoding** into feature families: location (lat/lon, simple numerics)
  and meta (categoricals as one-hot).
- **Label building** from long-format metadata (`surveyId`, `speciesId`) to a wide
  multi-hot matrix (`sp_<speciesId>` columns).
- **Model training** using one-vs-rest XGBoost and an optional **richness-based**
  per-sample Top-K estimator.
- **Ablation orchestration** with Fs1/Recall@K/Macro-AUC metrics.
- **Prediction export** compatible with competition-style submissions.

The public entry points commonly used are re-exported for convenience:
- :class:`~geoplant_xgb.config.ExperimentConfig`
- :class:`~geoplant_xgb.config.PredictorPairSpec`
- :func:`~geoplant_xgb.io_csv.load_metadata_csv`
- :func:`~geoplant_xgb.io_csv.load_predictor_pairs`
- :func:`~geoplant_xgb.io_csv.build_features_from_meta_and_predictors_pair`
- :func:`~geoplant_xgb.data.build_wide_labels_from_long_metadata`
- :func:`~geoplant_xgb.data.align_features_with_labels`
- :func:`~geoplant_xgb.experiment.run_one_ablation`
- :func:`~geoplant_xgb.experiment.run_all`
"""
from .config import ExperimentConfig, PredictorPairSpec
