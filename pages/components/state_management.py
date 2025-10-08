#!/usr/bin/env python3
"""
Session state management components for Abstract Renumber Tool Streamlit interface.

Contains shared session state utility functions to eliminate duplication
and provide consistent state management patterns across different pages.
"""

import gc
import time
from typing import Any, Optional

import streamlit as st


class SessionStateManager:
    """Manages session state initialization and utilities."""

    def __init__(self) -> None:
        """Initialize the SessionStateManager."""
        pass

    def initialize_common_state(self) -> None:
        """Initialize common session state variables used across pages."""
        # UI adapter
        if "ui_adapter" not in st.session_state:
            from adapters.ui_streamlit import StreamlitUIAdapter

            st.session_state.ui_adapter = StreamlitUIAdapter()

        # File paths
        if "excel_temp_path" not in st.session_state:
            st.session_state.excel_temp_path = None
        if "pdf_temp_path" not in st.session_state:
            st.session_state.pdf_temp_path = None

        # Uploaded files
        if "uploaded_excel" not in st.session_state:
            st.session_state.uploaded_excel = None
        if "uploaded_pdf" not in st.session_state:
            st.session_state.uploaded_pdf = None

        # Processing state
        if "show_downloads" not in st.session_state:
            st.session_state.show_downloads = False

        # Status messages
        if "status_messages" not in st.session_state:
            st.session_state.status_messages = []

    def initialize_uploader_keys(self, page_type: str = "single") -> None:
        """Initialize file uploader keys for clearing functionality.

        Args:
            page_type: Type of page ('single' or 'merge') for key differentiation
        """
        if page_type == "single":
            if "excel_uploader_key" not in st.session_state:
                st.session_state.excel_uploader_key = "excel_uploader_0"
            if "pdf_uploader_key" not in st.session_state:
                st.session_state.pdf_uploader_key = "pdf_uploader_0"
        elif page_type == "merge":
            # Primary pair keys
            if "primary_excel_uploader_key" not in st.session_state:
                st.session_state.primary_excel_uploader_key = "primary_excel_0"
            if "primary_pdf_uploader_key" not in st.session_state:
                st.session_state.primary_pdf_uploader_key = "primary_pdf_0"

            # Additional pair keys
            if "additional_excel_uploader_key" not in st.session_state:
                st.session_state.additional_excel_uploader_key = "additional_excel_0"
            if "additional_pdf_uploader_key" not in st.session_state:
                st.session_state.additional_pdf_uploader_key = "additional_pdf_0"

    def initialize_processing_options(self) -> None:
        """Initialize processing option defaults."""
        if "sort_bookmarks_enabled" not in st.session_state:
            st.session_state.sort_bookmarks_enabled = True
        if "reorder_pages_enabled" not in st.session_state:
            st.session_state.reorder_pages_enabled = True
        if "check_document_images_enabled" not in st.session_state:
            st.session_state.check_document_images_enabled = True

    def initialize_filtering_state(self) -> None:
        """Initialize filtering-related state variables."""
        if "wants_filtering" not in st.session_state:
            st.session_state.wants_filtering = False
        if "filter_enabled" not in st.session_state:
            st.session_state.filter_enabled = False
        if "filter_column" not in st.session_state:
            st.session_state.filter_column = None
        if "filter_values" not in st.session_state:
            st.session_state.filter_values = []

    def initialize_merge_state(self) -> None:
        """Initialize merge workflow specific state variables."""
        if "primary_pair" not in st.session_state:
            st.session_state.primary_pair = None
        if "additional_pairs" not in st.session_state:
            st.session_state.additional_pairs = []
        if "merge_pairs" not in st.session_state:
            st.session_state.merge_pairs = None

    def clear_file_uploaders(self, page_type: str = "single") -> None:
        """Clear file uploaders by rotating their keys.

        Args:
            page_type: Type of page ('single' or 'merge') for key differentiation
        """
        timestamp = int(time.time() * 1000)  # Use milliseconds for uniqueness

        if page_type == "single":
            st.session_state.excel_uploader_key = f"excel_uploader_{timestamp}"
            st.session_state.pdf_uploader_key = f"pdf_uploader_{timestamp + 1}"
        elif page_type == "merge":
            st.session_state.primary_excel_uploader_key = f"primary_excel_{timestamp}"
            st.session_state.primary_pdf_uploader_key = f"primary_pdf_{timestamp + 1}"
            st.session_state.additional_excel_uploader_key = (
                f"additional_excel_{timestamp + 2}"
            )
            st.session_state.additional_pdf_uploader_key = (
                f"additional_pdf_{timestamp + 3}"
            )

    def reset_workflow_state(self, page_type: str = "single") -> None:
        """Reset workflow state for a fresh start.

        Args:
            page_type: Type of page ('single' or 'merge') for appropriate reset
        """
        # Clear file uploaders
        self.clear_file_uploaders(page_type)

        # Reset common state
        st.session_state.show_downloads = False

        # Reset filter settings
        st.session_state.wants_filtering = False
        st.session_state.filter_enabled = False
        st.session_state.filter_column = None
        st.session_state.filter_values = []

        # Reset processing options to defaults
        st.session_state.sort_bookmarks_enabled = True
        st.session_state.reorder_pages_enabled = True
        st.session_state.check_document_images_enabled = True

        # Reset merge-specific state if needed
        if page_type == "merge":
            st.session_state.primary_pair = None
            st.session_state.additional_pairs = []
            st.session_state.merge_pairs = None

        # Memory cleanup: Remove large objects from session state
        try:
            # Clear large DataFrames and cached data
            large_objects_to_clear = [
                "merged_preview_data",  # Multi-file merge preview cache
                "processed_excel_data",  # Processed Excel data
                "processed_pdf_data",  # Processed PDF data
                "pipeline_context",  # Pipeline context with PDF objects
                "final_pdf",  # Final PDF writer objects
                "pdf_writer",  # Any PDF writer objects
                "excel_dataframe",  # Large Excel DataFrames
                "preview_dataframe",  # Preview DataFrames
            ]

            for obj_key in large_objects_to_clear:
                if obj_key in st.session_state:
                    del st.session_state[obj_key]
                    print(f"Memory cleanup: Cleared {obj_key} from session state")
        except Exception as e:
            print(f"Memory cleanup warning: {e}")

        # Trigger garbage collection after cleanup
        gc.collect()

        # Reset UI adapter
        if hasattr(st.session_state, "ui_adapter"):
            st.session_state.ui_adapter.reset_gui()

    def get_current_step_info(self) -> Optional[str]:
        """Get information about the current workflow step.

        Returns:
            String describing current step or None if not in progress
        """
        if st.session_state.get("filter_decision_made"):
            if st.session_state.get("wants_filtering") and not st.session_state.get(
                "filter_configured"
            ):
                return "📍 **Current Step:** Filter Configuration"
            elif not st.session_state.get("processing_options_decided"):
                return "📍 **Current Step:** Processing Options"
            elif st.session_state.get("processing_options_decided"):
                return "📍 **Current Step:** Ready to Process"
        elif st.session_state.get("excel_temp_path") and st.session_state.get(
            "pdf_temp_path"
        ):
            return "📍 **Current Step:** Filter Decision"

        return None

    def store_uploaded_files(
        self, excel_file: Optional[Any], pdf_file: Optional[Any]
    ) -> None:
        """Store uploaded files in session state.

        Args:
            excel_file: Uploaded Excel file object
            pdf_file: Uploaded PDF file object
        """
        if excel_file:
            st.session_state.uploaded_excel = excel_file
        if pdf_file:
            st.session_state.uploaded_pdf = pdf_file
