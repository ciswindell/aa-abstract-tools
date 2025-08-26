#!/usr/bin/env python3
"""
Lightweight input sheet validation utilities (SOLID/DRY).
Validates required headers case-insensitively and detects duplicates in required set.
"""

from typing import Dict, List


def _to_lower_set(items: List[str]) -> set:
    return {str(x).lower() for x in items}


def find_missing_required_columns(df, required_columns: List[str]) -> List[str]:
    if df is None:
        return required_columns
    present_lower = _to_lower_set(list(df.columns))
    return [c for c in required_columns if str(c).lower() not in present_lower]


def find_duplicate_columns(df) -> List[str]:
    """Find ALL duplicate column names, including pandas auto-renamed duplicates."""
    if df is None:
        return []

    duplicates = []

    # 1. Find actual duplicate column names (case-insensitive)
    column_counts = {}
    for col in df.columns:
        key = str(col).lower().strip()
        column_counts[key] = column_counts.get(key, 0) + 1

    seen = set()
    for col in df.columns:
        key = str(col).lower().strip()
        if column_counts[key] > 1 and key not in seen:
            duplicates.append(str(col))
            seen.add(key)

    # 2. Find pandas auto-renamed duplicates (e.g., "Index#.1", "Index#.2")
    for col in df.columns:
        col_str = str(col)
        if "." in col_str:
            parts = col_str.split(".")
            if len(parts) == 2 and parts[1].isdigit():
                base_name = parts[0]
                # Check if the base name exists in columns
                if base_name in df.columns:
                    # Add both the base name and the renamed column as duplicates
                    if base_name not in duplicates:
                        duplicates.append(base_name)
                    if col_str not in duplicates:
                        duplicates.append(col_str)

    return duplicates


def find_duplicate_index_values(df, index_col: str = "Index#") -> List[str]:
    """Find duplicate values in the Index# column (PRD requirement #3)."""
    if df is None or index_col not in df.columns:
        return []

    try:
        index_values = df[index_col].astype(str).str.strip()
        duplicates = index_values[index_values.duplicated()].unique()
        return list(duplicates)
    except AttributeError:
        # Handle case where df[index_col] returns DataFrame (duplicate column names)
        return []


def validate(df, required_columns: List[str]) -> Dict[str, List[str]]:
    return {
        "missing": find_missing_required_columns(df, required_columns),
        "duplicate_columns": find_duplicate_columns(df),
        "duplicate_indices": find_duplicate_index_values(df),
    }
