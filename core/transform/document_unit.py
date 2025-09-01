#!/usr/bin/env python3
"""
DocumentUnit utility functions for the two-phase processing architecture.

This module provides core operations for DocumentUnit objects, supporting
the memory-efficient two-phase approach that eliminates data coupling fragility.
"""

from typing import Any, Dict, List, Mapping, Optional

import pandas as pd

from core.models import DocumentUnit
from core.transform.pdf import detect_page_ranges, extract_original_index


def create_document_unit_from_bookmark(
    bookmark: Mapping[str, Any],
    excel_row: pd.Series,
    page_offset: int,
    source_info: str,
    page_ranges: Dict[str, Dict[str, int]],
) -> Optional[DocumentUnit]:
    """Create a DocumentUnit from a PDF bookmark and linked Excel row.

    Args:
        bookmark: PDF bookmark dictionary with title, page, level
        excel_row: Linked Excel row containing Document_ID and other data
        page_offset: Offset to add to page numbers for merged PDF positioning
        source_info: "excel_path:pdf_path" for debugging
        page_ranges: Pre-computed page ranges for all bookmarks

    Returns:
        DocumentUnit if linking successful, None if bookmark cannot be linked
    """
    bookmark_title = str(bookmark.get("title", ""))

    # Get page range for this bookmark
    if bookmark_title not in page_ranges:
        return None

    original_range = page_ranges[bookmark_title]
    start_page = original_range["start"]
    end_page = original_range["end"]

    # Adjust for merged PDF position
    merged_start = start_page + page_offset
    merged_end = end_page + page_offset

    return DocumentUnit(
        document_id=str(excel_row["Document_ID"]),
        merged_page_range=(merged_start, merged_end),
        excel_row_data=excel_row,
        source_info=source_info,
    )


def link_bookmarks_to_excel_rows(
    bookmarks: List[Mapping[str, Any]],
    excel_df: pd.DataFrame,
    page_offset: int,
    source_info: str,
    total_pages: int,
) -> List[DocumentUnit]:
    """Link PDF bookmarks to Excel rows within a single file pair.

    This function prevents Document ID collisions by processing each file
    individually before merging. It assumes Document IDs have already been
    added to the Excel DataFrame.

    Args:
        bookmarks: List of PDF bookmark dictionaries
        excel_df: DataFrame with Document_ID column already added
        page_offset: Page offset for merged PDF positioning
        source_info: "excel_path:pdf_path" for debugging
        total_pages: Total pages in this PDF for range detection

    Returns:
        List of DocumentUnits for successfully linked bookmarks
    """
    if excel_df.empty or not bookmarks:
        return []

    # Detect page ranges for all bookmarks in this PDF
    page_ranges = detect_page_ranges(bookmarks, total_pages)

    # Create mapping from original index to Excel rows (fail on duplicates)
    excel_index_map = {}
    duplicate_indices = []

    for idx, row in excel_df.iterrows():
        original_index = str(row["Index#"]).strip()
        if original_index in excel_index_map:
            duplicate_indices.append(
                {
                    "index": original_index,
                    "first_row": excel_index_map[original_index].name,
                    "duplicate_row": row.name,
                    "first_document_id": excel_index_map[original_index]["Document_ID"],
                    "duplicate_document_id": row["Document_ID"],
                }
            )
        excel_index_map[original_index] = row

    # Fail if duplicates found with detailed information
    if duplicate_indices:
        error_details = []
        for dup in duplicate_indices:
            error_details.append(
                f"  Index# '{dup['index']}': "
                f"Row {dup['first_row']} (ID: {dup['first_document_id'][:8]}...) "
                f"vs Row {dup['duplicate_row']} (ID: {dup['duplicate_document_id'][:8]}...)"
            )

        raise ValueError(
            f"Duplicate Index# values found in {source_info}:\n"
            + "\n".join(error_details)
            + f"\n\nTotal duplicates: {len(duplicate_indices)}"
        )

    document_units = []

    for bookmark in bookmarks:
        bookmark_title = str(bookmark.get("title", ""))

        # Extract original index from bookmark title (e.g., "12-Assignment" -> "12")
        original_index = extract_original_index(bookmark_title)
        if not original_index:
            continue

        # Find matching Excel row in this file's DataFrame
        if original_index not in excel_index_map:
            continue

        excel_row = excel_index_map[original_index]

        # Create DocumentUnit
        unit = create_document_unit_from_bookmark(
            bookmark, excel_row, page_offset, source_info, page_ranges
        )

        if unit:
            document_units.append(unit)

    return document_units


def get_page_count_for_unit(unit: DocumentUnit) -> int:
    """Get the number of pages in a DocumentUnit's page range.

    Args:
        unit: DocumentUnit to count pages for

    Returns:
        Number of pages in the unit's page range
    """
    start, end = unit.merged_page_range
    return end - start + 1
