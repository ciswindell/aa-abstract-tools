#!/usr/bin/env python3
"""
PDF processing module for the Abstract Renumber Tool.
Handles PDF bookmark operations and management.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from natsort import natsorted, ns
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import Fit


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

    def update_bookmarks_with_new_titles(
        self, new_titles: Dict[str, str], sort_naturally: bool = False
    ) -> bool:
        """Update PDF bookmarks with new titles while preserving non-matching bookmarks.

        Args:
            new_titles: Dictionary mapping original index (as string) to new bookmark title
            sort_naturally: If True, sort bookmarks naturally before adding to PDF
        """
        if not self.writer or not self.bookmarks:
            return False

        # Prepare bookmarks with updated titles
        updated_bookmarks = []
        for bookmark in self.bookmarks:
            bookmark_title = bookmark.get("title", "")

            # Try to extract index from bookmark title (returns string for alphanumeric support)
            extracted_index = self.extract_original_index_from_bookmark(bookmark_title)

            # Use string comparison for bookmark matching (supports alphanumeric values like A1, B5, etc.)
            if extracted_index is not None and extracted_index in new_titles:
                # This bookmark matches our format and has a new title - update it
                new_title = new_titles[extracted_index]
                updated_bookmark = bookmark.copy()
                updated_bookmark["title"] = new_title
                updated_bookmarks.append(updated_bookmark)
            else:
                # This bookmark doesn't match our format - preserve it
                updated_bookmarks.append(bookmark)

        # Sort bookmarks if requested
        if sort_naturally:
            updated_bookmarks = natsorted(
                updated_bookmarks,
                key=lambda bookmark: bookmark.get("title", ""),
                alg=ns.IGNORECASE,  # Case-insensitive natural sorting
            )

        # Add all bookmarks to writer in the correct order
        bookmarks_added = 0
        for bookmark in updated_bookmarks:
            bookmark_title = bookmark.get("title", "")
            page_num = bookmark.get("page", 1) - 1  # Convert to 0-based index

            if 0 <= page_num < len(self.writer.pages):
                try:
                    page_obj = self.writer.pages[page_num]
                    # Create a fit that inherits current zoom (XYZ with null zoom factor)
                    inherit_zoom_fit = Fit.xyz(left=None, top=None, zoom=None)
                    self.writer.add_outline_item(
                        bookmark_title, page_obj, fit=inherit_zoom_fit
                    )
                    bookmarks_added += 1
                except Exception:
                    # Silently skip failed bookmarks
                    pass

        # Update internal bookmarks list to match what was added
        self.bookmarks = updated_bookmarks

        return bookmarks_added > 0

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
        if not self.writer:
            return False

        # Set the page mode to show outlines (bookmarks) by default
        try:
            self.writer.page_mode = "/UseOutlines"
        except Exception:
            pass  # Not critical if this fails

        try:
            with open(output_path, "wb") as output_file:
                self.writer.write(output_file)
            return True
        except Exception:
            return False

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

    def sort_bookmarks_naturally(self) -> bool:
        """
        Sort PDF outline/bookmarks naturally using natsort library.

        Note: This method is now a no-op since sorting happens during bookmark update.
        The sorting is handled by passing sort_naturally=True to update_bookmarks_with_new_titles().

        Returns:
            bool: True (always succeeds since sorting happens elsewhere)
        """
        return True

    def detect_bookmark_page_ranges(self) -> Dict[str, Dict[str, int]]:
        """
        Detect consecutive pages belonging to each bookmark.

        Each bookmark is assumed to cover pages from its bookmark page
        up to (but not including) the next bookmark's page.

        Returns:
            Dict mapping bookmark title to {"start": int, "end": int} page ranges.
            Page numbers are 1-based (same as bookmark pages).

        Example:
            {
                "1-Assignment": {"start": 3, "end": 5},
                "2-Document": {"start": 6, "end": 8},
                "3-Report": {"start": 9, "end": 12}
            }
        """
        if not self.bookmarks:
            return {}

        # Sort bookmarks by page number to determine ranges
        sorted_by_page = sorted(self.bookmarks, key=lambda b: b.get("page", 1))

        page_ranges = {}
        total_pages = (
            self.pages_count
            if hasattr(self, "pages_count")
            else len(self.reader.pages) if self.reader else 0
        )

        for i, bookmark in enumerate(sorted_by_page):
            title = bookmark.get("title", "")
            start_page = bookmark.get("page", 1)

            # Determine end page (up to next bookmark or end of PDF)
            if i + 1 < len(sorted_by_page):
                # End at the page before the next bookmark
                end_page = sorted_by_page[i + 1].get("page", 1) - 1
            else:
                # Last bookmark goes to end of PDF
                end_page = total_pages

            # Ensure valid range
            if end_page < start_page:
                end_page = start_page

            page_ranges[title] = {"start": start_page, "end": end_page}

        return page_ranges

    def reorder_pages_by_bookmarks(self) -> bool:
        """
        Physically reorder PDF pages to match current bookmark sequence.

        Pages are reordered based on the current bookmark order in self.bookmarks.
        Page ranges move together as units. Bookmark page references are updated
        to match new positions.

        Returns:
            bool: True if reordering was successful
        """
        if not self.writer or not self.bookmarks or not self.reader:
            return False

        try:
            # Get page ranges for current bookmarks
            page_ranges = self.detect_bookmark_page_ranges()

            if not page_ranges:
                return False

            # Create new writer for reordered pages
            new_writer = PdfWriter()

            # Track new page positions for bookmark updates
            bookmark_page_updates = {}
            current_new_page = 1  # 1-based page numbering

            # Reorder pages according to current bookmark sequence
            for bookmark in self.bookmarks:
                title = bookmark.get("title", "")

                if title in page_ranges:
                    page_range = page_ranges[title]
                    start_page = page_range["start"]
                    end_page = page_range["end"]

                    # Record new position for this bookmark
                    bookmark_page_updates[title] = current_new_page

                    # Add all pages in this bookmark's range
                    for page_num in range(start_page, end_page + 1):
                        if 1 <= page_num <= len(self.reader.pages):
                            page_index = page_num - 1  # Convert to 0-based
                            new_writer.add_page(self.reader.pages[page_index])
                            current_new_page += 1

            # Update self.writer with reordered pages
            self.writer = new_writer

            # Update bookmark page references to new positions
            for bookmark in self.bookmarks:
                title = bookmark.get("title", "")
                if title in bookmark_page_updates:
                    bookmark["page"] = bookmark_page_updates[title]

            # Re-add all bookmarks to the new writer (the new writer has no bookmarks since it was just created)
            for bookmark in self.bookmarks:
                bookmark_title = bookmark.get("title", "")
                page_num = bookmark.get("page", 1) - 1  # Convert to 0-based index

                if 0 <= page_num < len(self.writer.pages):
                    try:
                        page_obj = self.writer.pages[page_num]
                        # Create a fit that inherits current zoom (XYZ with null zoom factor)
                        inherit_zoom_fit = Fit.xyz(left=None, top=None, zoom=None)
                        self.writer.add_outline_item(
                            bookmark_title, page_obj, fit=inherit_zoom_fit
                        )
                    except Exception:
                        pass  # Silently skip failed bookmarks

            return True

        except Exception as e:
            raise ValueError(f"Failed to reorder pages by bookmarks: {str(e)}")
