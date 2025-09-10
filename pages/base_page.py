#!/usr/bin/env python3
"""
Base page class for Abstract Renumber Tool Streamlit interface.

Provides common functionality and initialization patterns for all Streamlit pages
to ensure consistency and reduce code duplication.
"""

from typing import Optional

import streamlit as st

from .components.state_management import SessionStateManager
from .components.styling import StyleManager


class BaseStreamlitPage:
    """Base class for all Streamlit pages in the Abstract Renumber Tool."""

    def __init__(self, page_type: str = "single") -> None:
        """Initialize the base page with common functionality.

        Args:
            page_type: Type of page ('single' or 'merge') for appropriate initialization
        """
        self.page_type = page_type
        self.style_manager = StyleManager()
        self.state_manager = SessionStateManager()

        # Initialize common components
        self._initialize_page()

    def _initialize_page(self) -> None:
        """Initialize common page components and state."""
        # Inject custom CSS
        self.style_manager.inject_custom_css()

        # Initialize session state
        self.state_manager.initialize_common_state()
        self.state_manager.initialize_uploader_keys(self.page_type)
        self.state_manager.initialize_processing_options()
        self.state_manager.initialize_filtering_state()

        # Initialize merge-specific state if needed
        if self.page_type == "merge":
            self.state_manager.initialize_merge_state()

    def show_back_to_mode_button(self, button_key: str) -> None:
        """Show back to mode selection button.

        Args:
            button_key: Unique key for the button
        """
        if st.button("← Back to Mode Selection", key=button_key):
            st.session_state.current_page = "mode_selection"
            st.rerun()

    def show_page_title(self, title: str) -> None:
        """Show page title with consistent formatting.

        Args:
            title: Title text to display
        """
        st.title(title)
        st.markdown("---")

    def show_status_messages(self) -> None:
        """Display status messages if they exist."""
        if st.session_state.get("status_messages"):
            st.markdown("---")
            st.session_state.ui_adapter.display_status_messages()

    def get_ui_adapter(self):
        """Get the UI adapter from session state.

        Returns:
            StreamlitUIAdapter instance
        """
        return st.session_state.ui_adapter

    def reset_workflow(self) -> None:
        """Reset the workflow state for a fresh start."""
        self.state_manager.reset_workflow_state(self.page_type)

    def check_files_uploaded(self) -> bool:
        """Check if required files are uploaded.

        Returns:
            True if files are uploaded, False otherwise
        """
        if self.page_type == "single":
            return bool(
                st.session_state.get("uploaded_excel")
                and st.session_state.get("uploaded_pdf")
            )
        elif self.page_type == "merge":
            return bool(st.session_state.get("primary_pair"))

        return False

    def show_file_upload_status(self) -> Optional[str]:
        """Show file upload status and return current status.

        Returns:
            Status string or None if no specific status
        """
        if self.page_type == "single":
            excel = st.session_state.get("uploaded_excel")
            pdf = st.session_state.get("uploaded_pdf")

            if excel and pdf:
                return "files_uploaded"
            elif excel or pdf:
                st.warning("⚠️ Please upload both Excel and PDF files to continue.")
                return "partial_upload"
            else:
                st.info("📤 Please select your files using the uploaders above.")
                return "no_files"

        elif self.page_type == "merge":
            primary_pair = st.session_state.get("primary_pair")
            if primary_pair:
                return "primary_pair_set"
            else:
                st.info("👆 Please select a primary file pair to begin the workflow.")
                return "no_primary_pair"

        return None

    def get_current_step_info(self) -> Optional[str]:
        """Get information about current workflow step.

        Returns:
            String describing current step or None
        """
        return self.state_manager.get_current_step_info()

    def store_uploaded_files(self, excel_file=None, pdf_file=None) -> None:
        """Store uploaded files in session state.

        Args:
            excel_file: Uploaded Excel file object
            pdf_file: Uploaded PDF file object
        """
        self.state_manager.store_uploaded_files(excel_file, pdf_file)

    def clear_file_uploaders(self) -> None:
        """Clear file uploaders by rotating their keys."""
        self.state_manager.clear_file_uploaders(self.page_type)

    def show_processing_complete_message(self) -> None:
        """Show processing complete message."""
        st.success("✅ Files processed successfully!")

    def show_processing_error(self, error_message: str) -> None:
        """Show processing error message.

        Args:
            error_message: Error message to display
        """
        st.error(f"Processing failed: {error_message}")
        if hasattr(st.session_state, "ui_adapter"):
            st.session_state.ui_adapter.log_status(f"ERROR: {error_message}")
