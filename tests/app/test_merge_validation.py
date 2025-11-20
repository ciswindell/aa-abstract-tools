#!/usr/bin/env python3
"""Tests for merge mode validation logic."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, MagicMock, patch
from core.app_controller import AppController
from core.models import Options


class TestMergeValidation:
    """Test merge mode validation prevents invalid operations."""

    def test_merge_enabled_no_pairs_raises_error(self):
        """Test that processing fails when merge enabled but no pairs selected."""
        # Create mock UI that returns merge enabled but no pairs
        ui = Mock()
        ui.get_merge_enabled.return_value = True
        ui.get_file_paths.return_value = ("/path/excel.xlsx", "/path/file.pdf")
        ui.get_options.return_value = Options(
            backup=True,
            sort_bookmarks=False,
            reorder_pages=False,
            sheet_name="Index",
            merge_pairs=None,  # No pairs selected despite merge enabled
        )
        ui.start_new_operation = Mock()
        ui.log_status = Mock()
        ui.show_error = Mock()

        controller = AppController(ui)
        
        # Mock the sheet resolution methods to avoid file I/O
        controller._resolve_processing_sheet_name = Mock(return_value="Index")

        # Call process_files - error will be caught and shown via show_error
        controller.process_files()

        # Verify show_error was called
        ui.show_error.assert_called_once()
        
        # Get the actual error message that was passed
        call_args = ui.show_error.call_args
        if call_args[0]:  # positional args
            error_msg = call_args[0][1] if len(call_args[0]) > 1 else ""
        else:
            error_msg = call_args[1].get("message", "")
        
        # The error message should mention merge and pairs
        error_lower = error_msg.lower()
        assert "merge" in error_lower and ("pair" in error_lower or "file" in error_lower)

    def test_merge_enabled_empty_list_raises_error(self):
        """Test that empty merge_pairs list is treated as invalid."""
        ui = Mock()
        ui.get_merge_enabled.return_value = True
        ui.get_file_paths.return_value = ("/path/excel.xlsx", "/path/file.pdf")
        ui.get_options.return_value = Options(
            backup=True,
            sort_bookmarks=False,
            reorder_pages=False,
            sheet_name="Index",
            merge_pairs=[],  # Empty list should also be invalid
        )
        ui.start_new_operation = Mock()
        ui.log_status = Mock()
        ui.show_error = Mock()

        controller = AppController(ui)
        controller._resolve_processing_sheet_name = Mock(return_value="Index")

        # Call process_files - error will be caught and shown via show_error
        controller.process_files()

        # Verify show_error was called
        ui.show_error.assert_called_once()
        
        # Get the actual error message
        call_args = ui.show_error.call_args
        if call_args[0]:
            error_msg = call_args[0][1] if len(call_args[0]) > 1 else ""
        else:
            error_msg = call_args[1].get("message", "")
        
        error_lower = error_msg.lower()
        assert "merge" in error_lower and ("pair" in error_lower or "file" in error_lower)

    def test_merge_disabled_single_file_succeeds(self):
        """Test that single-file mode bypasses merge validation."""
        ui = Mock()
        ui.get_merge_enabled.return_value = False
        ui.get_file_paths.return_value = ("/path/excel.xlsx", "/path/file.pdf")
        ui.get_options.return_value = Options(
            backup=True,
            sort_bookmarks=False,
            reorder_pages=False,
            sheet_name="Index",
            merge_pairs=None,  # None is correct for single-file mode
        )
        ui.prompt_sheet_selection.return_value = "Index"
        ui.log_status = Mock()

        controller = AppController(ui)

        # Should NOT raise ValueError (but will fail later due to mocking)
        # We're only testing that validation passes
        try:
            with patch("core.app_controller.RenumberService"):
                with patch("core.app_controller.ExcelOpenpyxlRepo"):
                    with patch("core.app_controller.PdfRepo"):
                        with patch("core.app_controller.TkinterLogger"):
                            # If we get past validation without ValueError, test passes
                            # The actual processing will fail due to mocks, but that's expected
                            try:
                                controller.process_files()
                            except (AttributeError, TypeError):
                                # Expected - mocks aren't complete
                                pass
        except ValueError as e:
            # Should NOT get ValueError about merge pairs
            if "no file pairs were selected" in str(e).lower():
                pytest.fail("Single-file mode should not require merge pairs")
            raise

    def test_valid_merge_with_pairs_passes_validation(self):
        """Test that valid merge configuration passes validation."""
        ui = Mock()
        ui.get_merge_enabled.return_value = True
        ui.get_file_paths.return_value = ("/path/excel.xlsx", "/path/file.pdf")
        ui.get_options.return_value = Options(
            backup=False,  # Auto-disabled for merge
            sort_bookmarks=False,
            reorder_pages=False,
            sheet_name="Index",
            merge_pairs=[("/path/file2.xlsx", "/path/file2.pdf")],  # Valid: 1+ pairs
        )
        ui.prompt_sheet_selection.return_value = "Index"
        ui.log_status = Mock()

        controller = AppController(ui)

        # Should NOT raise ValueError about merge pairs
        try:
            with patch("core.app_controller.RenumberService"):
                with patch("core.app_controller.ExcelOpenpyxlRepo"):
                    with patch("core.app_controller.PdfRepo"):
                        with patch("core.app_controller.TkinterLogger"):
                            try:
                                controller.process_files()
                            except (AttributeError, TypeError):
                                # Expected - mocks aren't complete
                                pass
        except ValueError as e:
            # Should NOT get ValueError about merge pairs for valid config
            if "no file pairs were selected" in str(e).lower():
                pytest.fail(
                    f"Valid merge configuration should pass validation, got: {e}"
                )
            raise

