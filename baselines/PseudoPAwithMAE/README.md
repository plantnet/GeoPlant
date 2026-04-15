# PseudoPAwithMAE

This baseline keeps the original notebook experiment and adds a cleaner species-only training package built around the method you converged on:

1. PA masked reconstruction
2. PO positive-unlabeled ranking
3. joint PA+PO training instead of a hard stage switch
4. prevalence-aware sampling and bias initialization
5. evaluation with top-k retrieval metrics

The current implementation intentionally does not use GPS or any other external covariates yet. The model only sees species sets.

## What Is Included

- `pseudo_pa_with_mae.ipynb`: your original exploratory notebook
- `geoplant_pseudopa/`: reusable baseline package
- `run_species_only.py`: simple CLI entrypoint for the improved species-only method
- `requirements.txt`: baseline dependencies
- `.gitignore`: ignores local generated metadata, checkpoints, and notebook cache files

## Method

### PA Masked Reconstruction

For each PA plot, mask a subset of observed species and predict only the masked species against sampled negatives. This is a cleaner objective than reconstructing the full input after corruption.

### PO Positive-Unlabeled Ranking

For PO plots, observed species are treated as positives, while unobserved species are sampled as unlabeled negatives for a pairwise ranking objective. This avoids interpreting all missing PO labels as true absences.

### Joint Training

The training loop keeps the PA objective active while adding the PO objective:

`L = L_pa_masked + lambda_po * L_po_rank`

The code supports a short PA-only warmup followed by joint training.

### Prevalence Correction

The model initializes species biases from PA prevalence and uses prevalence-aware negative sampling so very common species do not dominate the optimization.

## Files

- `geoplant_pseudopa/config.py`: training hyperparameters
- `geoplant_pseudopa/data.py`: species-set parsing and dataset helpers
- `geoplant_pseudopa/model.py`: two-tower species-only model
- `geoplant_pseudopa/training.py`: masked PA loss, PO ranking loss, and joint training loop
- `geoplant_pseudopa/evaluation.py`: prevalence initialization and top-k metrics

## Expected Local Inputs

The original notebook expects generated metadata CSV files in a local `metadata/` directory next to the notebook. These files are not committed because they are large generated artifacts.

Expected filenames:

- `metadata/GPNv2--metadata_train.csv`
- `metadata/GPNv2--metadata_val.csv`
- `metadata/GPNv2--metadata_test.csv`
- `metadata/GPNv2-['CH']-metadata_train.csv`
- `metadata/GPNv2-['CH']-metadata_val.csv`
- `metadata/GPNv2-['CH']-metadata_test.csv`
- `metadata/GPNv2-['DK']-metadata_train.csv`
- `metadata/GPNv2-['DK']-metadata_val.csv`
- `metadata/GPNv2-['DK']-metadata_test.csv`
- `metadata/GPNv2-['NL']-metadata_train.csv`
- `metadata/GPNv2-['NL']-metadata_val.csv`
- `metadata/GPNv2-['NL']-metadata_test.csv`

For the training script, the CSVs need at least:

- `survey_id`
- `species_set`
- `source`
- `subset`

## Example

```bash
PYTHONPATH=baselines/PseudoPAwithMAE \
python baselines/PseudoPAwithMAE/run_species_only.py \
  --train-metadata baselines/PseudoPAwithMAE/metadata/GPNv2--metadata_train.csv \
  --val-metadata baselines/PseudoPAwithMAE/metadata/GPNv2--metadata_val.csv \
  --num-species 15286 \
  --device cpu
```

## Dataset Ideas For Next Steps

If you want to push this method further later, strong candidate datasets are:

- GeoPlant PA + PO as the primary benchmark
- GBIF for larger presence-only coverage
- sPlotOpen or EVA for richer vegetation-plot supervision
- TRY for future species-trait regularization

## Running The Notebook

Open the notebook from this directory so its relative `./metadata/...` paths resolve correctly.
