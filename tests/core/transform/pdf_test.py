#!/usr/bin/env python3
"""
Unit tests for core.transform.pdf.
"""

import pandas as pd

from core.transform.pdf import extract_original_index, make_titles, detect_page_ranges


def test_extract_original_index():
    assert extract_original_index("12-Doc-1/1/2024") == "12"
    assert extract_original_index("A5-Doc-1/1/2024") == "A5"
    assert extract_original_index("") is None


def test_make_titles_happy_path():
    df = pd.DataFrame(
        {
            "Original_Index": ["A", "B"],
            "Index#": [1, 2],
            "Document Type": ["Doc", "Doc"],
            "Received Date": ["2024-01-01", "2024-01-02"],
        }
    )
    titles = make_titles(df)
    assert titles.get("A", "").startswith("1-Doc-")
    assert titles.get("B", "").startswith("2-Doc-")


def test_detect_page_ranges_sequential():
    bms = [
        {"title": "1-Doc", "page": 1},
        {"title": "2-Doc", "page": 3},
        {"title": "3-Doc", "page": 5},
    ]
    rng = detect_page_ranges(bms, total_pages=6)
    assert rng["1-Doc"] == {"start": 1, "end": 2}
    assert rng["2-Doc"] == {"start": 3, "end": 4}
    assert rng["3-Doc"] == {"start": 5, "end": 6}
