#!/usr/bin/env python3
"""End-to-end: approving new bookmarks adds a linked, correctly-named row (#2)."""

import tempfile
from pathlib import Path

from openpyxl import Workbook
from pypdf import PdfWriter

from adapters.excel_repo import ExcelOpenpyxlRepo
from adapters.pdf_repo import PypdfPdfRepo
from core.pipeline.context import PipelineContext
from core.pipeline.steps.load_step import LoadStep
from core.pipeline.steps.validate_step import ValidateStep
from core.transform.pdf import make_titles


class _Logger:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass


class _YesUI:
    def prompt_add_new_bookmarks(self, bookmark_titles):
        return True


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


def test_approved_new_bookmark_is_added_linked_and_named():
    excel_repo, pdf_repo, logger = ExcelOpenpyxlRepo(), PypdfPdfRepo(), _Logger()
    with tempfile.TemporaryDirectory() as d:
        xlsx, pdf = _make_files(Path(d))
        ctx = PipelineContext(
            file_pairs=[(xlsx, pdf, "Sheet")],
            options={"sheet_name": "Sheet", "backup": False},
        )

        ValidateStep(excel_repo, pdf_repo, logger, _YesUI()).execute(ctx)
        assert ctx.new_bookmark_titles == {"Merger 2014"}

        LoadStep(excel_repo, pdf_repo, logger, None).execute(ctx)

        # The new row exists with the bookmark name as Document Type.
        merger_rows = ctx.df[ctx.df["Document Type"] == "Merger 2014"]
        assert len(merger_rows) == 1

        # All three bookmarks now link to rows (the orphan is no longer skipped).
        assert len(ctx.document_units) == 3

        # The bookmark name follows the convention with N/A for the blank date.
        titles = make_titles(ctx.df)
        new_doc_id = str(merger_rows.iloc[0]["Document_ID"])
        assert titles[new_doc_id] == "3-Merger 2014-N/A"
