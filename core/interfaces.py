#!/usr/bin/env python3
"""
Interfaces (Protocols) for core services and adapters.

Defines minimal contracts to decouple UI and IO from core logic.
"""

from typing import Any, Mapping, Optional, Protocol, Sequence, Tuple, List

import pandas as pd


class Logger(Protocol):
    """Minimal logger used by application services."""

    def info(self, message: str) -> None:
        """Log an informational message."""

    def error(self, message: str) -> None:
        """Log an error message."""


class ExcelRepo(Protocol):
    """Excel repository for loading and saving workbooks."""

    def load(self, path: str, sheet: Optional[str]) -> pd.DataFrame:
        """Load a worksheet into a DataFrame."""

    def save(
        self, df: pd.DataFrame, template_path: str, target_sheet: str, out_path: str
    ) -> None:
        """Save DataFrame into an existing workbook template and sheet."""


class PdfRepo(Protocol):
    """PDF repository for reading and writing PDFs with bookmarks."""

    def read(self, path: str) -> Tuple[List[Mapping[str, Any]], int]:
        """Return (bookmarks, total_pages)."""

    def pages(self, path: str) -> Sequence[Any]:
        """Return a sequence of page objects for the given PDF path."""

    def write(
        self,
        pages: Sequence[Any],
        bookmarks: Sequence[Mapping[str, Any]],
        out_path: str,
    ) -> None:
        """Write pages and bookmarks to output PDF path."""
