#!/usr/bin/env python3
"""Tests for add_rows_for_new_bookmarks (issue #2)."""

import pandas as pd

from core.transform.pdf import add_rows_for_new_bookmarks


def _df():
    return pd.DataFrame(
        {
            "Index#": ["1", "2"],
            "Document Type": ["Deed", "Release"],
            "Received Date": ["2020-01-01", "2020-02-02"],
            "Legal Description": ["L1", "L2"],
        }
    )


def _bookmarks():
    return [
        {"title": "1-Deed-1/1/2020", "level": 0, "page": 1},
        {"title": "2-Release-2/2/2020", "level": 0, "page": 2},
        {"title": "Merger 2014", "level": 0, "page": 3},
    ]


def test_appends_row_and_relabels_bookmark():
    df, bookmarks = _df(), _bookmarks()
    new_df, new_bm = add_rows_for_new_bookmarks(df, bookmarks, {"Merger 2014"})

    # A row was appended for the orphan, with the next index.
    assert len(new_df) == 3
    row = new_df.iloc[-1]
    assert row["Index#"] == "3"
    assert row["Document Type"] == "Merger 2014"
    assert pd.isna(row["Received Date"])
    # Other (non-specified) columns are blank for the new row.
    assert pd.isna(row["Legal Description"])

    # Only the orphan bookmark is relabeled, in place/order.
    assert new_bm[0]["title"] == "1-Deed-1/1/2020"
    assert new_bm[1]["title"] == "2-Release-2/2/2020"
    assert new_bm[2]["title"] == "3-Merger 2014"

    # Inputs are not mutated.
    assert len(df) == 2
    assert bookmarks[2]["title"] == "Merger 2014"

    # Orphan column: new row is "Yes", existing rows are "No".
    assert "Orphan" in new_df.columns
    assert list(new_df["Orphan"]) == ["No", "No", "Yes"]


def test_multiple_orphans_get_sequential_indices():
    df = pd.DataFrame(
        {"Index#": ["5"], "Document Type": ["Deed"], "Received Date": ["x"]}
    )
    bookmarks = [
        {"title": "5-Deed-1/1/2020", "level": 0, "page": 1},
        {"title": "Merger 2014", "level": 0, "page": 2},
        {"title": "Exhibit A", "level": 0, "page": 3},
    ]
    new_df, new_bm = add_rows_for_new_bookmarks(
        df, bookmarks, {"Merger 2014", "Exhibit A"}
    )
    assert list(new_df["Index#"]) == ["5", "6", "7"]
    assert new_bm[1]["title"] == "6-Merger 2014"
    assert new_bm[2]["title"] == "7-Exhibit A"

    # Orphan column: original row is "No", both added rows are "Yes".
    assert "Orphan" in new_df.columns
    assert new_df.iloc[0]["Orphan"] == "No"
    assert new_df.iloc[1]["Orphan"] == "Yes"
    assert new_df.iloc[2]["Orphan"] == "Yes"


def test_no_matching_titles_returns_equivalent_data():
    df, bookmarks = _df(), _bookmarks()
    new_df, new_bm = add_rows_for_new_bookmarks(df, bookmarks, set())
    assert len(new_df) == 2
    assert [b["title"] for b in new_bm] == [b["title"] for b in bookmarks]
    # No Orphan column when no rows are added.
    assert "Orphan" not in new_df.columns


def test_non_numeric_index_ignored_when_computing_next_index():
    """Non-numeric Index# values are ignored; max is taken from numeric-only entries."""
    df = pd.DataFrame(
        {
            "Index#": ["A5", "2"],
            "Document Type": ["Deed", "Release"],
            "Received Date": ["2020-01-01", "2020-02-02"],
        }
    )
    bookmarks = [
        {"title": "A5-Deed-1/1/2020", "level": 0, "page": 1},
        {"title": "2-Release-2/2/2020", "level": 0, "page": 2},
        {"title": "Merger 2014", "level": 0, "page": 3},
    ]
    new_df, new_bm = add_rows_for_new_bookmarks(df, bookmarks, {"Merger 2014"})

    # Max numeric index is 2, so the orphan gets index 3.
    assert new_df.iloc[-1]["Index#"] == "3"
    assert new_bm[2]["title"] == "3-Merger 2014"
    # The added row is marked as an orphan.
    assert new_df.iloc[-1]["Orphan"] == "Yes"


def test_no_match_returned_bookmarks_are_independent_copies():
    """On the no-match path, returned bookmark dicts are copies; mutating them
    does not affect the original input bookmark dicts."""
    df, bookmarks = _df(), _bookmarks()
    _original_titles = [b["title"] for b in bookmarks]

    _new_df, new_bm = add_rows_for_new_bookmarks(df, bookmarks, set())

    # Mutate the returned copies.
    for bm in new_bm:
        bm["title"] = "MUTATED"

    # Original input dicts are unchanged.
    assert [b["title"] for b in bookmarks] == _original_titles
