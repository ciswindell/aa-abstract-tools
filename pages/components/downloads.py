#!/usr/bin/env python3
"""
Download components for Abstract Renumber Tool Streamlit interface.

Contains shared download UI and ZIP creation logic to eliminate duplication
across different pages.
"""

import io
import time
import zipfile
from pathlib import Path
from typing import Tuple

import streamlit as st


class DownloadManager:
    """Manages download UI and file preparation."""

    def __init__(self) -> None:
        """Initialize the DownloadManager."""
        pass

    def create_download_zip(
        self, excel_data: bytes, pdf_data: bytes, excel_name: str, pdf_name: str
    ) -> io.BytesIO:
        """Create ZIP file with processed files.

        Args:
            excel_data: Excel file data as bytes
            pdf_data: PDF file data as bytes
            excel_name: Name for Excel file in ZIP
            pdf_name: Name for PDF file in ZIP

        Returns:
            BytesIO buffer containing the ZIP file
        """
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(excel_name, excel_data)
            zip_file.writestr(pdf_name, pdf_data)
        zip_buffer.seek(0)
        return zip_buffer

    def read_file_safely(self, file_path: str) -> bytes:
        """Read file and return data, raise exception if fails.

        Args:
            file_path: Path to the file to read

        Returns:
            File data as bytes

        Raises:
            ValueError: If file is empty or cannot be read
        """
        with open(file_path, "rb") as f:
            data = f.read()
        if len(data) == 0:
            raise ValueError(f"File appears to be empty: {file_path}")
        return data

    def create_processed_filename(self, original_name: str, extension: str) -> str:
        """Create processed filename from original name.

        Args:
            original_name: Original filename
            extension: File extension (without dot)

        Returns:
            Processed filename with _processed suffix
        """
        base_name = Path(original_name).stem
        return f"{base_name}_processed.{extension}"

    def create_merged_filename(self, original_name: str, extension: str) -> str:
        """Create merged filename from original name.

        Args:
            original_name: Original filename
            extension: File extension (without dot)

        Returns:
            Merged filename with _merged suffix
        """
        base_name = Path(original_name).stem
        return f"{base_name}_merged.{extension}"

    def show_download_button(
        self,
        zip_data: bytes,
        zip_filename: str,
        excel_name: str,
        pdf_name: str,
        button_label: str = "📦 Download Processed Files (ZIP)",
    ) -> None:
        """Display download button for ZIP file.

        Args:
            zip_data: ZIP file data as bytes
            zip_filename: Name for the ZIP file
            excel_name: Name of Excel file in ZIP (for help text)
            pdf_name: Name of PDF file in ZIP (for help text)
            button_label: Label for the download button
        """
        timestamp = int(time.time())
        download_key = f"download_zip_{timestamp}"

        st.download_button(
            label=button_label,
            data=zip_data,
            file_name=zip_filename,
            mime="application/zip",
            use_container_width=True,
            help=f"Downloads both {excel_name} and {pdf_name} in a ZIP archive",
            key=download_key,
            type="primary",
        )

    def get_filename_or_default(
        self, session_key: str, default: str = "document"
    ) -> str:
        """Get filename from session state or return default.

        Args:
            session_key: Session state key to check for file object
            default: Default filename if no file found

        Returns:
            Filename from session state or default
        """
        file_obj = st.session_state.get(session_key)
        return file_obj.name if file_obj else default

    def prepare_download_files(
        self,
        excel_path: str,
        pdf_path: str,
        excel_session_key: str = "uploaded_excel",
        pdf_session_key: str = "uploaded_pdf",
        is_merge: bool = False,
    ) -> Tuple[bytes, str, str, str]:
        """Prepare files for download and return ZIP data and filenames.

        Args:
            excel_path: Path to processed Excel file
            pdf_path: Path to processed PDF file
            excel_session_key: Session state key for original Excel file
            pdf_session_key: Session state key for original PDF file
            is_merge: Whether this is a merge operation

        Returns:
            Tuple of (zip_data, zip_filename, excel_zip_name, pdf_zip_name)
        """
        # Get original filenames
        excel_name = self.get_filename_or_default(excel_session_key)
        pdf_name = self.get_filename_or_default(pdf_session_key)

        # Create processed filenames
        if is_merge:
            processed_excel_name = self.create_merged_filename(excel_name, "xlsx")
            processed_pdf_name = self.create_merged_filename(pdf_name, "pdf")
            zip_filename = self.create_merged_filename(excel_name, "zip")
        else:
            processed_excel_name = self.create_processed_filename(excel_name, "xlsx")
            processed_pdf_name = self.create_processed_filename(pdf_name, "pdf")
            zip_filename = self.create_processed_filename(excel_name, "zip")

        # Read processed files
        excel_data = self.read_file_safely(excel_path)
        pdf_data = self.read_file_safely(pdf_path)

        # Create ZIP
        zip_buffer = self.create_download_zip(
            excel_data, pdf_data, processed_excel_name, processed_pdf_name
        )

        return (
            zip_buffer.getvalue(),
            zip_filename,
            processed_excel_name,
            processed_pdf_name,
        )
