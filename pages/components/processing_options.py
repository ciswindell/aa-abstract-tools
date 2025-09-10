#!/usr/bin/env python3
"""
Processing options components for Abstract Renumber Tool Streamlit interface.

Contains shared processing options UI components to eliminate duplication
across different pages.
"""

from typing import Any, Dict

import streamlit as st


class ProcessingOptionsManager:
    """Manages processing options UI components."""

    def __init__(self) -> None:
        """Initialize the ProcessingOptionsManager."""
        pass

    def render_sidebar_options(self, page_type: str = "single") -> None:
        """Render processing options in the sidebar.

        Args:
            page_type: Type of page ('single' or 'merge') for key differentiation
        """
        with st.sidebar:
            st.markdown("### ⚙️ Processing Options")

            # Sort bookmarks option
            sort_key = (
                f"sort_bookmarks_enabled_{page_type}"
                if page_type == "merge"
                else "sort_bookmarks_enabled"
            )
            sort_bookmarks = st.checkbox(
                "Sort PDF Bookmarks",
                value=st.session_state.get(sort_key, True),
                key=sort_key,
                help="Sort PDF bookmarks naturally",
            )

            # Reorder pages option (dependent on sort bookmarks)
            reorder_key = (
                f"reorder_pages_enabled_{page_type}"
                if page_type == "merge"
                else "reorder_pages_enabled"
            )
            reorder_pages = st.checkbox(
                "Reorder Pages to Match Bookmarks",
                value=st.session_state.get(reorder_key, True) and sort_bookmarks,
                key=reorder_key,
                disabled=not sort_bookmarks,
                help="Physically reorder pages to match sorted bookmarks",
            )

            # Check document images option
            check_key = (
                f"check_document_images_enabled_{page_type}"
                if page_type == "merge"
                else "check_document_images_enabled"
            )
            st.checkbox(
                "Check for Document Images",
                value=st.session_state.get(check_key, True),
                key=check_key,
                help="Add/update Document_Found column in Excel output",
            )

            # Filter option (for merge workflow)
            if page_type == "merge":
                st.checkbox(
                    "Enable Data Filtering",
                    value=st.session_state.get("filter_enabled_merge", False),
                    key="filter_enabled_merge",
                    help="Filter data by column values (will prompt during processing)",
                )

    def render_tab_options(self, page_type: str = "single") -> Dict[str, Any]:
        """Render processing options in a tab interface.

        Args:
            page_type: Type of page ('single' or 'merge') for key differentiation

        Returns:
            Dictionary of current option values
        """
        st.markdown("### ⚙️ Processing Options")
        st.markdown("Configure how your files will be processed.")

        # Processing options
        col1, col2 = st.columns(2)

        with col1:
            sort_key = (
                f"sort_bookmarks_tab_{page_type}"
                if page_type == "merge"
                else "sort_bookmarks_tab"
            )
            sort_bookmarks = st.checkbox(
                "Sort PDF Bookmarks",
                value=st.session_state.get("sort_bookmarks_enabled", True),
                key=sort_key,
                help="Sort PDF bookmarks naturally",
            )

            reorder_key = (
                f"reorder_pages_tab_{page_type}"
                if page_type == "merge"
                else "reorder_pages_tab"
            )
            reorder_pages = st.checkbox(
                "Reorder Pages to Match Bookmarks",
                value=st.session_state.get("reorder_pages_enabled", True)
                and sort_bookmarks,
                key=reorder_key,
                disabled=not sort_bookmarks,
                help="Physically reorder pages to match sorted bookmarks",
            )

        with col2:
            check_key = (
                f"check_images_tab_{page_type}"
                if page_type == "merge"
                else "check_images_tab"
            )
            check_images = st.checkbox(
                "Check Document Images",
                value=st.session_state.get("check_document_images_enabled", True),
                key=check_key,
                help="Verify document images during processing",
            )

        # Store the options in session state
        st.session_state.sort_bookmarks_enabled = sort_bookmarks
        st.session_state.reorder_pages_enabled = reorder_pages
        st.session_state.check_document_images_enabled = check_images

        return {
            "sort_bookmarks": sort_bookmarks,
            "reorder_pages": reorder_pages,
            "check_images": check_images,
        }

    def display_options_summary(self, options: Dict[str, Any]) -> None:
        """Display a summary of current processing options.

        Args:
            options: Dictionary of option values to display
        """
        st.markdown("#### Current Settings")
        settings_summary = []

        settings_summary.append(
            f"**Sort Bookmarks:** {'✅ Enabled' if options.get('sort_bookmarks') else '❌ Disabled'}"
        )
        settings_summary.append(
            f"**Reorder Pages:** {'✅ Enabled' if options.get('reorder_pages') else '❌ Disabled'}"
        )
        settings_summary.append(
            f"**Check Images:** {'✅ Enabled' if options.get('check_images') else '❌ Disabled'}"
        )

        st.info("\n".join(settings_summary))
