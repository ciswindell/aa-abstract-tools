#!/usr/bin/env python3
"""
Session state management components for Abstract Renumber Tool Streamlit interface.

Contains shared session state utility functions to eliminate duplication
and provide consistent state management patterns across different pages.
"""

import gc
import os
import time
from typing import Optional

import psutil
import streamlit as st


class SessionStateManager:
    """Manages session state initialization and utilities."""

    def __init__(self) -> None:
        """Initialize the SessionStateManager."""
        pass

    def initialize_common_state(self) -> None:
        """Initialize common session state variables used across pages."""
        # UI adapter
        if "ui_adapter" not in st.session_state:
            from adapters.ui_streamlit import StreamlitUIAdapter

            st.session_state.ui_adapter = StreamlitUIAdapter()

        # File paths for single file processing (not UploadedFile objects!)
        # We only store temp file paths, not the 500MB UploadedFile objects
        if "excel_temp_path" not in st.session_state:
            st.session_state.excel_temp_path = None
        if "pdf_temp_path" not in st.session_state:
            st.session_state.pdf_temp_path = None

        # Processing state
        if "show_downloads" not in st.session_state:
            st.session_state.show_downloads = False

        # Status messages
        if "status_messages" not in st.session_state:
            st.session_state.status_messages = []

    def initialize_uploader_keys(self, page_type: str = "single") -> None:
        """Initialize file uploader keys for clearing functionality.

        Args:
            page_type: Type of page ('single' or 'merge') for key differentiation
        """
        if page_type == "single":
            if "excel_uploader_key" not in st.session_state:
                st.session_state.excel_uploader_key = "excel_uploader_0"
            if "pdf_uploader_key" not in st.session_state:
                st.session_state.pdf_uploader_key = "pdf_uploader_0"
        elif page_type == "merge":
            # Primary pair keys
            if "primary_excel_uploader_key" not in st.session_state:
                st.session_state.primary_excel_uploader_key = "primary_excel_0"
            if "primary_pdf_uploader_key" not in st.session_state:
                st.session_state.primary_pdf_uploader_key = "primary_pdf_0"

            # Additional pair keys
            if "additional_excel_uploader_key" not in st.session_state:
                st.session_state.additional_excel_uploader_key = "additional_excel_0"
            if "additional_pdf_uploader_key" not in st.session_state:
                st.session_state.additional_pdf_uploader_key = "additional_pdf_0"

    def initialize_processing_options(self) -> None:
        """Initialize processing option defaults."""
        if "sort_bookmarks_enabled" not in st.session_state:
            st.session_state.sort_bookmarks_enabled = True
        if "reorder_pages_enabled" not in st.session_state:
            st.session_state.reorder_pages_enabled = True
        if "check_document_images_enabled" not in st.session_state:
            st.session_state.check_document_images_enabled = True

    def initialize_filtering_state(self) -> None:
        """Initialize filtering-related state variables."""
        if "wants_filtering" not in st.session_state:
            st.session_state.wants_filtering = False
        if "filter_enabled" not in st.session_state:
            st.session_state.filter_enabled = False
        if "filter_column" not in st.session_state:
            st.session_state.filter_column = None
        if "filter_values" not in st.session_state:
            st.session_state.filter_values = []

    def initialize_merge_state(self) -> None:
        """Initialize merge workflow specific state variables."""
        if "primary_pair" not in st.session_state:
            st.session_state.primary_pair = None
        if "additional_pairs" not in st.session_state:
            st.session_state.additional_pairs = []
        if "merge_pairs" not in st.session_state:
            st.session_state.merge_pairs = None

    def clear_file_uploaders(self, page_type: str = "single") -> None:
        """Clear file uploaders by rotating their keys.

        Args:
            page_type: Type of page ('single' or 'merge') for key differentiation
        """
        timestamp = int(time.time() * 1000)  # Use milliseconds for uniqueness

        if page_type == "single":
            st.session_state.excel_uploader_key = f"excel_uploader_{timestamp}"
            st.session_state.pdf_uploader_key = f"pdf_uploader_{timestamp + 1}"
        elif page_type == "merge":
            st.session_state.primary_excel_uploader_key = f"primary_excel_{timestamp}"
            st.session_state.primary_pdf_uploader_key = f"primary_pdf_{timestamp + 1}"
            st.session_state.additional_excel_uploader_key = (
                f"additional_excel_{timestamp + 2}"
            )
            st.session_state.additional_pdf_uploader_key = (
                f"additional_pdf_{timestamp + 3}"
            )

    def reset_workflow_state(self, page_type: str = "single") -> None:
        """Reset workflow state for a fresh start.

        Args:
            page_type: Type of page ('single' or 'merge') for appropriate reset
        """
        # Get memory info helper
        process = psutil.Process(os.getpid())
        mem_before_reset = process.memory_info().rss / 1024 / 1024  # MB
        print(f"\n{'=' * 60}")
        print(f"MEMORY BEFORE RESET: {mem_before_reset:.2f} MB")
        print(f"{'=' * 60}\n")

        # Clear file uploaders
        self.clear_file_uploaders(page_type)

        # Reset common state
        st.session_state.show_downloads = False

        # Reset filter settings
        st.session_state.wants_filtering = False
        st.session_state.filter_enabled = False
        st.session_state.filter_column = None
        st.session_state.filter_values = []

        # Reset processing options to defaults
        st.session_state.sort_bookmarks_enabled = True
        st.session_state.reorder_pages_enabled = True
        st.session_state.check_document_images_enabled = True

        # Reset merge-specific state if needed
        if page_type == "merge":
            st.session_state.primary_pair = None
            st.session_state.additional_pairs = []
            st.session_state.merge_pairs = None

            # NOTE: File uploader keys regeneration doesn't work because Streamlit's
            # MediaFileManager is per-session and holds ALL uploaded files.
            # The only way to clear them is to end the session (close browser tab)
            # or use a hack to clear all session state keys (which we do below)

        # Memory cleanup: Remove large objects from session state
        try:
            # Clear large DataFrames and cached data
            large_objects_to_clear = [
                "merged_preview_data",  # Multi-file merge preview cache
                "processed_excel_data",  # Processed Excel data
                "processed_pdf_data",  # Processed PDF data
                "pipeline_context",  # Pipeline context with PDF objects
                "final_pdf",  # Final PDF writer objects
                "pdf_writer",  # Any PDF writer objects
                "excel_dataframe",  # Large Excel DataFrames
                "preview_dataframe",  # Preview DataFrames
                "download_ui_rendered",  # Reset download UI flag
            ]

            for obj_key in large_objects_to_clear:
                if obj_key in st.session_state:
                    del st.session_state[obj_key]
                    print(f"Memory cleanup: Cleared {obj_key} from session state")

            # Clean up temporary input files (os is already imported at top of file)

            # Clean up single-file processing temp files
            temp_paths_to_clean = ["excel_temp_path", "pdf_temp_path"]
            for path_key in temp_paths_to_clean:
                if path_key in st.session_state and st.session_state[path_key]:
                    try:
                        if os.path.exists(st.session_state[path_key]):
                            os.unlink(st.session_state[path_key])
                            print(
                                f"Memory cleanup: Deleted temp file {st.session_state[path_key]}"
                            )
                    except Exception as file_err:
                        print(
                            f"Memory cleanup: Could not delete {st.session_state[path_key]}: {file_err}"
                        )

            # Clean up multi-file merge temp files
            if "primary_pair" in st.session_state and st.session_state.primary_pair:
                for path_key in ["excel_path", "pdf_path"]:
                    if path_key in st.session_state.primary_pair:
                        file_path = st.session_state.primary_pair[path_key]
                        if file_path:
                            try:
                                if os.path.exists(file_path):
                                    os.unlink(file_path)
                                    print(
                                        f"Memory cleanup: Deleted primary pair temp file {file_path}"
                                    )
                            except Exception as file_err:
                                print(
                                    f"Memory cleanup: Could not delete {file_path}: {file_err}"
                                )

            if (
                "additional_pairs" in st.session_state
                and st.session_state.additional_pairs
            ):
                for i, pair in enumerate(st.session_state.additional_pairs):
                    for path_key in ["excel_path", "pdf_path"]:
                        if path_key in pair:
                            file_path = pair[path_key]
                            if file_path:
                                try:
                                    if os.path.exists(file_path):
                                        os.unlink(file_path)
                                        print(
                                            f"Memory cleanup: Deleted additional pair {i} temp file {file_path}"
                                        )
                                except Exception as file_err:
                                    print(
                                        f"Memory cleanup: Could not delete {file_path}: {file_err}"
                                    )
        except Exception as e:
            print(f"Memory cleanup warning: {e}")

        # Clear ALL uploaded file objects AND download button caches from session state
        print("\n[RESET] Scanning for uploaded file objects and download caches...")
        keys_to_clear = []
        for key in list(st.session_state.keys()):
            obj = st.session_state.get(key)
            # Check if it's an UploadedFile object
            if hasattr(obj, "getvalue") and hasattr(obj, "name"):
                keys_to_clear.append(key)
            # Check if it's a download cache (keys starting with "download_")
            elif key.startswith("download_"):
                keys_to_clear.append(key)
            # Check if it's a file uploader widget key
            elif "uploader" in key.lower() or "uploaded" in key.lower():
                keys_to_clear.append(key)
            # Check if it's a FormSubmitter (download button internal state)
            elif "FormSubmitter:" in str(type(obj)):
                keys_to_clear.append(key)

        for key in keys_to_clear:
            if key in st.session_state:
                try:
                    obj = st.session_state[key]
                    if hasattr(obj, "getvalue"):
                        import sys

                        size_mb = len(obj.getvalue()) / 1024 / 1024
                        print(
                            f"[RESET] Clearing uploaded file: {key} ({size_mb:.2f} MB)"
                        )
                    elif key.startswith("download_zip_"):
                        # Download ZIP caches are stored as bytes
                        import sys

                        size_mb = sys.getsizeof(obj) / 1024 / 1024
                        print(
                            f"[RESET] Clearing download ZIP cache: {key} ({size_mb:.2f} MB)"
                        )
                    else:
                        print(f"[RESET] Clearing: {key}")
                    del st.session_state[key]
                except:
                    pass

        # Clear Streamlit's cache to release cached ZIP files
        # This is CRITICAL for releasing the ~1GB ZIP files created for downloads
        print("\n[RESET] Clearing Streamlit cache (ZIP files)...")
        try:
            st.cache_data.clear()
            print("[RESET] Streamlit cache cleared successfully")
        except Exception as cache_err:
            print(f"[RESET] Warning: Could not clear Streamlit cache: {cache_err}")

        # Trigger garbage collection after cleanup
        mem_before_gc = process.memory_info().rss / 1024 / 1024

        # Force clear Python module caches that might hold references
        try:
            import sys

            import pypdf

            # Clear any module-level caches
            if hasattr(pypdf, "_cache"):
                del pypdf._cache
            if hasattr(pypdf.PdfReader, "_cache"):
                pypdf.PdfReader._cache = {}
            if hasattr(pypdf.PdfWriter, "_cache"):
                pypdf.PdfWriter._cache = {}
            print("[RESET] Cleared pypdf module caches")
        except Exception as e:
            print(f"[RESET] Could not clear pypdf caches: {e}")

        for _ in range(5):  # Increased from 3 to 5
            gc.collect()
        mem_after_gc = process.memory_info().rss / 1024 / 1024

        print(
            f"\n[RESET] MEMORY AFTER gc.collect(): {mem_after_gc:.2f} MB (change: {mem_after_gc - mem_before_gc:+.2f} MB)"
        )

        # Force Python to release memory back to OS (Linux only)
        # This is necessary because Python's allocator holds freed memory in its heap
        # malloc_trim(0) forces glibc to release unused memory back to the kernel
        try:
            import ctypes

            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
            mem_after_trim = process.memory_info().rss / 1024 / 1024
            print(
                f"[RESET] MEMORY AFTER malloc_trim(): {mem_after_trim:.2f} MB (freed: {mem_after_gc - mem_after_trim:.2f} MB)"
            )
        except Exception as trim_err:
            print(f"[RESET] malloc_trim not available (non-Linux?): {trim_err}")

        # Analyze what's still in session state
        print(f"\n[RESET] SESSION STATE KEYS: {list(st.session_state.keys())}")
        print("\n[RESET] ANALYZING ALL SESSION STATE OBJECTS:")
        import sys

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
                        print(f"  - {key}: {obj_type}, sys.getsizeof={size_mb:.2f} MB")
                elif size_mb > 0.1:  # Show objects > 100KB
                    print(f"  - {key}: {obj_type}, {size_mb:.2f} MB")
            except Exception:
                pass  # Silently skip errors

        print(f"\n{'=' * 60}")
        print(
            f"[RESET] TOTAL MEMORY FREED BY RESET: {mem_before_reset - mem_after_gc:.2f} MB"
        )
        print(f"[RESET] FINAL MEMORY AFTER RESET: {mem_after_gc:.2f} MB")
        print(f"{'=' * 60}\n")

        # CRITICAL FIX: Force file uploaders to release memory by changing their keys
        # Per Streamlit docs: uploaded files stay in RAM until tab closes OR uploader key changes
        # Changing keys forces Streamlit to drop the old uploader's cached files
        print("[RESET] Regenerating file uploader keys to force file cache clear...")
        import uuid

        uploader_keys = [
            "primary_excel_uploader_key",
            "primary_pdf_uploader_key",
            "additional_excel_uploader_key",
            "additional_pdf_uploader_key",
        ]
        for key in uploader_keys:
            new_key_value = str(uuid.uuid4())
            st.session_state[key] = new_key_value
            print(f"[RESET] Regenerated {key} = {new_key_value}")

        # CRITICAL: Completely wipe session state to force Streamlit to clear MediaFileManager
        # This is the ONLY way to clear uploaded file data from Streamlit's internal cache
        # We must preserve ui_adapter as it's needed for the next run
        print("[RESET] Performing complete session state wipe to clear file cache...")
        ui_adapter_backup = st.session_state.get("ui_adapter")

        # Backup the new uploader keys we just generated
        uploader_keys_backup = {key: st.session_state.get(key) for key in uploader_keys}

        # Delete ALL keys (this triggers Streamlit's internal cleanup)
        keys_to_delete = list(st.session_state.keys())
        for key in keys_to_delete:
            try:
                del st.session_state[key]
            except:
                pass

        # Restore essential state
        if ui_adapter_backup is not None:
            st.session_state.ui_adapter = ui_adapter_backup

        # Restore the new uploader keys
        for key, value in uploader_keys_backup.items():
            if value is not None:
                st.session_state[key] = value

        print(f"[RESET] Wiped {len(keys_to_delete)} session state keys")
        print("[RESET] Restored uploader keys with new UUIDs for fresh file uploaders")
        print("[RESET] Session state wipe complete - ready for fresh run")

    def get_current_step_info(self) -> Optional[str]:
        """Get information about the current workflow step.

        Returns:
            String describing current step or None if not in progress
        """
        if st.session_state.get("filter_decision_made"):
            if st.session_state.get("wants_filtering") and not st.session_state.get(
                "filter_configured"
            ):
                return "📍 **Current Step:** Filter Configuration"
            elif not st.session_state.get("processing_options_decided"):
                return "📍 **Current Step:** Processing Options"
            elif st.session_state.get("processing_options_decided"):
                return "📍 **Current Step:** Ready to Process"
        elif st.session_state.get("excel_temp_path") and st.session_state.get(
            "pdf_temp_path"
        ):
            return "📍 **Current Step:** Filter Decision"

        return None

    # REMOVED: store_uploaded_files() - we no longer store 500MB UploadedFile objects
    # in session state. Files are written to /tmp immediately and we only store paths.
