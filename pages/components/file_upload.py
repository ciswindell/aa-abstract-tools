#!/usr/bin/env python3
"""
File upload components for Abstract Renumber Tool Streamlit interface.

Contains shared file upload widgets and validation logic to eliminate
duplication across different pages.
"""

import tempfile
from typing import Optional, Tuple

import streamlit as st


class FileUploadManager:
    """Manages file upload widgets and validation."""

    def __init__(self) -> None:
        """Initialize the FileUploadManager."""
        pass

    def create_excel_uploader(
        self,
        key: str,
        label: str = "Choose Excel file",
        help_text: str = "Upload your Excel file containing the data to process",
    ) -> Optional[st.runtime.uploaded_file_manager.UploadedFile]:
        """Create an Excel file uploader widget.

        Args:
            key: Unique key for the uploader widget
            label: Label text for the uploader
            help_text: Help text displayed with the uploader

        Returns:
            Uploaded file object or None
        """
        return st.file_uploader(
            label,
            type=["xlsx", "xls"],
            key=key,
            help=help_text,
        )

    def create_pdf_uploader(
        self,
        key: str,
        label: str = "Choose PDF file",
        help_text: str = "Upload your PDF file to be processed",
    ) -> Optional[st.runtime.uploaded_file_manager.UploadedFile]:
        """Create a PDF file uploader widget.

        Args:
            key: Unique key for the uploader widget
            label: Label text for the uploader
            help_text: Help text displayed with the uploader

        Returns:
            Uploaded file object or None
        """
        return st.file_uploader(
            label,
            type=["pdf"],
            key=key,
            help=help_text,
        )

    def validate_file_size(
        self,
        uploaded_file: st.runtime.uploaded_file_manager.UploadedFile,
        max_mb: int = 400,
    ) -> Tuple[bool, Optional[str]]:
        """Validate uploaded file size.

        Args:
            uploaded_file: The uploaded file to validate
            max_mb: Maximum allowed file size in MB

        Returns:
            Tuple of (is_valid, error_message)
        """
        if uploaded_file is None:
            return False, "No file provided"

        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

        if file_size_mb > max_mb:
            return (
                False,
                f"File too large: {file_size_mb:.1f}MB. Maximum allowed: {max_mb}MB",
            )

        return True, None

    def save_to_temp(
        self,
        uploaded_file: st.runtime.uploaded_file_manager.UploadedFile,
        file_type: str,
    ) -> str:
        """Save uploaded file to temporary location.

        Args:
            uploaded_file: The file to save
            file_type: Type of file ('excel' or 'pdf')

        Returns:
            Path to the temporary file
        """
        suffix = ".xlsx" if file_type == "excel" else ".pdf"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

        # Stream file in chunks instead of loading entire file into RAM
        uploaded_file.seek(0)
        while True:
            chunk = uploaded_file.read(8192)  # 8KB chunks
            if not chunk:
                break
            temp_file.write(chunk)

        temp_file.close()

        return temp_file.name

    def display_file_info(
        self,
        uploaded_file: st.runtime.uploaded_file_manager.UploadedFile,
        file_type: str,
    ) -> None:
        """Display file information in a success message.

        Args:
            uploaded_file: The uploaded file
            file_type: Type of file for display purposes
        """
        if uploaded_file:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            icon = "📊" if file_type.lower() == "excel" else "📄"
            st.success(f"✅ {icon} **{uploaded_file.name}** ({file_size_mb:.1f}MB)")
