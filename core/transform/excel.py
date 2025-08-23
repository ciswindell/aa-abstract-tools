#!/usr/bin/env python3
"""
Pure Excel DataFrame transforms.

Functions here are side‑effect free and return new DataFrames.
"""

from typing import Dict, Iterable, List, Optional

import pandas as pd
from utils.dates import parse_robust


def clean_types(
    df: pd.DataFrame,
    index_col: str = "Index#",
    text_columns: Optional[Iterable[str]] = None,
    date_columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Return a copy of df with light type cleaning.

    - Ensures index_col is a trimmed string and preserves an "Original_Index" copy
    - Normalizes common text columns to trimmed strings
    - Attempts to parse date columns; leaves values unchanged on parse failure
    """

    new_df = df.copy()

    if text_columns is None:
        text_columns = [
            "Legal Description",
            "Grantee",
            "Grantor",
            "Document Type",
        ]
    if date_columns is None:
        date_columns = ["Document Date", "Received Date"]

    if index_col in new_df.columns:
        new_df[index_col] = new_df[index_col].astype(str).str.strip()
        new_df[index_col] = new_df[index_col].replace("nan", "")
        if "Original_Index" not in new_df.columns:
            new_df["Original_Index"] = new_df[index_col].astype(str)

    for col in text_columns:
        if col in new_df.columns:
            new_df[col] = new_df[col].astype(str).str.strip().replace("nan", "")

    for col in date_columns:
        if col in new_df.columns:
            new_df[col] = new_df[col].map(parse_robust)

    return new_df


def sort_and_renumber(
    df: pd.DataFrame,
    sort_columns: Optional[List[str]] = None,
    index_col: str = "Index#",
) -> pd.DataFrame:
    """Sort by available columns ascending and renumber index_col from 1..N."""

    if sort_columns is None:
        sort_columns = [
            "Received Date",
            "Document Date",
            "Document Type",
            "Grantor",
            "Grantee",
            "Legal Description",
        ]

    new_df = df.copy()
    cols = [c for c in sort_columns if c in new_df.columns]
    if cols:
        new_df = new_df.sort_values(by=cols, ascending=True, na_position="last")
        new_df = new_df.reset_index(drop=True)

    if index_col in new_df.columns:
        new_df[index_col] = range(1, len(new_df) + 1)

    return new_df


def build_original_index_mapping(
    df: pd.DataFrame,
    index_col: str = "Index#",
    original_index_col: str = "Original_Index",
) -> Dict[str, int]:
    """Map original index string to new sequential index integer."""

    if index_col not in df.columns or original_index_col not in df.columns:
        return {}

    mapping: Dict[str, int] = {}
    for _, row in df.iterrows():
        original = str(row[original_index_col]).strip()
        try:
            new_val = int(row[index_col])
        except Exception:
            continue
        mapping[original] = new_val
    return mapping
