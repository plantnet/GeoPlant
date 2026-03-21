
# Baseline Results

Below is a placeholder table for your baseline runs. Replace it with your results CSV.

| groups                    | n_features | n_species | AUC   | Recall | Fs1   | TopK        |
|--------------------------:|-----------:|----------:|------:|-------:|------:|:------------|
| climatic                  | 123        | 500       | 0.78  | 0.41   | 0.28  | per-sample  |
| soilgrids                 | 88         | 500       | 0.74  | 0.38   | 0.26  | per-sample  |
| climatic + soilgrids      | 211        | 500       | 0.81  | 0.44   | 0.31  | per-sample  |

To regenerate this table from your experiments:

```python
results = run_all(cfg, X_train_aligned, Y_train_aligned, X_test_aligned, Y_test_placeholder, species_cols)
results.to_csv("docs/assets/baseline_results.csv", index=False)
```

Then embed it in this page as a Markdown table or via MkDocs’ `pymdownx.tabular` if desired.
