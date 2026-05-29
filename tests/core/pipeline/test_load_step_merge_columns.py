#!/usr/bin/env python3
"""
Tests for LoadStep._merge_dataframes column alignment.

Regression coverage for the bug where two merged files whose column headers
differ only by case or surrounding/inner whitespace (e.g. "Source " vs
"Source") were concatenated into TWO distinct columns. Each column was then
populated for only one file's rows, so one file's data appeared to be dropped
from that column in the final output.
"""

import pandas as pd

from core.pipeline.steps.load_step import LoadStep


def _make_step() -> LoadStep:
    """LoadStep instance with no real dependencies (_merge_dataframes needs none)."""
    return LoadStep(excel_repo=None, pdf_repo=None, logger=None, ui=None)


class TestMergeDataframesColumnAlignment:
    def test_whitespace_variant_columns_collapse_to_one(self):
        """'Source ' (trailing space) and 'Source' must merge into a single column."""
        a = pd.DataFrame({"Source ": ["A1", "A2"], "Index#": ["1", "2"]})
        b = pd.DataFrame({"Source": ["B1", "B2"], "Index#": ["1", "2"]})

        merged = _make_step()._merge_dataframes([a, b])

        source_cols = [c for c in merged.columns if str(c).strip().lower() == "source"]
        assert len(source_cols) == 1, (
            f"Expected one 'source' column, got {source_cols}"
        )
        # No values dropped: all four rows have a Source value.
        col = source_cols[0]
        assert merged[col].tolist() == ["A1", "A2", "B1", "B2"]

    def test_case_variant_columns_collapse_to_one(self):
        """Case-only differences ('Grantee' vs 'grantee') must also merge."""
        a = pd.DataFrame({"Grantee": ["x"], "Index#": ["1"]})
        b = pd.DataFrame({"grantee": ["y"], "Index#": ["1"]})

        merged = _make_step()._merge_dataframes([a, b])

        grantee_cols = [
            c for c in merged.columns if str(c).strip().lower() == "grantee"
        ]
        assert len(grantee_cols) == 1
        assert merged[grantee_cols[0]].tolist() == ["x", "y"]

    def test_distinct_columns_are_preserved(self):
        """Genuinely different columns must still be kept separate."""
        a = pd.DataFrame({"Source": ["a"], "Status": ["ok"]})
        b = pd.DataFrame({"Source": ["b"], "Comments": ["note"]})

        merged = _make_step()._merge_dataframes([a, b])

        normalized = {str(c).strip().lower() for c in merged.columns}
        assert {"source", "status", "comments"} <= normalized
