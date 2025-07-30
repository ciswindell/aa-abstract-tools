#!/usr/bin/env python3
"""
PDF validation module for the Abstract Renumber Tool.
Handles PDF validation logic including bookmark conflict detection.
"""

from typing import Dict, List, Optional, Tuple


class PDFValidator:
    """
    Handles PDF validation operations including bookmark conflict detection.

    This class is responsible for validating bookmark data that has already
    been extracted by PDFProcessor, focusing purely on validation logic
    without dealing with file I/O operations.
    """

    @staticmethod
    def validate_bookmark_page_conflicts(
        bookmarks: List[Dict],
    ) -> Optional[Dict[str, List[str]]]:
        """
        Validate that no multiple bookmarks point to the same page number.

        Args:
            bookmarks: List of bookmark dictionaries with 'title' and 'page' keys

        Returns:
            None if no conflicts found, otherwise dict with conflict details:
            {
                "conflicts": [
                    {"page": 5, "bookmarks": ["Bookmark 1", "Bookmark 2"]},
                    ...
                ]
            }
        """
        if not bookmarks:
            return None

        # Group bookmarks by page number
        page_to_bookmarks = {}
        for bookmark in bookmarks:
            page = bookmark.get("page", 1)
            title = bookmark.get("title", "Unknown")

            if page not in page_to_bookmarks:
                page_to_bookmarks[page] = []
            page_to_bookmarks[page].append(title)

        # Find pages with multiple bookmarks
        conflicts = []
        for page, bookmark_titles in page_to_bookmarks.items():
            if len(bookmark_titles) > 1:
                conflicts.append({"page": page, "bookmarks": bookmark_titles})

        return {"conflicts": conflicts} if conflicts else None
