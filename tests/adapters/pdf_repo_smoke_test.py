#!/usr/bin/env python3
"""
Smoke/Parity test for PdfPyPDF2Repo bookmark read/write.

Creates a small PDF with blank pages, writes bookmarks, reads them back,
and asserts title order/content parity.
"""

from pathlib import Path
import tempfile

from PyPDF2 import PdfReader, PdfWriter

from adapters.pdf_repo import PdfPyPDF2Repo, PdfRepoEngine


def test_pdf_bookmark_parity_roundtrip(pdf_engine_env):
    # Create a temporary source PDF with 3 blank pages
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as src_tmp:
        src_path = Path(src_tmp.name)

    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_blank_page(width=200, height=200)
    writer.add_blank_page(width=200, height=200)
    with open(src_path, "wb") as fh:
        writer.write(fh)

    # Read pages from source using the configured repo engine
    repo = PdfRepoEngine()
    pages = repo.pages(str(src_path))

    # Define bookmarks to write (titles in order, 1-based page refs)
    expected_titles = ["1-Doc-A-1/1/2024", "2-Doc-B-1/2/2024", "3-Doc-C-1/3/2024"]
    bookmarks = [
        {"title": expected_titles[0], "page": 1},
        {"title": expected_titles[1], "page": 2},
        {"title": expected_titles[2], "page": 3},
    ]

    # Write bookmarks to an output PDF using the adapter
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as out_tmp:
        out_path = Path(out_tmp.name)

    repo.write(pages=pages, bookmarks=bookmarks, out_path=str(out_path))

    # Read back and verify title order and content
    roundtrip_bookmarks, _ = repo.read(str(out_path))
    roundtrip_titles = [b.get("title", "") for b in roundtrip_bookmarks]
    assert roundtrip_titles == expected_titles
