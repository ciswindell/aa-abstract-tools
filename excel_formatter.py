#!/usr/bin/env python3
"""
Excel formatting module for the Abstract Renumber Tool.
Handles all Excel file formatting operations including alignment, widths, and styling.
"""

from typing import Any, List, Optional

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


class ExcelFormatter:
    """Handles Excel file formatting operations."""

    def __init__(
        self, columns: List[Any], bookmark_formula_column: Optional[str] = None
    ) -> None:
        self.columns = columns
        self.bookmark_formula_column = bookmark_formula_column

    def apply_formatting(self, workbook_path: str, output_df: pd.DataFrame) -> bool:
        """Apply all formatting to the Excel file."""
        try:
            wb = load_workbook(workbook_path)
            ws = wb.active

            # Apply all formatting
            self._apply_cell_alignments(ws, output_df)
            self._apply_text_wrapping(ws, output_df)
            self._apply_date_formatting(ws, output_df)
            self._apply_auto_filters(ws, output_df)
            self._apply_freeze_panes(ws, output_df)

            # Apply bookmark formulas if needed
            if self.bookmark_formula_column:
                self._apply_bookmark_formulas(ws, output_df)

            wb.save(workbook_path)
            wb.close()

            return True

        except Exception as e:
            raise ValueError(f"Failed to apply formatting: {str(e)}")

    def _apply_column_widths(self, worksheet: Worksheet) -> None:
        """Apply column widths from source file."""
        for col_info in self.columns:
            # Skip internal columns that don't appear in final output
            if col_info.original_name == "Original_Index":
                continue

            # Get the actual column letter based on the column's position in the worksheet
            # This ensures we're applying widths to the correct columns
            col_letter = self._get_column_letter_by_position(col_info.position)
            worksheet.column_dimensions[col_letter].width = col_info.width

    def _get_column_letter_by_position(self, position: int) -> str:
        """Convert position to Excel column letter (0=A, 1=B, etc.)."""
        if position < 0:
            return ""

        result = ""
        while position >= 0:
            result = chr(position % 26 + ord("A")) + result
            position = position // 26 - 1
        return result

    def _apply_cell_alignments(
        self, worksheet: Worksheet, output_df: pd.DataFrame
    ) -> None:
        """Apply cell alignments to all cells."""
        for col_info in self.columns:
            # Skip internal columns that don't appear in final output
            if col_info.original_name == "Original_Index":
                continue

            col_letter = self._get_column_letter_by_position(col_info.position)

            # Apply special header row alignment (center/bottom)
            header_cell = worksheet[f"{col_letter}1"]
            header_cell.alignment = Alignment(horizontal="center", vertical="bottom")

            # Apply data row alignment to all data cells in this column
            for row_num in range(2, len(output_df) + 2):  # Skip header row
                cell = worksheet[f"{col_letter}{row_num}"]
                cell.alignment = Alignment(
                    horizontal=col_info.horizontal_alignment,
                    vertical=col_info.vertical_alignment,
                )

    def _apply_text_wrapping(
        self, worksheet: Worksheet, output_df: pd.DataFrame
    ) -> None:
        """Apply text wrapping to all cells while preserving alignment."""
        for col_info in self.columns:
            # Skip internal columns that don't appear in final output
            if col_info.original_name == "Original_Index":
                continue

            col_letter = self._get_column_letter_by_position(col_info.position)

            # Apply text wrapping to header row while preserving center/bottom alignment
            header_cell = worksheet[f"{col_letter}1"]
            header_cell.alignment = Alignment(
                horizontal="center", vertical="bottom", wrapText=True
            )

            # Apply text wrapping to data rows while preserving their alignment
            for row_num in range(2, len(output_df) + 2):  # Skip header row
                cell = worksheet[f"{col_letter}{row_num}"]
                cell.alignment = Alignment(
                    horizontal=col_info.horizontal_alignment,
                    vertical=col_info.vertical_alignment,
                    wrapText=True,
                )

    def _apply_date_formatting(
        self, worksheet: Worksheet, output_df: pd.DataFrame
    ) -> None:
        """Apply M/D/YYYY formatting to date columns."""
        # Define the date format
        date_format = "m/d/yyyy"

        # Find date columns in the column info
        date_column_names = ["Document Date", "Received Date"]

        for col_info in self.columns:
            # Skip internal columns that don't appear in final output
            if col_info.original_name == "Original_Index":
                continue

            # Check if this column is a date column (by current name)
            if col_info.current_name in date_column_names:
                # Apply date formatting to the entire column
                col_letter = self._get_column_letter_by_position(col_info.position)

                # Format all data cells in this column (skip header row)
                for row_num in range(2, len(output_df) + 2):
                    cell = worksheet[f"{col_letter}{row_num}"]
                    cell.number_format = date_format

    def _apply_auto_filters(
        self, worksheet: Worksheet, output_df: pd.DataFrame
    ) -> None:
        """Apply auto-filters to the worksheet."""
        try:
            # Calculate the range for the filter
            # Start from A1 (header row) to the last data row and column
            start_col = 1  # Column A
            end_col = len(output_df.columns)  # Last column
            start_row = 1  # Header row
            end_row = len(output_df) + 1  # Last data row (including header)

            # Create range string (e.g., "A1:G10")
            start_letter = self._get_column_letter_by_position(
                start_col - 1
            )  # Convert to 0-based
            end_letter = self._get_column_letter_by_position(
                end_col - 1
            )  # Convert to 0-based
            range_str = f"{start_letter}{start_row}:{end_letter}{end_row}"

            # Apply auto-filter to the entire range
            worksheet.auto_filter.ref = range_str

        except Exception as e:
            # If auto-filter fails, just continue without it
            print(f"Warning: Could not apply auto-filter: {e}")
            pass

    def _apply_freeze_panes(
        self, worksheet: Worksheet, output_df: pd.DataFrame
    ) -> None:
        """Freeze the top row of the worksheet."""
        try:
            # Freeze the first row (header)
            worksheet.freeze_panes = "A2"
        except Exception as e:
            print(f"Warning: Could not freeze panes: {e}")
            pass

    def _apply_bookmark_formulas(
        self, worksheet: Worksheet, output_df: pd.DataFrame
    ) -> None:
        """Apply bookmark formulas using original column structure."""
        try:
            # Find bookmark column info
            bookmark_col_info = None
            for col_info in self.columns:
                if col_info.current_name == self.bookmark_formula_column:
                    bookmark_col_info = col_info
                    break

            if not bookmark_col_info:
                return

            # Find required column positions in original structure
            index_col_info = self._find_column_by_current_name("Index#")
            doc_type_col_info = self._find_column_by_current_name("Document Type")
            received_date_col_info = self._find_column_by_current_name("Received Date")

            if all([index_col_info, doc_type_col_info, received_date_col_info]):
                # Generate formulas using original column letters
                for row_num in range(2, len(output_df) + 2):
                    formula = (
                        f'={self._get_column_letter_by_position(index_col_info.position)}{row_num}&"-"&'
                        f'{self._get_column_letter_by_position(doc_type_col_info.position)}{row_num}&"-"&'
                        f'TEXT({self._get_column_letter_by_position(received_date_col_info.position)}{row_num},"m/d/yyyy")'
                    )

                    cell = f"{self._get_column_letter_by_position(bookmark_col_info.position)}{row_num}"
                    worksheet[cell] = formula

        except Exception:
            pass  # Skip if bookmark formulas can't be applied

    def _find_column_by_current_name(self, current_name: str) -> Optional[Any]:
        """Find column info by current (mapped) name."""
        for col_info in self.columns:
            if col_info.current_name == current_name:
                return col_info
        return None
