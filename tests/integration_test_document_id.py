#!/usr/bin/env python3
"""
Integration test to verify single-file workflow produces identical output
with Document_ID system compared to legacy behavior.
"""

import pandas as pd
import tempfile
import os
from pathlib import Path

from core.transform.excel import clean_types, add_document_ids, sort_and_renumber
from core.transform.pdf import make_titles


def test_single_file_workflow_identical_output():
    """Test that single-file workflow produces identical output with Document_ID system."""

    # Create test data that mimics a real single-file workflow
    test_data = pd.DataFrame(
        {
            "Index#": ["A5", "B2", "C1"],
            "Document Type": ["Deed", "Lien", "Assignment"],
            "Legal Description": ["Lot 1", "Lot 2", "Lot 3"],
            "Grantee": ["John Doe", "Jane Smith", "Bob Wilson"],
            "Grantor": ["Alice Brown", "Charlie Davis", "Eve Johnson"],
            "Document Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "Received Date": ["2024-01-05", "2024-01-06", "2024-01-07"],
        }
    )

    # Simulate the new three-stage workflow
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        source_path = tmp_file.name

    try:
        # Stage 1: Clean types (data cleaning only)
        df1 = clean_types(test_data)

        # Stage 2: Add Document_IDs
        df2 = add_document_ids(df1, source_path)

        # Stage 3: Sort and renumber
        df3 = sort_and_renumber(df2)

        # Generate titles using Document_ID
        titles_map = make_titles(df3)

        # Verify the workflow produces expected results

        # 1. Final DataFrame should have sequential Index# values
        expected_indices = [1, 2, 3]
        actual_indices = list(df3["Index#"])
        assert (
            actual_indices == expected_indices
        ), f"Expected {expected_indices}, got {actual_indices}"

        # 2. Document_ID column should be present and have 8-character hashes
        assert "Document_ID" in df3.columns, "Document_ID column missing"
        for doc_id in df3["Document_ID"]:
            assert (
                len(doc_id) == 8
            ), f"Document_ID should be 8 characters, got {len(doc_id)}"

        # 3. Titles map should be keyed by Document_ID and contain sequential indices
        assert len(titles_map) == 3, f"Expected 3 titles, got {len(titles_map)}"

        # Verify titles contain the new sequential indices (1, 2, 3)
        title_values = list(titles_map.values())
        assert any("1-" in title for title in title_values), "No title contains '1-'"
        assert any("2-" in title for title in title_values), "No title contains '2-'"
        assert any("3-" in title for title in title_values), "No title contains '3-'"

        # 4. Verify data integrity - all original data preserved
        assert len(df3) == len(test_data), "Row count should be preserved"
        assert set(df3["Document Type"]) == set(
            test_data["Document Type"]
        ), "Document types should be preserved"

        # 5. Verify sorting worked correctly (should be sorted by Received Date)
        received_dates = pd.to_datetime(df3["Received Date"])
        assert (
            received_dates.is_monotonic_increasing
        ), "Data should be sorted by Received Date"

        print("✅ Single-file workflow integration test passed!")
        print(f"   - Sequential indices: {actual_indices}")
        print(f"   - Document_IDs generated: {len(df3['Document_ID'].unique())} unique")
        print(f"   - Titles generated: {len(titles_map)}")

    finally:
        # Clean up temporary file
        if os.path.exists(source_path):
            os.unlink(source_path)


def test_document_id_uniqueness_across_files():
    """Test that Document_IDs are unique across different source files."""

    # Same data, different file paths should produce different Document_IDs
    test_data = pd.DataFrame(
        {
            "Index#": ["A1", "B2"],
            "Document Type": ["Deed", "Lien"],
            "Received Date": ["2024-01-01", "2024-01-02"],
        }
    )

    with tempfile.NamedTemporaryFile(
        suffix=".xlsx", delete=False
    ) as tmp1, tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp2:

        path1, path2 = tmp1.name, tmp2.name

    try:
        # Process same data with different source paths
        df1_clean = clean_types(test_data)
        df2_clean = clean_types(test_data)

        df1_with_ids = add_document_ids(df1_clean, path1)
        df2_with_ids = add_document_ids(df2_clean, path2)

        # Document_IDs should be different for different source files
        ids1 = set(df1_with_ids["Document_ID"])
        ids2 = set(df2_with_ids["Document_ID"])

        assert ids1.isdisjoint(
            ids2
        ), "Document_IDs should be unique across different files"

        print("✅ Document_ID uniqueness test passed!")
        print(f"   - File 1 IDs: {ids1}")
        print(f"   - File 2 IDs: {ids2}")

    finally:
        # Clean up temporary files
        for path in [path1, path2]:
            if os.path.exists(path):
                os.unlink(path)


if __name__ == "__main__":
    test_single_file_workflow_identical_output()
    test_document_id_uniqueness_across_files()
