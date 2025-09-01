#!/usr/bin/env python3
"""
Interfaces (Protocols) for core services and adapters.

Defines minimal contracts to decouple UI and IO from core logic.
"""

from typing import Any, List, Mapping, Optional, Protocol, Sequence, Tuple

import pandas as pd

from core.models import Options


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

    def get_sheet_names(self, path: str) -> List[str]:
        """Get list of sheet names in the Excel file."""

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


class UIController(Protocol):
    """Interface for UI controllers that handle user interactions."""

    def get_file_paths(self) -> Tuple[Optional[str], Optional[str]]:
        """Get selected Excel and PDF file paths."""

    def get_options(self) -> Options:
        """Get processing options from UI."""

    def log_status(self, message: str) -> None:
        """Log a status message to the UI."""

    def show_error(self, title: str, message: str) -> None:
        """Show an error message to the user."""

    def show_success(self, message: str) -> None:
        """Show a success message to the user."""

    def prompt_sheet_selection(
        self,
        file_path: str,
        sheet_names: List[str],
        default_sheet: Optional[str] = None,
    ) -> Optional[str]:
        """Prompt user to select a sheet from available options."""

    def prompt_filter_selection(
        self, df: pd.DataFrame
    ) -> Tuple[Optional[str], List[str]]:
        """Prompt user to pick a filter column and values; returns (column, values).

        Returns (None, []) if the user cancels.
        """

    def prompt_merge_pairs(self) -> Optional[List[Tuple[str, str]]]:
        """Prompt user to select one or more (Excel, PDF) pairs for merge.

        Returns None if the user cancels.
        """
