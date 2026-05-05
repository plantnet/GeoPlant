
# GeoPlant XGBoost Baseline (Refactored)

This repository provides a clean, minimal framework to run presence–absence
baselines with XGBoost on GeoPlant datasets. It focuses on **clarity**:
descriptive variable names, rich docstrings, and straightforward data flow.

**Highlights**
- Separate TRAIN/TEST predictor CSVs per family (e.g., bioclimatic, soilgrids).
- Metadata encoding → location+meta features.
- Build labels directly from long-format train metadata (`surveyId`, `speciesId`).
- One-vs-rest models, optional richness estimator for per-sample Top‑K.
- Ablations with Fs1, Recall@K, Macro AUC.
