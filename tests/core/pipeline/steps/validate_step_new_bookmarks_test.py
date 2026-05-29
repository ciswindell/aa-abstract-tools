#!/usr/bin/env python3
"""ValidateStep behavior for orphaned bookmarks with the Yes/No prompt (#2)."""

import tempfile
from pathlib import Path

import pytest
from openpyxl import Workbook
from pypdf import PdfWriter

from adapters.excel_repo import ExcelOpenpyxlRepo
from adapters.pdf_repo import PypdfPdfRepo
from core.pipeline.context import PipelineContext
from core.pipeline.steps.validate_step import ValidateStep


class _Logger:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass


class _StubUI:
    """UI stub that records the prompt and returns a fixed answer."""

    def __init__(self, answer: bool):
        self.answer = answer
        self.asked_with: list[str] | None = None

    def prompt_add_new_bookmarks(self, bookmark_titles):
        self.asked_with = list(bookmark_titles)
        return self.answer


def _make_files(tmp: Path):
    xlsx = tmp / "in.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet"
    ws.append(
        [
            "Index#",
            "Document Type",
            "Received Date",
            "Legal Description",
            "Grantee",
            "Grantor",
            "Document Date",
        ]
    )
    ws.append([1, "Deed", "2020-01-01", "L1", "A", "B", "2020-01-01"])
    ws.append([2, "Release", "2020-02-02", "L2", "C", "D", "2020-02-02"])
    wb.save(xlsx)

    pdf = tmp / "in.pdf"
    w = PdfWriter()
    for _ in range(3):
        w.add_blank_page(width=200, height=200)
    w.add_outline_item("1-Deed-1/1/2020", 0)
    w.add_outline_item("2-Release-2/2/2020", 1)
    w.add_outline_item("Merger 2014", 2)  # orphan
    with open(pdf, "wb") as fh:
        w.write(fh)
    return str(xlsx), str(pdf)


def _context(xlsx, pdf):
    return PipelineContext(
        file_pairs=[(xlsx, pdf, "Sheet")],
        options={"sheet_name": "Sheet", "backup": False},
    )


def test_yes_records_titles_and_does_not_raise():
    with tempfile.TemporaryDirectory() as d:
        xlsx, pdf = _make_files(Path(d))
        ctx = _context(xlsx, pdf)
        ui = _StubUI(answer=True)
        step = ValidateStep(ExcelOpenpyxlRepo(), PypdfPdfRepo(), _Logger(), ui)
        step.execute(ctx)
        assert ctx.new_bookmark_titles == {"Merger 2014"}
        assert ui.asked_with == ["Merger 2014"]


def test_no_raises_current_error():
    with tempfile.TemporaryDirectory() as d:
        xlsx, pdf = _make_files(Path(d))
        ctx = _context(xlsx, pdf)
        step = ValidateStep(
            ExcelOpenpyxlRepo(), PypdfPdfRepo(), _Logger(), _StubUI(False)
        )
        with pytest.raises(ValueError, match="no matching Excel row"):
            step.execute(ctx)
        assert ctx.new_bookmark_titles is None


def test_no_ui_raises_current_error():
    with tempfile.TemporaryDirectory() as d:
        xlsx, pdf = _make_files(Path(d))
        ctx = _context(xlsx, pdf)
        step = ValidateStep(ExcelOpenpyxlRepo(), PypdfPdfRepo(), _Logger(), None)
        with pytest.raises(ValueError, match="no matching Excel row"):
            step.execute(ctx)
