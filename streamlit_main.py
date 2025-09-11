#!/usr/bin/env python3
"""
Streamlit main entry point for Abstract Renumber Tool.

Multi-page web application for Excel and PDF document processing.
"""

import streamlit as st

from pages.components.styling import StyleManager

# Import page modules
from pages.mode_selection import show_mode_selection
from pages.multi_file_merge import show_multi_file_merge
from pages.single_file_processing import show_single_file_processing

# Configure the Streamlit page for native responsive behavior
st.set_page_config(
    page_title="Abstract Renumber Tool",
    page_icon="📄",
    layout="wide",  # Use full-width for desktop optimization
    initial_sidebar_state="auto",  # Let Streamlit decide sidebar behavior
)


def main():
    """Main Streamlit application entry point."""

    # Apply minimal button styling only - let Streamlit handle layout
    style_manager = StyleManager()
    style_manager.inject_custom_css()

    # Initialize session state for navigation if not exists
    if "current_page" not in st.session_state:
        st.session_state.current_page = "mode_selection"

    # Using native Streamlit navigation - no custom sidebar modifications

    # Route to appropriate page based on session state
    if st.session_state.current_page == "mode_selection":
        show_mode_selection()
    elif st.session_state.current_page == "single_file":
        show_single_file_processing()
    elif st.session_state.current_page == "multi_file":
        show_multi_file_merge()


if __name__ == "__main__":
    main()
