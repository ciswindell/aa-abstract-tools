#!/usr/bin/env python3
"""
Core models (dataclasses) used by application services and adapters.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Tuple


@dataclass
class Options:
    """Runtime options collected from the UI.

    Attributes:
        backup: Whether to create timestamped backups before writing outputs.
        sort_bookmarks: Whether to sort PDF bookmarks naturally.
        reorder_pages: Whether to reorder pages to match bookmark order.
        sheet_name: Excel sheet name to process (None = resolve/prompt).
        filter_enabled: Whether filtering is enabled in the UI.
        filter_column: Name of the Excel column to filter by (None = no filter).
        filter_values: Values to keep in the selected filter column.
        merge_pairs: List of (excel_path, pdf_path) pairs to merge (None = no merge).
        merge_pairs_with_sheets: Optional list of (excel_path, pdf_path, sheet_name) for
            per-file sheet selection during merge.
    """

    backup: bool
    sort_bookmarks: bool
    reorder_pages: bool
    sheet_name: Optional[str]
    filter_enabled: bool = False
    filter_column: Optional[str] = None
    filter_values: Optional[List[str]] = None
    merge_pairs: Optional[List[Tuple[str, str]]] = None
    merge_pairs_with_sheets: Optional[List[Tuple[str, str, str]]] = None


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
