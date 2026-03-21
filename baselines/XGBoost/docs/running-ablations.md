
# Running Ablations

```python
from geoplant_xgb.experiment import run_all

cfg.ablations = [
    ["climatic"],
    ["soilgrids"],
    ["climatic","soilgrids"],
]

results = run_all(cfg, X_train_aligned, Y_train_aligned, X_test_aligned, Y_test_placeholder, species_cols)
results.to_csv("xgb_ablation_results.csv", index=False)
```

**Columns**
- `groups` — feature families used.
- `n_features` — number of columns used for modeling.
- `n_species` — number of species modeled.
- `AUC` — Macro ROC‑AUC.
- `Recall` — average Recall@K across samples.
- `Fs1` — average sample F1 at K.
- `TopK` — fixed integer or `"per-sample"`.
