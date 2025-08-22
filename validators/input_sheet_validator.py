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


def find_duplicate_required_columns(df, required_columns: List[str]) -> List[str]:
    if df is None:
        return []
    required_lower = _to_lower_set(required_columns)
    counts: Dict[str, int] = {}
    for c in df.columns:
        key = str(c).lower()
        if key in required_lower:
            counts[key] = counts.get(key, 0) + 1
    return [c for c in required_columns if counts.get(str(c).lower(), 0) > 1]


def validate(df, required_columns: List[str]) -> Dict[str, List[str]]:
    return {
        "missing": find_missing_required_columns(df, required_columns),
        "duplicates": find_duplicate_required_columns(df, required_columns),
    }
