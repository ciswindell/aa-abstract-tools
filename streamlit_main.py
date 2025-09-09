#!/usr/bin/env python3
"""
Streamlit main entry point for Abstract Renumber Tool.

Multi-page web application for Excel and PDF document processing.
"""

import streamlit as st

# Import page modules
from pages.mode_selection import show_mode_selection
from pages.multi_file_merge import show_multi_file_merge
from pages.single_file_processing import show_single_file_processing

# Configure the Streamlit page
st.set_page_config(
    page_title="Abstract Renumber Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main Streamlit application entry point."""

    # Initialize session state for navigation if not exists
    if "current_page" not in st.session_state:
        st.session_state.current_page = "mode_selection"

    # Sidebar navigation
    st.sidebar.title("📄 Abstract Renumber Tool")
    st.sidebar.markdown("---")

    # Navigation menu
    page_options = {
        "mode_selection": "🏠 Mode Selection",
        "single_file": "📄 Single File Processing",
        "multi_file": "📚 Multi-File Merge",
    }

    # Display current page indicator
    for page_key, page_label in page_options.items():
        if st.session_state.current_page == page_key:
            st.sidebar.markdown(f"**→ {page_label}**")
        else:
            if st.sidebar.button(page_label, key=f"nav_{page_key}"):
                st.session_state.current_page = page_key
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("*Web interface for Excel and PDF document processing*")

    # Route to appropriate page based on session state
    if st.session_state.current_page == "mode_selection":
        show_mode_selection()
    elif st.session_state.current_page == "single_file":
        show_single_file_processing()
    elif st.session_state.current_page == "multi_file":
        show_multi_file_merge()


if __name__ == "__main__":
    main()
