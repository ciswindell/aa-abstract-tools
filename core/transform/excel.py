#!/usr/bin/env python3
"""
Pure Excel DataFrame transforms.

Functions here are side‑effect free and return new DataFrames.
"""

import hashlib
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence

import pandas as pd

from core.config import DEFAULT_SORT_COLUMNS
from utils.dates import parse_robust


def generate_document_id(
    original_index: str, source_path: str, row_position: int
) -> str:
    """Generate unique document ID from source file, position, and original index.

    Args:
        original_index: Original index value from Excel (e.g., "A5", "12")
        source_path: Path to the source Excel file
        row_position: 0-based row position in the DataFrame

    Returns:
        8-character hash string that uniquely identifies the document

    Raises:
        ValueError: If hash generation fails due to invalid inputs
    """
    try:
        # Use full filename + row position + original index for uniqueness
        source_name = Path(source_path).name  # Full filename with extension
        composite = f"{source_name}_{row_position}_{original_index}"

        # Create short hash (8 chars) for compactness
        hash_obj = hashlib.md5(composite.encode())
        return hash_obj.hexdigest()[:8]
    except Exception as e:
        raise ValueError(
            f"Failed to generate document ID for {original_index}: {e}"
        ) from e


def add_document_ids(
    df: pd.DataFrame,
    source_path: str,
    index_col: str = "Index#",
) -> pd.DataFrame:
    """Add Document_ID column to DataFrame using source file path.

    Single responsibility: Generate unique document identifiers.

    Args:
        df: Input DataFrame with cleaned index column
        source_path: Path to source file for ID generation
        index_col: Name of the index column (default "Index#")

    Returns:
        DataFrame with Document_ID column added

    Raises:
        ValueError: If index column is missing or Document_ID generation fails
    """
    if index_col not in df.columns:
        raise ValueError(f"Index column '{index_col}' not found in DataFrame")

    new_df = df.copy()
    if "Document_ID" not in new_df.columns:
        new_df["Document_ID"] = [
            generate_document_id(str(orig_idx), source_path, row_pos)
            for row_pos, orig_idx in enumerate(new_df[index_col])
        ]

    return new_df


def clean_types(
    df: pd.DataFrame,
    index_col: str = "Index#",
    text_columns: Optional[Iterable[str]] = None,
    date_columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Return a copy of df with light type cleaning.

    Single responsibility: Clean and normalize data types.

    - Ensures index_col is a trimmed string
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

    # Clean index column safely
    if index_col in new_df.columns:
        try:
            new_df[index_col] = new_df[index_col].astype(str).str.strip()
            new_df[index_col] = new_df[index_col].replace("nan", "")
        except Exception as e:
            raise ValueError(f"Failed to clean index column '{index_col}': {e}") from e

    # Clean text columns safely
    for col in text_columns:
        if col in new_df.columns:
            try:
                new_df[col] = new_df[col].astype(str).str.strip().replace("nan", "")
            except Exception as e:
                raise ValueError(f"Failed to clean text column '{col}': {e}") from e

    # Parse date columns safely
    for col in date_columns:
        if col in new_df.columns:
            try:
                new_df[col] = new_df[col].map(parse_robust)
            except Exception as e:
                raise ValueError(f"Failed to parse date column '{col}': {e}") from e

    return new_df


def sort_and_renumber(
    df: pd.DataFrame,
    sort_columns: Optional[List[str]] = None,
    index_col: str = "Index#",
) -> pd.DataFrame:
    """Sort by available columns ascending and renumber index_col from 1..N."""

    if sort_columns is None:
        sort_columns = list(DEFAULT_SORT_COLUMNS)

    new_df = df.copy()
    cols = [c for c in sort_columns if c in new_df.columns]
    if cols:
        new_df = new_df.sort_values(by=cols, ascending=True, na_position="last")
        new_df = new_df.reset_index(drop=True)

    if index_col in new_df.columns:
        new_df[index_col] = range(1, len(new_df) + 1)

    return new_df


def filter_df(
    df: pd.DataFrame, column: Optional[str], values: Optional[Sequence[Any]]
) -> pd.DataFrame:
    """Return a filtered copy of df where df[column] is in values.

    If column or values are not provided, or column is missing, returns df copy.
    Always resets index.
    """

    if not column or not values or column not in df.columns:
        return df.copy()

    filtered = df[df[column].isin(values)].copy()
    return filtered.reset_index(drop=True)
