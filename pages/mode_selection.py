#!/usr/bin/env python3
"""
Mode selection page for Abstract Renumber Tool.

Landing page where users choose between single file processing or multi-file merge workflow.
"""

import streamlit as st


def show_mode_selection():
    """Display the mode selection page."""
    st.title("📄 Abstract Renumber Tool")
    st.markdown("---")

    st.markdown("""
    Welcome to the Abstract Renumber Tool web interface. This tool automates the process of 
    sorting Excel data and renumbering corresponding PDF bookmarks while maintaining 
    synchronized numbering between documents.
    """)

    st.markdown("### Choose Your Workflow:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📄 Single File Processing")
        st.markdown("""
        Process one Excel file and one PDF file:
        - Sort Excel data by multiple criteria
        - Renumber Index# column starting from 1
        - Update PDF bookmarks to match new order
        - Download processed files with `_processed` suffix
        """)

        if st.button(
            "Start Single File Processing",
            type="primary",
            width="stretch",
            key="single_file_btn",
        ):
            st.session_state.current_page = "single_file"
            st.rerun()

    with col2:
        st.markdown("#### 📚 Multi-File Merge")
        st.markdown("""
        Merge multiple Excel/PDF file pairs:
        - Combine multiple document sets
        - Maintain document relationships across files
        - Sort and renumber merged data
        - Download consolidated results
        """)

        if st.button(
            "Start Multi-File Merge",
            type="primary",
            width="stretch",
            key="multi_file_btn",
        ):
            st.session_state.current_page = "multi_file"
            st.rerun()

    # Information section
    st.markdown("---")
    st.markdown("### ℹ️ About This Tool")

    with st.expander("Learn More"):
        st.markdown("""
        **What this tool does:**
        - Sorts Excel data by Legal Description, Grantee, Grantor, Document Type, Document Date, and Received Date
        - Renumbers the Index# column starting from 1
        - Updates PDF bookmarks to match the new Excel order
        - Maintains synchronized numbering between Excel and PDF documents
        
        **File Requirements:**
        - **Excel files:** .xlsx or .xls format (max 400MB)
        - **PDF files:** .pdf format with bookmarks (max 400MB)
        - **Excel columns required:** Index#, Document Type, Legal Description, Grantee, Grantor, Document Date, Received Date
        
        **Processing Options:**
        - Sort PDF bookmarks naturally
        - Reorder PDF pages to match bookmark order
        - Filter data by column values
        - Check for document images
        """)

    # Reset any previous processing state when returning to mode selection
    if st.session_state.get("processing_complete", False):
        if st.button("🔄 Start New Processing Session", type="secondary"):
            # Clear processing state
            keys_to_clear = [
                "processing_complete",
                "uploaded_excel_file",
                "uploaded_pdf_file",
                "excel_temp_path",
                "pdf_temp_path",
                "filter_column",
                "filter_values",
                "merge_pairs",
                "status_messages",
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    show_mode_selection()
