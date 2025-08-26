#!/usr/bin/env python3
"""
PDF validation module for the Abstract Renumber Tool.
Handles PDF validation logic including bookmark conflict detection.
"""

from typing import Dict, List, Optional


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

    @staticmethod
    def validate_bookmark_index_duplicates(
        bookmarks: List[Dict],
    ) -> Optional[Dict[str, List[Dict[str, str]]]]:
        """
        Validate that bookmark leading numbers are unique (PRD requirement #3).

        Args:
            bookmarks: List of bookmark dictionaries with 'title' keys

        Returns:
            None if no duplicates found, otherwise dict with duplicate details:
            {
                "duplicate_groups": [
                    {
                        "index": "5",
                        "titles": ["5-Deed-1/1/2024", "5-Assignment-1/2/2024"]
                    }
                ]
            }
        """
        if not bookmarks:
            return None

        # Import here to avoid circular imports
        from core.transform.pdf import extract_original_index

        # Group bookmark titles by their index numbers
        index_to_titles = {}
        for bookmark in bookmarks:
            title = str(bookmark.get("title", ""))
            original_idx = extract_original_index(title)
            if original_idx:
                if original_idx not in index_to_titles:
                    index_to_titles[original_idx] = []
                index_to_titles[original_idx].append(title)

        # Find groups with duplicates
        duplicate_groups = []
        for index, titles in index_to_titles.items():
            if len(titles) > 1:
                duplicate_groups.append({"index": index, "titles": titles})

        return {"duplicate_groups": duplicate_groups} if duplicate_groups else None
