#!/usr/bin/env python3
"""
Single file processing page for Abstract Renumber Tool.

Handles the workflow for processing one Excel file and one PDF file.
"""

import io
import zipfile
from pathlib import Path

import streamlit as st

from adapters.ui_streamlit import StreamlitUIAdapter
from core.app_controller import AppController


def show_single_file_processing():
    """Display the single file processing page."""
    st.title("📄 Single File Processing")
    st.markdown("---")

    # Initialize UI adapter
    if "ui_adapter" not in st.session_state:
        st.session_state.ui_adapter = StreamlitUIAdapter()

    # Back to mode selection button
    if st.button("← Back to Mode Selection", key="back_to_mode"):
        st.session_state.current_page = "mode_selection"
        st.rerun()

    # File upload section
    st.markdown("### 📁 File Upload")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Excel File (.xlsx, .xls)**")
        uploaded_excel = st.file_uploader(
            "Choose Excel file",
            type=["xlsx", "xls"],
            key="excel_uploader",
            help="Maximum file size: 400MB",
        )

        if uploaded_excel:
            # Validate file size
            file_size_mb = len(uploaded_excel.getvalue()) / (1024 * 1024)
            if file_size_mb > 400:
                st.error(
                    f"File too large: {file_size_mb:.1f}MB. Maximum allowed: 400MB"
                )
            else:
                st.success(f"✅ {uploaded_excel.name} ({file_size_mb:.1f}MB)")
                # Save to temporary file
                st.session_state.ui_adapter.save_uploaded_file(uploaded_excel, "excel")
                st.session_state.uploaded_excel_file = uploaded_excel

    with col2:
        st.markdown("**PDF File (.pdf)**")
        uploaded_pdf = st.file_uploader(
            "Choose PDF file",
            type=["pdf"],
            key="pdf_uploader",
            help="Maximum file size: 400MB",
        )

        if uploaded_pdf:
            # Validate file size
            file_size_mb = len(uploaded_pdf.getvalue()) / (1024 * 1024)
            if file_size_mb > 400:
                st.error(
                    f"File too large: {file_size_mb:.1f}MB. Maximum allowed: 400MB"
                )
            else:
                st.success(f"✅ {uploaded_pdf.name} ({file_size_mb:.1f}MB)")
                # Save to temporary file
                st.session_state.ui_adapter.save_uploaded_file(uploaded_pdf, "pdf")
                st.session_state.uploaded_pdf_file = uploaded_pdf

    # Processing options sidebar
    show_processing_options_sidebar()

    # Processing/Download section
    if uploaded_excel and uploaded_pdf:
        st.markdown("---")

        # Check if we should process files
        if st.button(
            "🚀 Process Files",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get("processing_complete", False),
        ):
            process_files()

        # Show download section if processing is complete
        if st.session_state.get("processing_complete"):
            st.markdown("---")
            show_download_section()
    else:
        st.info("Please upload both Excel and PDF files to continue.")

    # Status messages
    if st.session_state.get("status_messages"):
        st.markdown("---")
        st.session_state.ui_adapter.display_status_messages()


def show_processing_options_sidebar():
    """Display processing options in the sidebar."""
    with st.sidebar:
        st.markdown("### ⚙️ Processing Options")

        # Sort bookmarks option
        sort_bookmarks = st.checkbox(
            "Sort PDF Bookmarks",
            value=st.session_state.get("sort_bookmarks_enabled", True),
            key="sort_bookmarks_enabled",
            help="Sort PDF bookmarks naturally",
        )

        # Reorder pages option (dependent on sort bookmarks)
        st.checkbox(
            "Reorder Pages to Match Bookmarks",
            value=st.session_state.get("reorder_pages_enabled", True)
            and sort_bookmarks,
            key="reorder_pages_enabled",
            disabled=not sort_bookmarks,
            help="Physically reorder pages to match sorted bookmarks",
        )

        # Check document images option
        st.checkbox(
            "Check for Document Images",
            value=st.session_state.get("check_document_images_enabled", True),
            key="check_document_images_enabled",
            help="Add/update Document_Found column in Excel output",
        )

        # Filter option
        st.checkbox(
            "Enable Data Filtering",
            value=st.session_state.get("filter_enabled", False),
            key="filter_enabled",
            help="Filter data by column values (will prompt during processing)",
        )


def process_files():
    """Process the uploaded files using the existing controller."""
    try:
        # Create controller with UI adapter
        controller = AppController(st.session_state.ui_adapter)

        # Show processing status
        with st.spinner("Processing files..."):
            progress_bar = st.progress(0)
            status_container = st.empty()

            # Update progress
            progress_bar.progress(25)
            status_container.text("Validating files...")

            # Process files
            controller.process_files()

            progress_bar.progress(100)
            status_container.text("Processing complete!")

        # Store processed file data in session state before rerun
        excel_path = st.session_state.get("excel_temp_path")
        pdf_path = st.session_state.get("pdf_temp_path")

        if excel_path and pdf_path:
            try:
                with open(excel_path, "rb") as f:
                    st.session_state.processed_excel_data = f.read()
                with open(pdf_path, "rb") as f:
                    st.session_state.processed_pdf_data = f.read()
            except Exception as e:
                st.error(f"Failed to store processed files: {e}")
                return

        st.session_state.processing_complete = True
        st.rerun()

    except Exception as e:
        st.error(f"Processing failed: {str(e)}")
        st.session_state.ui_adapter.log_status(f"ERROR: {str(e)}")


def show_download_section():
    """Display download section for processed files."""
    st.markdown("### 📥 Download Processed Files")

    # Get original filenames
    excel_name = (
        st.session_state.uploaded_excel_file.name
        if st.session_state.get("uploaded_excel_file")
        else "document"
    )
    pdf_name = (
        st.session_state.uploaded_pdf_file.name
        if st.session_state.get("uploaded_pdf_file")
        else "document"
    )

    # Create processed filenames
    excel_base = Path(excel_name).stem
    pdf_base = Path(pdf_name).stem

    processed_excel_name = f"{excel_base}_processed.xlsx"
    processed_pdf_name = f"{pdf_base}_processed.pdf"

    # Check if processed file data is available in session state
    excel_data = st.session_state.get("processed_excel_data")
    pdf_data = st.session_state.get("processed_pdf_data")

    if excel_data and pdf_data:
        # Create ZIP file with both processed files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            try:
                # Use processed data from session state
                if len(excel_data) == 0:
                    st.error("Excel file appears to be empty")
                    return
                zip_file.writestr(processed_excel_name, excel_data)

                if len(pdf_data) == 0:
                    st.error("PDF file appears to be empty")
                    return
                zip_file.writestr(processed_pdf_name, pdf_data)

            except Exception as e:
                st.error(f"Error creating ZIP file: {e}")
                return

        zip_buffer.seek(0)

        # Create base name for ZIP file with timestamp to bust cache
        import time

        timestamp = int(time.time())
        base_name = Path(excel_name).stem
        zip_filename = f"{base_name}_processed_{timestamp}.zip"

        # Use a unique key for the download button to prevent caching
        download_key = f"download_zip_{timestamp}"

        st.download_button(
            label="📦 Download Processed Files (ZIP)",
            data=zip_buffer.getvalue(),
            file_name=zip_filename,
            mime="application/zip",
            use_container_width=True,
            help=f"Downloads both {processed_excel_name} and {processed_pdf_name} in a ZIP archive",
            key=download_key,
        )

        # Show what's included
        st.info(
            f"📁 **{zip_filename}** contains:\n- 📊 {processed_excel_name}\n- 📄 {processed_pdf_name}"
        )

        # Add button to process new files
        st.markdown("---")
        if st.button("🔄 Process New Files", use_container_width=True):
            # Reset processing state and clear processed data
            st.session_state.processing_complete = False
            if "processed_excel_data" in st.session_state:
                del st.session_state.processed_excel_data
            if "processed_pdf_data" in st.session_state:
                del st.session_state.processed_pdf_data

            # Clear uploaded files from session state
            if "uploaded_excel_file" in st.session_state:
                del st.session_state.uploaded_excel_file
            if "uploaded_pdf_file" in st.session_state:
                del st.session_state.uploaded_pdf_file
            if "excel_temp_path" in st.session_state:
                del st.session_state.excel_temp_path
            if "pdf_temp_path" in st.session_state:
                del st.session_state.pdf_temp_path

            # Clear file uploader widget states
            if "excel_uploader" in st.session_state:
                del st.session_state.excel_uploader
            if "pdf_uploader" in st.session_state:
                del st.session_state.pdf_uploader

            st.session_state.ui_adapter.reset_gui()
            st.rerun()

    else:
        st.error("Processed files not available for download")


if __name__ == "__main__":
    show_single_file_processing()
