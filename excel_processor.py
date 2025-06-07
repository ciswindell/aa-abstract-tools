#!/usr/bin/env python3
"""
Excel processing module for the Abstract Renumber Tool.
Handles Excel file loading, validation, and data operations.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
from openpyxl import load_workbook

from excel_formatter import ExcelFormatter


@dataclass
class ColumnInfo:
    """Track all information about a column through the processing pipeline."""

    original_name: str  # Original name from source file
    current_name: str  # Current name after any mapping
    position: int  # Column position (0-based)
    width: float  # Column width from source
    horizontal_alignment: str = (
        "left"  # Horizontal alignment (left, center, right, general)
    )
    vertical_alignment: str = "top"  # Vertical alignment (top, center, bottom)
    excel_letter: str = ""  # Excel column letter (A, B, C, etc.)

    def __post_init__(self):
        """Calculate Excel letter from position."""
        if not self.excel_letter:
            self.excel_letter = self._position_to_excel_letter(self.position)

    def _position_to_excel_letter(self, pos: int) -> str:
        """Convert position to Excel column letter (0=A, 1=B, etc.)."""
        result = ""
        col = pos
        while col >= 0:
            result = chr(col % 26 + ord("A")) + result
            col = col // 26 - 1
        return result


class ExcelProcessor:
    """Handles Excel file operations and validation."""

    def __init__(self, required_columns: List[str]):
        self.required_columns = required_columns
        self.df: Optional[pd.DataFrame] = None
        self.original_file_path: Optional[str] = None
        self.processed_columns = set()  # Track which columns we've modified
        self.bookmark_formula_column: Optional[str] = None
        self.columns: List[ColumnInfo] = []  # Complete column information
        self.source_column_widths_by_position = (
            {}
        )  # Store original column widths by position

    def load_file(self, file_path: str) -> bool:
        """Load Excel file with basic validation."""
        try:
            # Load Excel file
            self.df = pd.read_excel(file_path, dtype=str)
            self.original_file_path = file_path

            if self.df.empty:
                raise ValueError("Excel file contains no data")

            # Initialize column information
            self._initialize_column_info()

            # Add Original_Index column
            self._add_original_index_column()

            # Detect bookmark formula column
            self._detect_bookmark_formula_column()

            # Process data types
            self._process_data_types()

            return True

        except Exception as e:
            raise ValueError(f"Failed to load Excel file: {str(e)}")

    def _initialize_column_info(self) -> None:
        """Initialize column information with source formatting from Excel file."""
        self.columns = []

        # Extract column widths and alignments from source Excel file
        source_widths = self._extract_source_column_widths()
        source_alignments = self._extract_source_alignments()

        # Create ColumnInfo for each column
        for pos, col_name in enumerate(self.df.columns):
            width = source_widths.get(pos, 15.0)  # Default width if not found
            h_align, v_align = source_alignments.get(pos, ("left", "top"))

            col_info = ColumnInfo(
                original_name=col_name,
                current_name=col_name,
                position=pos,
                width=width,
                horizontal_alignment=h_align,
                vertical_alignment=v_align,
                excel_letter="",  # Will be calculated in __post_init__
            )
            self.columns.append(col_info)

    def _extract_source_column_widths(self) -> Dict[int, float]:
        """Extract column widths from source Excel file."""
        widths = {}

        if not self.original_file_path:
            return widths

        try:
            wb = load_workbook(self.original_file_path)
            ws = wb.active

            for pos in range(len(self.df.columns)):
                col_letter = self._get_excel_column_letter(pos)
                width = ws.column_dimensions[col_letter].width
                widths[pos] = width if width else 15.0

            wb.close()
        except:
            # Use defaults if extraction fails
            for pos in range(len(self.df.columns)):
                widths[pos] = 15.0

        return widths

    def _extract_source_alignments(self) -> Dict[int, tuple]:
        """Extract column alignments from source Excel file."""
        alignments = {}

        if not self.original_file_path:
            return alignments

        try:
            wb = load_workbook(self.original_file_path)
            ws = wb.active

            for pos in range(len(self.df.columns)):
                col_letter = self._get_excel_column_letter(pos)
                cell = ws[f"{col_letter}2"]  # Check first data row

                h_align = "left"
                v_align = "top"

                if cell.alignment:
                    if cell.alignment.horizontal:
                        h_align = str(cell.alignment.horizontal)
                    if cell.alignment.vertical:
                        v_align = str(cell.alignment.vertical)

                alignments[pos] = (h_align, v_align)

            wb.close()
        except:
            # Use defaults if extraction fails
            for pos in range(len(self.df.columns)):
                alignments[pos] = ("left", "top")

        return alignments

    def _detect_bookmark_formula_column(self) -> None:
        """Detect which column contains bookmark formulas."""
        if self.df is None:
            return

        # Look for a column that might contain bookmark formulas
        # Common names: "Bookmark", "Bookmark Formula", "Formula", etc.
        possible_names = ["Bookmark", "Bookmark Formula", "Formula", "Bookmark Text"]

        for col in self.df.columns:
            if any(name.lower() in col.lower() for name in possible_names):
                self.bookmark_formula_column = col
                break

    def _get_excel_column_letter(self, col_index: int) -> str:
        """Convert column index to Excel column letter (0=A, 1=B, etc.)."""
        result = ""
        while col_index >= 0:
            result = chr(col_index % 26 + ord("A")) + result
            col_index = col_index // 26 - 1
        return result

    def _process_data_types(self) -> None:
        """Process data types for specific columns to optimize sorting and display."""
        if self.df is None:
            return

        # Convert Index# to numeric if it exists
        if "Index#" in self.df.columns:
            try:
                self.df["Index#"] = pd.to_numeric(self.df["Index#"], errors="coerce")
                self.processed_columns.add("Index#")
            except (ValueError, TypeError):
                pass

        # Convert date columns to datetime if they exist - this is more comprehensive than before
        date_columns = ["Document Date", "Received Date"]
        for col in date_columns:
            if col in self.df.columns:
                try:
                    # Convert to datetime but preserve original format in string representation
                    self.df[col] = pd.to_datetime(self.df[col], errors="coerce")
                    self.processed_columns.add(col)
                except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime):
                    # If conversion fails, keep as string
                    pass

        # Clean text columns
        text_columns = ["Legal Description", "Grantee", "Grantor", "Document Type"]
        for col in text_columns:
            if col in self.df.columns:
                try:
                    # Ensure string type and strip whitespace
                    self.df[col] = self.df[col].astype(str).str.strip()
                    # Handle NaN values
                    self.df[col] = self.df[col].replace("nan", "")
                    self.processed_columns.add(col)
                except (ValueError, TypeError, AttributeError):
                    pass

    def check_duplicate_columns(self) -> List[str]:
        """Check for duplicate column names in the loaded DataFrame."""
        return self.df.columns[self.df.columns.duplicated()].tolist()

    def get_missing_columns(self) -> List[str]:
        """Check for required columns and return list of missing ones."""
        if self.df is None:
            return self.required_columns
        return [col for col in self.required_columns if col not in self.df.columns]

    def apply_column_mapping(self, mapping: Dict[str, str]) -> bool:
        """Apply column name mappings to the DataFrame."""
        # Update column info with new mappings
        for col_info in self.columns:
            if col_info.current_name in mapping:
                col_info.current_name = mapping[col_info.current_name]

        # Apply mappings to DataFrame
        self.df.rename(columns=mapping, inplace=True)

        # Verify all required columns are now present
        still_missing = self.get_missing_columns()
        if still_missing:
            raise ValueError(f"Still missing columns after mapping: {still_missing}")

        # Reprocess data types after column mapping
        self._process_data_types()
        return True

    def get_column_info(self) -> Dict[str, any]:
        """Get information about the loaded DataFrame."""
        if self.df is None:
            return {}

        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": self.df.columns.tolist(),
        }

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the loaded DataFrame.

        Returns:
            Optional[pd.DataFrame]: The loaded pandas DataFrame, or None if no file loaded
        """
        return self.df

    def sort_data(self) -> bool:
        """Sort the DataFrame according to PRD requirements."""
        # Sort order: Received Date, Document Date, Document Type, Grantor, Grantee, Legal Description
        sort_columns = [
            "Received Date",
            "Document Date",
            "Document Type",
            "Grantor",
            "Grantee",
            "Legal Description",
        ]

        # Filter to only include columns that exist in the DataFrame
        existing_sort_columns = [col for col in sort_columns if col in self.df.columns]

        # Handle null/missing values before sorting
        self._handle_missing_values()

        # Ensure proper data types for sorting columns before sorting
        self._prepare_sorting_data_types()

        # Sort by multiple columns - all ascending
        self.df = self.df.sort_values(
            by=existing_sort_columns, ascending=True, na_position="last"
        )
        # Reset index to maintain proper row order
        self.df = self.df.reset_index(drop=True)

        # Renumber Index# column starting from 1
        self._renumber_index()
        return True

    def _prepare_sorting_data_types(self) -> None:
        """Ensure proper data types for sorting columns."""
        # Clean and prepare text columns for proper sorting
        text_columns = ["Legal Description", "Grantee", "Grantor", "Document Type"]
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
                self.df[col] = self.df[col].replace("nan", "")

        # Ensure date columns are properly formatted for sorting
        date_columns = ["Document Date", "Received Date"]
        for col in date_columns:
            if col in self.df.columns:
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors="coerce")
                except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime):
                    self.df[col] = self.df[col].astype(str).str.strip()

    def _renumber_index(self) -> None:
        """Renumber the Index# column starting from 1 and incrementing by 1."""
        if "Index#" in self.df.columns:
            self.df["Index#"] = range(1, len(self.df) + 1)
            self.processed_columns.add("Index#")

    def _handle_missing_values(self) -> None:
        """Handle null/missing values in sorting columns."""
        text_columns = ["Legal Description", "Grantee", "Grantor", "Document Type"]
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna("")
                self.processed_columns.add(col)

    def get_processed_columns(self) -> set:
        """Return set of columns that have been processed/modified.

        Returns:
            set: Set of column names that have been processed or modified
        """
        return self.processed_columns.copy()

    def get_unprocessed_columns(self) -> List[str]:
        """Return list of columns that haven't been processed.

        Returns:
            List[str]: List of column names that have not been processed or modified
        """
        if self.df is None:
            return []
        return [col for col in self.df.columns if col not in self.processed_columns]

    def save_with_formulas(self, output_path: str) -> bool:
        """Save Excel file preserving formatting."""
        # Create output DataFrame
        output_df = self._create_output_dataframe()

        # Save to Excel
        output_df.to_excel(output_path, index=False)

        # Apply formatting
        formatter = ExcelFormatter(self.columns, self.bookmark_formula_column)
        formatter.apply_formatting(output_path, output_df)
        return True

    def _create_output_dataframe(self) -> pd.DataFrame:
        """Create DataFrame with original column names for export, excluding internal columns."""
        output_df = self.df.copy()

        # Remove the Original_Index column - it's only used internally for PDF bookmark mapping
        # and should not appear in the final Excel output
        if "Original_Index" in output_df.columns:
            output_df = output_df.drop(columns=["Original_Index"])

        # Create mapping from current names back to original names
        name_mapping = {}
        for col_info in self.columns:
            # Only include columns that are not internal/temporary columns
            if (
                col_info.current_name in output_df.columns
                and col_info.original_name != "Original_Index"
            ):
                name_mapping[col_info.current_name] = col_info.original_name

        # Rename columns back to original names
        output_df.rename(columns=name_mapping, inplace=True)

        return output_df

    def _find_column_by_current_name(self, current_name: str) -> Optional[ColumnInfo]:
        """Find column info by current (mapped) name."""
        for col_info in self.columns:
            if col_info.current_name == current_name:
                return col_info
        return None

    def get_bookmark_formula_column(self) -> Optional[str]:
        """Return the name of the bookmark formula column if detected.

        Returns:
            Optional[str]: Name of the detected bookmark formula column, or None if not found
        """
        return self.bookmark_formula_column

    def _add_original_index_column(self) -> None:
        """Add Original_Index column to preserve original Index# values for PDF bookmark mapping."""
        if "Index#" in self.df.columns:
            self.df["Original_Index"] = self.df["Index#"].copy()
            self.processed_columns.add("Original_Index")

            # Add column info for Original_Index
            original_index_col_info = ColumnInfo(
                original_name="Original_Index",
                current_name="Original_Index",
                position=len(self.columns),
                width=0,
                horizontal_alignment="left",
                vertical_alignment="top",
                excel_letter="",
            )
            self.columns.append(original_index_col_info)

    def get_original_index_mapping(self) -> Dict[int, int]:
        """Get mapping from original index values to new index values."""
        if (
            self.df is None
            or "Original_Index" not in self.df.columns
            or "Index#" not in self.df.columns
        ):
            return {}

        # Create mapping: original_index -> new_index
        mapping = {}
        for _, row in self.df.iterrows():
            original_idx = int(row["Original_Index"])
            new_idx = int(row["Index#"])
            mapping[original_idx] = new_idx

        return mapping
