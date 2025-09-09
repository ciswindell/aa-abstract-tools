#!/usr/bin/env python3
"""
Multi-file merge page for Abstract Renumber Tool.

Handles the workflow for merging multiple Excel/PDF file pairs.
"""

import io
import zipfile
from pathlib import Path

import streamlit as st

from adapters.ui_streamlit import StreamlitUIAdapter
from core.app_controller import AppController


def show_multi_file_merge():
    """Display the multi-file merge page."""
    st.title("📚 Multi-File Merge")
    st.markdown("---")

    # Initialize UI adapter
    if "ui_adapter" not in st.session_state:
        st.session_state.ui_adapter = StreamlitUIAdapter()

    # Initialize merge pairs in session state
    if "merge_file_pairs" not in st.session_state:
        st.session_state.merge_file_pairs = []

    # Back to mode selection button
    if st.button("← Back to Mode Selection", key="back_to_mode_merge"):
        st.session_state.current_page = "mode_selection"
        st.rerun()

    # File pair management section
    st.markdown("### 📁 File Pair Management")

    # Add new file pair section
    with st.expander(
        "➕ Add New File Pair", expanded=len(st.session_state.merge_file_pairs) == 0
    ):
        add_file_pair_interface()

    # Display existing file pairs
    if st.session_state.merge_file_pairs:
        st.markdown("### 📋 Selected File Pairs")
        display_file_pairs()
    else:
        st.info("No file pairs added yet. Add your first pair above to get started.")

    # Processing options sidebar
    show_processing_options_sidebar()

    # Processing section
    if st.session_state.merge_file_pairs:
        st.markdown("---")
        st.markdown("### ⚙️ Processing")

        if st.button(
            "🚀 Process All File Pairs", type="primary", use_container_width=True
        ):
            process_merge_files()

    # Status messages
    if st.session_state.get("status_messages"):
        st.markdown("---")
        st.session_state.ui_adapter.display_status_messages()

    # Download section
    show_download_section()


def add_file_pair_interface():
    """Interface for adding a new file pair."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Excel File (.xlsx, .xls)**")
        excel_file = st.file_uploader(
            "Choose Excel file",
            type=["xlsx", "xls"],
            key="new_excel_uploader",
            help="Maximum file size: 400MB",
        )

    with col2:
        st.markdown("**PDF File (.pdf)**")
        pdf_file = st.file_uploader(
            "Choose PDF file",
            type=["pdf"],
            key="new_pdf_uploader",
            help="Maximum file size: 400MB",
        )

    if excel_file and pdf_file:
        # Validate file sizes
        excel_size_mb = len(excel_file.getvalue()) / (1024 * 1024)
        pdf_size_mb = len(pdf_file.getvalue()) / (1024 * 1024)

        if excel_size_mb > 400:
            st.error(
                f"Excel file too large: {excel_size_mb:.1f}MB. Maximum allowed: 400MB"
            )
            return

        if pdf_size_mb > 400:
            st.error(f"PDF file too large: {pdf_size_mb:.1f}MB. Maximum allowed: 400MB")
            return

        # Show file info and add button
        st.success(f"✅ Excel: {excel_file.name} ({excel_size_mb:.1f}MB)")
        st.success(f"✅ PDF: {pdf_file.name} ({pdf_size_mb:.1f}MB)")

        if st.button("➕ Add This File Pair", type="secondary"):
            # Save files to temporary locations
            excel_temp_path = save_temp_file(excel_file, "excel")
            pdf_temp_path = save_temp_file(pdf_file, "pdf")

            # Add to session state
            pair_info = {
                "excel_name": excel_file.name,
                "pdf_name": pdf_file.name,
                "excel_path": excel_temp_path,
                "pdf_path": pdf_temp_path,
                "excel_size": excel_size_mb,
                "pdf_size": pdf_size_mb,
            }

            st.session_state.merge_file_pairs.append(pair_info)
            st.success(f"Added file pair: {excel_file.name} + {pdf_file.name}")
            st.rerun()


def display_file_pairs():
    """Display the list of added file pairs."""
    for i, pair in enumerate(st.session_state.merge_file_pairs):
        with st.container():
            col1, col2, col3 = st.columns([3, 3, 1])

            with col1:
                st.markdown(f"**📊 {pair['excel_name']}**")
                st.caption(f"Size: {pair['excel_size']:.1f}MB")

            with col2:
                st.markdown(f"**📄 {pair['pdf_name']}**")
                st.caption(f"Size: {pair['pdf_size']:.1f}MB")

            with col3:
                if st.button("🗑️", key=f"remove_pair_{i}", help="Remove this pair"):
                    st.session_state.merge_file_pairs.pop(i)
                    st.rerun()

        if i < len(st.session_state.merge_file_pairs) - 1:
            st.markdown("---")

    # Summary
    total_pairs = len(st.session_state.merge_file_pairs)
    total_size = sum(
        pair["excel_size"] + pair["pdf_size"]
        for pair in st.session_state.merge_file_pairs
    )

    st.markdown(f"**Summary:** {total_pairs} file pairs, {total_size:.1f}MB total")

    if st.button("🗑️ Clear All Pairs", type="secondary"):
        st.session_state.merge_file_pairs = []
        st.rerun()


def show_processing_options_sidebar():
    """Display processing options in the sidebar."""
    with st.sidebar:
        st.markdown("### ⚙️ Processing Options")

        # Sort bookmarks option
        sort_bookmarks = st.checkbox(
            "Sort PDF Bookmarks",
            value=st.session_state.get("sort_bookmarks_enabled", True),
            key="sort_bookmarks_enabled_merge",
            help="Sort PDF bookmarks naturally",
        )

        # Reorder pages option (dependent on sort bookmarks)
        reorder_pages = st.checkbox(
            "Reorder Pages to Match Bookmarks",
            value=st.session_state.get("reorder_pages_enabled", True)
            and sort_bookmarks,
            key="reorder_pages_enabled_merge",
            disabled=not sort_bookmarks,
            help="Physically reorder pages to match sorted bookmarks",
        )

        # Check document images option
        st.checkbox(
            "Check for Document Images",
            value=st.session_state.get("check_document_images_enabled", True),
            key="check_document_images_enabled_merge",
            help="Add/update Document_Found column in Excel output",
        )

        # Filter option
        st.checkbox(
            "Enable Data Filtering",
            value=st.session_state.get("filter_enabled", False),
            key="filter_enabled_merge",
            help="Filter data by column values (will prompt during processing)",
        )


def save_temp_file(uploaded_file, file_type: str) -> str:
    """Save uploaded file to temporary location."""
    import tempfile

    suffix = ".xlsx" if file_type == "excel" else ".pdf"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(uploaded_file.getvalue())
    temp_file.close()

    return temp_file.name


def process_merge_files():
    """Process the merge file pairs using the existing controller."""
    try:
        # Prepare merge pairs for the controller
        merge_pairs = [
            (pair["excel_path"], pair["pdf_path"])
            for pair in st.session_state.merge_file_pairs
        ]
        st.session_state.merge_pairs = merge_pairs

        # Create controller with UI adapter
        controller = AppController(st.session_state.ui_adapter)

        # Show processing status
        with st.spinner("Processing file pairs..."):
            progress_bar = st.progress(0)
            status_container = st.empty()

            # Update progress
            progress_bar.progress(25)
            status_container.text("Validating file pairs...")

            # Process files (using first pair as primary, others as merge pairs)
            if merge_pairs:
                # Set primary files from first pair
                st.session_state.excel_temp_path = merge_pairs[0][0]
                st.session_state.pdf_temp_path = merge_pairs[0][1]

                progress_bar.progress(50)
                status_container.text("Processing merge...")

                controller.process_files()

                progress_bar.progress(100)
                status_container.text("Merge processing complete!")

        st.session_state.processing_complete = True

    except Exception as e:
        st.error(f"Merge processing failed: {str(e)}")
        st.session_state.ui_adapter.log_status(f"ERROR: {str(e)}")


def show_download_section():
    """Display download section for processed merged files."""
    if st.session_state.get("processing_complete"):
        st.markdown("---")
        st.markdown("### 📥 Download Merged Files")

        # Check if both files are available
        excel_available = (
            st.session_state.get("excel_temp_path")
            and Path(st.session_state.excel_temp_path).exists()
        )
        pdf_available = (
            st.session_state.get("pdf_temp_path")
            and Path(st.session_state.pdf_temp_path).exists()
        )

        if excel_available and pdf_available:
            # Create ZIP file with both processed files
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # Add Excel file
                with open(st.session_state.excel_temp_path, "rb") as excel_file:
                    zip_file.writestr(
                        "merged_documents_processed.xlsx", excel_file.read()
                    )

                # Add PDF file
                with open(st.session_state.pdf_temp_path, "rb") as pdf_file:
                    zip_file.writestr("merged_documents_processed.pdf", pdf_file.read())

            zip_buffer.seek(0)

            st.download_button(
                label="📦 Download Merged Files (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="merged_documents_processed.zip",
                mime="application/zip",
                use_container_width=True,
                help="Downloads both merged Excel and PDF files in a ZIP archive",
            )

            # Show what's included
            st.info(
                "📁 **merged_documents_processed.zip** contains:\n- 📊 merged_documents_processed.xlsx\n- 📄 merged_documents_processed.pdf"
            )

        else:
            st.error("Processed files not available for download")


if __name__ == "__main__":
    show_multi_file_merge()
