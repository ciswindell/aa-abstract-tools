#!/usr/bin/env python3
"""
Excel repository adapter using pandas and openpyxl.

Loads a worksheet into a DataFrame and saves DataFrame values
back into an existing workbook template and sheet, then applies
formatting via `ExcelFormatter`.
"""

from typing import List, Optional

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from fileops.files import atomic_write_with_template

from utils.bookmark_formulas import (
    apply_bookmark_formulas,
    detect_bookmark_column,
    has_bookmark_formulas,
)


class ExcelOpenpyxlRepo:
    """Concrete ExcelRepo implementation using pandas/openpyxl."""

    def load(self, path: str, sheet: Optional[str]) -> pd.DataFrame:
        """Load a worksheet into a DataFrame (values as strings)."""
        return pd.read_excel(path, dtype=str, sheet_name=sheet)

    def _write_dataframe_to_workbook(
        self,
        temp_path: str,
        df: pd.DataFrame,
        target_sheet: str,
        bookmark_col_name: Optional[str],
    ) -> None:
        """Write DataFrame to workbook and apply bookmark formulas if needed."""
        wb = load_workbook(temp_path)
        try:
            # Find target sheet
            lower_to_name = {name.lower(): name for name in wb.sheetnames}
            sheet_name = lower_to_name.get(str(target_sheet).lower())
            if not sheet_name:
                raise RuntimeError(
                    f"Processing sheet '{target_sheet}' not found in output workbook"
                )
            ws = wb[sheet_name]

            # Build header map
            header_values = [
                "" if cell.value is None else str(cell.value).strip() for cell in ws[1]
            ]
            header_to_col = {
                h.lower(): idx + 1 for idx, h in enumerate(header_values) if h != ""
            }

            # Write DataFrame values
            for df_col in df.columns:
                if (
                    bookmark_col_name
                    and str(df_col).strip().lower() == bookmark_col_name.strip().lower()
                ):
                    continue  # Skip bookmark formula column
                col_idx = header_to_col.get(str(df_col).strip().lower())
                if col_idx:
                    for row_idx, value in enumerate(df[df_col].tolist(), start=2):
                        ws.cell(row=row_idx, column=col_idx, value=value)

            # Clear fills and save
            empty_fill = PatternFill(fill_type=None)
            for row in ws.iter_rows(
                min_row=1, max_row=ws.max_row, max_col=ws.max_column
            ):
                for cell in row:
                    cell.fill = empty_fill
            wb.save(temp_path)
        finally:
            wb.close()

        # Apply bookmark formulas if needed
        if bookmark_col_name and not has_bookmark_formulas(
            temp_path, bookmark_col_name
        ):
            apply_bookmark_formulas(temp_path, df, bookmark_col_name)

    def save(
        self,
        df: pd.DataFrame,
        template_path: str,
        target_sheet: str,
        out_path: str,
    ) -> None:
        """Atomically write DataFrame values into the workbook template and sheet.

        Preserves any bookmark formula column by not overwriting its cells and
        delegating formula application to ExcelFormatter.
        """

        if not target_sheet:
            raise RuntimeError("Target sheet name not provided")

        # Detect bookmark formula column name in the DataFrame
        bookmark_col_name = detect_bookmark_column(df)

        def _write_into(temp_path: str) -> None:
            self._write_dataframe_to_workbook(
                temp_path, df, target_sheet, bookmark_col_name
            )

        atomic_write_with_template(
            template_path=template_path,
            out_path=out_path,
            write_into_path=_write_into,
        )
