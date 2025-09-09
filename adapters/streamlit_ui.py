#!/usr/bin/env python3
"""
Streamlit UI adapter that implements the UIController interface.
"""

import tempfile
from typing import List, Optional, Tuple

import pandas as pd
import streamlit as st

from core.models import Options


class StreamlitUIAdapter:
    """Streamlit implementation of UIController interface."""

    def __init__(self) -> None:
        """Initialize Streamlit UI adapter."""
        # Initialize session state for file handling
        if "uploaded_excel_file" not in st.session_state:
            st.session_state.uploaded_excel_file = None
        if "uploaded_pdf_file" not in st.session_state:
            st.session_state.uploaded_pdf_file = None
        if "excel_temp_path" not in st.session_state:
            st.session_state.excel_temp_path = None
        if "pdf_temp_path" not in st.session_state:
            st.session_state.pdf_temp_path = None
        if "status_messages" not in st.session_state:
            st.session_state.status_messages = []

    def get_file_paths(self) -> Tuple[Optional[str], Optional[str]]:
        """Get selected Excel and PDF file paths from session state."""
        return st.session_state.excel_temp_path, st.session_state.pdf_temp_path

    def get_options(self) -> Options:
        """Get processing options from Streamlit widgets in session state."""
        # Get options from session state (will be set by UI widgets)
        sort_bookmarks = st.session_state.get("sort_bookmarks_enabled", False)
        reorder_pages = st.session_state.get("reorder_pages_enabled", False)
        check_document_images = st.session_state.get(
            "check_document_images_enabled", True
        )
        filter_enabled = st.session_state.get("filter_enabled", False)
        filter_column = st.session_state.get("filter_column", None)
        filter_values = st.session_state.get("filter_values", None)
        merge_pairs = st.session_state.get("merge_pairs", None)

        return Options(
            backup=False,  # Disabled for Streamlit version as per PRD
            sort_bookmarks=sort_bookmarks,
            reorder_pages=reorder_pages,
            check_document_images=check_document_images,
            sheet_name=None,  # Will be set separately
            filter_enabled=filter_enabled,
            filter_column=filter_column,
            filter_values=filter_values,
            merge_pairs=merge_pairs,
        )

    def log_status(self, message: str) -> None:
        """Log a status message to the UI."""
        if "status_messages" not in st.session_state:
            st.session_state.status_messages = []
        st.session_state.status_messages.append(message)

    def show_error(self, title: str, message: str) -> None:
        """Show an error message to the user."""
        st.error(f"**{title}**\n\n{message}")
        self.log_status(f"ERROR: {title} - {message}")

    def show_success(self, message: str) -> None:
        """Show a success message to the user."""
        st.success(message)
        self.log_status(f"SUCCESS: {message}")

    def reset_gui(self) -> None:
        """Reset GUI to initial state after successful processing."""
        # Clear file uploads
        st.session_state.uploaded_excel_file = None
        st.session_state.uploaded_pdf_file = None
        st.session_state.excel_temp_path = None
        st.session_state.pdf_temp_path = None

        # Clear processing options (but keep user preferences)
        if "filter_column" in st.session_state:
            del st.session_state.filter_column
        if "filter_values" in st.session_state:
            del st.session_state.filter_values
        if "merge_pairs" in st.session_state:
            del st.session_state.merge_pairs

        # Keep status messages for user reference
        self.log_status("GUI reset - ready for new files!")

    def prompt_sheet_selection(
        self,
        file_path: str,
        sheet_names: List[str],
        default_sheet: Optional[str] = None,
    ) -> Optional[str]:
        """Prompt user to select a sheet from available options."""
        if not sheet_names:
            return None

        # Determine default selection
        default_index = 0
        if default_sheet:
            desired = default_sheet.lower()
            for i, name in enumerate(sheet_names):
                if name.lower() == desired:
                    default_index = i
                    break

        st.warning(
            f"The Excel file does not contain the expected sheet '{default_sheet or 'Index'}'. "
            "Please select the correct sheet to process:"
        )

        selected_sheet = st.selectbox(
            "Select Excel Sheet:",
            options=sheet_names,
            index=default_index,
            key="sheet_selection",
        )

        return selected_sheet

    def prompt_filter_selection(
        self, df: pd.DataFrame
    ) -> Tuple[Optional[str], List[str]]:
        """Prompt user to pick a filter column and values; returns (column, values)."""
        if df is None or df.empty:
            return None, []

        columns = [c for c in df.columns if str(c).strip()]
        if not columns:
            return None, []

        st.info("Configure data filtering (optional):")

        # Column selection
        filter_column = st.selectbox(
            "Select column to filter by:",
            options=["None"] + columns,
            key="filter_column_select",
        )

        if filter_column == "None":
            return None, []

        # Get unique values for the selected column
        unique_values = sorted(df[filter_column].dropna().unique().astype(str))

        # Value selection
        selected_values = st.multiselect(
            f"Select values to keep from '{filter_column}':",
            options=unique_values,
            key="filter_values_select",
        )

        if not selected_values:
            return None, []

        return filter_column, selected_values

    def prompt_merge_pairs(self) -> Optional[List[Tuple[str, str]]]:
        """Prompt user to select one or more (Excel, PDF) pairs for merge."""
        st.info(
            "Multi-file merge pair selection will be implemented in the workflow pages."
        )
        # This will be implemented in the multi-file merge page
        # For now, return None to indicate no merge pairs
        return None

    def save_uploaded_file(self, uploaded_file, file_type: str) -> str:
        """Save uploaded file to temporary location and return path."""
        if uploaded_file is None:
            return None

        # Create temporary file
        suffix = ".xlsx" if file_type == "excel" else ".pdf"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(uploaded_file.getvalue())
        temp_file.close()

        # Store in session state
        if file_type == "excel":
            st.session_state.excel_temp_path = temp_file.name
        else:
            st.session_state.pdf_temp_path = temp_file.name

        return temp_file.name

    def display_status_messages(self):
        """Display accumulated status messages."""
        if st.session_state.get("status_messages"):
            with st.expander("Processing Status", expanded=True):
                for message in st.session_state.status_messages[
                    -10:
                ]:  # Show last 10 messages
                    st.text(message)
