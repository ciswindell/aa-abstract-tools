#!/usr/bin/env python3
"""
Regression test for nested outline flattening (issue #1).

A PDF whose outline contains sub-bookmarks (nested under parent/section
entries) must be flattened into a single ordered bookmark list at read time,
so downstream linking/renumbering sees every bookmark regardless of depth.
"""

import tempfile
from pathlib import Path

from pypdf import PdfWriter

from adapters.pdf_repo import PdfRepo


def _build_nested_pdf(path: Path) -> None:
    """Create a PDF with a multi-level nested outline.

    Section A                       (level 0, page 1)
        1-Deed-1/1/2020             (level 1, page 2)
            1a-Exhibit-1/3/2020     (level 2, page 3)  -- grandchild
        2-Release-2/2/2020          (level 1, page 4)
    Section B                       (level 0, page 5)
        Merger 2014                 (level 1, page 6)  -- unformatted (issue #2)
    """
    writer = PdfWriter()
    for _ in range(6):
        writer.add_blank_page(width=200, height=200)

    sec_a = writer.add_outline_item("Section A", 0)
    deed = writer.add_outline_item("1-Deed-1/1/2020", 1, parent=sec_a)
    writer.add_outline_item("1a-Exhibit-1/3/2020", 2, parent=deed)
    writer.add_outline_item("2-Release-2/2/2020", 3, parent=sec_a)
    sec_b = writer.add_outline_item("Section B", 4)
    writer.add_outline_item("Merger 2014", 5, parent=sec_b)

    with open(path, "wb") as fh:
        writer.write(fh)


def test_read_flattens_nested_outline():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = Path(tmp.name)

    try:
        _build_nested_pdf(pdf_path)

        bookmarks, pages = PdfRepo().read(str(pdf_path))

        assert pages == 6

        # Every bookmark at every depth is present, in document order.
        titles = [b["title"] for b in bookmarks]
        assert titles == [
            "Section A",
            "1-Deed-1/1/2020",
            "1a-Exhibit-1/3/2020",
            "2-Release-2/2/2020",
            "Section B",
            "Merger 2014",
        ]

        # Nesting depth is preserved in the flattened entries.
        levels = {b["title"]: b["level"] for b in bookmarks}
        assert levels["Section A"] == 0
        assert levels["1-Deed-1/1/2020"] == 1
        assert levels["1a-Exhibit-1/3/2020"] == 2  # grandchild fully flattened
        assert levels["Section B"] == 0
        assert levels["Merger 2014"] == 1

        # Page targets survive flattening (1-based).
        pages_by_title = {b["title"]: b["page"] for b in bookmarks}
        assert pages_by_title["1-Deed-1/1/2020"] == 2
        assert pages_by_title["1a-Exhibit-1/3/2020"] == 3
        assert pages_by_title["Merger 2014"] == 6
    finally:
        pdf_path.unlink(missing_ok=True)
