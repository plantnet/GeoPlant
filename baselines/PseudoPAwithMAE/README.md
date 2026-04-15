# PseudoPAwithMAE

This baseline integrates the local `PseudoPAwithMAE` exploratory project into the GeoPlant repository as a separate branch.

## What Is Included

- `pseudo_pa_with_mae.ipynb`: the original notebook, renamed and moved into the repository
- `.gitignore`: ignores local generated metadata, checkpoints, and notebook cache files

## Expected Local Inputs

The notebook expects generated metadata CSV files in a local `metadata/` directory next to the notebook. These files are not committed because they are large generated artifacts.

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

## Notebook Summary

The notebook defines a two-tower species model trained in two stages:

1. presence-absence pretraining with corrupted inputs and weighted BCE
2. presence-only fine-tuning with a BPR ranking loss

It also includes validation utilities, checkpoint helpers, and simple post-hoc calibration code.

## Running

Open the notebook from this directory so its relative `./metadata/...` paths resolve correctly.
