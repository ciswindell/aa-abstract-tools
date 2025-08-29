#!/usr/bin/env python3
"""
Validation service that composes Excel and PDF validators.

Raises ValueError for hard validation failures per PRD.
"""

from typing import Any, Dict, List, Mapping, Optional

import pandas as pd

from validators.input_sheet_validator import validate as validate_sheet
from validators.pdf_validator import PDFValidator


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
            duplicate_columns = sheet_results.get("duplicate_columns", [])
            duplicate_base_names = sheet_results.get("duplicate_base_names", [])
            duplicate_indices = sheet_results.get("duplicate_indices", [])
            has_auto_renamed = bool(sheet_results.get("has_auto_renamed", False))

            if missing or duplicate_columns or duplicate_indices:
                details: List[str] = []
                if duplicate_columns:
                    if has_auto_renamed and duplicate_base_names:
                        base_list = "\n".join(
                            f"  • '{name}'" for name in duplicate_base_names
                        )
                        details.append(
                            f"Your Excel file has duplicate column names:\n{base_list}\n\n"
                            f"Please rename the duplicate columns so each column has a unique name."
                        )
                    else:
                        duplicate_list = "\n".join(
                            f"  • '{dup}'" for dup in duplicate_columns
                        )
                        details.append(
                            f"Duplicate column names found:\n{duplicate_list}\n\n"
                            f"Please rename the duplicate columns so each column has a unique name."
                        )
                if missing:
                    details.append("Missing required columns: " + ", ".join(missing))
                if duplicate_indices:
                    duplicate_list = ", ".join(f"'{dup}'" for dup in duplicate_indices)
                    details.append(
                        f"Excel validation failed: Duplicate Index# values found: {duplicate_list}. "
                        f"Each row must have a unique Index# value. Please check your Excel file and remove or rename duplicate entries."
                    )
                raise ValueError("; ".join(details))
            report["excel"] = {"ok": True}

        if bookmarks is not None:
            # Check for page conflicts
            conflicts = PDFValidator.validate_bookmark_page_conflicts(list(bookmarks))
            if conflicts and conflicts.get("conflicts"):
                formatted = "; ".join(
                    f"page {c.get('page')}: {', '.join(c.get('bookmarks', []))}"
                    for c in conflicts.get("conflicts", [])
                )
                raise ValueError("PDF bookmark conflicts detected: " + formatted)

            # Check for duplicate bookmark indices (PRD requirement #3)
            index_duplicates = PDFValidator.validate_bookmark_index_duplicates(
                list(bookmarks)
            )
            if index_duplicates and index_duplicates.get("duplicate_groups"):
                duplicate_groups = index_duplicates.get("duplicate_groups", [])

                # Build simple error message showing all problematic bookmarks
                error_parts = ["These bookmarks have duplicate index numbers:\n"]

                for group in duplicate_groups:
                    titles = group["titles"]
                    for title in titles:
                        error_parts.append(f"\n  • {title}")

                error_parts.append(
                    f"\n\nEach bookmark must have a unique index number at the beginning of its title. "
                    f"Please check your PDF bookmarks and ensure no index numbers are repeated."
                )

                raise ValueError("".join(error_parts))

            report["pdf"] = {"ok": True}

        return report
