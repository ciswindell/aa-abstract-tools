#!/usr/bin/env python3
"""
PDF repository adapter with a pluggable backend (default: pypdf).

Provides bookmark reading and writing while keeping calling code
independent of backend types.
"""

import contextlib
from collections.abc import Mapping, Sequence
from typing import Any

# pypdf backend imports
from pypdf import PdfReader as PyPdfReader
from pypdf import PdfWriter as PyPdfWriter
from pypdf.generic import Fit as PyPdfFit


class PypdfPdfRepo:
    """PDF repository using pypdf for read/pages/write with bookmarks."""

    def read(self, path: str) -> tuple[list[Mapping[str, Any]], int]:
        reader = PyPdfReader(path)
        pages_count = len(reader.pages)
        outline = getattr(reader, "outline", None)
        if not outline:
            outline = getattr(reader, "outlines", None)
        if not outline:
            return [], pages_count

        bookmarks: list[dict[str, Any]] = []
        self._parse_outline(reader, outline, bookmarks, level=0)
        return bookmarks, pages_count

    def pages(self, path: str) -> Sequence[Any]:
        reader = PyPdfReader(path)
        return list(reader.pages)

    def write(
        self,
        pages: Sequence[Any],
        bookmarks: Sequence[Mapping[str, Any]],
        out_path: str,
    ) -> None:
        writer = PyPdfWriter()
        for p in pages:
            try:
                writer.add_page(p)
            except (TypeError, ValueError, AttributeError):
                continue

        with contextlib.suppress(AttributeError):
            writer.page_mode = "/UseOutlines"

        for bm in bookmarks:
            title = str(bm.get("title", ""))
            page_num = int(bm.get("page", 1)) - 1
            if 0 <= page_num < len(writer.pages):
                try:
                    fit = PyPdfFit.xyz(left=None, top=None, zoom=None)
                    writer.add_outline_item(title, page_num, fit=fit)
                except (ValueError, TypeError, AttributeError, IndexError):
                    continue

        with open(out_path, "wb") as fh:
            writer.write(fh)

    def _parse_outline(
        self,
        reader: PyPdfReader,
        outline: list[Any],
        bookmarks: list[dict[str, Any]],
        level: int,
    ) -> None:
        for item in outline:
            if isinstance(item, list):
                self._parse_outline(reader, item, bookmarks, level + 1)
            else:
                title = getattr(item, "title", "")
                page = self._resolve_bookmark_page(reader, item)
                bookmarks.append({"title": title, "level": level, "page": page})

    def _resolve_bookmark_page(self, reader: PyPdfReader, item: Any) -> int:
        if hasattr(reader, "get_destination_page_number"):
            try:
                idx = reader.get_destination_page_number(item)
                return int(idx) + 1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
        try:
            if hasattr(item, "page") and item.page is not None:
                page_ref = item.page
                try:
                    return reader.pages.index(page_ref) + 1
                except (ValueError, TypeError):
                    pass
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


# Backwards compatibility alias
PdfRepo = PypdfPdfRepo
