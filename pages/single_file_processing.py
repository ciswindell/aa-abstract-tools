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

    # Progressive workflow after files are uploaded
    if uploaded_excel and uploaded_pdf:
        show_progressive_workflow()

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
    """Display minimal sidebar info."""
    with st.sidebar:
        st.markdown("### ℹ️ Processing Info")
        st.info("Upload your files to begin the guided workflow.")

        # Show current workflow step if in progress
        if st.session_state.get("filter_decision_made"):
            if st.session_state.get("wants_filtering") and not st.session_state.get(
                "filter_configured"
            ):
                st.info("📍 **Current Step:** Filter Configuration")
            elif not st.session_state.get("processing_options_decided"):
                st.info("📍 **Current Step:** Processing Options")
            elif st.session_state.get("processing_options_decided"):
                st.info("📍 **Current Step:** Ready to Process")
        elif st.session_state.get("excel_temp_path") and st.session_state.get(
            "pdf_temp_path"
        ):
            st.info("📍 **Current Step:** Filter Decision")


def show_progressive_workflow():
    """Show the progressive workflow with decision points."""
    st.markdown("---")

    # Step 1: Filter Decision Point
    if "filter_decision_made" not in st.session_state:
        show_filter_decision_point()
        return

    # Step 2: Filter Configuration (if filtering was chosen)
    if st.session_state.get("filter_decision_made") and st.session_state.get(
        "wants_filtering"
    ):
        if "filter_configured" not in st.session_state:
            show_filter_configuration()
            return

    # Step 3: Processing Options Decision Point
    if "processing_options_decided" not in st.session_state:
        show_processing_options_decision()
        return

    # Step 4: Final Processing
    show_final_processing_section()


def show_filter_decision_point():
    """Show the filter decision point."""
    st.markdown("### 🔍 Data Filtering")
    st.markdown("Would you like to filter this data before processing?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "📊 No, Process All Data", type="primary", use_container_width=True
        ):
            st.session_state.filter_decision_made = True
            st.session_state.wants_filtering = False
            st.session_state.filter_enabled = False
            st.session_state.filter_column = None
            st.session_state.filter_values = []
            st.rerun()

    with col2:
        if st.button("🔍 Yes, Set Up Filtering", use_container_width=True):
            st.session_state.filter_decision_made = True
            st.session_state.wants_filtering = True
            st.session_state.filter_enabled = True
            st.rerun()


def show_filter_configuration():
    """Show filter configuration interface."""
    st.markdown("### 🔍 Filter Configuration")

    # Load Excel data for filtering
    excel_path = st.session_state.get("excel_temp_path")
    if not excel_path:
        st.error("Excel file not found. Please re-upload your Excel file.")
        return

    try:
        from adapters.excel_repo import ExcelOpenpyxlRepo

        excel_repo = ExcelOpenpyxlRepo()
        df = excel_repo.load(excel_path, sheet="Sheet")

        if df is None or df.empty:
            st.error("Could not load Excel data for filtering.")
            return

        # Get filterable columns (exclude system columns)
        system_columns = {"_include", "Index#", "Document_ID"}
        filterable_columns = [col for col in df.columns if col not in system_columns]

        if not filterable_columns:
            st.warning("No filterable columns found in the Excel data.")
            return

        # Column selection
        filter_column = st.selectbox(
            "Select column to filter by:",
            options=filterable_columns,
            key="filter_column_widget",
            help="Choose which column to use for filtering the data",
        )

        if filter_column:
            # Get unique values for the selected column
            unique_values = sorted(df[filter_column].dropna().unique().tolist())

            if not unique_values:
                st.warning(f"No values found in column '{filter_column}'.")
                return

            # Value selection
            filter_values = st.multiselect(
                f"Select values to include from '{filter_column}':",
                options=unique_values,
                key="filter_values_widget",
                help="Choose which values to include. Only rows with these values will be processed.",
            )

            # Show filter summary
            if filter_values:
                filtered_count = len(df[df[filter_column].isin(filter_values)])
                st.success(
                    f"📈 **Filter Summary:** {filtered_count} out of {len(df)} rows will be included"
                )

                # Continue button
                if st.button(
                    "✅ Continue with Filter Settings",
                    type="primary",
                    use_container_width=True,
                ):
                    # Explicitly store the filter values before moving to next step
                    st.session_state.filter_column = filter_column
                    st.session_state.filter_values = filter_values
                    st.session_state.filter_configured = True
                    st.rerun()
            else:
                st.info("Select values above to continue.")

    except Exception as e:
        st.error(f"Error loading Excel data for filtering: {e}")


def show_processing_options_decision():
    """Show processing options decision point."""
    st.markdown("### ⚙️ Processing Options")
    st.markdown("Configure how you want your files processed:")

    # Default values
    default_sort = True
    default_reorder = True
    default_check_images = True

    # Processing options with defaults
    sort_bookmarks = st.checkbox(
        "Sort PDF Bookmarks",
        value=default_sort,
        key="sort_bookmarks_enabled",
        help="Sort PDF bookmarks naturally",
    )

    st.checkbox(
        "Reorder Pages to Match Bookmarks",
        value=default_reorder and sort_bookmarks,
        key="reorder_pages_enabled",
        disabled=not sort_bookmarks,
        help="Physically reorder pages to match sorted bookmarks",
    )

    st.checkbox(
        "Check Document Images",
        value=default_check_images,
        key="check_document_images_enabled",
        help="Verify document images during processing",
    )

    # Continue button
    if st.button(
        "✅ Continue with These Settings", type="primary", use_container_width=True
    ):
        st.session_state.processing_options_decided = True
        st.rerun()


def show_final_processing_section():
    """Show the final processing section."""
    st.markdown("### 🚀 Ready to Process")

    # Show summary of what will be processed
    summary_parts = []

    # Filter summary
    if st.session_state.get("wants_filtering"):
        filter_column = st.session_state.get("filter_column")
        filter_values = st.session_state.get("filter_values", [])
        if filter_column and filter_values:
            summary_parts.append(f"**Filtering:** {filter_column} = {filter_values}")
        else:
            summary_parts.append("**Filtering:** Configured but no values selected")
    else:
        summary_parts.append("**Filtering:** Process all data")

    # Processing options summary
    options = []
    if st.session_state.get("sort_bookmarks_enabled", True):
        options.append("Sort bookmarks")
    if st.session_state.get("reorder_pages_enabled", True):
        options.append("Reorder pages")
    if st.session_state.get("check_document_images_enabled", True):
        options.append("Check images")

    if options:
        summary_parts.append(f"**Options:** {', '.join(options)}")

    # Display summary
    if summary_parts:
        st.info(
            "📋 **Processing Summary:**\n"
            + "\n".join(f"- {part}" for part in summary_parts)
        )

    # Process button
    if st.button("🚀 Process Files", type="primary", use_container_width=True):
        process_files()
        st.session_state.show_downloads = True


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
        # Clear all workflow state
        st.session_state.filter_decision_made = False
        st.session_state.wants_filtering = False
        st.session_state.filter_configured = False
        st.session_state.processing_options_decided = False
        st.session_state.filter_enabled = False
        st.session_state.filter_column = None
        st.session_state.filter_values = []
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
