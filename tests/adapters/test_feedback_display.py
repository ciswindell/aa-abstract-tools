#!/usr/bin/env python3
"""
Tests for user feedback display functionality, specifically error message simplification.
"""

import pytest

from adapters.ui_tkinter import simplify_error


class TestErrorSimplification:
    """Tests for the simplify_error() helper function."""

    def test_file_not_found_error_simplification(self):
        """FileNotFoundError should produce user-friendly message."""
        error = FileNotFoundError("No such file or directory: 'missing.xlsx'")
        result = simplify_error(error)
        assert "Cannot find the file" in result
        assert "file path" in result
        assert "FileNotFoundError" not in result

    def test_permission_error_simplification(self):
        """PermissionError should produce user-friendly message."""
        error = PermissionError("Permission denied: 'readonly.pdf'")
        result = simplify_error(error)
        assert "Cannot access the file" in result
        assert "permissions" in result or "close the file" in result
        assert "PermissionError" not in result

    def test_generic_error_fallback(self):
        """Unknown errors should use generic fallback message."""
        error = RuntimeError("Something unexpected happened")
        result = simplify_error(error)
        assert "error occurred" in result.lower()
        assert "Something unexpected happened" in result
        assert "try again" in result

    def test_invalid_format_error(self):
        """Errors containing 'invalid' should preserve details."""
        error = ValueError("Invalid date format in row 12")
        result = simplify_error(error)
        assert "Invalid" in result
        assert "row 12" in result

