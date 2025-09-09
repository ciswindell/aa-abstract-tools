#!/usr/bin/env python3
"""
Single file processing page for Abstract Renumber Tool.

Handles the workflow for processing one Excel file and one PDF file.
"""

import io
import time
import zipfile
from pathlib import Path

import streamlit as st

from adapters.ui_streamlit import StreamlitUIAdapter
from core.app_controller import AppController


# Custom CSS for button styling
def inject_custom_css():
    """Inject custom CSS for button styling."""
    st.markdown(
        """
        <style>
        /* Download button - Green primary style */
        .stDownloadButton > button {
            background-color: #28a745 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stDownloadButton > button:hover {
            background-color: #218838 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3) !important;
        }
        
        /* Alternative selector for download button */
        button[kind="primary"] {
            background-color: #28a745 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        button[kind="primary"]:hover {
            background-color: #218838 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3) !important;
        }
        
        /* Process button - Red primary style - Multiple selectors to ensure it works */
        .stButton > button[kind="primary"]:not([data-testid*="download"]) {
            background-color: #dc3545 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button[kind="primary"]:not([data-testid*="download"]):hover {
            background-color: #c82333 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3) !important;
        }
        
        /* Alternative selector for process button */
        button[data-testid="baseButton-primary"] {
            background-color: #dc3545 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        button[data-testid="baseButton-primary"]:hover {
            background-color: #c82333 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3) !important;
        }

        /* Reset button - Orange secondary style */
        .stButton > button[kind="secondary"] {
            background-color: #fd7e14 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background-color: #e8690b !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(253, 126, 20, 0.3) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def clear_file_uploaders():
    """Clear file uploaders by rotating their keys."""
    # Generate new unique keys to force uploader reset
    timestamp = int(time.time() * 1000)  # Use milliseconds for uniqueness
    st.session_state.excel_uploader_key = f"excel_uploader_{timestamp}"
    st.session_state.pdf_uploader_key = f"pdf_uploader_{timestamp + 1}"


def show_single_file_processing():
    """Display the single file processing page."""
    # Inject custom CSS for button styling
    inject_custom_css()

    st.title("📄 Single File Processing")
    st.markdown("---")

    # Initialize UI adapter
    if "ui_adapter" not in st.session_state:
        st.session_state.ui_adapter = StreamlitUIAdapter()

    # Initialize uploader keys for clearing functionality
    if "excel_uploader_key" not in st.session_state:
        st.session_state.excel_uploader_key = "excel_uploader_0"
    if "pdf_uploader_key" not in st.session_state:
        st.session_state.pdf_uploader_key = "pdf_uploader_0"

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
            key=st.session_state.excel_uploader_key,
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
            key=st.session_state.pdf_uploader_key,
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

    # Processing section
    if uploaded_excel and uploaded_pdf:
        st.markdown("---")

        # Simple process button
        if st.button("🚀 Process Files", type="primary", use_container_width=True):
            process_files()
            st.session_state.show_downloads = True

        # Handle post-processing workflow if processing completed
        if st.session_state.get("show_downloads"):
            handle_post_processing()
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

        # Show simple processing status
        with st.spinner("Processing files..."):
            # Process files
            controller.process_files()

        st.success("✅ Files processed successfully!")

    except Exception as e:
        st.error(f"Processing failed: {str(e)}")
        st.session_state.ui_adapter.log_status(f"ERROR: {str(e)}")


def get_filename_or_default(session_key: str, default: str = "document") -> str:
    """Get filename from session state or return default."""
    file_obj = st.session_state.get(session_key)
    return file_obj.name if file_obj else default


def create_processed_filename(original_name: str, extension: str) -> str:
    """Create processed filename from original name."""
    base_name = Path(original_name).stem
    return f"{base_name}.{extension}"


def read_file_safely(file_path: str) -> bytes:
    """Read file and return data, raise exception if fails."""
    with open(file_path, "rb") as f:
        data = f.read()
    if len(data) == 0:
        raise ValueError(f"File appears to be empty: {file_path}")
    return data


def create_download_zip(
    excel_data: bytes, pdf_data: bytes, excel_name: str, pdf_name: str
) -> io.BytesIO:
    """Create ZIP file with processed files."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(excel_name, excel_data)
        zip_file.writestr(pdf_name, pdf_data)
    zip_buffer.seek(0)
    return zip_buffer


def show_download_ui(
    zip_data: bytes, zip_filename: str, excel_name: str, pdf_name: str
):
    """Display download UI components."""
    timestamp = int(time.time())
    download_key = f"download_zip_{timestamp}"

    st.download_button(
        label="📦 Download Processed Files (ZIP)",
        data=zip_data,
        file_name=zip_filename,
        mime="application/zip",
        use_container_width=True,
        help=f"Downloads both {excel_name} and {pdf_name} in a ZIP archive",
        key=download_key,
        type="primary",
    )


def show_reset_ui():
    """Display reset UI and handle reset functionality."""
    st.markdown("---")
    if st.button("🔄 Process New Files", use_container_width=True, type="secondary"):
        clear_file_uploaders()
        st.session_state.show_downloads = False
        st.session_state.ui_adapter.reset_gui()
        st.rerun()


def handle_post_processing():
    """Handle post-processing workflow: downloads and reset functionality."""
    st.markdown("### 📥 Download Processed Files")

    # Get file paths
    excel_path = st.session_state.get("excel_temp_path")
    pdf_path = st.session_state.get("pdf_temp_path")

    if not excel_path or not pdf_path:
        st.error("Processed files not available for download")
        return

    try:
        # Get filenames
        excel_name = get_filename_or_default("uploaded_excel_file")
        pdf_name = get_filename_or_default("uploaded_pdf_file")

        # Create processed filenames
        processed_excel_name = create_processed_filename(excel_name, "xlsx")
        processed_pdf_name = create_processed_filename(pdf_name, "pdf")

        # Read processed files
        excel_data = read_file_safely(excel_path)
        pdf_data = read_file_safely(pdf_path)

        # Create ZIP
        zip_buffer = create_download_zip(
            excel_data, pdf_data, processed_excel_name, processed_pdf_name
        )

        # Create ZIP filename with timestamp
        timestamp = int(time.time())
        base_name = Path(excel_name).stem
        zip_filename = f"{base_name}_processed_{timestamp}.zip"

        # Show download UI
        show_download_ui(
            zip_buffer.getvalue(),
            zip_filename,
            processed_excel_name,
            processed_pdf_name,
        )

        # Show reset UI
        show_reset_ui()

    except Exception as e:
        st.error(f"Error preparing download: {e}")


if __name__ == "__main__":
    show_single_file_processing()
