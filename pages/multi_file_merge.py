#!/usr/bin/env python3
"""
Multi-file merge page for Abstract Renumber Tool.

Handles the workflow for merging multiple Excel/PDF file pairs.
"""

import gc
from pathlib import Path

import pandas as pd
import streamlit as st

from core.app_controller import AppController

from .base_page import BaseStreamlitPage
from .components.downloads import DownloadManager
from .components.file_upload import FileUploadManager
from .components.processing_options import ProcessingOptionsManager
from .components.tabbed_workflow import TabbedWorkflowManager


class MultiFileMergePage(BaseStreamlitPage):
    """Multi-file merge page using shared components."""

    def __init__(self):
        """Initialize the multi-file merge page."""
        super().__init__(page_type="merge")
        self.file_manager = FileUploadManager()
        self.options_manager = ProcessingOptionsManager()
        self.download_manager = DownloadManager()
        self.workflow_manager = TabbedWorkflowManager()

    def show(self):
        """Display the multi-file merge page with native layout."""
        # Use native responsive layout from BaseStreamlitPage
        with self.create_responsive_layout():
            # Show page title and back button
            self.show_page_title("📚 Multi-File Merge")
            self.show_back_to_mode_button("back_to_mode_merge")

            # Show tabbed workflow interface
            self.show_tabbed_workflow()

            # Handle post-processing workflow if processing completed
            if st.session_state.get("show_downloads"):
                self.handle_post_processing()

            # Show status messages
            self.show_status_messages()

    def show_tabbed_workflow(self):
        """Show the tabbed workflow interface for multi-file merge."""
        tab_labels = ["📁 Files", "🔍 Filtering", "⚙️ Options", "🚀 Process"]
        tab_functions = [
            self.show_files_tab,
            self.show_filtering_tab,
            self.show_options_tab,
            self.show_processing_tab,
        ]

        self.workflow_manager.create_workflow_tabs(tab_labels, tab_functions, "merge")

    def show_files_tab(self):
        """Show the files tab with multi-file pair selection."""
        st.markdown("### 📁 File Pairs")
        st.markdown("Select your Excel and PDF file pairs for merging.")

        # Primary pair selection section
        st.markdown("#### 🎯 Primary File Pair")
        st.info(
            "Select the main Excel and PDF files that will serve as the base for merging."
        )

        self.show_primary_pair_interface()

        # Additional pairs section (only show if primary pair is selected)
        if st.session_state.get("primary_pair"):
            st.markdown("---")
            st.markdown("#### ➕ Additional File Pairs")
            st.info("Add more Excel-PDF pairs to merge with the primary pair.")

            self.show_additional_pairs_interface()

            # Show summary
            total_pairs = 1 + len(st.session_state.get("additional_pairs", []))
            if total_pairs == 1:
                st.success("📊 **File Pairs:** 1 (primary only)")
            else:
                additional_count = len(st.session_state.get("additional_pairs", []))
                st.success(
                    f"📊 **File Pairs:** {total_pairs} (1 primary + {additional_count} additional)"
                )

            st.markdown("---")
            self.workflow_manager.show_tab_navigation_help("files")
        else:
            st.info(
                "👆 Please select a primary file pair first, then you can add additional pairs to merge."
            )

    def show_primary_pair_interface(self):
        """Interface for selecting the primary file pair."""
        if st.session_state.get("primary_pair"):
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
                    if st.button(
                        "🔄", key="change_primary", help="Change primary pair"
                    ):
                        st.session_state.primary_pair = None
                        # Clear merge preview cache when primary pair is removed
                        self._clear_merge_cache()
                        st.rerun()
        else:
            # Interface for selecting primary pair
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Excel File (.xlsx, .xls)**")
                excel_file = self.file_manager.create_excel_uploader(
                    key=st.session_state.get(
                        "primary_excel_uploader_key", "primary_excel_0"
                    ),
                    label="Choose primary Excel file",
                    help_text="Maximum file size: 400MB",
                )

            with col2:
                st.markdown("**PDF File (.pdf)**")
                pdf_file = self.file_manager.create_pdf_uploader(
                    key=st.session_state.get(
                        "primary_pdf_uploader_key", "primary_pdf_0"
                    ),
                    label="Choose primary PDF file",
                    help_text="Maximum file size: 400MB",
                )

            if excel_file and pdf_file:
                # Validate file sizes
                excel_valid, excel_error = self.file_manager.validate_file_size(
                    excel_file
                )
                pdf_valid, pdf_error = self.file_manager.validate_file_size(pdf_file)

                if not excel_valid:
                    st.error(excel_error)
                    return

                if not pdf_valid:
                    st.error(pdf_error)
                    return

                # Show file info and set button
                self.file_manager.display_file_info(excel_file, "excel")
                self.file_manager.display_file_info(pdf_file, "pdf")

                if st.button("🎯 Set as Primary Pair", type="primary"):
                    # Save files to temporary locations
                    excel_temp_path = self.file_manager.save_to_temp(
                        excel_file, "excel"
                    )
                    pdf_temp_path = self.file_manager.save_to_temp(pdf_file, "pdf")

                    # Set as primary pair
                    excel_size_mb = len(excel_file.getvalue()) / (1024 * 1024)
                    pdf_size_mb = len(pdf_file.getvalue()) / (1024 * 1024)

                    st.session_state.primary_pair = {
                        "excel_name": excel_file.name,
                        "pdf_name": pdf_file.name,
                        "excel_path": excel_temp_path,
                        "pdf_path": pdf_temp_path,
                        "excel_size": excel_size_mb,
                        "pdf_size": pdf_size_mb,
                    }
                    # Clear merge preview cache when primary pair changes
                    self._clear_merge_cache()
                    st.success(
                        f"✅ Primary pair set: {excel_file.name} + {pdf_file.name}"
                    )
                    st.rerun()

    def show_additional_pairs_interface(self):
        """Interface for managing additional file pairs."""
        # Add new additional pair section
        with st.expander(
            "➕ Add Additional File Pair",
            expanded=len(st.session_state.get("additional_pairs", [])) == 0,
        ):
            self.add_additional_pair_interface()

        # Display existing additional pairs
        if st.session_state.get("additional_pairs"):
            st.markdown("#### 📋 Additional Pairs")
            self.display_additional_pairs()
        else:
            st.info(
                "No additional pairs added yet. The primary pair will be processed alone."
            )

    def add_additional_pair_interface(self):
        """Interface for adding an additional file pair."""
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Excel File (.xlsx, .xls)**")
            excel_file = self.file_manager.create_excel_uploader(
                key=st.session_state.get(
                    "additional_excel_uploader_key", "additional_excel_0"
                ),
                label="Choose additional Excel file",
                help_text="Maximum file size: 400MB",
            )

        with col2:
            st.markdown("**PDF File (.pdf)**")
            pdf_file = self.file_manager.create_pdf_uploader(
                key=st.session_state.get(
                    "additional_pdf_uploader_key", "additional_pdf_0"
                ),
                label="Choose additional PDF file",
                help_text="Maximum file size: 400MB",
            )

        if excel_file and pdf_file:
            # Validate file sizes
            excel_valid, excel_error = self.file_manager.validate_file_size(excel_file)
            pdf_valid, pdf_error = self.file_manager.validate_file_size(pdf_file)

            if not excel_valid:
                st.error(excel_error)
                return

            if not pdf_valid:
                st.error(pdf_error)
                return

            # Show file info and add button
            self.file_manager.display_file_info(excel_file, "excel")
            self.file_manager.display_file_info(pdf_file, "pdf")

            if st.button("➕ Add Additional Pair", type="secondary"):
                # Save files to temporary locations
                excel_temp_path = self.file_manager.save_to_temp(excel_file, "excel")
                pdf_temp_path = self.file_manager.save_to_temp(pdf_file, "pdf")

                # Add to additional pairs
                excel_size_mb = len(excel_file.getvalue()) / (1024 * 1024)
                pdf_size_mb = len(pdf_file.getvalue()) / (1024 * 1024)

                pair_info = {
                    "excel_name": excel_file.name,
                    "pdf_name": pdf_file.name,
                    "excel_path": excel_temp_path,
                    "pdf_path": pdf_temp_path,
                    "excel_size": excel_size_mb,
                    "pdf_size": pdf_size_mb,
                }

                if "additional_pairs" not in st.session_state:
                    st.session_state.additional_pairs = []
                st.session_state.additional_pairs.append(pair_info)
                # Clear merge preview cache when additional pairs change
                self._clear_merge_cache()
                st.success(
                    f"✅ Added additional pair: {excel_file.name} + {pdf_file.name}"
                )
                st.rerun()

    def display_additional_pairs(self):
        """Display the list of additional file pairs."""
        for i, pair in enumerate(st.session_state.get("additional_pairs", [])):
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
                        # Clear merge preview cache when pairs are removed
                        self._clear_merge_cache()
                        st.rerun()

            if i < len(st.session_state.get("additional_pairs", [])) - 1:
                st.markdown("---")

        # Summary and clear all button
        if st.session_state.get("additional_pairs"):
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
                # Clear merge preview cache when all pairs are cleared
                self._clear_merge_cache()
                st.rerun()

    def show_filtering_tab(self):
        """Show the filtering tab content for multi-file merge."""
        if not self.workflow_manager.check_prerequisites_for_tab("filtering", "merge"):
            return

        st.markdown("### 🔍 Data Filtering")
        st.markdown("Configure filtering that will apply to all selected file pairs.")

        # Filter decision
        wants_filtering = st.radio(
            "Would you like to filter the merged data?",
            options=[False, True],
            format_func=lambda x: "📊 No, Process All Data"
            if not x
            else "🔍 Yes, Set Up Filtering",
            key="wants_filtering_merge_radio",
            horizontal=True,
        )

        # Store the decision
        st.session_state.wants_filtering = wants_filtering
        st.session_state.filter_enabled = wants_filtering

        if wants_filtering:
            st.markdown("#### Configure Filter Settings")
            st.info(
                "Filtering will be applied to the merged dataset from all file pairs."
            )

            # Preview merge and show filter configuration
            self.show_merge_filter_configuration()
        else:
            # Clear filter settings if not filtering
            st.session_state.filter_column = None
            st.session_state.filter_values = []
            st.info("✅ All merged data will be processed without filtering.")

        st.markdown("---")
        self.workflow_manager.show_tab_navigation_help("filtering")

    def show_merge_filter_configuration(self):
        """Show filter configuration for merged data by previewing the merge."""
        try:
            # Get merged preview data
            merged_df = self.get_merged_preview_data()

            if merged_df is None or merged_df.empty:
                st.warning(
                    "⚠️ Unable to preview merged data. Please check your file pairs."
                )
                return

            # Show data preview
            with st.expander("📊 Merged Data Preview", expanded=False):
                st.markdown(f"**Total rows:** {len(merged_df)}")
                st.markdown(f"**Columns:** {', '.join(merged_df.columns)}")
                st.dataframe(merged_df.head(10), width="stretch")

            # Get filterable columns (exclude system columns)
            system_columns = {"_include", "Index#", "Document_ID"}
            filterable_columns = [
                col for col in merged_df.columns if col not in system_columns
            ]

            if not filterable_columns:
                st.warning("No suitable columns found for filtering.")
                return

            # Column selection
            filter_column = st.selectbox(
                "Select column to filter by:",
                options=["None"] + filterable_columns,
                key="filter_column_merge_tab",
                help="Choose which column to use for filtering the merged data",
            )

            if filter_column and filter_column != "None":
                # Get unique values for the selected column
                unique_values = sorted(
                    merged_df[filter_column].dropna().unique().astype(str)
                )

                # Value selection
                filter_values = st.multiselect(
                    f"Select values to include from '{filter_column}':",
                    options=unique_values,
                    key="filter_values_merge_tab",
                    help="Choose which values to include. Only rows with these values will be processed.",
                )

                # Store filter settings
                st.session_state.filter_column = filter_column
                st.session_state.filter_values = filter_values

                if filter_values:
                    # Show preview of filtered data
                    filtered_count = merged_df[
                        merged_df[filter_column].isin(filter_values)
                    ].shape[0]
                    total_count = merged_df.shape[0]
                    st.success(
                        f"✅ Filter configured: {filtered_count}/{total_count} rows will be processed"
                    )

                    # Show filtered data preview
                    with st.expander("🔍 Filtered Data Preview", expanded=False):
                        filtered_df = merged_df[
                            merged_df[filter_column].isin(filter_values)
                        ]
                        st.dataframe(filtered_df.head(10), width="stretch")
                else:
                    st.info("Select values to see filtering preview.")
            else:
                # Clear filter settings if no column selected
                st.session_state.filter_column = None
                st.session_state.filter_values = []

        except Exception as e:
            st.error(f"Error loading merged data preview: {str(e)}")
            st.session_state.filter_column = None
            st.session_state.filter_values = []

    def get_merged_preview_data(self):
        """Get a preview of the merged Excel data from all file pairs."""
        try:
            # Check if we have the required data
            if not st.session_state.get("primary_pair"):
                return None

            # Use caching to avoid reloading data unnecessarily
            cache_key = self._get_merge_cache_key()
            if st.session_state.get("merged_preview_cache_key") == cache_key:
                return st.session_state.get("merged_preview_data")

            # Collect all Excel file paths
            excel_files = []

            # Add primary pair
            primary = st.session_state.primary_pair
            excel_files.append(primary["excel_path"])

            # Add additional pairs
            for pair in st.session_state.get("additional_pairs", []):
                excel_files.append(pair["excel_path"])

            # Load and merge Excel files
            merged_dfs = []
            for excel_path in excel_files:
                try:
                    # Use the same Excel repo as the pipeline
                    from adapters.excel_repo import ExcelOpenpyxlRepo

                    excel_repo = ExcelOpenpyxlRepo()

                    # Get available sheet names and use appropriate sheet
                    available_sheets = excel_repo.get_sheet_names(excel_path)
                    sheet_name = (
                        "Sheet"
                        if "Sheet" in available_sheets
                        else available_sheets[0]
                        if available_sheets
                        else "Sheet"
                    )

                    df = excel_repo.load(excel_path, sheet=sheet_name)
                    if not df.empty:
                        merged_dfs.append(df)

                except Exception as e:
                    st.warning(f"Could not load {excel_path}: {str(e)}")
                    continue

            if not merged_dfs:
                return None

            # Merge all DataFrames
            if len(merged_dfs) == 1:
                merged_df = merged_dfs[0]
            else:
                # Concatenate all DataFrames
                merged_df = pd.concat(merged_dfs, ignore_index=True, sort=False)

            # Cache the result
            st.session_state.merged_preview_cache_key = cache_key
            st.session_state.merged_preview_data = merged_df

            return merged_df

        except Exception as e:
            st.error(f"Error creating merged preview: {str(e)}")
            return None

    def _get_merge_cache_key(self):
        """Generate a cache key based on current file pairs."""
        key_parts = []

        # Add primary pair
        if st.session_state.get("primary_pair"):
            primary = st.session_state.primary_pair
            key_parts.append(f"{primary['excel_path']}:{primary['excel_size']}")

        # Add additional pairs
        for pair in st.session_state.get("additional_pairs", []):
            key_parts.append(f"{pair['excel_path']}:{pair['excel_size']}")

        return "|".join(key_parts)

    def _clear_merge_cache(self):
        """Clear the merged preview data cache."""
        if "merged_preview_cache_key" in st.session_state:
            del st.session_state.merged_preview_cache_key
        if "merged_preview_data" in st.session_state:
            del st.session_state.merged_preview_data

    def show_options_tab(self):
        """Show the processing options tab content for multi-file merge."""
        if not self.workflow_manager.check_prerequisites_for_tab("options", "merge"):
            return

        # Use the options manager to render the tab content
        options = self.options_manager.render_tab_options("merge")

        # Show summary
        self.options_manager.display_options_summary(options)

        st.markdown("---")
        self.workflow_manager.show_tab_navigation_help("options")

    def show_processing_tab(self):
        """Show the processing tab content for multi-file merge."""
        if not self.workflow_manager.check_prerequisites_for_tab("process", "merge"):
            return

        st.markdown("### 🚀 Ready to Process")
        st.markdown("Review your settings and start processing all file pairs.")

        # Show comprehensive summary
        self.show_processing_summary()

        # Process button
        if st.button("🚀 Process All File Pairs", type="primary", width="stretch"):
            self.process_merge_files()
            st.session_state.show_downloads = True

    def show_processing_summary(self):
        """Show a comprehensive processing summary for merge workflow."""
        summary_parts = []

        # File pairs summary
        total_pairs = 1 + len(st.session_state.get("additional_pairs", []))
        if total_pairs == 1:
            summary_parts.append("**File Pairs:** 1 (primary only)")
        else:
            additional_count = len(st.session_state.get("additional_pairs", []))
            summary_parts.append(
                f"**File Pairs:** {total_pairs} (1 primary + {additional_count} additional)"
            )

        # Filter summary
        if st.session_state.get("wants_filtering"):
            summary_parts.append("**Filtering:** Will be applied to merged data")
        else:
            summary_parts.append("**Filtering:** Process all merged data")

        # Processing options summary
        sort_enabled = st.session_state.get("sort_bookmarks_enabled_merge", True)
        reorder_enabled = st.session_state.get("reorder_pages_enabled_merge", True)
        check_enabled = st.session_state.get(
            "check_document_images_enabled_merge", True
        )

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

    def process_merge_files(self):
        """Process the primary pair and additional pairs using the existing controller."""
        try:
            if not st.session_state.get("primary_pair"):
                st.error("No primary pair selected")
                return

            # Set primary files from primary pair
            primary = st.session_state.primary_pair
            st.session_state.excel_temp_path = primary["excel_path"]
            st.session_state.pdf_temp_path = primary["pdf_path"]

            # Set additional merge pairs
            additional_merge_pairs = [
                (pair["excel_path"], pair["pdf_path"])
                for pair in st.session_state.get("additional_pairs", [])
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

                # Explicitly delete controller to release memory
                # The controller holds references to the pipeline context which contains
                # large PdfWriter objects and DataFrames
                del controller

                progress_bar.progress(100)
                status_container.text("Processing complete!")

            # Aggressive memory cleanup
            # Force multiple garbage collection cycles to ensure all objects are freed
            # This is necessary because Python's GC may not immediately free large objects
            for _ in range(3):
                gc.collect()

            self.show_processing_complete_message()

        except Exception as e:
            self.show_processing_error(str(e))

    def handle_post_processing(self):
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
        is_merge = len(st.session_state.get("additional_pairs", [])) > 0

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
                # Use download manager to create ZIP and show download button
                excel_data = self.download_manager.read_file_safely(
                    str(excel_output_path)
                )
                pdf_data = self.download_manager.read_file_safely(str(pdf_output_path))

                zip_buffer = self.download_manager.create_download_zip(
                    excel_data, pdf_data, excel_zip_name, pdf_zip_name
                )

                self.download_manager.show_download_button(
                    zip_buffer.getvalue(), zip_filename, excel_zip_name, pdf_zip_name
                )

                # Show reset UI
                self.show_reset_ui()
            else:
                st.error(
                    f"Processed files not available for download. Expected files:\n- {excel_output_path}\n- {pdf_output_path}"
                )

        except Exception as e:
            st.error(f"Error preparing download: {e}")

    def show_reset_ui(self):
        """Display reset UI and handle reset functionality."""
        st.markdown("---")
        if st.button("🔄 Process New Files", width="stretch", type="secondary"):
            self.reset_workflow()
            st.session_state.show_downloads = False
            st.session_state.primary_pair = None
            st.session_state.additional_pairs = []


def show_multi_file_merge():
    """Display the multi-file merge page."""
    page = MultiFileMergePage()
    page.show()


if __name__ == "__main__":
    show_multi_file_merge()
