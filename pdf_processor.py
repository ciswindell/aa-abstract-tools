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
    """Handles PDF file operations and bookmark management.

    This class processes PDF bookmarks with support for alphanumeric Index# values.
    Bookmark matching uses string comparison to support formats like "A1", "B5", "AGH42", etc.,
    while maintaining backward compatibility with numeric-only Index# values.
    """

    def __init__(self) -> None:
        self.pdf_path: Optional[str] = None
        self.reader: Optional[PdfReader] = None
        self.writer: Optional[PdfWriter] = None
        self.bookmarks: List[Dict[str, Any]] = []
        self.pages_count: int = 0

    def load_pdf(self, file_path: str) -> bool:
        """Load PDF file and extract bookmarks."""
        try:
            self.reader = PdfReader(file_path)
            self.pdf_path = file_path
            self.pages_count = len(self.reader.pages)
            self.bookmarks = self._extract_bookmarks()
            return True
        except Exception as e:
            raise ValueError(f"Failed to load PDF: {str(e)}")

    def _extract_bookmarks(self) -> List:
        """Extract current bookmark structure from PDF."""
        if not self.reader:
            return []

        try:
            outline = self.reader.outline
            if not outline:
                return []

            bookmarks = []
            self._parse_bookmark_outline(outline, bookmarks)
            return bookmarks
        except:
            return []

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
        """Copy all pages from source PDF to new PdfWriter object."""
        try:
            self.writer = PdfWriter()
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
        self, excel_data: List[Dict], index_mapping: Dict[str, int]
    ) -> Dict[str, str]:
        """Generate new bookmark titles using Excel data and index mapping.

        Args:
            excel_data: List of dictionaries containing Excel row data
            index_mapping: Dictionary mapping original index (as string) to new index (as int)

        Returns:
            Dict[str, str]: Mapping from original index (as string) to new bookmark title
        """
        if not excel_data or not index_mapping:
            return {}

        new_titles = {}

        for row_data in excel_data:
            try:
                # Get original and new index numbers
                original_index = str(row_data.get("Original_Index", "")).strip()
                new_index = index_mapping.get(original_index)

                if new_index is None:
                    continue

                # Extract required fields for bookmark title
                doc_type = str(row_data.get("Document Type", "")).strip()
                received_date = row_data.get("Received Date", "")

                # Format the received date
                formatted_date = self._format_date_for_bookmark(received_date)

                # Generate new bookmark title: "Index#-Document Type-Received Date"
                new_title = f"{new_index}-{doc_type}-{formatted_date}"
                new_titles[original_index] = new_title

            except (ValueError, KeyError):
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
                # Try common formats from Excel
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d"]:
                    try:
                        parsed_date = datetime.strptime(date_value, fmt)
                        return self._format_datetime_to_mdy(parsed_date)
                    except ValueError:
                        continue

                # If none worked, try pandas parsing
                parsed_date = pd.to_datetime(date_value)
                return self._format_datetime_to_mdy(parsed_date)

            # For any other type, convert to string
            return str(date_value)

        except Exception:
            return "N/A"

    def _format_datetime_to_mdy(self, dt: Any) -> str:
        """Convert datetime object to M/D/YYYY format (no leading zeros)."""
        try:
            return dt.strftime("%-m/%-d/%Y")
        except ValueError:
            # Windows doesn't support %-m, so remove leading zeros manually
            formatted = dt.strftime("%m/%d/%Y")
            parts = formatted.split("/")
            month = str(int(parts[0]))
            day = str(int(parts[1]))
            year = parts[2]
            return f"{month}/{day}/{year}"
        except:
            return str(dt)

    def extract_original_index_from_bookmark(
        self, bookmark_title: str
    ) -> Optional[str]:
        """Extract original index from existing bookmark title.

        Supports alphanumeric index values (e.g., "A1", "B5", "AGH42") by returning
        the index part as a string rather than converting to integer.

        Args:
            bookmark_title: The bookmark title to extract index from

        Returns:
            Optional[str]: Original index as string, or None if not found
        """
        if not bookmark_title:
            return None

        try:
            if "-" in bookmark_title:
                index_part = bookmark_title.split("-")[0].strip()
                return index_part
        except (ValueError, IndexError):
            pass

        return None

    def update_bookmarks_with_new_titles(self, new_titles: Dict[str, str]) -> bool:
        """Update PDF bookmarks with new titles while preserving non-matching bookmarks.

        Args:
            new_titles: Dictionary mapping original index (as string) to new bookmark title
        """
        if not self.writer or not self.bookmarks:
            return False

        # Process existing bookmarks: preserve non-matching ones, update matching ones
        for bookmark in self.bookmarks:
            bookmark_title = bookmark.get("title", "")
            page_num = bookmark.get("page", 1) - 1  # Convert to 0-based index

            # Try to extract index from bookmark title (returns string for alphanumeric support)
            extracted_index = self.extract_original_index_from_bookmark(bookmark_title)

            # Use string comparison for bookmark matching (supports alphanumeric values like A1, B5, etc.)
            if extracted_index is not None and extracted_index in new_titles:
                # This bookmark matches our format and has a new title - update it
                new_title = new_titles[extracted_index]
                if 0 <= page_num < len(self.writer.pages):
                    self.writer.add_outline_item(new_title, page_num)
            else:
                # This bookmark doesn't match our format - preserve it
                if 0 <= page_num < len(self.writer.pages):
                    self.writer.add_outline_item(bookmark_title, page_num)

        return True

    def _create_bookmark_page_mapping(
        self, new_titles: Dict[str, str]
    ) -> Dict[str, int]:
        """Create mapping from original index to page number for bookmarks.

        Returns:
            Dict[str, int]: Mapping from original index (as string) to page number
        """
        page_mapping = {}

        for original_index in new_titles.keys():
            # Find the original bookmark with this index using string comparison
            for bookmark in self.bookmarks:
                bookmark_title = bookmark.get("title", "")
                extracted_index = self.extract_original_index_from_bookmark(
                    bookmark_title
                )

                # Use string comparison for matching (supports alphanumeric values)
                if extracted_index == original_index:
                    # Found the matching bookmark, get its page number
                    page_num = bookmark.get("page", 1) - 1  # Convert to 0-based index
                    page_mapping[original_index] = page_num
                    break

        return page_mapping

    def save_pdf(self, output_path: str) -> bool:
        """Save the updated PDF with new bookmarks to the specified path."""
        with open(output_path, "wb") as output_file:
            self.writer.write(output_file)
        return True

    def get_bookmark_update_summary(self, new_titles: Dict[str, str]) -> Dict[str, any]:
        """Get summary of bookmark updates for user feedback.

        Args:
            new_titles (Dict[str, str]): Dictionary of new bookmark titles

        Returns:
            Dict[str, any]: Dictionary containing:
                - total_bookmarks_updated (int): Number of bookmarks updated
                - total_bookmarks_preserved (int): Number of bookmarks preserved
                - new_titles_preview (List[str]): Preview of first 5 new titles
                - original_bookmark_count (int): Original number of bookmarks
        """
        # Count how many existing bookmarks match our format using string comparison
        matching_bookmarks = 0
        non_matching_bookmarks = 0

        for bookmark in self.bookmarks:
            bookmark_title = bookmark.get("title", "")
            extracted_index = self.extract_original_index_from_bookmark(bookmark_title)

            # Use string comparison for matching (supports alphanumeric values)
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
