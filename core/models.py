#!/usr/bin/env python3
"""
Core models (dataclasses) used by application services and adapters.
"""

from dataclasses import dataclass

import pandas as pd


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
        check_document_images: Whether to add/update Document_Found column in Excel output.
    """

    backup: bool
    sort_bookmarks: bool
    reorder_pages: bool
    sheet_name: str | None
    filter_enabled: bool = False
    filter_column: str | None = None
    filter_values: list[str] | None = None
    merge_pairs: list[tuple[str, str]] | None = None
    merge_pairs_with_sheets: list[tuple[str, str, str]] | None = None
    check_document_images: bool = False


@dataclass
class Result:
    """Outcome from a service operation."""

    success: bool
    message: str | None = None


@dataclass
class DocumentUnit:
    """Atomic unit linking Excel row to PDF page range in merged PDF.

    This dataclass represents the fundamental relationship between an Excel row
    and its corresponding PDF page range. It prevents the fragile separation
    of bookmarks and pages that caused data corruption in the original pipeline.

    Attributes:
        document_id: Immutable hash key linking to Excel row (never changes during processing).
        merged_page_range: (start_page, end_page) position in intermediate merged PDF (1-based).
        excel_row_data: The linked Excel row containing all document metadata.
        source_info: "excel_path:pdf_path" for debugging and tracing origins.
    """

    document_id: str
    merged_page_range: tuple[int, int]
    excel_row_data: pd.Series
    source_info: str
