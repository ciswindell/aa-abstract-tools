#!/usr/bin/env python3
"""
PDF processing module for the Abstract Renumber Tool.
Handles PDF bookmark operations and management.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from PyPDF2 import PdfReader, PdfWriter


class PDFProcessor:
    """Handles PDF file operations and bookmark management."""

    def __init__(self) -> None:
        self.pdf_path: Optional[str] = None
        self.reader: Optional[PdfReader] = None
        self.writer: Optional[PdfWriter] = None
        self.bookmarks: List[Dict[str, Any]] = []
        self.pages_count: int = 0

    def load_pdf(self, file_path: str) -> bool:
        """Load PDF file and extract basic information.

        Args:
            file_path (str): Path to the PDF file to load

        Returns:
            bool: True if PDF was loaded successfully

        Raises:
            FileNotFoundError: If PDF file does not exist
            Exception: If PDF loading or bookmark extraction fails
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF file not found: {file_path}")

            # Load PDF file
            self.reader = PdfReader(file_path)
            self.pdf_path = file_path
            self.pages_count = len(self.reader.pages)

            # Extract bookmark structure
            self.bookmarks = self._extract_bookmarks()

            return True

        except Exception as e:
            raise e

    def _extract_bookmarks(self) -> List:
        """Extract current bookmark structure from PDF."""
        if not self.reader:
            return []

        try:
            # Get bookmark outline from PDF
            outline = self.reader.outline
            if not outline:
                return []

            # Extract bookmark information
            bookmarks = []
            self._parse_bookmark_outline(outline, bookmarks)

            return bookmarks

        except Exception as e:
            raise ValueError(f"Failed to extract bookmarks: {str(e)}")

    def _parse_bookmark_outline(
        self, outline: List[Any], bookmarks: List[Dict[str, Any]], level: int = 0
    ) -> None:
        """Recursively parse bookmark outline structure."""
        for item in outline:
            if isinstance(item, list):
                # Nested bookmark level
                self._parse_bookmark_outline(item, bookmarks, level + 1)
            else:
                # Individual bookmark
                bookmark_info = {
                    "title": item.title,
                    "level": level,
                    "page": self._get_bookmark_page(item),
                    "original_item": item,
                }
                bookmarks.append(bookmark_info)

    def _get_bookmark_page(self, bookmark: Any) -> int:
        """Get the page number for a bookmark."""
        try:
            if hasattr(bookmark, "page") and bookmark.page:
                # Get page reference and find its index
                page_ref = bookmark.page
                if hasattr(page_ref, "idnum"):
                    # Find the page index by matching the page reference
                    for i, page in enumerate(self.reader.pages):
                        if (
                            hasattr(page, "indirect_reference")
                            and page.indirect_reference.idnum == page_ref.idnum
                        ):
                            return i + 1  # 1-based page numbering

                # Fallback: try to get page directly
                return self.reader.pages.index(page_ref) + 1

            return 1  # Default to page 1 if cannot determine

        except Exception:
            return 1  # Default to page 1 on any error

    def get_bookmark_info(self) -> Dict[str, any]:
        """Get information about loaded PDF and bookmarks.

        Returns:
            Dict[str, any]: Dictionary containing:
                - pages_count (int): Number of pages in the PDF
                - bookmarks_count (int): Number of bookmarks found
                - bookmark_titles (List[str]): List of bookmark titles
        """
        return {
            "pages_count": self.pages_count,
            "bookmarks_count": len(self.bookmarks),
            "bookmark_titles": [b["title"] for b in self.bookmarks],
        }

    def get_bookmarks(self) -> List:
        """Get the extracted bookmarks list.

        Returns:
            List: List of bookmark dictionaries containing title, level, page, and original_item
        """
        return self.bookmarks

    def find_bookmarks_by_pattern(self, pattern: str = None) -> List:
        """Find bookmarks that match a specific pattern.

        Args:
            pattern (str, optional): Pattern to search for in bookmark titles.
                                   If None, finds bookmarks starting with numbers.

        Returns:
            List: List of matching bookmark dictionaries
        """
        if not self.bookmarks:
            return []

        matching_bookmarks = []
        for bookmark in self.bookmarks:
            title = bookmark["title"]

            if pattern:
                # Check if title matches the pattern
                if pattern.lower() in title.lower():
                    matching_bookmarks.append(bookmark)
            else:
                # Default: find bookmarks that start with a number (likely index bookmarks)
                if title and title[0].isdigit():
                    matching_bookmarks.append(bookmark)

        return matching_bookmarks

    def copy_pages_to_writer(self) -> bool:
        """Copy all pages from source PDF to new PdfWriter object.

        Returns:
            bool: True if pages were copied successfully

        Raises:
            ValueError: If no PDF loaded or page copying fails
        """
        if not self.reader:
            raise ValueError("No PDF loaded. Call load_pdf() first.")

        try:
            # Create new PdfWriter object
            self.writer = PdfWriter()

            # Copy all pages from reader to writer
            for page in self.reader.pages:
                self.writer.add_page(page)

            return True

        except Exception as e:
            raise ValueError(f"Failed to copy PDF pages: {str(e)}")

    def get_writer(self) -> Optional[PdfWriter]:
        """Get the PdfWriter object with copied pages."""
        return self.writer

    def is_writer_ready(self) -> bool:
        """Check if PdfWriter is ready with copied pages."""
        return self.writer is not None and len(self.writer.pages) > 0

    def generate_new_bookmark_titles(
        self, excel_data: List[Dict], index_mapping: Dict[int, int]
    ) -> Dict[int, str]:
        """Generate new bookmark titles using Excel data and index mapping.

        Args:
            excel_data (List[Dict]): List of dictionaries containing Excel row data
            index_mapping (Dict[int, int]): Dictionary mapping original_index -> new_index

        Returns:
            Dict[int, str]: Dictionary mapping original_index -> new_bookmark_title
        """
        if not excel_data or not index_mapping:
            return {}

        new_titles = {}

        for row_data in excel_data:
            try:
                # Get original and new index numbers
                original_index = int(row_data.get("Original_Index", 0))
                new_index = index_mapping.get(original_index)

                if new_index is None:
                    continue

                # Extract required fields for bookmark title
                doc_type = str(row_data.get("Document Type", "")).strip()
                received_date = row_data.get("Received Date", "")

                # Format the received date (will be handled in next task)
                formatted_date = self._format_date_for_bookmark(received_date)

                # Generate new bookmark title: "Index#-Document Type-Received Date"
                new_title = f"{new_index}-{doc_type}-{formatted_date}"
                new_titles[original_index] = new_title

            except (ValueError, KeyError) as e:
                # Skip rows with invalid data
                continue

        return new_titles

    def _format_date_for_bookmark(self, date_value: Any) -> str:
        """Format date value for bookmark title in M/D/YYYY format."""
        if date_value is None or date_value == "":
            return "N/A"

        try:
            # Handle pandas Timestamp objects
            if isinstance(date_value, pd.Timestamp):
                return (
                    date_value.strftime("%-m/%-d/%Y")
                    if hasattr(date_value, "strftime")
                    else date_value.strftime("%m/%d/%Y").lstrip("0").replace("/0", "/")
                )

            # Handle datetime objects
            if isinstance(date_value, datetime):
                return (
                    date_value.strftime("%-m/%-d/%Y")
                    if hasattr(date_value, "strftime")
                    else date_value.strftime("%m/%d/%Y").lstrip("0").replace("/0", "/")
                )

            # Handle string dates
            if isinstance(date_value, str):
                # Try to parse various string formats
                try:
                    # Common formats from Excel
                    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d"]:
                        try:
                            parsed_date = datetime.strptime(date_value, fmt)
                            return self._format_datetime_to_mdy(parsed_date)
                        except ValueError:
                            continue

                    # If none worked, try pandas parsing
                    parsed_date = pd.to_datetime(date_value)
                    return self._format_datetime_to_mdy(parsed_date)

                except:
                    # If all parsing fails, return original string
                    return str(date_value)

            # For any other type, try to convert to string
            return str(date_value)

        except Exception:
            # Fallback: return "N/A" if value exists but can't be formatted
            return "N/A"

    def _format_datetime_to_mdy(self, dt: Any) -> str:
        """Convert datetime object to M/D/YYYY format (no leading zeros)."""
        try:
            # Use %-m and %-d on Unix systems to avoid leading zeros
            try:
                return dt.strftime("%-m/%-d/%Y")
            except ValueError:
                # Windows doesn't support %-m, so remove leading zeros manually
                formatted = dt.strftime("%m/%d/%Y")
                # Remove leading zeros: 01/02/2023 -> 1/2/2023
                parts = formatted.split("/")
                month = str(int(parts[0]))  # Remove leading zero from month
                day = str(int(parts[1]))  # Remove leading zero from day
                year = parts[2]  # Keep year as is
                return f"{month}/{day}/{year}"
        except:
            return str(dt)

    def extract_original_index_from_bookmark(
        self, bookmark_title: str
    ) -> Optional[int]:
        """Extract original index number from existing bookmark title."""
        if not bookmark_title:
            return None

        try:
            # Bookmark titles should start with "number-"
            if "-" in bookmark_title:
                index_part = bookmark_title.split("-")[0].strip()
                return int(index_part)
        except (ValueError, IndexError):
            pass

        return None

    def update_bookmarks_with_new_titles(self, new_titles: Dict[int, str]) -> bool:
        """Update PDF bookmarks with new titles while preserving non-matching bookmarks.

        Args:
            new_titles (Dict[int, str]): Dictionary mapping original_index -> new_bookmark_title

        Returns:
            bool: True if bookmarks were updated successfully

        Raises:
            ValueError: If bookmark update fails
        """
        if not self.writer or not self.bookmarks:
            return False

        try:
            # Process existing bookmarks: preserve non-matching ones, update matching ones
            for bookmark in self.bookmarks:
                bookmark_title = bookmark.get("title", "")
                page_num = bookmark.get("page", 1) - 1  # Convert to 0-based index

                # Try to extract index from bookmark title
                extracted_index = self.extract_original_index_from_bookmark(
                    bookmark_title
                )

                if extracted_index is not None and extracted_index in new_titles:
                    # This bookmark matches our format and has a new title - update it
                    new_title = new_titles[extracted_index]
                    if 0 <= page_num < len(self.writer.pages):
                        self.writer.add_outline_item(new_title, page_num)
                else:
                    # This bookmark doesn't match our format or doesn't have a new title - preserve it
                    if 0 <= page_num < len(self.writer.pages):
                        self.writer.add_outline_item(bookmark_title, page_num)

            return True

        except Exception as e:
            raise ValueError(f"Failed to update bookmarks: {str(e)}")

    def _create_bookmark_page_mapping(
        self, new_titles: Dict[int, str]
    ) -> Dict[int, int]:
        """Create mapping from original index to page number for bookmarks."""
        page_mapping = {}

        for original_index in new_titles.keys():
            # Find the original bookmark with this index
            for bookmark in self.bookmarks:
                bookmark_title = bookmark.get("title", "")
                extracted_index = self.extract_original_index_from_bookmark(
                    bookmark_title
                )

                if extracted_index == original_index:
                    # Found the matching bookmark, get its page number
                    page_num = bookmark.get("page", 1) - 1  # Convert to 0-based index
                    page_mapping[original_index] = page_num
                    break

        return page_mapping

    def save_pdf(self, output_path: str) -> bool:
        """Save the updated PDF with new bookmarks to the specified path.

        Args:
            output_path (str): Path where the PDF should be saved

        Returns:
            bool: True if PDF was saved successfully

        Raises:
            ValueError: If no PdfWriter available or save operation fails
        """
        if not self.writer:
            raise ValueError(
                "No PdfWriter available. Call copy_pages_to_writer() first."
            )

        try:
            with open(output_path, "wb") as output_file:
                self.writer.write(output_file)
            return True

        except Exception as e:
            raise ValueError(f"Failed to save PDF: {str(e)}")

    def get_bookmark_update_summary(self, new_titles: Dict[int, str]) -> Dict[str, any]:
        """Get summary of bookmark updates for user feedback.

        Args:
            new_titles (Dict[int, str]): Dictionary of new bookmark titles

        Returns:
            Dict[str, any]: Dictionary containing:
                - total_bookmarks_updated (int): Number of bookmarks updated
                - total_bookmarks_preserved (int): Number of bookmarks preserved
                - new_titles_preview (List[str]): Preview of first 5 new titles
                - original_bookmark_count (int): Original number of bookmarks
        """
        # Count how many existing bookmarks match our format
        matching_bookmarks = 0
        non_matching_bookmarks = 0

        for bookmark in self.bookmarks:
            bookmark_title = bookmark.get("title", "")
            extracted_index = self.extract_original_index_from_bookmark(bookmark_title)

            if extracted_index is not None and extracted_index in new_titles:
                matching_bookmarks += 1
            else:
                non_matching_bookmarks += 1

        return {
            "total_bookmarks_updated": matching_bookmarks,
            "total_bookmarks_preserved": non_matching_bookmarks,
            "new_titles_preview": list(new_titles.values())[
                :5
            ],  # Show first 5 as preview
            "original_bookmark_count": len(self.bookmarks),
        }
