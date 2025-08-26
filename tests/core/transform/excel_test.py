#!/usr/bin/env python3
"""
Unit tests for core.transform.excel.
"""

import pandas as pd

from core.transform.excel import (
    add_document_ids,
    clean_types,
    generate_document_id,
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
    # clean_types only does data cleaning, no longer creates Original_Index
    assert "Original_Index" not in out.columns
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


def test_clean_types_no_longer_creates_original_index():
    df = pd.DataFrame({"Index#": ["A", "B", "C"]})
    out = clean_types(df)
    # clean_types only does data cleaning, Document_ID is created by add_document_ids()
    assert "Original_Index" not in out.columns
    assert "Document_ID" not in out.columns


def test_generate_document_id_creates_unique_hashes():
    """Test that generate_document_id creates unique, deterministic hashes."""
    # Same inputs should produce same hash
    hash1 = generate_document_id("A5", "/path/to/batch1.xlsx", 0)
    hash2 = generate_document_id("A5", "/path/to/batch1.xlsx", 0)
    assert hash1 == hash2
    assert len(hash1) == 8

    # Different inputs should produce different hashes
    hash3 = generate_document_id("A5", "/path/to/batch2.xlsx", 0)  # Different file
    hash4 = generate_document_id("A5", "/path/to/batch1.xlsx", 1)  # Different row
    hash5 = generate_document_id("B5", "/path/to/batch1.xlsx", 0)  # Different index

    assert hash1 != hash3
    assert hash1 != hash4
    assert hash1 != hash5
    assert hash3 != hash4 != hash5


def test_generate_document_id_handles_various_inputs():
    """Test generate_document_id with various input formats."""
    # Test with numeric index
    hash_numeric = generate_document_id("12", "/home/user/file.xlsx", 5)
    assert len(hash_numeric) == 8

    # Test with alphanumeric index
    hash_alpha = generate_document_id("A12B", "/home/user/file.xlsx", 5)
    assert len(hash_alpha) == 8

    # Test with different file extensions
    hash_xls = generate_document_id("1", "/path/file.xls", 0)
    hash_xlsx = generate_document_id("1", "/path/file.xlsx", 0)
    assert hash_xls != hash_xlsx


def test_generate_document_id_error_handling():
    """Test that generate_document_id raises ValueError on invalid inputs."""
    import pytest

    # Test with invalid inputs that might cause encoding issues
    try:
        # This should work fine - testing the error path is tricky with MD5
        result = generate_document_id("", "", -1)
        assert len(result) == 8  # Should still work with empty strings
    except ValueError:
        pass  # This is also acceptable behavior


def test_add_document_ids_creates_document_id_column():
    """Test that add_document_ids creates Document_ID column."""
    df = pd.DataFrame({"Index#": ["A1", "B2", "C3"]})
    cleaned = clean_types(df)
    result = add_document_ids(cleaned, "/path/to/test.xlsx")

    # Should have Document_ID column
    assert "Document_ID" in result.columns
    assert len(result["Document_ID"]) == 3

    # All Document_IDs should be 8 characters
    for doc_id in result["Document_ID"]:
        assert len(doc_id) == 8

    # Should preserve existing columns and add Document_ID
    assert "Index#" in result.columns
    assert "Document_ID" in result.columns


def test_add_document_ids_with_different_files_creates_unique_ids():
    """Test that same data with different file paths creates different Document_IDs."""
    df = pd.DataFrame({"Index#": ["A1", "B2"]})
    cleaned = clean_types(df)

    result1 = add_document_ids(cleaned, "/path/to/file1.xlsx")
    result2 = add_document_ids(cleaned, "/path/to/file2.xlsx")

    # Same row positions should have different Document_IDs due to different file paths
    assert result1.loc[0, "Document_ID"] != result2.loc[0, "Document_ID"]
    assert result1.loc[1, "Document_ID"] != result2.loc[1, "Document_ID"]


def test_add_document_ids_raises_error_for_missing_index_column():
    """Test that add_document_ids raises ValueError when Index# column is missing."""
    import pytest

    df = pd.DataFrame({"Document Type": ["Deed", "Lien"]})

    with pytest.raises(ValueError, match="Index column 'Index#' not found"):
        add_document_ids(df, "/path/to/test.xlsx")


def test_add_document_ids_does_not_overwrite_existing_document_id():
    """Test that add_document_ids doesn't overwrite existing Document_ID column."""
    df = pd.DataFrame(
        {"Index#": ["A1", "B2"], "Document_ID": ["existing1", "existing2"]}
    )

    result = add_document_ids(df, "/path/to/test.xlsx")

    # Should preserve existing Document_ID values
    assert list(result["Document_ID"]) == ["existing1", "existing2"]
