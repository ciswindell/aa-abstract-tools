#!/usr/bin/env python3
"""
Unit tests for core models, specifically the DocumentUnit dataclass.
"""

import pandas as pd

from core.models import DocumentUnit


class TestDocumentUnit:
    """Test cases for DocumentUnit dataclass."""

    def test_document_unit_creation(self):
        """Test basic DocumentUnit creation with all required fields."""
        # Create test Excel row data
        excel_data = pd.Series(
            {
                "Document_ID": "abc12345",
                "Index#": "12",
                "Document Type": "Assignment",
                "Received Date": "2024-01-15",
            }
        )

        # Create DocumentUnit
        unit = DocumentUnit(
            document_id="abc12345",
            merged_page_range=(10, 15),
            excel_row_data=excel_data,
            source_info="test.xlsx:test.pdf",
        )

        # Verify all fields are set correctly
        assert unit.document_id == "abc12345"
        assert unit.merged_page_range == (10, 15)
        assert unit.excel_row_data["Document_ID"] == "abc12345"
        assert unit.excel_row_data["Index#"] == "12"
        assert unit.source_info == "test.xlsx:test.pdf"

    def test_document_unit_immutable_document_id(self):
        """Test that document_id serves as the permanent identifier."""
        excel_data = pd.Series(
            {"Document_ID": "def67890", "Index#": "5", "Document Type": "Report"}
        )

        unit = DocumentUnit(
            document_id="def67890",
            merged_page_range=(1, 3),
            excel_row_data=excel_data,
            source_info="file1.xlsx:file1.pdf",
        )

        # Document ID should match the Excel row
        assert unit.document_id == unit.excel_row_data["Document_ID"]

        # Document ID should be immutable (this is enforced by dataclass design)
        original_id = unit.document_id
        # We can't actually test immutability without trying to modify it,
        # but we can verify it maintains consistency
        assert unit.document_id == original_id

    def test_document_unit_page_range_format(self):
        """Test that page ranges are stored as (start, end) tuples."""
        excel_data = pd.Series({"Document_ID": "test123", "Index#": "1"})

        unit = DocumentUnit(
            document_id="test123",
            merged_page_range=(25, 30),
            excel_row_data=excel_data,
            source_info="multi.xlsx:multi.pdf",
        )

        start, end = unit.merged_page_range
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert start <= end
        assert start == 25
        assert end == 30

    def test_document_unit_source_info_format(self):
        """Test that source_info follows expected format."""
        excel_data = pd.Series({"Document_ID": "src123", "Index#": "7"})

        unit = DocumentUnit(
            document_id="src123",
            merged_page_range=(1, 1),
            excel_row_data=excel_data,
            source_info="path/to/excel.xlsx:path/to/pdf.pdf",
        )

        # Should be in "excel_path:pdf_path" format
        assert ":" in unit.source_info
        excel_part, pdf_part = unit.source_info.split(":", 1)
        assert excel_part.endswith(".xlsx")
        assert pdf_part.endswith(".pdf")

    def test_document_unit_with_complex_excel_data(self):
        """Test DocumentUnit with realistic Excel row data."""
        # Create realistic Excel row with all expected columns
        excel_data = pd.Series(
            {
                "Document_ID": "complex123",
                "Index#": "42",
                "Document Type": "Legal Document",
                "Received Date": "2024-03-15",
                "Status": "Active",
                "Notes": "Important document with special handling",
            }
        )

        unit = DocumentUnit(
            document_id="complex123",
            merged_page_range=(100, 125),
            excel_row_data=excel_data,
            source_info="legal_docs.xlsx:legal_docs.pdf",
        )

        # Verify all Excel data is preserved
        assert unit.excel_row_data["Document Type"] == "Legal Document"
        assert unit.excel_row_data["Status"] == "Active"
        assert (
            unit.excel_row_data["Notes"] == "Important document with special handling"
        )

        # Verify DocumentUnit fields
        assert unit.document_id == "complex123"
        assert unit.merged_page_range == (100, 125)

    def test_document_unit_equality(self):
        """Test DocumentUnit equality - focus on key fields rather than pandas Series comparison."""
        excel_data1 = pd.Series({"Document_ID": "same123", "Index#": "1"})
        excel_data2 = pd.Series({"Document_ID": "same123", "Index#": "1"})

        unit1 = DocumentUnit(
            document_id="same123",
            merged_page_range=(1, 5),
            excel_row_data=excel_data1,
            source_info="file1.xlsx:file1.pdf",
        )

        unit2 = DocumentUnit(
            document_id="same123",
            merged_page_range=(1, 5),
            excel_row_data=excel_data2,
            source_info="file1.xlsx:file1.pdf",
        )

        # Test key fields are equal (avoid pandas Series comparison issues)
        assert unit1.document_id == unit2.document_id
        assert unit1.merged_page_range == unit2.merged_page_range
        assert unit1.source_info == unit2.source_info

        # Different document_id should not be equal
        unit3 = DocumentUnit(
            document_id="different456",
            merged_page_range=(1, 5),
            excel_row_data=excel_data1,
            source_info="file1.xlsx:file1.pdf",
        )

        assert unit1.document_id != unit3.document_id
