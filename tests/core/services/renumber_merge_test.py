#!/usr/bin/env python3
"""
Unit tests for merge behavior in RenumberService (PDF bookmark ordering).
"""

from typing import Any, List, Mapping, Optional, Sequence, Tuple

import pandas as pd

from core.interfaces import ExcelRepo, Logger, PdfRepo
from core.models import Options, Result
from core.services.renumber import RenumberService
from core.services.validate import ValidationService


class _MemoryLogger:
    def __init__(self) -> None:
        self.messages: List[str] = []

    def info(self, message: str) -> None:  # noqa: D401 - simple logger
        self.messages.append(f"INFO {message}")

    def error(self, message: str) -> None:  # noqa: D401 - simple logger
        self.messages.append(f"ERROR {message}")


class _FakeExcelRepo(ExcelRepo):
    def __init__(self, data_by_path: Mapping[str, pd.DataFrame]) -> None:
        self._data = data_by_path
        self.saved: Optional[Tuple[pd.DataFrame, str]] = None

    def load(self, path: str, sheet: Optional[str]) -> pd.DataFrame:
        return self._data[path].copy()

    def save(
        self, df: pd.DataFrame, template_path: str, target_sheet: str, out_path: str
    ) -> None:
        self.saved = (df.copy(), out_path)


class _FakePdfRepo(PdfRepo):
    def __init__(
        self, bookmarks_by_path: Mapping[str, List[Mapping[str, Any]]]
    ) -> None:
        self._bookmarks = bookmarks_by_path
        self.written: Optional[Tuple[List[Any], List[Mapping[str, Any]], str]] = None

    def read(self, path: str) -> Tuple[List[Mapping[str, Any]], int]:
        bms = self._bookmarks[path]
        # Simulate 1 page per bookmark for simplicity
        total = max([int(b.get("page", 1)) for b in bms]) if bms else 0
        return (bms, total)

    def pages(self, path: str) -> Sequence[Any]:
        # Not used in merge non-reorder path, but return placeholders
        bms = self._bookmarks[path]
        return [f"{path}-p{int(b.get('page', 1))}" for b in bms]

    def write(
        self,
        pages: Sequence[Any],
        bookmarks: Sequence[Mapping[str, Any]],
        out_path: str,
    ) -> None:
        self.written = (list(pages), list(bookmarks), out_path)


def _make_df(index_values: List[str], dates: List[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Index#": index_values,
            "Document Type": ["Doc"] * len(index_values),
            "Legal Description": ["L"] * len(index_values),
            "Grantee": ["G"] * len(index_values),
            "Grantor": ["R"] * len(index_values),
            "Document Date": dates,
            "Received Date": dates,
        }
    )


def _extract_indices(bookmarks: List[Mapping[str, Any]]) -> List[int]:
    out: List[int] = []
    for bm in bookmarks:
        title = str(bm.get("title", ""))
        try:
            num = int(title.split("-", 1)[0])
            out.append(num)
        except Exception:
            continue
    return out


def _setup_merge_service(
    sort_bookmarks: bool,
) -> Tuple[RenumberService, Options, _FakePdfRepo]:
    # Pair A: dates 1,3,5; Pair B: dates 2,4,6 (interleave after global sort)
    df_a = _make_df(["1", "2", "3"], ["2024-01-01", "2024-01-03", "2024-01-05"])
    df_b = _make_df(["1", "2", "3"], ["2024-01-02", "2024-01-04", "2024-01-06"])

    excel_repo = _FakeExcelRepo({"A.xlsx": df_a, "B.xlsx": df_b})

    bookmarks_a = [
        {"title": "1-X", "page": 1, "level": 0},
        {"title": "2-X", "page": 2, "level": 0},
        {"title": "3-X", "page": 3, "level": 0},
    ]
    bookmarks_b = [
        {"title": "1-X", "page": 1, "level": 0},
        {"title": "2-X", "page": 2, "level": 0},
        {"title": "3-X", "page": 3, "level": 0},
    ]
    pdf_repo = _FakePdfRepo({"A.pdf": bookmarks_a, "B.pdf": bookmarks_b})

    required = [
        "Index#",
        "Document Type",
        "Legal Description",
        "Grantee",
        "Grantor",
        "Document Date",
        "Received Date",
    ]
    validator = ValidationService(required)
    logger = _MemoryLogger()

    service = RenumberService(excel_repo, pdf_repo, validator, logger)
    opts = Options(
        backup=False,
        sort_bookmarks=sort_bookmarks,
        reorder_pages=False,
        sheet_name="Index",
        filter_enabled=False,
        filter_column=None,
        filter_values=None,
        merge_pairs=[("A.xlsx", "A.pdf"), ("B.xlsx", "B.pdf")],
        merge_pairs_with_sheets=[
            ("A.xlsx", "A.pdf", "Index"),
            ("B.xlsx", "B.pdf", "Index"),
        ],
    )
    return service, opts, pdf_repo


def test_merge_without_sort_keeps_concatenation_order_but_relabels() -> None:
    service, opts, pdf_repo = _setup_merge_service(sort_bookmarks=False)
    result: Result = service.run("A.xlsx", "A.pdf", opts)
    assert result.success
    assert pdf_repo.written is not None
    _, bookmarks, _ = pdf_repo.written
    order = _extract_indices(bookmarks)
    # Expect concatenation order but titles reflect global renumber: 1,3,5, then 2,4,6
    assert order == [1, 3, 5, 2, 4, 6]


def test_merge_with_sort_naturally_orders_bookmarks() -> None:
    service, opts, pdf_repo = _setup_merge_service(sort_bookmarks=True)
    result: Result = service.run("A.xlsx", "A.pdf", opts)
    assert result.success
    assert pdf_repo.written is not None
    _, bookmarks, _ = pdf_repo.written
    order = _extract_indices(bookmarks)
    assert order == [1, 2, 3, 4, 5, 6]
