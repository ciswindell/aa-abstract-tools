#!/usr/bin/env python3
"""
Excel repository adapter using pandas and openpyxl.

Loads a worksheet into a DataFrame and saves DataFrame values
back into an existing workbook template and sheet, then applies
formatting via `ExcelFormatter`.
"""

from typing import Dict, List, Optional

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
            wb = load_workbook(temp_path)
            try:
                lower_to_name: Dict[str, str] = {
                    name.lower(): name for name in wb.sheetnames
                }
                sheet_name = lower_to_name.get(str(target_sheet).lower())
                if not sheet_name:
                    raise RuntimeError(
                        f"Processing sheet '{target_sheet}' not found in output workbook"
                    )
                ws = wb[sheet_name]

                # Build header map (1-based index)
                header_values: List[str] = [
                    "" if cell.value is None else str(cell.value).strip()
                    for cell in ws[1]
                ]
                header_to_col: Dict[str, int] = {
                    h.lower(): idx + 1 for idx, h in enumerate(header_values) if h != ""
                }

                # Check if bookmark column needs formulas
                apply_formulas_flag = bookmark_col_name and not has_bookmark_formulas(
                    temp_path, bookmark_col_name
                )

                # Write values by matching header names
                for df_col in df.columns:
                    # Keep formulas: do not write values into the bookmark formula column
                    if (
                        bookmark_col_name
                        and str(df_col).strip().lower()
                        == bookmark_col_name.strip().lower()
                    ):
                        continue
                    col_idx = header_to_col.get(str(df_col).strip().lower())
                    if not col_idx:
                        continue
                    values = df[df_col].tolist()
                    for row_idx, value in enumerate(values, start=2):
                        ws.cell(row=row_idx, column=col_idx, value=value)

                # Ensure target sheet is active for downstream formatting
                try:
                    wb.active = wb.sheetnames.index(ws.title)
                except Exception:
                    pass

                # Clear hard-coded fills (reset temporary highlights), keep CF rules
                empty_fill = PatternFill(fill_type=None)
                for row in ws.iter_rows(
                    min_row=2, max_row=ws.max_row, max_col=ws.max_column
                ):
                    for cell in row:
                        cell.fill = empty_fill

                # Save workbook with updated values
                wb.save(temp_path)
            finally:
                wb.close()

            # Apply bookmark formulas if needed
            if apply_formulas_flag and bookmark_col_name:
                apply_bookmark_formulas(temp_path, df, bookmark_col_name)

        atomic_write_with_template(
            template_path=template_path,
            out_path=out_path,
            write_into_path=_write_into,
        )
