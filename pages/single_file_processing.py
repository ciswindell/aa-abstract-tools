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

from adapters.excel_repo import ExcelOpenpyxlRepo
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

    # Initialize only essential workflow state variables (don't override existing values)
    # These will be set by user interactions or reset function
    pass

    # Back to mode selection button
    if st.button("← Back to Mode Selection", key="back_to_mode"):
        st.session_state.current_page = "mode_selection"
        st.rerun()

    # Processing options sidebar
    show_processing_options_sidebar()

    # Tabbed workflow interface
    show_tabbed_workflow()

    # Handle post-processing workflow if processing completed
    if st.session_state.get("show_downloads"):
        handle_post_processing()

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


def show_tabbed_workflow():
    """Show the tabbed workflow interface."""
    # Create tabs for each step
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📁 Files", "🔍 Filtering", "⚙️ Options", "🚀 Process"]
    )

    with tab1:
        show_file_upload_tab()

    with tab2:
        show_filtering_tab()

    with tab3:
        show_options_tab()

    with tab4:
        show_processing_tab()


def show_file_upload_tab():
    """Show the file upload tab content."""
    st.markdown("### 📁 Upload Files")
    st.markdown("Upload your Excel and PDF files to get started.")

    # File upload widgets (moved into the tab)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Excel File (.xlsx, .xls)**")
        uploaded_excel = st.file_uploader(
            "Choose Excel file",
            type=["xlsx", "xls"],
            key=st.session_state.get("excel_uploader_key", "excel_uploader_0"),
            help="Upload your Excel file containing the data to process",
        )

    with col2:
        st.markdown("**PDF File (.pdf)**")
        uploaded_pdf = st.file_uploader(
            "Choose PDF file",
            type=["pdf"],
            key=st.session_state.get("pdf_uploader_key", "pdf_uploader_0"),
            help="Upload your PDF file to be processed",
        )

    # Store uploaded files in session state and save to temp files
    if uploaded_excel:
        # Validate file size
        file_size_mb = len(uploaded_excel.getvalue()) / (1024 * 1024)
        if file_size_mb > 400:
            st.error(f"File too large: {file_size_mb:.1f}MB. Maximum allowed: 400MB")
        else:
            st.session_state.uploaded_excel = uploaded_excel
            # Save to temp file using UI adapter
            st.session_state.ui_adapter.save_uploaded_file(uploaded_excel, "excel")

    if uploaded_pdf:
        # Validate file size
        file_size_mb = len(uploaded_pdf.getvalue()) / (1024 * 1024)
        if file_size_mb > 400:
            st.error(f"File too large: {file_size_mb:.1f}MB. Maximum allowed: 400MB")
        else:
            st.session_state.uploaded_pdf = uploaded_pdf
            # Save to temp file using UI adapter
            st.session_state.ui_adapter.save_uploaded_file(uploaded_pdf, "pdf")

    # Show upload status
    if uploaded_excel and uploaded_pdf:
        st.success("✅ Files uploaded successfully!")

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📊 **Excel:** {uploaded_excel.name}")
        with col2:
            st.info(f"📄 **PDF:** {uploaded_pdf.name}")

        st.markdown("---")
        st.info(
            "👉 **Next:** Click on the **Filtering** tab above to configure data filtering."
        )
    elif uploaded_excel or uploaded_pdf:
        st.warning("⚠️ Please upload both Excel and PDF files to continue.")
    else:
        st.info("📤 Please select your files using the uploaders above.")


def show_filtering_tab():
    """Show the filtering tab content."""
    uploaded_excel = st.session_state.get("uploaded_excel")
    uploaded_pdf = st.session_state.get("uploaded_pdf")

    if not (uploaded_excel and uploaded_pdf):
        st.warning("⚠️ Please upload files in the **Files** tab first.")
        return

    st.markdown("### 🔍 Data Filtering")
    st.markdown("Choose whether to filter your data before processing.")

    # Filter decision
    wants_filtering = st.radio(
        "Would you like to filter this data?",
        options=[False, True],
        format_func=lambda x: "📊 No, Process All Data"
        if not x
        else "🔍 Yes, Set Up Filtering",
        key="wants_filtering_radio",
        horizontal=True,
    )

    # Store the decision
    st.session_state.wants_filtering = wants_filtering
    st.session_state.filter_enabled = wants_filtering

    if wants_filtering:
        st.markdown("#### Configure Filter Settings")
        show_filter_configuration_content()
    else:
        # Clear filter settings if not filtering
        st.session_state.filter_column = None
        st.session_state.filter_values = []
        st.info("✅ All data will be processed without filtering.")

        st.markdown("---")
    st.info(
        "👉 **Next:** Click on the **Options** tab above to configure processing options."
    )


def show_options_tab():
    """Show the processing options tab content."""
    uploaded_excel = st.session_state.get("uploaded_excel")
    uploaded_pdf = st.session_state.get("uploaded_pdf")

    if not (uploaded_excel and uploaded_pdf):
        st.warning("⚠️ Please upload files in the **Files** tab first.")
        return

        st.markdown("### ⚙️ Processing Options")
    st.markdown("Configure how your files will be processed.")

    # Processing options
    col1, col2 = st.columns(2)

    with col1:
        sort_bookmarks = st.checkbox(
            "Sort PDF Bookmarks",
            value=st.session_state.get("sort_bookmarks_enabled", True),
            key="sort_bookmarks_tab",
            help="Sort PDF bookmarks naturally",
        )

        reorder_pages = st.checkbox(
            "Reorder Pages to Match Bookmarks",
            value=st.session_state.get("reorder_pages_enabled", True)
            and sort_bookmarks,
            key="reorder_pages_tab",
            disabled=not sort_bookmarks,
            help="Physically reorder pages to match sorted bookmarks",
        )

    with col2:
        check_images = st.checkbox(
            "Check Document Images",
            value=st.session_state.get("check_document_images_enabled", True),
            key="check_images_tab",
            help="Verify document images during processing",
        )

    # Store the options
    st.session_state.sort_bookmarks_enabled = sort_bookmarks
    st.session_state.reorder_pages_enabled = reorder_pages
    st.session_state.check_document_images_enabled = check_images

    # Show summary
    st.markdown("#### Current Settings")
    settings_summary = []
    settings_summary.append(
        f"**Sort Bookmarks:** {'✅ Enabled' if sort_bookmarks else '❌ Disabled'}"
    )
    settings_summary.append(
        f"**Reorder Pages:** {'✅ Enabled' if reorder_pages else '❌ Disabled'}"
    )
    settings_summary.append(
        f"**Check Images:** {'✅ Enabled' if check_images else '❌ Disabled'}"
    )

    st.info("\n".join(settings_summary))

    st.markdown("---")
    st.info(
        "👉 **Next:** Click on the **Process** tab above to review and start processing."
    )


def show_processing_tab():
    """Show the processing tab content."""
    uploaded_excel = st.session_state.get("uploaded_excel")
    uploaded_pdf = st.session_state.get("uploaded_pdf")

    if not (uploaded_excel and uploaded_pdf):
        st.warning("⚠️ Please upload files in the **Files** tab first.")
        return

    st.markdown("### 🚀 Ready to Process")
    st.markdown("Review your settings and start processing.")

    # Show comprehensive summary
    show_processing_summary()

    # Process button
    if st.button("🚀 Process Files", type="primary", use_container_width=True):
        process_files()
        st.session_state.show_downloads = True


def show_filter_configuration_content():
    """Show the filter configuration content (extracted from original function)."""
    try:
        # Load Excel data for filtering
        excel_temp_path = st.session_state.get("excel_temp_path")
        if not excel_temp_path:
            st.error("Excel file not found. Please re-upload your files.")
            return

        excel_repo = ExcelOpenpyxlRepo()

        # Get available sheet names and use appropriate sheet
        available_sheets = excel_repo.get_sheet_names(excel_temp_path)
        sheet_name = (
            "Sheet"
            if "Sheet" in available_sheets
            else available_sheets[0]
            if available_sheets
            else "Sheet"
        )

        df = excel_repo.load(excel_temp_path, sheet=sheet_name)

        # Get filterable columns (exclude system columns)
        system_columns = {"_include", "Index#", "Document_ID"}
        filterable_columns = [col for col in df.columns if col not in system_columns]

        if not filterable_columns:
            st.warning("No suitable columns found for filtering.")
            return

        # Column selection
        filter_column = st.selectbox(
            "Select column to filter by:",
            options=filterable_columns,
            key="filter_column_tab",
            help="Choose which column to use for filtering the data",
        )

        if filter_column:
            # Get unique values for the selected column
            unique_values = sorted(df[filter_column].dropna().unique())

            # Value selection
            filter_values = st.multiselect(
                f"Select values to include from '{filter_column}':",
                options=unique_values,
                key="filter_values_tab",
                help="Choose which values to include. Only rows with these values will be processed.",
            )

            # Store filter settings
            st.session_state.filter_column = filter_column
            st.session_state.filter_values = filter_values

            if filter_values:
                # Show preview of filtered data
                filtered_count = df[df[filter_column].isin(filter_values)].shape[0]
                total_count = df.shape[0]
                st.success(
                    f"✅ Filter configured: {filtered_count}/{total_count} rows will be processed"
                )
            else:
                st.info("Select values to see filtering preview.")

    except Exception as e:
        st.error(f"Error loading Excel data for filtering: {str(e)}")


def show_processing_summary():
    """Show a comprehensive processing summary."""
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
    sort_enabled = st.session_state.get("sort_bookmarks_enabled", True)
    reorder_enabled = st.session_state.get("reorder_pages_enabled", True)
    check_enabled = st.session_state.get("check_document_images_enabled", True)

    options_summary = []
    if sort_enabled:
        options_summary.append("Sort Bookmarks")
    if reorder_enabled:
        options_summary.append("Reorder Pages")
    if check_enabled:
        options_summary.append("Check Images")

    if options_summary:
        summary_parts.append(f"**Options:** {', '.join(options_summary)}")
    else:
        summary_parts.append("**Options:** None selected")

    # Display summary
    if summary_parts:
        st.info(
            "📋 **Processing Summary:**\n"
            + "\n".join(f"- {part}" for part in summary_parts)
        )


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
        excel_repo = ExcelOpenpyxlRepo()

        # Get available sheet names and let user select if needed
        available_sheets = excel_repo.get_sheet_names(excel_path)

        # Try default sheet first, then prompt if not found
        sheet_name = "Sheet"
        if sheet_name not in available_sheets:
            if len(available_sheets) == 1:
                sheet_name = available_sheets[0]
                st.info(f"Using sheet: '{sheet_name}'")
            else:
                st.warning(
                    f"Sheet '{sheet_name}' not found. Available sheets: {', '.join(available_sheets)}"
                )
                sheet_name = st.selectbox(
                    "Select Excel sheet to use for filtering:",
                    options=available_sheets,
                    key="filter_sheet_selection",
                )

        df = excel_repo.load(excel_path, sheet=sheet_name)

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
        key="sort_bookmarks_widget",
        help="Sort PDF bookmarks naturally",
    )

    reorder_pages = st.checkbox(
        "Reorder Pages to Match Bookmarks",
        value=default_reorder and sort_bookmarks,
        key="reorder_pages_widget",
        disabled=not sort_bookmarks,
        help="Physically reorder pages to match sorted bookmarks",
    )

    check_images = st.checkbox(
        "Check Document Images",
        value=default_check_images,
        key="check_document_images_widget",
        help="Verify document images during processing",
    )

    # Continue button
    if st.button(
        "✅ Continue with These Settings", type="primary", use_container_width=True
    ):
        # Explicitly store the processing option values before moving to next step
        st.session_state.sort_bookmarks_enabled = sort_bookmarks
        st.session_state.reorder_pages_enabled = reorder_pages
        st.session_state.check_document_images_enabled = check_images

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


def reset_workflow_state():
    """Reset all workflow state for a fresh start."""
    # Clear file uploaders
    clear_file_uploaders()
    st.session_state.show_downloads = False

    # Reset filter settings
    st.session_state.wants_filtering = False
    st.session_state.filter_enabled = False
    st.session_state.filter_column = None
    st.session_state.filter_values = []

    # Reset processing option states to defaults
    st.session_state.sort_bookmarks_enabled = True
    st.session_state.reorder_pages_enabled = True
    st.session_state.check_document_images_enabled = True

    # Reset widget states
    st.session_state.filter_column_widget = None
    st.session_state.filter_values_widget = []

    # Reset UI adapter
    st.session_state.ui_adapter.reset_gui()


def show_reset_ui():
    """Display reset UI and handle reset functionality."""
    st.markdown("---")
    st.button(
        "🔄 Process New Files",
        use_container_width=True,
        type="secondary",
        on_click=reset_workflow_state,
    )


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
