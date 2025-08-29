#!/usr/bin/env python3
"""
PDF repository adapter using PyPDF2.

Provides bookmark reading and writing while keeping calling code
independent of PyPDF2 types.
"""

from typing import Any, Dict, List, Mapping, Sequence, Tuple

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import Fit
from PyPDF2.errors import DeprecationError


class PdfPyPDF2Repo:
    """Concrete PdfRepo implementation using PyPDF2."""

    def read(self, path: str) -> Tuple[List[Mapping[str, Any]], int]:
        """Return extracted bookmarks and total page count from a PDF path."""
        reader = PdfReader(path)
        pages_count = len(reader.pages)
        # Tolerate PyPDF2 attribute differences across versions
        # Prefer 'outline' (PyPDF2 >=3) and fall back to 'outlines' (older),
        # guarding against DeprecationError on access.
        outline = getattr(reader, "outline", None)
        if not outline:
            try:
                outline = getattr(reader, "outlines", None)
            except DeprecationError:
                outline = None
        if not outline:
            return [], pages_count

        bookmarks: List[Dict[str, Any]] = []
        self._parse_outline(reader, outline, bookmarks, level=0)
        return bookmarks, pages_count

    def pages(self, path: str):
        """Return a list of page objects from a PDF path."""
        reader = PdfReader(path)
        return list(reader.pages)

    def write(
        self,
        pages: Sequence[Any],
        bookmarks: Sequence[Mapping[str, Any]],
        out_path: str,
    ) -> None:
        """Write pages and bookmarks to a new PDF at out_path."""
        writer = PdfWriter()

        for p in pages:
            try:
                writer.add_page(p)
            except (TypeError, ValueError, AttributeError):
                # Skip invalid page types
                continue

        # Set default to show outlines if possible
        try:
            writer.page_mode = "/UseOutlines"
        except AttributeError:
            pass

        # Add bookmarks
        for bm in bookmarks:
            title = str(bm.get("title", ""))
            page_num = int(bm.get("page", 1)) - 1
            if 0 <= page_num < len(writer.pages):
                try:
                    page_obj = writer.pages[page_num]
                    fit = Fit.xyz(left=None, top=None, zoom=None)
                    writer.add_outline_item(title, page_obj, fit=fit)
                except (ValueError, TypeError, AttributeError, IndexError):
                    continue

        with open(out_path, "wb") as fh:
            writer.write(fh)

    def _parse_outline(
        self,
        reader: PdfReader,
        outline: List[Any],
        bookmarks: List[Dict[str, Any]],
        level: int,
    ) -> None:
        """Populate bookmarks with flat entries from a nested outline."""
        for item in outline:
            if isinstance(item, list):
                self._parse_outline(reader, item, bookmarks, level + 1)
            else:
                title = getattr(item, "title", "")
                page = self._resolve_bookmark_page(reader, item)
                bookmarks.append({"title": title, "level": level, "page": page})

    def _resolve_bookmark_page(self, reader: PdfReader, item: Any) -> int:
        """Resolve a bookmark's 1-based page number with fallbacks."""
        # Primary: use reader API when available
        if hasattr(reader, "get_destination_page_number"):
            try:
                idx = reader.get_destination_page_number(item)
                return int(idx) + 1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass

        try:
            if hasattr(item, "page") and item.page is not None:
                page_ref = item.page
                # Direct index if the page object is the same reference
                try:
                    return reader.pages.index(page_ref) + 1
                except (ValueError, TypeError):
                    pass
                # Match by indirect reference id if available
                try:
                    target_id = getattr(page_ref, "idnum", None)
                    if target_id is not None:
                        for i, page in enumerate(reader.pages):
                            ind = getattr(page, "indirect_reference", None)
                            if (
                                ind is not None
                                and getattr(ind, "idnum", None) == target_id
                            ):
                                return i + 1
                except AttributeError:
                    pass
        except AttributeError:
            pass
        return 1
