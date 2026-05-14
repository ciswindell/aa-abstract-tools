#!/usr/bin/env python3
"""
Unit tests for ValidateStep class.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from core.pipeline.context import PipelineContext
from core.pipeline.steps.validate_step import ValidateStep


class TestValidateStep:
    """Test cases for ValidateStep comprehensive validation logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.excel_repo = Mock()
        self.pdf_repo = Mock()

        self.logger = Mock()
        self.ui = Mock()

        self.validate_step = ValidateStep(
            excel_repo=self.excel_repo,
            pdf_repo=self.pdf_repo,
            logger=self.logger,
            ui=self.ui,
        )

    def create_test_context(self, file_pairs):
        """Create a test context with given file pairs."""
        return PipelineContext(
            file_pairs=file_pairs,
            options={"backup": False, "sort_bookmarks": False, "reorder_pages": False},
        )

    def test_execute_success_single_file(self):
        """Test successful validation with single file."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # Mock all validation methods to succeed
        with (
            patch.object(self.validate_step, "_validate_file_existence"),
            patch.object(self.validate_step, "_validate_excel_sheets"),
            patch.object(self.validate_step, "_validate_excel_data_integrity"),
            patch.object(self.validate_step, "_validate_pdf_bookmarks"),
            patch.object(self.validate_step, "_validate_pdf_excel_cross_reference"),
        ):
            # Should complete without error.
            # Per-step info logs were reduced in spec 003-reduce-info-logging.
            self.validate_step.execute(context)

    def test_execute_success_multiple_files(self):
        """Test successful validation with multiple files."""
        context = self.create_test_context(
            [("file1.xlsx", "file1.pdf", "Sheet1"), ("file2.xlsx", "file2.pdf", "Data")]
        )

        # Mock all validation methods to succeed
        with (
            patch.object(self.validate_step, "_validate_file_existence"),
            patch.object(self.validate_step, "_validate_excel_sheets"),
            patch.object(self.validate_step, "_validate_excel_data_integrity"),
            patch.object(self.validate_step, "_validate_pdf_bookmarks"),
            patch.object(self.validate_step, "_validate_pdf_excel_cross_reference"),
        ):
            # No-raise across multiple file pairs.
            self.validate_step.execute(context)

    # File Existence Validation Tests

    def test_validate_file_existence_success(self):
        """Test successful file existence validation."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        with patch.object(self.validate_step, "_validate_file_exists") as mock_validate:
            self.validate_step._validate_file_existence(context)

            # Should validate both Excel and PDF files
            assert mock_validate.call_count == 2
            mock_validate.assert_any_call("test.xlsx", "Excel file 1")
            mock_validate.assert_any_call("test.pdf", "PDF file 1")

    def test_validate_file_exists_success(self):
        """Test successful individual file validation."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=True),
            patch("builtins.open", create=True) as mock_open,
        ):
            mock_file = Mock()
            mock_file.read.return_value = b"test"
            mock_open.return_value.__enter__.return_value = mock_file

            # Should not raise any exception
            self.validate_step._validate_file_exists("test.xlsx", "Excel file")

    def test_validate_file_exists_empty_path(self):
        """Test file validation with empty path."""
        with pytest.raises(ValueError, match="Excel file file path is empty"):
            self.validate_step._validate_file_exists("", "Excel file")

    def test_validate_file_exists_not_found(self):
        """Test file validation when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(
                FileNotFoundError, match=r"Excel file file not found: missing\.xlsx"
            ):
                self.validate_step._validate_file_exists("missing.xlsx", "Excel file")

    def test_validate_file_exists_not_file(self):
        """Test file validation when path is not a file."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=False),
        ):
            with pytest.raises(
                ValueError, match="Excel file path is not a file: directory"
            ):
                self.validate_step._validate_file_exists("directory", "Excel file")

    def test_validate_file_exists_not_readable(self):
        """Test file validation when file is not readable."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=True),
            patch("builtins.open", side_effect=PermissionError("Access denied")),
        ):
            with pytest.raises(
                Exception, match=r"Excel file file is not readable.*Access denied"
            ):
                self.validate_step._validate_file_exists("protected.xlsx", "Excel file")

    # Excel Sheet Validation Tests

    def test_validate_excel_sheets_success(self):
        """Test successful Excel sheet validation."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        with patch.object(
            self.validate_step, "_validate_excel_sheet", return_value="Sheet1"
        ):
            self.validate_step._validate_excel_sheets(context)

            # Context should remain unchanged
            assert context.file_pairs == [("test.xlsx", "test.pdf", "Sheet1")]

    def test_validate_excel_sheets_updated(self):
        """Test Excel sheet validation with sheet name update."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "BadSheet")])

        with patch.object(
            self.validate_step, "_validate_excel_sheet", return_value="GoodSheet"
        ):
            self.validate_step._validate_excel_sheets(context)

            # Context should be updated with new sheet name
            assert context.file_pairs == [("test.xlsx", "test.pdf", "GoodSheet")]

    def test_validate_excel_sheet_exists(self):
        """Test Excel sheet validation when sheet exists."""
        self.excel_repo.get_sheet_names.return_value = ["Sheet1", "Data", "Summary"]

        result = self.validate_step._validate_excel_sheet("test.xlsx", "Sheet1")

        assert result == "Sheet1"

    def test_validate_excel_sheet_not_exists_user_selects(self):
        """Test Excel sheet validation when sheet doesn't exist and user selects one."""
        self.excel_repo.get_sheet_names.return_value = ["Sheet1", "Data", "Summary"]
        self.ui.prompt_sheet_selection.return_value = "Data"

        result = self.validate_step._validate_excel_sheet("test.xlsx", "BadSheet")

        assert result == "Data"
        self.ui.prompt_sheet_selection.assert_called_once_with(
            file_path="test.xlsx",
            sheet_names=["Sheet1", "Data", "Summary"],
            default_sheet="Sheet1",
        )

    def test_validate_excel_sheet_no_sheets_available(self):
        """Test Excel sheet validation when no sheets are available."""
        self.excel_repo.get_sheet_names.return_value = []

        with pytest.raises(Exception, match="No sheets found in Excel file"):
            self.validate_step._validate_excel_sheet("test.xlsx", "Sheet1")

    def test_validate_excel_sheet_user_cancels(self):
        """Test Excel sheet validation when user cancels selection."""
        self.excel_repo.get_sheet_names.return_value = ["Sheet1", "Data"]
        self.ui.prompt_sheet_selection.return_value = None

        with pytest.raises(Exception, match="No sheet selected for Excel file"):
            self.validate_step._validate_excel_sheet("test.xlsx", "BadSheet")

    # Excel Data Integrity Tests

    def test_validate_excel_data_integrity_success(self):
        """Test successful Excel data integrity validation."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # Mock valid DataFrame
        valid_df = pd.DataFrame(
            {"Index#": ["1", "2", "3"], "Document Type": ["Type1", "Type2", "Type3"]}
        )
        self.excel_repo.load.return_value = valid_df

        # Should complete without error
        self.validate_step._validate_excel_data_integrity(context)

    def test_validate_excel_data_integrity_empty_dataframe(self):
        """Test Excel data integrity validation with empty DataFrame."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        self.excel_repo.load.return_value = pd.DataFrame()

        with pytest.raises(
            Exception, match=r"Excel sheet 'Sheet1' is empty in file 'test\.xlsx'"
        ):
            self.validate_step._validate_excel_data_integrity(context)

    def test_validate_excel_data_integrity_missing_index_column(self):
        """Test Excel data integrity validation with missing Index# column."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # DataFrame without Index# column
        invalid_df = pd.DataFrame(
            {"Document Type": ["Type1", "Type2"], "Date": ["2024-01-01", "2024-01-02"]}
        )
        self.excel_repo.load.return_value = invalid_df

        with pytest.raises(Exception, match="Required column 'Index#' not found"):
            self.validate_step._validate_excel_data_integrity(context)

    def test_validate_excel_data_integrity_duplicate_indices(self):
        """Test Excel data integrity validation with duplicate Index# values."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # DataFrame with duplicate Index# values
        duplicate_df = pd.DataFrame(
            {
                "Index#": ["1", "2", "1", "3", "2"],  # Duplicates: 1, 2
                "Document Type": ["Type1", "Type2", "Type3", "Type4", "Type5"],
            }
        )
        self.excel_repo.load.return_value = duplicate_df

        with pytest.raises(Exception) as exc_info:
            self.validate_step._validate_excel_data_integrity(context)

        error_msg = str(exc_info.value)
        assert "Duplicate Index# values found" in error_msg
        assert "'1'" in error_msg and "'2'" in error_msg

    def test_validate_excel_data_integrity_empty_indices(self):
        """Test Excel data integrity validation with empty Index# values."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # DataFrame with empty Index# values
        empty_df = pd.DataFrame(
            {
                "Index#": ["1", "", "3", None, "nan"],
                "Document Type": ["Type1", "Type2", "Type3", "Type4", "Type5"],
            }
        )
        self.excel_repo.load.return_value = empty_df

        with pytest.raises(Exception) as exc_info:
            self.validate_step._validate_excel_data_integrity(context)

        error_msg = str(exc_info.value)
        assert "empty Index# values" in error_msg

    # PDF Bookmark Validation Tests

    def test_validate_pdf_bookmarks_success(self):
        """Test successful PDF bookmark validation."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # Mock valid bookmarks
        valid_bookmarks = [
            {"title": "1-Document One", "page": 1},
            {"title": "2-Document Two", "page": 5},
            {"title": "3-Document Three", "page": 10},
        ]
        self.pdf_repo.read.return_value = (valid_bookmarks, 15)

        with patch(
            "core.transform.pdf.extract_original_index", side_effect=["1", "2", "3"]
        ):
            self.validate_step._validate_pdf_bookmarks(context)

    def test_validate_pdf_bookmarks_no_pages(self):
        """Test PDF bookmark validation with no pages."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        self.pdf_repo.read.return_value = ([], 0)

        with pytest.raises(ValueError, match=r"PDF 'test\.pdf' has no pages"):
            self.validate_step._validate_pdf_bookmarks(context)

    def test_validate_pdf_bookmarks_no_bookmarks(self):
        """Test PDF bookmark validation with no bookmarks."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        self.pdf_repo.read.return_value = ([], 10)

        with pytest.raises(ValueError, match=r"PDF 'test\.pdf' has no bookmarks"):
            self.validate_step._validate_pdf_bookmarks(context)

    def test_validate_pdf_bookmarks_invalid_format(self):
        """Test PDF bookmark validation with invalid bookmark format."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        invalid_bookmarks = [
            {"title": "1-Valid Document", "page": 1},
            {"title": "Invalid Bookmark", "page": 5},
            {"title": "Another Bad One", "page": 10},
        ]
        self.pdf_repo.read.return_value = (invalid_bookmarks, 15)

        # Mock extract_original_index to return None for invalid bookmarks
        def mock_extract(title):
            return "1" if "1-Valid" in title else None

        with patch(
            "core.transform.pdf.extract_original_index", side_effect=mock_extract
        ):
            with pytest.raises(ValueError) as exc_info:
                self.validate_step._validate_pdf_bookmarks(context)

            error_msg = str(exc_info.value)
            assert "don't follow required Index# format" in error_msg
            assert "Invalid Bookmark" in error_msg

    def test_validate_pdf_bookmarks_duplicate_indices(self):
        """Test PDF bookmark validation with duplicate bookmark indices."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        duplicate_bookmarks = [
            {"title": "1-Document One", "page": 1},
            {"title": "1-Another Document", "page": 5},  # Duplicate index
            {"title": "2-Document Two", "page": 10},
        ]
        self.pdf_repo.read.return_value = (duplicate_bookmarks, 15)

        with patch(
            "core.transform.pdf.extract_original_index", side_effect=["1", "1", "2"]
        ):
            with pytest.raises(ValueError) as exc_info:
                self.validate_step._validate_pdf_bookmarks(context)

            error_msg = str(exc_info.value)
            assert "Duplicate bookmark indices" in error_msg
            assert "'1'" in error_msg

    def test_validate_pdf_bookmarks_duplicate_pages(self):
        """Test PDF bookmark validation with multiple bookmarks on same page."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        same_page_bookmarks = [
            {"title": "1-Document One", "page": 1},
            {"title": "2-Document Two", "page": 1},  # Same page
            {"title": "3-Document Three", "page": 5},
        ]
        self.pdf_repo.read.return_value = (same_page_bookmarks, 10)

        with patch(
            "core.transform.pdf.extract_original_index", side_effect=["1", "2", "3"]
        ):
            with pytest.raises(ValueError) as exc_info:
                self.validate_step._validate_pdf_bookmarks(context)

            error_msg = str(exc_info.value)
            assert "Multiple bookmarks point to the same pages" in error_msg
            assert "Page 1:" in error_msg
            assert "1-Document One" in error_msg
            assert "2-Document Two" in error_msg

    # Cross-Reference Validation Tests

    def test_validate_pdf_excel_cross_reference_success(self):
        """Test successful PDF-Excel cross-reference validation."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # Mock Excel data
        excel_df = pd.DataFrame(
            {"Index#": ["1", "2", "3"], "Document Type": ["Type1", "Type2", "Type3"]}
        )
        self.excel_repo.load.return_value = excel_df

        # Mock PDF bookmarks
        bookmarks = [
            {"title": "1-Document One", "page": 1},
            {"title": "2-Document Two", "page": 5},
        ]
        self.pdf_repo.read.return_value = (bookmarks, 10)

        # Mock extract_original_index to return appropriate values
        def mock_extract(title):
            if "1-Document" in title:
                return "1"
            elif "2-Document" in title:
                return "2"
            return None

        with patch(
            "core.transform.pdf.extract_original_index", side_effect=mock_extract
        ):
            self.validate_step._validate_pdf_excel_cross_reference(context)

    def test_validate_pdf_excel_cross_reference_orphaned_bookmarks(self):
        """Test cross-reference validation with orphaned PDF bookmarks."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # Mock Excel data (only has indices 1, 2)
        excel_df = pd.DataFrame(
            {"Index#": ["1", "2"], "Document Type": ["Type1", "Type2"]}
        )
        self.excel_repo.load.return_value = excel_df

        # Mock PDF bookmarks (has indices 1, 2, 3, 4)
        bookmarks = [
            {"title": "1-Document One", "page": 1},
            {"title": "2-Document Two", "page": 5},
            {"title": "3-Orphaned Doc", "page": 10},
            {"title": "4-Another Orphan", "page": 15},
        ]
        self.pdf_repo.read.return_value = (bookmarks, 20)

        # Mock extract_original_index to return appropriate values
        def mock_extract(title):
            if "1-Document" in title:
                return "1"
            elif "2-Document" in title:
                return "2"
            elif "3-Orphaned" in title:
                return "3"
            elif "4-Another" in title:
                return "4"
            return None

        with patch(
            "core.transform.pdf.extract_original_index", side_effect=mock_extract
        ):
            with pytest.raises(Exception) as exc_info:
                self.validate_step._validate_pdf_excel_cross_reference(context)

            error_msg = str(exc_info.value)
            assert "PDF bookmark(s) have no matching Excel row" in error_msg
            assert "'3'" in error_msg and "'4'" in error_msg

    def test_validate_pdf_excel_cross_reference_no_valid_bookmarks(self):
        """Test cross-reference validation when no bookmarks have valid indices."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # Mock Excel data
        excel_df = pd.DataFrame(
            {"Index#": ["1", "2"], "Document Type": ["Type1", "Type2"]}
        )
        self.excel_repo.load.return_value = excel_df

        # Mock PDF bookmarks with invalid format
        bookmarks = [
            {"title": "Invalid Bookmark", "page": 1},
            {"title": "Another Invalid", "page": 5},
        ]
        self.pdf_repo.read.return_value = (bookmarks, 10)

        # Mock extract_original_index to return None for all bookmarks
        with patch("core.transform.pdf.extract_original_index", return_value=None):
            # Should complete successfully (no valid bookmarks to cross-reference)
            self.validate_step._validate_pdf_excel_cross_reference(context)

    def test_multiple_file_pairs_validation(self):
        """Test validation with multiple file pairs."""
        context = self.create_test_context(
            [("file1.xlsx", "file1.pdf", "Sheet1"), ("file2.xlsx", "file2.pdf", "Data")]
        )

        # Mock successful validation for both files
        with (
            patch.object(self.validate_step, "_validate_file_exists"),
            patch.object(
                self.validate_step,
                "_validate_excel_sheet",
                side_effect=["Sheet1", "Data"],
            ),
        ):
            # Mock Excel data for both files
            excel_df1 = pd.DataFrame({"Index#": ["1", "2"]})
            excel_df2 = pd.DataFrame({"Index#": ["3", "4"]})
            self.excel_repo.load.side_effect = [
                excel_df1,
                excel_df2,
                excel_df1,
                excel_df2,
            ]

            # Mock PDF data for both files (need enough calls for bookmarks + cross-ref)
            bookmarks1 = [{"title": "1-Doc1", "page": 1}]
            bookmarks2 = [{"title": "3-Doc3", "page": 1}]
            self.pdf_repo.read.side_effect = [
                (bookmarks1, 5),
                (bookmarks2, 3),
                (bookmarks1, 5),
                (bookmarks2, 3),
            ]

            # Mock extract_original_index to return appropriate values
            def mock_extract(title):
                if "1-Doc1" in title:
                    return "1"
                elif "3-Doc3" in title:
                    return "3"
                return None

            with patch(
                "core.transform.pdf.extract_original_index", side_effect=mock_extract
            ):
                self.validate_step.execute(context)

                # Verify both files were processed
                assert (
                    self.excel_repo.load.call_count == 4
                )  # 2 calls per file (integrity + cross-ref)
                assert (
                    self.pdf_repo.read.call_count == 4
                )  # 2 calls per file (bookmarks + cross-ref)

    def test_validation_error_propagation(self):
        """Test that validation errors are properly propagated with context."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # Mock file existence to pass, but Excel data integrity to fail
        with (
            patch.object(self.validate_step, "_validate_file_existence"),
            patch.object(self.validate_step, "_validate_excel_sheets"),
        ):
            # Mock Excel repo to raise an exception
            self.excel_repo.load.side_effect = Exception("Excel file corrupted")

            with pytest.raises(Exception) as exc_info:
                self.validate_step.execute(context)

            # Production re-raises the underlying error without wrapping
            # (validate_step.py comment: "error messages are already clear").
            error_msg = str(exc_info.value)
            assert "Excel file corrupted" in error_msg
