#!/usr/bin/env python3
"""
Single file processing page for Abstract Renumber Tool.

Handles the workflow for processing one Excel file and one PDF file.
"""

import gc
import os

import psutil
import streamlit as st

from adapters.excel_repo import ExcelOpenpyxlRepo
from core.app_controller import AppController

from .base_page import BaseStreamlitPage
from .components.downloads import DownloadManager
from .components.file_upload import FileUploadManager
from .components.processing_options import ProcessingOptionsManager
from .components.tabbed_workflow import TabbedWorkflowManager


class SingleFileProcessingPage(BaseStreamlitPage):
    """Single file processing page using shared components."""

    def __init__(self):
        """Initialize the single file processing page."""
        super().__init__(page_type="single")
        self.file_manager = FileUploadManager()
        self.options_manager = ProcessingOptionsManager()
        self.download_manager = DownloadManager()
        self.workflow_manager = TabbedWorkflowManager()

    def show(self):
        """Display the single file processing page with native layout."""
        # Use native responsive layout from BaseStreamlitPage
        with self.create_responsive_layout():
            # Show page title and back button
            self.show_page_title("📄 Single File Processing")
            self.show_back_to_mode_button("back_to_mode")

            # Show tabbed workflow interface
            self.show_tabbed_workflow()

            # Handle post-processing workflow if processing completed
            if st.session_state.get("show_downloads"):
                self.handle_post_processing()

            # Show status messages
            self.show_status_messages()

    def show_tabbed_workflow(self):
        """Show the tabbed workflow interface."""
        tab_labels = ["📁 Files", "🔍 Filtering", "⚙️ Options", "🚀 Process"]
        tab_functions = [
            self.show_file_upload_tab,
            self.show_filtering_tab,
            self.show_options_tab,
            self.show_processing_tab,
        ]

        self.workflow_manager.create_workflow_tabs(tab_labels, tab_functions, "single")

    def show_file_upload_tab(self):
        """Show the file upload tab content."""
        st.markdown("### 📁 Upload Files")
        st.markdown("Upload your Excel and PDF files to get started.")

        # File upload widgets
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Excel File (.xlsx, .xls)**")
            uploaded_excel = self.file_manager.create_excel_uploader(
                key=st.session_state.get("excel_uploader_key", "excel_uploader_0"),
                help_text="Upload your Excel file containing the data to process",
            )

        with col2:
            st.markdown("**PDF File (.pdf)**")
            uploaded_pdf = self.file_manager.create_pdf_uploader(
                key=st.session_state.get("pdf_uploader_key", "pdf_uploader_0"),
                help_text="Upload your PDF file to be processed",
            )

        # Handle uploaded files
        if uploaded_excel:
            is_valid, error_msg = self.file_manager.validate_file_size(uploaded_excel)
            if not is_valid:
                st.error(error_msg)
            else:
                # Save to temp file using UI adapter (writes to /tmp)
                # NO LONGER storing UploadedFile in session state - it's 253MB+ of wasted RAM!
                # The file is on disk at /tmp, we only need the path
                st.session_state.ui_adapter.save_uploaded_file(uploaded_excel, "excel")

        if uploaded_pdf:
            is_valid, error_msg = self.file_manager.validate_file_size(uploaded_pdf)
            if not is_valid:
                st.error(error_msg)
            else:
                # Save to temp file using UI adapter (writes to /tmp)
                # NO LONGER storing UploadedFile in session state - it's 253MB+ of wasted RAM!
                # The file is on disk at /tmp, we only need the path
                st.session_state.ui_adapter.save_uploaded_file(uploaded_pdf, "pdf")

        # Show upload status
        if uploaded_excel and uploaded_pdf:
            st.success("✅ Files uploaded successfully!")

            col1, col2 = st.columns(2)
            with col1:
                self.file_manager.display_file_info(uploaded_excel, "excel")
            with col2:
                self.file_manager.display_file_info(uploaded_pdf, "pdf")

            st.markdown("---")
            self.workflow_manager.show_tab_navigation_help("files")
        elif uploaded_excel or uploaded_pdf:
            st.warning("⚠️ Please upload both Excel and PDF files to continue.")
        else:
            st.info("📤 Please select your files using the uploaders above.")

    def show_filtering_tab(self):
        """Show the filtering tab content."""
        if not self.workflow_manager.check_prerequisites_for_tab("filtering", "single"):
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
        self.workflow_manager.show_tab_navigation_help("filtering")

    def show_options_tab(self):
        """Show the processing options tab content."""
        if not self.workflow_manager.check_prerequisites_for_tab("options", "single"):
            return

        # Use the options manager to render the tab content
        options = self.options_manager.render_tab_options("single")

        # Show summary
        self.options_manager.display_options_summary(options)

        st.markdown("---")
        self.workflow_manager.show_tab_navigation_help("options")

    def show_processing_tab(self):
        """Show the processing tab content."""
        if not self.workflow_manager.check_prerequisites_for_tab("process", "single"):
            return

        st.markdown("### 🚀 Ready to Process")
        st.markdown("Review your settings and start processing.")

        # Show comprehensive summary
        self.show_processing_summary()

        # Process button
        if st.button("🚀 Process Files", type="primary", width="stretch"):
            self.process_files()
            st.session_state.show_downloads = True

    def show_processing_summary(self):
        """Show a comprehensive processing summary."""
        summary_parts = []

        # Filter summary
        if st.session_state.get("wants_filtering"):
            filter_column = st.session_state.get("filter_column")
            filter_values = st.session_state.get("filter_values", [])
            if filter_column and filter_values:
                summary_parts.append(
                    f"**Filtering:** {filter_column} = {filter_values}"
                )
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

    def process_files(self):
        """Process the uploaded files using the existing controller."""
        try:
            # Get memory info helper
            process = psutil.Process(os.getpid())

            # Log memory BEFORE processing
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
            print(f"\n{'=' * 60}")
            print(f"MEMORY BEFORE PROCESSING: {mem_before:.2f} MB")
            print(f"{'=' * 60}\n")

            # Create controller with UI adapter
            controller = AppController(st.session_state.ui_adapter)

            # Show simple processing status
            with st.spinner("Processing files..."):
                # Process files
                controller.process_files()

                # Log memory AFTER processing, BEFORE cleanup
                mem_after_processing = process.memory_info().rss / 1024 / 1024
                print(f"\n{'=' * 60}")
                print(f"MEMORY AFTER PROCESSING: {mem_after_processing:.2f} MB")
                print(f"MEMORY INCREASE: +{mem_after_processing - mem_before:.2f} MB")
                print(f"{'=' * 60}\n")

                # Explicitly delete controller to release memory
                del controller

                # Log memory after deleting controller
                mem_after_del = process.memory_info().rss / 1024 / 1024
                print(
                    f"MEMORY AFTER del controller: {mem_after_del:.2f} MB (change: {mem_after_del - mem_after_processing:+.2f} MB)"
                )

            # Clear ALL uploaded file objects from session state
            # Streamlit stores uploaded files under multiple keys:
            # 1. Widget keys (e.g., "excel_uploader_0", "pdf_uploader_0")
            # 2. Custom keys (e.g., "uploaded_excel", "uploaded_pdf")
            keys_to_clear = []
            for key in list(st.session_state.keys()):
                obj = st.session_state.get(key)
                # Check if it's an UploadedFile object
                if hasattr(obj, "getvalue") and hasattr(obj, "name"):
                    keys_to_clear.append(key)
                # Also clear known uploaded file keys
                elif "uploaded" in key.lower() and (
                    "_file" in key or key in ["uploaded_excel", "uploaded_pdf"]
                ):
                    keys_to_clear.append(key)

            for key in keys_to_clear:
                if key in st.session_state:
                    try:
                        # Log the size if possible
                        obj = st.session_state[key]
                        if hasattr(obj, "getvalue"):
                            size_mb = len(obj.getvalue()) / 1024 / 1024
                            print(f"Clearing uploaded file: {key} ({size_mb:.2f} MB)")
                        else:
                            print(f"Clearing uploaded file: {key}")
                        del st.session_state[key]
                    except:
                        pass

            # Aggressive memory cleanup
            for _ in range(3):
                gc.collect()

            # Log memory after garbage collection
            mem_after_gc = process.memory_info().rss / 1024 / 1024
            print(
                f"MEMORY AFTER gc.collect(): {mem_after_gc:.2f} MB (change: {mem_after_gc - mem_after_del:+.2f} MB)"
            )

            # Check what's in session state
            print(f"\nSESSION STATE KEYS: {list(st.session_state.keys())}")

            # Analyze ALL objects in session state for memory usage
            print("\nANALYZING ALL SESSION STATE OBJECTS:")
            for key in st.session_state.keys():
                try:
                    obj = st.session_state[key]
                    obj_type = type(obj).__name__
                    size_mb = sys.getsizeof(obj) / 1024 / 1024

                    # For UploadedFile objects, check actual data size
                    if hasattr(obj, "getvalue"):
                        try:
                            actual_size_mb = len(obj.getvalue()) / 1024 / 1024
                            print(
                                f"  - {key}: {obj_type}, sys.getsizeof={size_mb:.2f} MB, ACTUAL DATA={actual_size_mb:.2f} MB ⚠️"
                            )
                        except:
                            print(
                                f"  - {key}: {obj_type}, sys.getsizeof={size_mb:.2f} MB"
                            )
                    elif size_mb > 0.1:  # Show objects > 100KB
                        print(f"  - {key}: {obj_type}, {size_mb:.2f} MB")
                except Exception:
                    pass  # Silently skip errors

            print(f"\n{'=' * 60}")
            print(f"TOTAL MEMORY FREED: {mem_after_processing - mem_after_gc:.2f} MB")
            print(f"MEMORY STILL LEAKED: {mem_after_gc - mem_before:.2f} MB")
            print(f"FINAL MEMORY: {mem_after_gc:.2f} MB")
            print(f"{'=' * 60}\n")

            self.show_processing_complete_message()

        except Exception as e:
            self.show_processing_error(str(e))

    def handle_post_processing(self):
        """Handle post-processing workflow: downloads and reset functionality."""
        st.markdown("### 📥 Download Processed Files")

        # Get file paths
        excel_path = st.session_state.get("excel_temp_path")
        pdf_path = st.session_state.get("pdf_temp_path")

        if not excel_path or not pdf_path:
            st.error("Processed files not available for download")
            return

        try:
            # Prepare download files using download manager
            zip_data, zip_filename, excel_name, pdf_name = (
                self.download_manager.prepare_download_files(
                    excel_path,
                    pdf_path,
                    "uploaded_excel",
                    "uploaded_pdf",
                    is_merge=False,
                )
            )

            # Show download button
            self.download_manager.show_download_button(
                zip_data, zip_filename, excel_name, pdf_name
            )

            # Show reset UI
            self.show_reset_ui()

        except Exception as e:
            st.error(f"Error preparing download: {e}")

    def show_reset_ui(self):
        """Display reset UI and handle reset functionality."""
        import os

        import psutil

        st.markdown("---")
        if st.button(
            "🔄 Process New Files",
            key="reset_single_workflow",
            type="secondary",
        ):
            process = psutil.Process(os.getpid())
            mem_before_reset_click = process.memory_info().rss / 1024 / 1024
            print(f"\n{'=' * 60}")
            print("[RESET BUTTON] ✓ User clicked Reset button!")
            print(
                f"[RESET BUTTON] Memory at button click: {mem_before_reset_click:.2f} MB"
            )
            print(f"{'=' * 60}\n")

            self.reset_workflow_state()

            mem_after_workflow_reset = process.memory_info().rss / 1024 / 1024
            print(
                f"[RESET BUTTON] Memory after reset_workflow_state(): {mem_after_workflow_reset:.2f} MB"
            )

            # Force complete page reload to clear Streamlit's internal file cache
            print("[RESET BUTTON] Calling st.rerun() to force page reload...")
            st.rerun()

    def reset_workflow_state(self):
        """Reset all workflow state for a fresh start."""
        self.reset_workflow()
        st.session_state.show_downloads = False


def show_single_file_processing():
    """Display the single file processing page."""
    page = SingleFileProcessingPage()
    page.show()


# Keep the filter configuration content function as it's still used
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


if __name__ == "__main__":
    show_single_file_processing()
