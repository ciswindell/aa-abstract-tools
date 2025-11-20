#!/usr/bin/env python3
"""
Unit tests for Document Found checkbox functionality in TkinterApp.
"""

import tkinter as tk
from unittest.mock import Mock, patch

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.tk_app import TkinterApp


class TestTkAppDocumentFoundCheckbox:
    """Test cases for Document Found checkbox functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a root window for testing
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing

        # Mock dependencies
        self.mock_controller = Mock()
        self.mock_logger = Mock()

        # Create TkinterApp instance
        self.app = TkinterApp(self.root, self.mock_controller, self.mock_logger)

    def teardown_method(self):
        """Clean up after tests."""
        if self.root:
            self.root.destroy()

    def test_check_document_images_default_state(self):
        """Test that check_document_images checkbox is checked by default."""
        # The checkbox should be checked by default
        assert self.app.check_document_images_enabled.get() is True

        # The getter method should return True
        assert self.app.get_check_document_images_enabled() is True

    def test_check_document_images_checkbox_exists(self):
        """Test that the checkbox widget is created."""
        # The checkbox widget should be created during initialization
        assert self.app.check_document_images_checkbox is not None
        assert isinstance(self.app.check_document_images_checkbox, tk.Checkbutton)

    def test_check_document_images_info_label_exists(self):
        """Test that the info label widget is created."""
        # The info label should be created during initialization
        assert self.app.check_document_images_info_label is not None
        assert isinstance(self.app.check_document_images_info_label, tk.Label)

    def test_check_document_images_toggle_functionality(self):
        """Test toggling the checkbox state."""
        # Start with default True state
        assert self.app.check_document_images_enabled.get() is True

        # Toggle to False
        self.app.check_document_images_enabled.set(False)
        assert self.app.check_document_images_enabled.get() is False
        assert self.app.get_check_document_images_enabled() is False

        # Toggle back to True
        self.app.check_document_images_enabled.set(True)
        assert self.app.check_document_images_enabled.get() is True
        assert self.app.get_check_document_images_enabled() is True

    def test_check_document_images_callback_enabled(self):
        """Test callback when checkbox is enabled."""
        # Mock the log_status method
        with patch.object(self.app, "log_status") as mock_log:
            # Simulate enabling the checkbox
            self.app.check_document_images_enabled.set(True)
            self.app._on_check_document_images_option_changed()

            # Should log enabled message
            mock_log.assert_called_once_with(
                "Document image checking enabled - will add Document_Found column"
            )

    def test_check_document_images_callback_disabled(self):
        """Test callback when checkbox is disabled."""
        # Mock the log_status method
        with patch.object(self.app, "log_status") as mock_log:
            # Simulate disabling the checkbox
            self.app.check_document_images_enabled.set(False)
            self.app._on_check_document_images_option_changed()

            # Should log disabled message
            mock_log.assert_called_once_with("Document image checking disabled")

    def test_reset_gui_restores_default_state(self):
        """Test that reset_gui restores checkbox to default True state."""
        # Change checkbox to False
        self.app.check_document_images_enabled.set(False)
        assert self.app.check_document_images_enabled.get() is False

        # Reset GUI
        self.app.reset_gui()

        # Should be back to default True state
        assert self.app.check_document_images_enabled.get() is True
        assert self.app.get_check_document_images_enabled() is True

    def test_checkbox_state_persistence_during_session(self):
        """Test that checkbox state persists during a session until reset."""
        # Set to False
        self.app.check_document_images_enabled.set(False)

        # State should persist
        assert self.app.get_check_document_images_enabled() is False

        # Multiple calls should return same value
        assert self.app.get_check_document_images_enabled() is False
        assert self.app.get_check_document_images_enabled() is False

        # Change to True
        self.app.check_document_images_enabled.set(True)
        assert self.app.get_check_document_images_enabled() is True

    def test_checkbox_integration_with_other_options(self):
        """Test that document images checkbox works alongside other options."""
        # Enable document images
        self.app.check_document_images_enabled.set(True)

        # Enable other options
        self.app.backup_enabled.set(True)
        self.app.sort_bookmarks_enabled.set(True)

        # All should be enabled independently
        assert self.app.get_check_document_images_enabled() is True
        assert self.app.get_backup_enabled() is True
        assert self.app.get_sort_bookmarks_enabled() is True

        # Disable document images, others should remain
        self.app.check_document_images_enabled.set(False)
        assert self.app.get_check_document_images_enabled() is False
        assert self.app.get_backup_enabled() is True
        assert self.app.get_sort_bookmarks_enabled() is True

    def test_checkbox_widget_configuration(self):
        """Test that checkbox widget is properly configured."""
        checkbox = self.app.check_document_images_checkbox

        # Should have correct text
        assert checkbox.cget("text") == "Check for Document Images"

        # Should be linked to the BooleanVar
        assert checkbox.cget("variable") == str(self.app.check_document_images_enabled)

        # Should have the callback command
        # Note: We can't easily test the exact command, but we can verify it's set
        assert checkbox.cget("command") is not None

    def test_info_label_configuration(self):
        """Test that info label is properly configured."""
        info_label = self.app.check_document_images_info_label

        # Should have correct text
        expected_text = (
            "📄 Adds 'Document_Found' column if missing (always updates if present)"
        )
        assert info_label.cget("text") == expected_text

        # Should have blue foreground
        assert info_label.cget("foreground") == "blue"
