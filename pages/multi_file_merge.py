#!/usr/bin/env python3
"""
Multi-file merge page for Abstract Renumber Tool.

Handles the workflow for merging multiple Excel/PDF file pairs.
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
    st.session_state.primary_excel_uploader_key = f"primary_excel_{timestamp}"
    st.session_state.primary_pdf_uploader_key = f"primary_pdf_{timestamp + 1}"
    st.session_state.additional_excel_uploader_key = f"additional_excel_{timestamp + 2}"
    st.session_state.additional_pdf_uploader_key = f"additional_pdf_{timestamp + 3}"


def show_multi_file_merge():
    """Display the multi-file merge page."""
    # Inject custom CSS for button styling
    inject_custom_css()

    st.title("📚 Multi-File Merge")
    st.markdown("---")

    # Initialize UI adapter
    if "ui_adapter" not in st.session_state:
        st.session_state.ui_adapter = StreamlitUIAdapter()

    # Initialize primary pair and additional pairs in session state
    if "primary_pair" not in st.session_state:
        st.session_state.primary_pair = None
    if "additional_pairs" not in st.session_state:
        st.session_state.additional_pairs = []

    # Initialize uploader keys for clearing functionality
    if "primary_excel_uploader_key" not in st.session_state:
        st.session_state.primary_excel_uploader_key = "primary_excel_0"
    if "primary_pdf_uploader_key" not in st.session_state:
        st.session_state.primary_pdf_uploader_key = "primary_pdf_0"
    if "additional_excel_uploader_key" not in st.session_state:
        st.session_state.additional_excel_uploader_key = "additional_excel_0"
    if "additional_pdf_uploader_key" not in st.session_state:
        st.session_state.additional_pdf_uploader_key = "additional_pdf_0"

    # Back to mode selection button
    if st.button("← Back to Mode Selection", key="back_to_mode_merge"):
        st.session_state.current_page = "mode_selection"
        st.rerun()

    # Primary pair selection section
    st.markdown("### 🎯 Primary File Pair")
    st.info(
        "Select the main Excel and PDF files that will serve as the base for merging."
    )

    show_primary_pair_interface()

    # Additional pairs section (only show if primary pair is selected)
    if st.session_state.primary_pair:
        st.markdown("---")
        st.markdown("### ➕ Additional File Pairs")
        st.info("Add more Excel-PDF pairs to merge with the primary pair.")

        show_additional_pairs_interface()
    else:
        st.info(
            "👆 Please select a primary file pair first, then you can add additional pairs to merge."
        )

    # Processing options sidebar
    show_processing_options_sidebar()

    # Processing section
    if st.session_state.primary_pair:
        st.markdown("---")
        st.markdown("### ⚙️ Processing")

        # Show summary of what will be processed
        total_pairs = 1 + len(st.session_state.additional_pairs)
        if total_pairs == 1:
            st.info("📊 Ready to process: **1 file pair** (primary only)")
        else:
            st.info(
                f"📊 Ready to process: **{total_pairs} file pairs** (1 primary + {len(st.session_state.additional_pairs)} additional)"
            )

        if st.button(
            "🚀 Process All File Pairs", type="primary", use_container_width=True
        ):
            process_merge_files()
            st.session_state.show_downloads = True

    # Download section - only show if processing completed
    if st.session_state.get("show_downloads"):
        handle_post_processing()

    # Status messages - exactly like single file processing
    if st.session_state.get("status_messages"):
        st.markdown("---")
        st.session_state.ui_adapter.display_status_messages()


def show_primary_pair_interface():
    """Interface for selecting the primary file pair."""
    if st.session_state.primary_pair:
        # Show current primary pair
        pair = st.session_state.primary_pair

        with st.container():
            col1, col2, col3 = st.columns([3, 3, 1])

            with col1:
                st.success(f"📊 **{pair['excel_name']}**")
                st.caption(f"Size: {pair['excel_size']:.1f}MB")

            with col2:
                st.success(f"📄 **{pair['pdf_name']}**")
                st.caption(f"Size: {pair['pdf_size']:.1f}MB")

            with col3:
                if st.button("🔄", key="change_primary", help="Change primary pair"):
                    st.session_state.primary_pair = None
                    st.rerun()
    else:
        # Interface for selecting primary pair
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Excel File (.xlsx, .xls)**")
            excel_file = st.file_uploader(
                "Choose primary Excel file",
                type=["xlsx", "xls"],
                key=st.session_state.primary_excel_uploader_key,
                help="Maximum file size: 400MB",
            )

        with col2:
            st.markdown("**PDF File (.pdf)**")
            pdf_file = st.file_uploader(
                "Choose primary PDF file",
                type=["pdf"],
                key=st.session_state.primary_pdf_uploader_key,
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
                st.error(
                    f"PDF file too large: {pdf_size_mb:.1f}MB. Maximum allowed: 400MB"
                )
                return

            # Show file info and set button
            st.success(f"✅ Excel: {excel_file.name} ({excel_size_mb:.1f}MB)")
            st.success(f"✅ PDF: {pdf_file.name} ({pdf_size_mb:.1f}MB)")

            if st.button("🎯 Set as Primary Pair", type="primary"):
                # Save files to temporary locations
                excel_temp_path = save_temp_file(excel_file, "excel")
                pdf_temp_path = save_temp_file(pdf_file, "pdf")

                # Set as primary pair
                st.session_state.primary_pair = {
                    "excel_name": excel_file.name,
                    "pdf_name": pdf_file.name,
                    "excel_path": excel_temp_path,
                    "pdf_path": pdf_temp_path,
                    "excel_size": excel_size_mb,
                    "pdf_size": pdf_size_mb,
                }
                st.success(f"✅ Primary pair set: {excel_file.name} + {pdf_file.name}")
                st.rerun()


def show_additional_pairs_interface():
    """Interface for managing additional file pairs."""
    # Add new additional pair section
    with st.expander(
        "➕ Add Additional File Pair",
        expanded=len(st.session_state.additional_pairs) == 0,
    ):
        add_additional_pair_interface()

    # Display existing additional pairs
    if st.session_state.additional_pairs:
        st.markdown("#### 📋 Additional Pairs")
        display_additional_pairs()
    else:
        st.info(
            "No additional pairs added yet. The primary pair will be processed alone."
        )


def add_additional_pair_interface():
    """Interface for adding an additional file pair."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Excel File (.xlsx, .xls)**")
        excel_file = st.file_uploader(
            "Choose additional Excel file",
            type=["xlsx", "xls"],
            key=st.session_state.additional_excel_uploader_key,
            help="Maximum file size: 400MB",
        )

    with col2:
        st.markdown("**PDF File (.pdf)**")
        pdf_file = st.file_uploader(
            "Choose additional PDF file",
            type=["pdf"],
            key=st.session_state.additional_pdf_uploader_key,
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

        if st.button("➕ Add Additional Pair", type="secondary"):
            # Save files to temporary locations
            excel_temp_path = save_temp_file(excel_file, "excel")
            pdf_temp_path = save_temp_file(pdf_file, "pdf")

            # Add to additional pairs
            pair_info = {
                "excel_name": excel_file.name,
                "pdf_name": pdf_file.name,
                "excel_path": excel_temp_path,
                "pdf_path": pdf_temp_path,
                "excel_size": excel_size_mb,
                "pdf_size": pdf_size_mb,
            }

            st.session_state.additional_pairs.append(pair_info)
            st.success(f"✅ Added additional pair: {excel_file.name} + {pdf_file.name}")
            st.rerun()


def display_additional_pairs():
    """Display the list of additional file pairs."""
    for i, pair in enumerate(st.session_state.additional_pairs):
        with st.container():
            col1, col2, col3 = st.columns([3, 3, 1])

            with col1:
                st.markdown(f"**📊 {pair['excel_name']}**")
                st.caption(f"Size: {pair['excel_size']:.1f}MB")

            with col2:
                st.markdown(f"**📄 {pair['pdf_name']}**")
                st.caption(f"Size: {pair['pdf_size']:.1f}MB")

            with col3:
                if st.button(
                    "🗑️", key=f"remove_additional_{i}", help="Remove this pair"
                ):
                    st.session_state.additional_pairs.pop(i)
                    st.rerun()

        if i < len(st.session_state.additional_pairs) - 1:
            st.markdown("---")

    # Summary
    if st.session_state.additional_pairs:
        total_additional = len(st.session_state.additional_pairs)
        total_size = sum(
            pair["excel_size"] + pair["pdf_size"]
            for pair in st.session_state.additional_pairs
        )

        st.markdown(
            f"**Summary:** {total_additional} additional pairs, {total_size:.1f}MB total"
        )

        if st.button("🗑️ Clear All Additional Pairs", type="secondary"):
            st.session_state.additional_pairs = []
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
    """Process the primary pair and additional pairs using the existing controller."""
    try:
        if not st.session_state.primary_pair:
            st.error("No primary pair selected")
            return

        # Set primary files from primary pair
        primary = st.session_state.primary_pair
        st.session_state.excel_temp_path = primary["excel_path"]
        st.session_state.pdf_temp_path = primary["pdf_path"]

        # Set additional merge pairs
        additional_merge_pairs = [
            (pair["excel_path"], pair["pdf_path"])
            for pair in st.session_state.additional_pairs
        ]
        st.session_state.merge_pairs = additional_merge_pairs

        # Create controller with UI adapter
        controller = AppController(st.session_state.ui_adapter)

        # Show processing status
        total_pairs = 1 + len(additional_merge_pairs)
        with st.spinner(f"Processing {total_pairs} file pairs..."):
            progress_bar = st.progress(0)
            status_container = st.empty()

            # Update progress
            progress_bar.progress(25)
            status_container.text("Validating file pairs...")

            progress_bar.progress(50)
            if total_pairs == 1:
                status_container.text("Processing primary pair...")
            else:
                status_container.text(f"Processing merge of {total_pairs} pairs...")

            controller.process_files()

            progress_bar.progress(100)
            status_container.text("Processing complete!")

    except Exception as e:
        st.error(f"Processing failed: {str(e)}")
        st.session_state.ui_adapter.log_status(f"ERROR: {str(e)}")


def show_reset_ui():
    """Display reset UI and handle reset functionality."""
    st.markdown("---")
    if st.button("🔄 Process New Files", use_container_width=True, type="secondary"):
        clear_file_uploaders()
        st.session_state.show_downloads = False
        st.session_state.primary_pair = None
        st.session_state.additional_pairs = []
        st.session_state.ui_adapter.reset_gui()
        st.rerun()


def handle_post_processing():
    """Handle post-processing workflow: downloads and reset functionality."""
    st.markdown("### 📥 Download Processed Files")

    # Get the base paths from the primary pair
    if not st.session_state.primary_pair:
        st.error("No primary pair available for download")
        return

    primary = st.session_state.primary_pair
    excel_base_path = Path(primary["excel_path"])
    pdf_base_path = Path(primary["pdf_path"])

    # Determine if this was a merge workflow or single file
    is_merge = len(st.session_state.additional_pairs) > 0

    try:
        if is_merge:
            # For merge workflows, files are saved with "_merged" suffix
            excel_output_path = excel_base_path.with_name(
                f"{excel_base_path.stem}_merged{excel_base_path.suffix}"
            )
            pdf_output_path = pdf_base_path.with_name(
                f"{pdf_base_path.stem}_merged{pdf_base_path.suffix}"
            )

            # Get original filenames from primary pair for naming
            primary_excel_name = primary["excel_name"]
            primary_pdf_name = primary["pdf_name"]
            excel_base_name = Path(primary_excel_name).stem
            pdf_base_name = Path(primary_pdf_name).stem

            zip_filename = f"{excel_base_name}_merged.zip"
            excel_zip_name = f"{excel_base_name}_merged.xlsx"
            pdf_zip_name = f"{pdf_base_name}_merged.pdf"
        else:
            # For single file workflows, files are saved to original paths
            excel_output_path = excel_base_path
            pdf_output_path = pdf_base_path
            zip_filename = f"{excel_base_path.stem}_processed.zip"
            excel_zip_name = f"{excel_base_path.stem}_processed.xlsx"
            pdf_zip_name = f"{pdf_base_path.stem}_processed.pdf"

        # Check if both files are available
        excel_available = excel_output_path.exists()
        pdf_available = pdf_output_path.exists()

        if excel_available and pdf_available:
            # Create ZIP file with both processed files
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # Add Excel file
                with open(excel_output_path, "rb") as excel_file:
                    zip_file.writestr(excel_zip_name, excel_file.read())

                # Add PDF file
                with open(pdf_output_path, "rb") as pdf_file:
                    zip_file.writestr(pdf_zip_name, pdf_file.read())

            zip_buffer.seek(0)

            # Create download button with timestamp for uniqueness
            timestamp = int(time.time())
            download_key = f"download_merge_zip_{timestamp}"

            st.download_button(
                label="📦 Download Processed Files (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=zip_filename,
                mime="application/zip",
                use_container_width=True,
                help="Downloads both processed Excel and PDF files in a ZIP archive",
                key=download_key,
                type="primary",
            )

            # Show reset UI
            show_reset_ui()

        else:
            st.error(
                f"Processed files not available for download. Expected files:\n- {excel_output_path}\n- {pdf_output_path}"
            )

    except Exception as e:
        st.error(f"Error preparing download: {e}")


if __name__ == "__main__":
    show_multi_file_merge()
