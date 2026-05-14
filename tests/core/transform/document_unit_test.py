#!/usr/bin/env python3
"""
Unit tests for DocumentUnit utility functions.
"""

import pandas as pd

from core.models import DocumentUnit
from core.transform.document_unit import (
    create_document_unit_from_bookmark,
    get_page_count_for_unit,
    link_bookmarks_to_excel_rows,
)


class TestCreateDocumentUnitFromBookmark:
    """Test cases for create_document_unit_from_bookmark function."""

    def test_create_unit_success(self):
        """Test successful DocumentUnit creation from bookmark and Excel row."""
        bookmark = {"title": "12-Assignment-1/15/2024", "page": 5, "level": 0}

        excel_row = pd.Series(
            {"Document_ID": "abc12345", "Index#": "12", "Document Type": "Assignment"}
        )

        page_ranges = {"12-Assignment-1/15/2024": {"start": 5, "end": 8}}

        unit = create_document_unit_from_bookmark(
            bookmark=bookmark,
            excel_row=excel_row,
            page_offset=10,
            source_info="test.xlsx:test.pdf",
            page_ranges=page_ranges,
        )

        assert unit is not None
        assert unit.document_id == "abc12345"
        assert unit.merged_page_range == (15, 18)  # 5+10, 8+10
        assert unit.excel_row_data["Index#"] == "12"
        assert unit.source_info == "test.xlsx:test.pdf"

    def test_create_unit_bookmark_not_in_ranges(self):
        """Test that None is returned when bookmark title not in page_ranges."""
        bookmark = {"title": "Unknown-Document", "page": 1, "level": 0}

        excel_row = pd.Series({"Document_ID": "test123", "Index#": "1"})
        page_ranges = {}  # Empty ranges

        unit = create_document_unit_from_bookmark(
            bookmark=bookmark,
            excel_row=excel_row,
            page_offset=0,
            source_info="test.xlsx:test.pdf",
            page_ranges=page_ranges,
        )

        assert unit is None

    def test_create_unit_with_page_offset(self):
        """Test that page offset is correctly applied to merged page range."""
        bookmark = {"title": "Test-Doc", "page": 1, "level": 0}
        excel_row = pd.Series({"Document_ID": "offset123", "Index#": "1"})
        page_ranges = {"Test-Doc": {"start": 3, "end": 7}}

        # Test with different page offsets
        unit1 = create_document_unit_from_bookmark(
            bookmark, excel_row, 0, "test.xlsx:test.pdf", page_ranges
        )
        assert unit1.merged_page_range == (3, 7)

        unit2 = create_document_unit_from_bookmark(
            bookmark, excel_row, 100, "test.xlsx:test.pdf", page_ranges
        )
        assert unit2.merged_page_range == (103, 107)


class TestLinkBookmarksToExcelRows:
    """Test cases for link_bookmarks_to_excel_rows function."""

    def test_link_bookmarks_success(self):
        """Test successful linking of bookmarks to Excel rows."""
        bookmarks = [
            {"title": "1-Doc1-1/1/2024", "page": 1, "level": 0},
            {"title": "2-Doc2-1/2/2024", "page": 5, "level": 0},
            {"title": "3-Doc3-1/3/2024", "page": 10, "level": 0},
        ]

        excel_df = pd.DataFrame(
            {
                "Index#": ["1", "2", "3"],
                "Document_ID": ["id1", "id2", "id3"],
                "Document Type": ["Type1", "Type2", "Type3"],
            }
        )

        units = link_bookmarks_to_excel_rows(
            bookmarks=bookmarks,
            excel_df=excel_df,
            page_offset=20,
            source_info="multi.xlsx:multi.pdf",
            total_pages=15,
        )

        assert len(units) == 3

        # Check first unit
        assert units[0].document_id == "id1"
        assert units[0].excel_row_data["Index#"] == "1"
        assert units[0].source_info == "multi.xlsx:multi.pdf"

        # Check that page ranges are offset correctly
        # (exact ranges depend on detect_page_ranges implementation)
        for unit in units:
            start, _end = unit.merged_page_range
            assert start > 20  # Should be offset by 20

    def test_link_bookmarks_empty_inputs(self):
        """Test handling of empty bookmarks or DataFrame."""
        # Empty bookmarks
        units1 = link_bookmarks_to_excel_rows(
            bookmarks=[],
            excel_df=pd.DataFrame({"Index#": ["1"], "Document_ID": ["id1"]}),
            page_offset=0,
            source_info="test.xlsx:test.pdf",
            total_pages=10,
        )
        assert units1 == []

        # Empty DataFrame
        units2 = link_bookmarks_to_excel_rows(
            bookmarks=[{"title": "1-Doc", "page": 1, "level": 0}],
            excel_df=pd.DataFrame(),
            page_offset=0,
            source_info="test.xlsx:test.pdf",
            total_pages=10,
        )
        assert units2 == []

    def test_link_bookmarks_no_matches(self):
        """Test when bookmarks don't match Excel rows."""
        bookmarks = [{"title": "999-NoMatch", "page": 1, "level": 0}]

        excel_df = pd.DataFrame({"Index#": ["1", "2"], "Document_ID": ["id1", "id2"]})

        units = link_bookmarks_to_excel_rows(
            bookmarks=bookmarks,
            excel_df=excel_df,
            page_offset=0,
            source_info="test.xlsx:test.pdf",
            total_pages=5,
        )

        assert units == []

    def test_link_bookmarks_partial_matches(self):
        """Test when only some bookmarks match Excel rows."""
        bookmarks = [
            {"title": "1-Match", "page": 1, "level": 0},
            {"title": "999-NoMatch", "page": 5, "level": 0},
            {"title": "2-Match", "page": 10, "level": 0},
        ]

        excel_df = pd.DataFrame({"Index#": ["1", "2"], "Document_ID": ["id1", "id2"]})

        units = link_bookmarks_to_excel_rows(
            bookmarks=bookmarks,
            excel_df=excel_df,
            page_offset=0,
            source_info="test.xlsx:test.pdf",
            total_pages=15,
        )

        # Should only get 2 units (the matching ones)
        assert len(units) == 2
        doc_ids = [unit.document_id for unit in units]
        assert "id1" in doc_ids
        assert "id2" in doc_ids


class TestGetPageCountForUnit:
    """Test cases for get_page_count_for_unit function."""

    def test_page_count_single_page(self):
        """Test page count for single-page DocumentUnit."""
        excel_data = pd.Series({"Document_ID": "single", "Index#": "1"})
        unit = DocumentUnit(
            document_id="single",
            merged_page_range=(5, 5),  # Single page
            excel_row_data=excel_data,
            source_info="test.xlsx:test.pdf",
        )

        count = get_page_count_for_unit(unit)
        assert count == 1

    def test_page_count_multiple_pages(self):
        """Test page count for multi-page DocumentUnit."""
        excel_data = pd.Series({"Document_ID": "multi", "Index#": "1"})
        unit = DocumentUnit(
            document_id="multi",
            merged_page_range=(10, 15),  # 6 pages
            excel_row_data=excel_data,
            source_info="test.xlsx:test.pdf",
        )

        count = get_page_count_for_unit(unit)
        assert count == 6

    def test_page_count_large_range(self):
        """Test page count for large page range."""
        excel_data = pd.Series({"Document_ID": "large", "Index#": "1"})
        unit = DocumentUnit(
            document_id="large",
            merged_page_range=(1, 100),  # 100 pages
            excel_row_data=excel_data,
            source_info="test.xlsx:test.pdf",
        )

        count = get_page_count_for_unit(unit)
        assert count == 100
