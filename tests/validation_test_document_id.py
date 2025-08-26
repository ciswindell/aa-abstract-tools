#!/usr/bin/env python3
"""
Tests for new validation functionality related to Document_ID system.
Tests duplicate indices and bookmark linking error handling.
"""

import pandas as pd
import pytest

from core.services.validate import ValidationService
from core.transform.excel import create_document_links
from validators.input_sheet_validator import find_duplicate_index_values
from validators.pdf_validator import PDFValidator


def test_find_duplicate_index_values_detects_duplicates():
    """Test that find_duplicate_index_values detects duplicate Index# values."""

    # DataFrame with duplicate Index# values
    df = pd.DataFrame(
        {
            "Index#": ["A1", "B2", "A1", "C3"],  # A1 is duplicated
            "Document Type": ["Deed", "Lien", "Assignment", "Deed"],
        }
    )

    duplicates = find_duplicate_index_values(df)
    assert "A1" in duplicates, "Should detect A1 as duplicate"
    assert len(duplicates) == 1, "Should find exactly one duplicate value"


def test_find_duplicate_index_values_no_duplicates():
    """Test that find_duplicate_index_values returns empty list when no duplicates."""

    df = pd.DataFrame(
        {"Index#": ["A1", "B2", "C3"], "Document Type": ["Deed", "Lien", "Assignment"]}
    )

    duplicates = find_duplicate_index_values(df)
    assert duplicates == [], "Should return empty list when no duplicates"


def test_find_duplicate_index_values_handles_missing_column():
    """Test that find_duplicate_index_values handles missing Index# column gracefully."""

    df = pd.DataFrame({"Document Type": ["Deed", "Lien"]})

    duplicates = find_duplicate_index_values(df)
    assert duplicates == [], "Should return empty list when Index# column missing"


def test_pdf_validator_detects_duplicate_bookmark_indices():
    """Test that PDFValidator detects duplicate bookmark leading numbers."""

    bookmarks = [
        {"title": "A1-Deed-1/1/2024", "page": 1},
        {"title": "B2-Lien-1/2/2024", "page": 3},
        {"title": "A1-Assignment-1/3/2024", "page": 5},  # A1 duplicated
    ]

    result = PDFValidator.validate_bookmark_index_duplicates(bookmarks)
    assert result is not None, "Should detect duplicates"
    duplicate_groups = result["duplicate_groups"]
    assert len(duplicate_groups) == 1, "Should have one duplicate group"
    assert duplicate_groups[0]["index"] == "A1", "Should detect A1 as duplicate"
    assert len(duplicate_groups[0]["titles"]) == 2, "Should have 2 titles with A1"


def test_pdf_validator_no_duplicate_bookmark_indices():
    """Test that PDFValidator returns None when no duplicate bookmark indices."""

    bookmarks = [
        {"title": "A1-Deed-1/1/2024", "page": 1},
        {"title": "B2-Lien-1/2/2024", "page": 3},
        {"title": "C3-Assignment-1/3/2024", "page": 5},
    ]

    result = PDFValidator.validate_bookmark_index_duplicates(bookmarks)
    assert result is None, "Should return None when no duplicates"


def test_validation_service_raises_on_duplicate_excel_indices():
    """Test that ValidationService raises ValueError for duplicate Excel indices."""

    df = pd.DataFrame(
        {
            "Index#": ["A1", "B2", "A1"],  # A1 duplicated
            "Document Type": ["Deed", "Lien", "Assignment"],
            "Legal Description": ["Lot 1", "Lot 2", "Lot 3"],
            "Grantee": ["John", "Jane", "Bob"],
            "Grantor": ["Alice", "Charlie", "Eve"],
            "Document Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "Received Date": ["2024-01-05", "2024-01-06", "2024-01-07"],
        }
    )

    required_columns = [
        "Index#",
        "Document Type",
        "Legal Description",
        "Grantee",
        "Grantor",
        "Document Date",
        "Received Date",
    ]

    validator = ValidationService(required_columns)

    with pytest.raises(ValueError) as exc_info:
        validator.run(df=df)

    error_message = str(exc_info.value)
    assert (
        "Duplicate Index# values" in error_message
    ), "Should mention duplicate Index# values"
    assert "A1" in error_message, "Should mention the specific duplicate value"


def test_validation_service_raises_on_duplicate_pdf_indices():
    """Test that ValidationService raises ValueError for duplicate PDF bookmark indices."""

    bookmarks = [
        {"title": "A1-Deed-1/1/2024", "page": 1},
        {"title": "B2-Lien-1/2/2024", "page": 3},
        {"title": "A1-Assignment-1/3/2024", "page": 5},  # A1 duplicated
    ]

    validator = ValidationService([])

    with pytest.raises(ValueError) as exc_info:
        validator.run(bookmarks=bookmarks)

    error_message = str(exc_info.value)
    assert (
        "Duplicate index numbers found in bookmarks" in error_message
    ), "Should mention duplicate bookmark indices"
    assert "A1-Deed-1/1/2024" in error_message, "Should show full bookmark title"
    assert "A1-Assignment-1/3/2024" in error_message, "Should show full bookmark title"


def test_create_document_links_raises_on_missing_bookmark():
    """Test that create_document_links raises ValueError when Excel row has no matching bookmark."""

    df = pd.DataFrame(
        {"Index#": ["A1", "B2", "C3"], "Document Type": ["Deed", "Lien", "Assignment"]}
    )

    # Bookmarks missing C3
    bookmarks = [
        {"title": "A1-Deed-1/1/2024", "page": 1, "level": 0},
        {"title": "B2-Lien-1/2/2024", "page": 3, "level": 0},
        # C3 missing
    ]

    with pytest.raises(ValueError) as exc_info:
        create_document_links(df, bookmarks, "/test/file.xlsx")

    error_message = str(exc_info.value)
    assert "No PDF bookmark found" in error_message, "Should mention missing bookmark"
    assert "C3" in error_message, "Should mention the specific missing index"


def test_create_document_links_raises_on_duplicate_bookmarks():
    """Test that create_document_links raises ValueError when multiple bookmarks have same index."""

    df = pd.DataFrame({"Index#": ["A1", "B2"], "Document Type": ["Deed", "Lien"]})

    # Multiple bookmarks with A1
    bookmarks = [
        {"title": "A1-Deed-1/1/2024", "page": 1, "level": 0},
        {"title": "A1-Assignment-1/2/2024", "page": 3, "level": 0},  # Duplicate A1
        {"title": "B2-Lien-1/3/2024", "page": 5, "level": 0},
    ]

    with pytest.raises(ValueError) as exc_info:
        create_document_links(df, bookmarks, "/test/file.xlsx")

    error_message = str(exc_info.value)
    assert (
        "Multiple bookmarks found" in error_message
    ), "Should mention multiple bookmarks"
    assert "A1" in error_message, "Should mention the specific duplicate index"


def test_create_document_links_succeeds_with_valid_data():
    """Test that create_document_links succeeds with valid data."""

    df = pd.DataFrame({"Index#": ["A1", "B2"], "Document Type": ["Deed", "Lien"]})

    bookmarks = [
        {"title": "A1-Deed-1/1/2024", "page": 1, "level": 0},
        {"title": "B2-Lien-1/2/2024", "page": 3, "level": 0},
    ]

    # Should succeed and return DocumentLink objects
    links = create_document_links(df, bookmarks, "/test/file.xlsx")

    assert len(links) == 2, "Should create 2 DocumentLink objects"
    assert all(
        len(link.document_id) == 8 for link in links
    ), "All Document_IDs should be 8 characters"
    assert (
        links[0].original_bookmark_title == "A1-Deed-1/1/2024"
    ), "Should preserve original bookmark title"


def test_validation_service_passes_with_valid_data():
    """Test that ValidationService passes with valid Excel and PDF data."""

    df = pd.DataFrame(
        {
            "Index#": ["A1", "B2", "C3"],  # No duplicates
            "Document Type": ["Deed", "Lien", "Assignment"],
            "Legal Description": ["Lot 1", "Lot 2", "Lot 3"],
            "Grantee": ["John", "Jane", "Bob"],
            "Grantor": ["Alice", "Charlie", "Eve"],
            "Document Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "Received Date": ["2024-01-05", "2024-01-06", "2024-01-07"],
        }
    )

    bookmarks = [
        {"title": "A1-Deed-1/1/2024", "page": 1},
        {"title": "B2-Lien-1/2/2024", "page": 3},
        {"title": "C3-Assignment-1/3/2024", "page": 5},  # No duplicates
    ]

    required_columns = [
        "Index#",
        "Document Type",
        "Legal Description",
        "Grantee",
        "Grantor",
        "Document Date",
        "Received Date",
    ]

    validator = ValidationService(required_columns)

    # Should not raise any exceptions
    result = validator.run(df=df, bookmarks=bookmarks)

    assert result["excel"]["ok"] is True, "Excel validation should pass"
    assert result["pdf"]["ok"] is True, "PDF validation should pass"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
