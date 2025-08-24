"""Solution parsing and wide conversion utilities (for offline scoring)."""
from __future__ import annotations

import pandas as pd


def parse_solution(solution_csv_path: str) -> pd.DataFrame:
    """Read a solution-like CSV with `[surveyId, predictions/speciesList]` columns."""
    df = pd.read_csv(solution_csv_path)
    pred_col = None
    for c in df.columns:
        lc = c.lower()
        if lc.startswith("pred") or lc.startswith("species"):
            pred_col = c
            break
    if pred_col is None:
        raise ValueError("No predictions/species column found in solution file.")
    return df.rename(columns={pred_col: "speciesList"})


def lists_to_wide(
    solution_df: pd.DataFrame, species_prefix: str = "sp_"
) -> tuple[pd.DataFrame, list[str]]:
    """Expand space-separated species IDs into a wide 0/1 table with `sp_<id>` columns."""
    all_ids = set()
    for s in solution_df["speciesList"].astype(str):
        toks = [t for t in s.split() if t.strip() != ""]
        all_ids.update(int(t) for t in toks)
    species_cols = [f"{species_prefix}{i}" for i in sorted(all_ids)]
    wide = pd.DataFrame({"survey_id": solution_df["surveyId"].values})
    for col in species_cols:
        wide[col] = 0
    for r, s in enumerate(solution_df["speciesList"].astype(str)):
        for tok in s.split():
            if tok:
                wide.at[r, f"{species_prefix}{int(tok)}"] = 1
    return wide, species_cols
