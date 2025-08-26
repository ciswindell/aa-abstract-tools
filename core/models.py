#!/usr/bin/env python3
"""
Core models (dataclasses) used by application services and adapters.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Options:
    """Runtime options collected from the UI.

    Attributes:
        backup: Whether to create timestamped backups before writing outputs.
        sort_bookmarks: Whether to sort PDF bookmarks naturally.
        reorder_pages: Whether to reorder pages to match bookmark order.
        sheet_name: Excel sheet name to process (None = resolve/prompt).
    """

    backup: bool
    sort_bookmarks: bool
    reorder_pages: bool
    sheet_name: Optional[str]


@dataclass
class Result:
    """Outcome from a service operation."""

    success: bool
    message: Optional[str] = None


@dataclass
class Bookmark:
    """A single PDF bookmark entry."""

    title: str
    page: int
    level: int = 0


@dataclass
class PageRange:
    """Inclusive page range (1-based)."""

    start: int
    end: int


@dataclass
class DocumentLink:
    """Links an Excel row to its corresponding PDF bookmark.

    Attributes:
        document_id: Unique hash identifier for the document.
        excel_row_index: Position in the DataFrame (0-based).
        original_bookmark_title: Original PDF bookmark title.
        original_bookmark_page: Original PDF bookmark page number (1-based).
        original_bookmark_level: Original PDF bookmark level.
    """

    document_id: str
    excel_row_index: int
    original_bookmark_title: str
    original_bookmark_page: int
    original_bookmark_level: int


@dataclass
class Record:
    """Excel row wrapper; stores raw column values.

    Note: Keep generic to avoid coupling to specific column names.
    """

    values: Dict[str, Any]
