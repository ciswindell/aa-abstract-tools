#!/usr/bin/env python3
"""
Excel repository adapter using pandas and openpyxl.

Loads a worksheet into a DataFrame and saves DataFrame values
back into an existing workbook template and sheet, then applies
formatting via `ExcelFormatter`.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from fileops.files import atomic_write_with_template

from excel_formatter import ExcelFormatter


@dataclass
class _ColumnInfoLite:
    """Lightweight column metadata to satisfy ExcelFormatter expectations."""

    original_name: str
    current_name: str
    position: int  # 0-based worksheet column index
    width: float = 15.0
    horizontal_alignment: str = "left"
    vertical_alignment: str = "top"


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

        # Detect bookmark formula column name in the DataFrame (by header text)
        def _detect_bookmark_col_name() -> Optional[str]:
            candidates = ["Bookmark Formula", "Bookmark", "Bookmark Text", "Formula"]
            for col in df.columns:
                for name in candidates:
                    if name.lower() in str(col).lower():
                        return str(col)
            return None

        bookmark_col_name = _detect_bookmark_col_name()

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

                # Detect if bookmark formula column already contains formulas in template
                apply_formulas_flag: bool = False
                if bookmark_col_name:
                    b_idx = header_to_col.get(bookmark_col_name.strip().lower())
                    if b_idx:
                        cell = ws.cell(row=2, column=b_idx)
                        has_formula = False
                        try:
                            has_formula = (getattr(cell, "data_type", None) == "f") or (
                                isinstance(cell.value, str)
                                and cell.value.startswith("=")
                            )
                        except Exception:
                            has_formula = False
                        apply_formulas_flag = not has_formula

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

            # Prepare columns metadata for formatter based on worksheet positions
            columns_meta: List[_ColumnInfoLite] = []
            # Re-open read-only to compute positions reliably
            wbr = load_workbook(temp_path, read_only=True, data_only=True)
            try:
                ws_r = wbr[target_sheet]
                header_values_r: List[str] = [
                    "" if cell.value is None else str(cell.value).strip()
                    for cell in ws_r[1]
                ]
                header_to_col_r: Dict[str, int] = {
                    h.lower(): idx + 1
                    for idx, h in enumerate(header_values_r)
                    if h != ""
                }
                for df_pos, name in enumerate(df.columns):
                    key = str(name).strip().lower()
                    col_idx = header_to_col_r.get(key, df_pos + 1)
                    columns_meta.append(
                        _ColumnInfoLite(
                            original_name=name,
                            current_name=name,
                            position=col_idx - 1,
                        )
                    )
            finally:
                wbr.close()

            # Apply only formulas if needed; otherwise rely entirely on template formatting
            if apply_formulas_flag:
                formatter = ExcelFormatter(
                    columns_meta, bookmark_formula_column=bookmark_col_name
                )
                try:
                    formatter.apply_formulas_only(temp_path, df)
                except AttributeError:
                    # Fallback to full formatting if helper not available
                    formatter.apply_formatting(temp_path, df)

        atomic_write_with_template(
            template_path=template_path,
            out_path=out_path,
            write_into_path=_write_into,
        )
