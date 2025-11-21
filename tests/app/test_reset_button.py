#!/usr/bin/env python3
"""
Tests for Reset Button functionality in AbstractRenumberGUI.
"""

import sys
from pathlib import Path

# Add project root to sys.path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import tkinter as tk
from unittest.mock import MagicMock

import pytest

from app.tk_app import AbstractRenumberGUI


@pytest.fixture
def gui():
    """Create GUI instance for testing."""
    root = tk.Tk()
    root.withdraw()  # Hide window during tests
    controller = MagicMock()
    gui_instance = AbstractRenumberGUI(root, controller)
    yield gui_instance
    root.destroy()


def test_reset_button_exists(gui):
    """Verify Reset button is created during GUI setup."""
    assert gui.reset_button is not None
    assert gui.reset_button.cget("text") == "Reset"


def test_reset_button_always_enabled(gui):
    """Verify Reset button is always enabled (spec FR-008)."""
    assert gui.reset_button.cget("state") == "normal"


def test_reset_clears_file_selections(gui):
    """Verify reset clears file path state."""
    gui.excel_file = "/path/to/test.xlsx"
    gui.pdf_file = "/path/to/test.pdf"

    gui.reset_gui()

    assert gui.excel_file is None
    assert gui.pdf_file is None


def test_reset_clears_filter_state(gui):
    """Verify reset clears filter configuration."""
    gui.filter_enabled.set(True)
    gui.filter_column = "test_column"
    gui.filter_values = ["value1", "value2"]

    gui.reset_gui()

    assert gui.filter_enabled.get() is False
    assert gui.filter_column is None
    assert gui.filter_values == []


def test_reset_clears_merge_state(gui):
    """Verify reset clears merge configuration."""
    gui.merge_enabled.set(True)
    gui.merge_pairs = [("/path/excel.xlsx", "/path/doc.pdf")]

    gui.reset_gui()

    assert gui.merge_enabled.get() is False
    assert gui.merge_pairs == []


def test_reset_preserves_backup_preference(gui):
    """Verify reset preserves user preference settings."""
    gui.backup_enabled.set(False)  # User changed default
    gui.sort_bookmarks_enabled.set(True)

    gui.reset_gui()

    # Preferences should be unchanged
    assert gui.backup_enabled.get() is False
    assert gui.sort_bookmarks_enabled.get() is True


def test_reset_disables_process_button(gui):
    """Verify reset disables Process button until new files selected."""
    gui.excel_file = "/path/to/test.xlsx"
    gui.pdf_file = "/path/to/test.pdf"
    gui._update_process_button_state()  # Enable it

    gui.reset_gui()

    assert gui.process_button.cget("state") == "disabled"


def test_reset_with_empty_state_safe(gui):
    """Verify reset with no files selected is safe no-op."""
    # Start with empty state
    assert gui.excel_file is None
    assert gui.pdf_file is None

    # Reset should not raise error
    gui.reset_gui()

    # State should remain empty
    assert gui.excel_file is None
    assert gui.pdf_file is None
