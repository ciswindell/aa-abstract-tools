#!/usr/bin/env python3
"""
Unit tests for core.transform.excel.
"""

import pandas as pd

from core.transform.excel import (
    clean_types,
    sort_and_renumber,
)


def test_clean_types_preserves_original_index_and_trims_text():
    df = pd.DataFrame(
        {
            "Index#": ["  A1 ", "2", None],
            "Document Type": ["  Deed ", "Lien", None],
            "Received Date": ["1/1/2024", "2024-01-02", ""],
        }
    )

    out = clean_types(df)
    assert "Original_Index" in out.columns
    assert out.loc[0, "Original_Index"] == "A1"
    assert out.loc[0, "Document Type"] == "Deed"
    # Dates become parseable timestamps or preserved
    assert out.loc[0, "Received Date"] is not None


def test_sort_and_renumber_assigns_sequential_indices():
    df = pd.DataFrame(
        {
            "Index#": ["3", "1", "2"],
            "Received Date": ["2024-01-03", "2024-01-01", "2024-01-02"],
        }
    )
    df2 = sort_and_renumber(clean_types(df))
    assert list(df2["Index#"]) == [1, 2, 3]


def test_original_index_column_present_after_clean_types():
    df = pd.DataFrame({"Index#": ["A", "B", "C"]})
    out = clean_types(df)
    assert list(out["Original_Index"]) == ["A", "B", "C"]
