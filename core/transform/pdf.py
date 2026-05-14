#!/usr/bin/env python3
"""
Pure PDF bookmark transforms.

All functions are side-effect free and independent of backend PDF types.
"""

from collections.abc import Mapping
from typing import Any

import pandas as pd

from utils.dates import format_mdy


def extract_original_index(bookmark_title: str) -> str | None:
    """Return the original index number before the first '-' in a bookmark title.

    This extracts the original Excel Index# value that was used to create the bookmark.
    The hash-based Document_ID is never user-facing and never appears in bookmark titles.

    Examples:
        "12-Assignment-1/1/2024" -> "12"  (original Excel Index#)
        "A5-Deed-2/2/2024" -> "A5"       (original Excel Index#)
    """

    if not bookmark_title:
        return None
    try:
        return bookmark_title.split("-", 1)[0].strip()
    except Exception:
        return None


def make_titles(df: pd.DataFrame) -> dict[str, str]:
    """Generate new bookmark titles from a processed DataFrame.

    Requires columns: "Document_ID", "Index#", "Document Type", "Received Date".

    Returns mapping: document_id (str) -> title (str) "{Index#}-{Document Type}-{M/D/YYYY}".
    Rows missing required fields are skipped.
    """

    required = ["Document_ID", "Index#", "Document Type", "Received Date"]
    for col in required:
        if col not in df.columns:
            return {}

    titles: dict[str, str] = {}
    for _, row in df.iterrows():
        try:
            doc_id = str(row["Document_ID"]).strip()
            new_idx = int(row["Index#"])  # must be sequential int
            doc_type = str(row["Document Type"]).strip()
            received = row["Received Date"]
            date_text = format_mdy(received)
            titles[doc_id] = f"{new_idx}-{doc_type}-{date_text}"
        except Exception:
            continue
    return titles


def detect_page_ranges(
    bookmarks: list[Mapping[str, Any]], total_pages: int
) -> dict[str, dict[str, int]]:
    """Detect inclusive page ranges for each bookmark, ordered by page.

    Input pages are 1-based. For each bookmark, the range extends up to
    the page before the next bookmark, or to total_pages for the last item.
    """

    if not bookmarks or total_pages <= 0:
        return {}

    ordered = sorted(bookmarks, key=lambda b: int(b.get("page", 1)))
    ranges: dict[str, dict[str, int]] = {}
    for i, bm in enumerate(ordered):
        title = str(bm.get("title", ""))
        start = int(bm.get("page", 1))
        if i + 1 < len(ordered):
            end = int(ordered[i + 1].get("page", start)) - 1
        else:
            end = total_pages
        if end < start:
            end = start
        ranges[title] = {"start": start, "end": end}
    return ranges
