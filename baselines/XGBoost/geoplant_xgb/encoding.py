"""Lightweight metadata encoders used by CSV ingestion."""
from __future__ import annotations

import pandas as pd


def one_hot(dataframe: pd.DataFrame, columns: list[str], prefix: str) -> pd.DataFrame:
    """One-hot encode selected categorical columns and apply a shared prefix.

    Missing column names are ignored silently. Categories are encoded without
    a separate NA column.

    Args:
        dataframe: Input table.
        columns: Categorical columns to encode (subset must exist).
        prefix: Prefix to prepend to the output feature names.

    Returns:
        One-hot encoded DataFrame (possibly empty if none of the columns exist).
    """
    present = [c for c in columns if c in dataframe.columns]
    if not present:
        return pd.DataFrame(index=dataframe.index)
    return pd.get_dummies(
        dataframe[present].astype("category"),
        dummy_na=False,
        prefix=[f"{prefix}{c}" for c in present],
    )


def to_numeric(
    dataframe: pd.DataFrame, columns: list[str], add_prefix: str | None = None
) -> pd.DataFrame:
    """Coerce selected columns to numeric and optionally add a prefix."""
    present = [c for c in columns if c in dataframe.columns]
    if not present:
        return pd.DataFrame(index=dataframe.index)
    out = dataframe[present].apply(pd.to_numeric, errors="coerce")
    return out.add_prefix(add_prefix) if add_prefix else out
