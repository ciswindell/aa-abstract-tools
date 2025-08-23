#!/usr/bin/env python3
"""
Validation service that composes Excel and PDF validators.

Raises ValueError for hard validation failures per PRD.
"""

from typing import Any, Dict, List, Mapping, Optional

import pandas as pd

from validators.input_sheet_validator import validate as validate_sheet
from pdf_validator import PDFValidator


class ValidationService:
    """Run composed validations for Excel and PDF inputs."""

    def __init__(self, required_columns: List[str]) -> None:
        """Store required Excel columns for header validation."""

        self.required_columns = required_columns

    def run(
        self,
        df: Optional[pd.DataFrame] = None,
        bookmarks: Optional[List[Mapping[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Validate provided inputs; raise on hard failures.

        Returns a report dict containing details for successful validations.
        """

        report: Dict[str, Any] = {}

        if df is not None:
            sheet_results = validate_sheet(df, self.required_columns)
            missing = sheet_results.get("missing", [])
            dupes = sheet_results.get("duplicates", [])
            if missing or dupes:
                details: List[str] = []
                if missing:
                    details.append("Missing required columns: " + ", ".join(missing))
                if dupes:
                    details.append("Duplicate required columns: " + ", ".join(dupes))
                raise ValueError("; ".join(details))
            report["excel"] = {"ok": True}

        if bookmarks is not None:
            conflicts = PDFValidator.validate_bookmark_page_conflicts(list(bookmarks))
            if conflicts and conflicts.get("conflicts"):
                formatted = "; ".join(
                    f"page {c.get('page')}: {', '.join(c.get('bookmarks', []))}"
                    for c in conflicts.get("conflicts", [])
                )
                raise ValueError("PDF bookmark conflicts detected: " + formatted)
            report["pdf"] = {"ok": True}

        return report
