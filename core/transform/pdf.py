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


def add_rows_for_new_bookmarks(
    df: pd.DataFrame,
    bookmarks: list[Mapping[str, Any]],
    new_bookmark_titles: set[str],
    index_col: str = "Index#",
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Append a placeholder Excel row for each approved new (orphaned) bookmark.

    For every bookmark whose title is in ``new_bookmark_titles``:
      * append a row to ``df`` with a unique ``Index#`` (max existing numeric
        index + 1, incrementing), ``Document Type`` set to the bookmark title,
        and a blank ``Received Date``; all other columns left blank.
      * rewrite the bookmark title to ``"<index>-<title>"`` so existing linking
        (``extract_original_index`` -> ``Index#`` match) connects it to the row.

    Returns a new (DataFrame, bookmarks) pair. Inputs are not mutated.
    """

    def _as_int(value: Any) -> int | None:
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return None

    existing = [n for n in (_as_int(v) for v in df.get(index_col, [])) if n is not None]
    next_idx = (max(existing) + 1) if existing else 1

    new_rows: list[dict[str, Any]] = []
    new_bookmarks: list[dict[str, Any]] = []
    for bm in bookmarks:
        bm_copy = dict(bm)
        title = str(bm.get("title", ""))
        if title in new_bookmark_titles:
            bm_copy["title"] = f"{next_idx}-{title}"
            new_rows.append(
                {
                    index_col: str(next_idx),
                    "Document Type": title,
                    "Received Date": None,
                    "Orphan": "Yes",
                }
            )
            next_idx += 1
        new_bookmarks.append(bm_copy)

    if not new_rows:
        return df, new_bookmarks

    df = df.copy()
    if "Orphan" in df.columns:
        df["Orphan"] = df["Orphan"].apply(
            lambda v: "Yes" if str(v).strip().lower() == "yes" else "No"
        )
    else:
        df["Orphan"] = "No"
    additions = pd.DataFrame(new_rows)
    new_df = pd.concat([df, additions], ignore_index=True)
    return new_df, new_bookmarks
