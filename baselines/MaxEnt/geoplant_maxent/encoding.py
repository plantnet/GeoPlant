"""Lightweight metadata encoders used by CSV ingestion."""

from __future__ import annotations

import pandas as pd


def align_one_hot(
    train_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
    columns: list[str],
    prefix: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """One-hot encode the same categorical schema for train and test frames."""
    present = [
        column
        for column in columns
        if column in train_frame.columns or column in test_frame.columns
    ]
    if not present:
        return pd.DataFrame(index=train_frame.index), pd.DataFrame(index=test_frame.index)

    combined = pd.concat(
        [
            train_frame.reindex(columns=present),
            test_frame.reindex(columns=present),
        ],
        axis=0,
        ignore_index=True,
    )
    encoded = pd.get_dummies(
        combined.astype("category"),
        dummy_na=False,
        prefix=[f"{prefix}{column}" for column in present],
    )
    train_encoded = encoded.iloc[: len(train_frame)].set_index(train_frame.index)
    test_encoded = encoded.iloc[len(train_frame) :].set_index(test_frame.index)
    return train_encoded, test_encoded


def to_numeric(
    dataframe: pd.DataFrame,
    columns: list[str],
    add_prefix: str | None = None,
) -> pd.DataFrame:
    """Coerce selected columns to numeric and optionally add a prefix."""
    present = [column for column in columns if column in dataframe.columns]
    if not present:
        return pd.DataFrame(index=dataframe.index)
    encoded = dataframe[present].apply(pd.to_numeric, errors="coerce")
    return encoded.add_prefix(add_prefix) if add_prefix else encoded
