#!/usr/bin/env python3
"""
Unit tests for core.transform.excel.
"""

import pandas as pd

from core.transform.excel import (
    clean_types,
    sort_and_renumber,
    build_original_index_mapping,
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


def test_build_original_index_mapping_maps_original_to_new():
    df = pd.DataFrame(
        {
            "Index#": [1, 2, 3],
            "Original_Index": ["A", "B", "C"],
        }
    )
    mapping = build_original_index_mapping(df)
    assert mapping == {"A": 1, "B": 2, "C": 3}
