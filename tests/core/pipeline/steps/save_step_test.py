#!/usr/bin/env python3
"""
Unit tests for SaveStep class.
"""

from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest
from pypdf import PdfWriter

from core.pipeline.context import PipelineContext
from core.pipeline.steps.save_step import SaveStep


class TestSaveStep:
    """Test cases for SaveStep backup logic and atomic saves."""

    def setup_method(self):
        """Set up test fixtures."""
        self.excel_repo = Mock()
        self.pdf_repo = Mock()

        self.logger = Mock()
        self.ui = Mock()

        self.save_step = SaveStep(
            excel_repo=self.excel_repo,
            pdf_repo=self.pdf_repo,
            logger=self.logger,
            ui=self.ui,
        )

    def create_test_context(self, file_pairs, options=None, with_data=True):
        """Create a test context with given file pairs and optional data."""
        if options is None:
            options = {"backup": False, "sort_bookmarks": False, "reorder_pages": False}

        context = PipelineContext(file_pairs=file_pairs, options=options)

        if with_data:
            # Add test DataFrame
            test_df = pd.DataFrame(
                {
                    "Index#": ["1", "2", "3"],
                    "Document Type": ["Type1", "Type2", "Type3"],
                    "_include": [True, True, False],  # Only first 2 rows flagged
                }
            )
            context.df = test_df

            # Add mock PdfWriter
            mock_writer = Mock(spec=PdfWriter)
            mock_writer.pages = [Mock(), Mock()]  # 2 pages
            mock_writer.outline = [Mock(), Mock()]  # 2 bookmarks
            context.final_pdf = mock_writer

        return context

    # Basic Execution Tests

    def test_execute_success_single_file_no_backup(self):
        """Test successful execution for single file without backup."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        with (
            patch.object(self.save_step, "_save_excel_output") as mock_excel,
            patch.object(self.save_step, "_save_pdf_output") as mock_pdf,
        ):
            self.save_step.execute(context)

            # Verify methods were called with correct parameters
            mock_excel.assert_called_once_with(context, "test.xlsx", False)
            mock_pdf.assert_called_once_with(context, "test.pdf", False)

    def test_execute_success_single_file_with_backup(self):
        """Test successful execution for single file with backup enabled."""
        context = self.create_test_context(
            [("test.xlsx", "test.pdf", "Sheet1")], options={"backup": True}
        )

        with (
            patch.object(self.save_step, "_save_excel_output") as mock_excel,
            patch.object(self.save_step, "_save_pdf_output") as mock_pdf,
        ):
            self.save_step.execute(context)

            # Verify backup is enabled for single file
            mock_excel.assert_called_once_with(context, "test.xlsx", True)
            mock_pdf.assert_called_once_with(context, "test.pdf", True)

    def test_execute_success_merge_workflow(self):
        """Test successful execution for merge workflow (backup disabled)."""
        context = self.create_test_context(
            [
                ("file1.xlsx", "file1.pdf", "Sheet1"),
                ("file2.xlsx", "file2.pdf", "Sheet1"),
            ],
            options={"backup": True},  # Should be ignored for merge workflow
        )

        with (
            patch.object(self.save_step, "_save_excel_output") as mock_excel,
            patch.object(self.save_step, "_save_pdf_output") as mock_pdf,
        ):
            self.save_step.execute(context)

            # Verify backup is disabled for merge workflow even if requested
            excel_out, pdf_out = context.get_output_paths()
            mock_excel.assert_called_once_with(context, excel_out, False)
            mock_pdf.assert_called_once_with(context, pdf_out, False)

    def test_execute_no_excel_data(self):
        """Test execution failure when no Excel data is available."""
        context = self.create_test_context(
            [("test.xlsx", "test.pdf", "Sheet1")], with_data=False
        )

        with pytest.raises(ValueError, match="No Excel data available for saving"):
            self.save_step.execute(context)

    def test_execute_no_pdf_writer(self):
        """Test execution failure when no PDF writer is available."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])
        context.final_pdf = None

        with pytest.raises(ValueError, match="No PDF writer available for saving"):
            self.save_step.execute(context)

    # Excel Output Tests

    @patch("core.pipeline.steps.save_step.atomic_save_with_backup")
    def test_save_excel_output_with_include_flag(self, mock_atomic):
        """Test Excel output saving with _include flag filtering."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # Mock atomic_save_with_backup to execute the write function
        def execute_write_func(original_path, write_func, create_backup):
            write_func(original_path)
            return None

        mock_atomic.side_effect = execute_write_func

        self.save_step._save_excel_output(context, "output.xlsx", False)

        # Verify atomic_save_with_backup was called
        mock_atomic.assert_called_once()

        # Should save only flagged rows (2 out of 3)
        self.excel_repo.save.assert_called_once()
        call_args = self.excel_repo.save.call_args
        saved_df = call_args.kwargs["df"]
        assert len(saved_df) == 2  # Only flagged rows
        assert list(saved_df["Index#"]) == ["1", "2"]

    @patch("core.pipeline.steps.save_step.atomic_save_with_backup")
    def test_save_excel_output_without_include_flag(self, mock_atomic):
        """Test Excel output saving without _include flag (save all rows)."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])
        # Remove _include column
        context.df = context.df.drop(columns=["_include"])

        def execute_write_func(original_path, write_func, create_backup):
            write_func(original_path)
            return None

        mock_atomic.side_effect = execute_write_func

        self.save_step._save_excel_output(context, "output.xlsx", False)

        saved_df = self.excel_repo.save.call_args.kwargs["df"]
        assert len(saved_df) == 3  # All rows

    @patch("core.pipeline.steps.save_step.atomic_save_with_backup")
    def test_save_excel_output_with_backup(self, mock_atomic):
        """Test Excel output saving with backup creation."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        def execute_write_func(original_path, write_func, create_backup):
            write_func(original_path)
            return "/path/to/backup.xlsx" if create_backup else None

        mock_atomic.side_effect = execute_write_func

        self.save_step._save_excel_output(context, "output.xlsx", True)

        # Verify backup was requested
        mock_atomic.assert_called_once()

    @patch("core.pipeline.steps.save_step.atomic_save_with_backup")
    def test_save_excel_output_custom_sheet_name(self, mock_atomic):
        """Test Excel output saving with custom sheet name."""
        context = self.create_test_context(
            [("test.xlsx", "test.pdf", "Sheet1")], options={"sheet_name": "CustomSheet"}
        )

        def execute_write_func(original_path, write_func, create_backup):
            write_func(original_path)
            return None

        mock_atomic.side_effect = execute_write_func

        self.save_step._save_excel_output(context, "output.xlsx", False)

        call_kwargs = self.excel_repo.save.call_args.kwargs
        assert call_kwargs["target_sheet"] == "CustomSheet"

    # NOTE: test_save_excel_output_source_breakdown_logging was deleted.
    # Per-source row-count info logs were removed in spec 003-reduce-info-logging.

    # PDF Output Tests

    @patch("core.pipeline.steps.save_step.atomic_save_with_backup")
    @patch("builtins.open", mock_open())
    def test_save_pdf_output_success(self, mock_atomic):
        """Test successful PDF output saving."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        def execute_write_func(original_path, write_func, create_backup):
            write_func(original_path)
            return None

        mock_atomic.side_effect = execute_write_func

        self.save_step._save_pdf_output(context, "output.pdf", False)

        # Verify atomic_save_with_backup was called
        mock_atomic.assert_called_once()

        # Verify PdfWriter.write was called
        context.final_pdf.write.assert_called_once()

    @patch("core.pipeline.steps.save_step.atomic_save_with_backup")
    @patch("builtins.open", mock_open())
    def test_save_pdf_output_with_backup(self, mock_atomic):
        """Test PDF output saving with backup creation."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        def execute_write_func(original_path, write_func, create_backup):
            write_func(original_path)
            return "/path/to/backup.pdf" if create_backup else None

        mock_atomic.side_effect = execute_write_func

        self.save_step._save_pdf_output(context, "output.pdf", True)

        # Verify backup was requested
        mock_atomic.assert_called_once()

    @patch("core.pipeline.steps.save_step.atomic_save_with_backup")
    @patch("builtins.open", mock_open())
    def test_save_pdf_output_write_failure(self, mock_atomic):
        """Test PDF output saving with write failure."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])
        context.final_pdf.write.side_effect = Exception("Write failed")

        def execute_write_func(original_path, write_func, create_backup):
            write_func(original_path)  # This will trigger the write failure
            return None

        mock_atomic.side_effect = execute_write_func

        # The write function should raise the expected exception
        with pytest.raises(Exception, match="Failed to write PDF to output.pdf"):
            self.save_step._save_pdf_output(context, "output.pdf", False)

    # NOTE: test_save_pdf_output_statistics_logging and
    # test_save_pdf_output_no_bookmarks were deleted. PDF-output stats info
    # logs were removed in spec 003-reduce-info-logging.

    # Integration Tests

    def test_backup_logic_single_file_enabled(self):
        """Test backup logic for single file with backup enabled."""
        context = self.create_test_context(
            [("test.xlsx", "test.pdf", "Sheet1")], options={"backup": True}
        )

        # Test the backup determination logic
        excel_out_path, pdf_out_path = context.get_output_paths()
        should_backup = (
            context.options.get("backup", False) and not context.is_merge_workflow()
        )

        assert should_backup is True
        assert excel_out_path == "test.xlsx"  # Single file uses original path
        assert pdf_out_path == "test.pdf"

    def test_backup_logic_single_file_disabled(self):
        """Test backup logic for single file with backup disabled."""
        context = self.create_test_context(
            [("test.xlsx", "test.pdf", "Sheet1")], options={"backup": False}
        )

        should_backup = (
            context.options.get("backup", False) and not context.is_merge_workflow()
        )

        assert should_backup is False

    def test_backup_logic_merge_workflow(self):
        """Test backup logic for merge workflow (backup always disabled)."""
        context = self.create_test_context(
            [
                ("file1.xlsx", "file1.pdf", "Sheet1"),
                ("file2.xlsx", "file2.pdf", "Sheet1"),
            ],
            options={"backup": True},  # Should be ignored
        )

        should_backup = (
            context.options.get("backup", False) and not context.is_merge_workflow()
        )

        assert should_backup is False  # Merge workflow disables backup

        excel_out_path, pdf_out_path = context.get_output_paths()
        assert "_merged" in excel_out_path  # Merge workflow uses _merged suffix
        assert "_merged" in pdf_out_path

    def test_output_path_generation_single_file(self):
        """Test output path generation for single file workflow."""
        context = self.create_test_context(
            [("/path/to/document.xlsx", "/path/to/document.pdf", "Sheet1")]
        )

        excel_out, pdf_out = context.get_output_paths()

        # Single file workflow should output to original paths
        assert excel_out == "/path/to/document.xlsx"
        assert pdf_out == "/path/to/document.pdf"

    def test_output_path_generation_merge_workflow(self):
        """Test output path generation for merge workflow."""
        context = self.create_test_context(
            [
                ("/path/to/file1.xlsx", "/path/to/file1.pdf", "Sheet1"),
                ("/path/to/file2.xlsx", "/path/to/file2.pdf", "Sheet1"),
            ]
        )

        excel_out, pdf_out = context.get_output_paths()

        # Merge workflow should use _merged suffix
        assert excel_out == "/path/to/file1_merged.xlsx"
        assert pdf_out == "/path/to/file1_merged.pdf"

    @patch("core.pipeline.steps.save_step.atomic_save_with_backup")
    def test_excel_save_parameters(self, mock_atomic):
        """Test that Excel save is called with correct parameters."""
        context = self.create_test_context(
            [("template.xlsx", "source.pdf", "DataSheet")]
        )

        def execute_write_func(original_path, write_func, create_backup):
            write_func(original_path)
            return None

        mock_atomic.side_effect = execute_write_func

        self.save_step._save_excel_output(context, "output.xlsx", False)

        # Verify excel_repo.save was called with correct parameters
        self.excel_repo.save.assert_called_once()
        call_kwargs = self.excel_repo.save.call_args.kwargs

        assert call_kwargs["template_path"] == "template.xlsx"
        assert call_kwargs["target_sheet"] == "Index"  # Default sheet name
        assert (
            call_kwargs["out_path"] == "output.xlsx"
        )  # Should use original path, not test path
        assert len(call_kwargs["df"]) == 2  # Filtered DataFrame

    def test_error_handling_excel_save_failure(self):
        """Test error handling when Excel save fails."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # Mock atomic_save_with_backup to call the write function and let it fail
        def mock_atomic_save(original_path, write_func, create_backup):
            write_func(original_path)  # This will trigger the excel_repo.save failure
            return None

        self.excel_repo.save.side_effect = Exception("Excel save failed")

        with patch(
            "core.pipeline.steps.save_step.atomic_save_with_backup",
            side_effect=mock_atomic_save,
        ):
            with pytest.raises(Exception, match="Excel save failed"):
                self.save_step._save_excel_output(context, "output.xlsx", False)

    def test_error_handling_pdf_save_failure(self):
        """Test error handling when PDF save fails."""
        context = self.create_test_context([("test.xlsx", "test.pdf", "Sheet1")])

        # Mock atomic_save_with_backup to call the write function and let it fail
        def mock_atomic_save(original_path, write_func, create_backup):
            write_func(original_path)  # This will trigger the PDF write failure
            return None

        with (
            patch(
                "core.pipeline.steps.save_step.atomic_save_with_backup",
                side_effect=mock_atomic_save,
            ),
            patch("builtins.open", side_effect=PermissionError("Access denied")),
        ):
            with pytest.raises(Exception, match="Failed to write PDF"):
                self.save_step._save_pdf_output(context, "output.pdf", False)

    @patch("core.pipeline.steps.save_step.atomic_save_with_backup")
    @patch("builtins.open", mock_open())
    def test_complete_workflow_integration(self, mock_atomic):
        """Test complete save workflow integration."""
        context = self.create_test_context(
            [("input.xlsx", "input.pdf", "Sheet1")],
            options={"backup": True, "sheet_name": "Results"},
        )

        def execute_write_func(original_path, write_func, create_backup):
            write_func(original_path)
            return "/backup/path" if create_backup else None

        mock_atomic.side_effect = execute_write_func

        self.save_step.execute(context)

        # Verify both Excel and PDF saves were attempted
        assert mock_atomic.call_count == 2
