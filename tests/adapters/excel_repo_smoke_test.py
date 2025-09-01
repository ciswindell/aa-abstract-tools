#!/usr/bin/env python3
"""
Smoke/Parity tests for ExcelOpenpyxlRepo save behavior using an existing fixture.

This test verifies that after applying pure transforms and saving back into a
template workbook/sheet, the resulting workbook data matches the transformed
DataFrame (content-identical on intersecting columns).
"""

import tempfile
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from adapters.excel_repo import ExcelOpenpyxlRepo
from core.transform.excel import sort_and_renumber


def _first_sheet_name(xlsx_path: str) -> str:
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    try:
        return wb.sheetnames[0]
    finally:
        wb.close()


def test_excel_save_parity_on_fixture():
    # Create a minimal test Excel file in memory
    test_data = {
        "Index#": ["1", "2", "3"],
        "Document Type": ["Assignment", "Report", "Contract"],
        "Document Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "Received Date": ["2024-01-15", "2024-01-16", "2024-01-17"],
    }
    df_original = pd.DataFrame(test_data)

    # Create temporary fixture file
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_fixture:
        fixture_path = Path(tmp_fixture.name)
        df_original.to_excel(fixture_path, index=False, sheet_name="Index")

    sheet = "Index"

    # Load fixture using ExcelRepo to mimic app behavior (preserves dates, cleans Index#)
    repo = ExcelOpenpyxlRepo()
    df = repo.load(str(fixture_path), sheet)

    # Apply pure transforms
    df_expected = sort_and_renumber(df)

    # Save into a temp output using the same template and target sheet
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        out_path = Path(tmp.name)

    # Use the original file as template to preserve formatting/sheets
    repo.save(
        df_expected,
        template_path=str(fixture_path),
        target_sheet=sheet,
        out_path=str(out_path),
    )

    # Read workbook back using ExcelRepo to get same data types as input
    df_out = repo.load(str(out_path), sheet)

    common_cols = [
        c
        for c in df_expected.columns
        if c in df_out.columns and c != "Bookmark Formula"
    ]
    assert common_cols, (
        "No common columns between expected DataFrame and saved workbook"
    )

    # Compare DataFrames - dates should now be preserved as datetime objects
    # Only convert to string for Index# and text columns, preserve datetime for date columns
    left = df_expected[common_cols].reset_index(drop=True)
    right = df_out[common_cols].reset_index(drop=True)

    # For date columns, normalize to date-only (remove time component) for comparison
    for date_col in ("Document Date", "Received Date"):
        if date_col in left.columns and date_col in right.columns:
            # Convert to datetime if not already, then to date-only
            left[date_col] = pd.to_datetime(left[date_col]).dt.date
            right[date_col] = pd.to_datetime(right[date_col]).dt.date

    pd.testing.assert_frame_equal(left, right, check_dtype=False)

    # Cleanup temporary files
    fixture_path.unlink(missing_ok=True)
    out_path.unlink(missing_ok=True)
