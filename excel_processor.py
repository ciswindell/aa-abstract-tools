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
        """Load Excel file and perform basic validation with proper data type handling.

        Args:
            file_path (str): Path to the Excel file to load

        Returns:
            bool: True if file was loaded successfully

        Raises:
            FileNotFoundError: If Excel file does not exist
            ValueError: If file format is invalid or contains no data
            PermissionError: If file cannot be accessed due to permissions
            ImportError: If required dependencies are missing
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Excel file not found: {file_path}")

            # Load Excel file with proper data type handling
            self.df = pd.read_excel(file_path, dtype=str)
            self.original_file_path = file_path

            # Validate DataFrame is not empty
            if self.df.empty:
                raise ValueError("Excel file contains no data")

            # Initialize column information with source formatting
            self._initialize_column_info()

            # Add Original_Index column to preserve original Index# values for PDF bookmark mapping
            self._add_original_index_column()

            # Detect bookmark formula column
            self._detect_bookmark_formula_column()

            # Process data types for specific columns
            self._process_data_types()

            return True

        except (FileNotFoundError, ValueError, PermissionError) as e:
            raise e
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            raise ValueError(f"Invalid Excel file format: {str(e)}")
        except ImportError as e:
            raise ValueError(f"Required dependencies missing: {str(e)}")

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
        """Extract column widths from source Excel file by position."""
        widths = {}

        if not self.original_file_path:
            return widths

        try:
            wb = load_workbook(self.original_file_path)
            ws = wb.active

            # Extract widths by position
            for pos in range(len(self.df.columns)):
                col_letter = self._get_excel_column_letter(pos)
                width = ws.column_dimensions[col_letter].width
                if width is None:
                    width = 8.43  # Excel default
                widths[pos] = width

            wb.close()

        except (FileNotFoundError, PermissionError, OSError) as e:
            # File access issues - set reasonable defaults
            default_widths = {
                "Index#": 8,
                "Document Type": 15,
                "Legal Description": 30,
                "Grantee": 20,
                "Grantor": 20,
                "Document Date": 12,
                "Received Date": 12,
            }

            for pos, col_name in enumerate(self.df.columns):
                widths[pos] = default_widths.get(col_name, 15)

        return widths

    def _extract_source_alignments(self) -> Dict[int, tuple]:
        """Extract column alignments from source Excel file by position."""
        alignments = {}

        if not self.original_file_path:
            return alignments

        try:
            wb = load_workbook(self.original_file_path)
            ws = wb.active

            # Extract alignments by position from first data row (row 2)
            for pos in range(len(self.df.columns)):
                col_letter = self._get_excel_column_letter(pos)
                cell = ws[f"{col_letter}2"]  # Check first data row

                h_align = "left"  # Default
                v_align = "top"  # Default

                if cell.alignment:
                    # Get horizontal alignment
                    if cell.alignment.horizontal:
                        h_align = str(cell.alignment.horizontal)

                    # Get vertical alignment
                    if cell.alignment.vertical:
                        v_align = str(cell.alignment.vertical)

                # Validate and convert alignment values according to openpyxl docs
                # Valid horizontal: {'fill', 'left', 'distributed', 'justify', 'center', 'general', 'centerContinuous', 'right'}
                if h_align not in [
                    "left",
                    "center",
                    "right",
                    "general",
                    "fill",
                    "distributed",
                    "justify",
                    "centerContinuous",
                ]:
                    h_align = "left"
                elif h_align == "general":
                    h_align = "left"

                # Valid vertical: {'distributed', 'justify', 'center', 'bottom', 'top'}
                if v_align not in ["top", "center", "bottom", "distributed", "justify"]:
                    v_align = "top"

                alignments[pos] = (h_align, v_align)

            wb.close()

        except (FileNotFoundError, PermissionError, OSError) as e:
            # File access issues - set reasonable defaults
            default_alignments = {
                "Index#": ("left", "top"),
                "Document Type": ("left", "top"),
                "Legal Description": ("left", "top"),
                "Grantee": ("left", "top"),
                "Grantor": ("left", "top"),
                "Document Date": ("left", "top"),
                "Received Date": ("left", "top"),
            }

            for pos, col_name in enumerate(self.df.columns):
                alignments[pos] = default_alignments.get(col_name, ("left", "top"))

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

    def validate_columns(self) -> List[str]:
        """Check for required columns and return list of missing ones.

        Returns:
            List[str]: List of column names that are required but missing from the DataFrame

        Raises:
            ValueError: If no Excel file has been loaded
        """
        if self.df is None:
            raise ValueError("No Excel file loaded")

        return [col for col in self.required_columns if col not in self.df.columns]

    def check_duplicate_columns(self) -> List[str]:
        """Check for duplicate column names in the loaded DataFrame.

        Returns:
            List[str]: List of column names that appear more than once
        """
        if self.df is None:
            return []
        return self.df.columns[self.df.columns.duplicated()].tolist()

    def apply_column_mapping(self, mapping: Dict[str, str]) -> bool:
        """Apply column name mappings to the DataFrame.

        Args:
            mapping (Dict[str, str]): Dictionary mapping existing column names to required column names

        Returns:
            bool: True if mapping was applied successfully

        Raises:
            ValueError: If no Excel file loaded or required columns still missing after mapping
        """
        if self.df is None:
            raise ValueError("No Excel file loaded")

        # Update column info with new mappings
        for col_info in self.columns:
            if col_info.current_name in mapping:
                col_info.current_name = mapping[col_info.current_name]

        # Apply mappings to DataFrame
        self.df.rename(columns=mapping, inplace=True)

        # Verify all required columns are now present
        still_missing = self.validate_columns()
        if still_missing:
            raise ValueError(f"Still missing columns after mapping: {still_missing}")

        # Reprocess data types after column mapping
        self._process_data_types()

        return True

    def get_column_info(self) -> Dict[str, any]:
        """Get information about the loaded DataFrame.

        Returns:
            Dict[str, any]: Dictionary containing:
                - rows (int): Number of rows in the DataFrame
                - columns (int): Number of columns in the DataFrame
                - column_names (List[str]): List of column names
        """
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
        """Sort the DataFrame according to PRD requirements while preserving Original_Index for PDF bookmark mapping.

        Sorts by: Received Date, Document Date, Document Type, Grantor, Grantee, Legal Description (all ascending).
        The Original_Index column is preserved to maintain mapping for PDF bookmark processing.

        Returns:
            bool: True if sorting completed successfully

        Raises:
            ValueError: If no Excel file loaded, no sorting columns found, or sorting fails
        """
        if self.df is None:
            raise ValueError("No Excel file loaded")

        # Sort order: Received Date, Document Date, Document Type, Grantor, Grantee, Legal Description
        sort_columns = [
            "Received Date",  # 1. Primary sort - chronological
            "Document Date",  # 2. Secondary sort - chronological
            "Document Type",  # 3. Tertiary sort - alphabetical
            "Grantor",  # 4. Fourth sort - alphabetical
            "Grantee",  # 5. Fifth sort - alphabetical
            "Legal Description",  # 6. Sixth sort - alphabetical
        ]

        # Filter to only include columns that exist in the DataFrame
        existing_sort_columns = [col for col in sort_columns if col in self.df.columns]

        if not existing_sort_columns:
            raise ValueError("No sorting columns found in DataFrame")

        # Handle null/missing values before sorting
        self._handle_missing_values()

        # Ensure proper data types for sorting columns before sorting
        self._prepare_sorting_data_types()

        try:
            # Sort by multiple columns - all ascending (alphabetical for text, chronological for dates)
            # Sorting reorders rows which affects all columns INCLUDING Original_Index
            # This preserves the Original_Index values with each row so we can map PDF bookmarks
            self.df = self.df.sort_values(
                by=existing_sort_columns, ascending=True, na_position="last"
            )
            # Reset index to maintain proper row order
            self.df = self.df.reset_index(drop=True)

            # Renumber Index# column starting from 1 (Original_Index remains unchanged)
            self._renumber_index()

            return True
        except (ValueError, TypeError, KeyError) as e:
            raise ValueError(f"Failed to sort data: {str(e)}")

    def _prepare_sorting_data_types(self) -> None:
        """Ensure proper data types for sorting columns."""
        if self.df is None:
            return

        # Clean and prepare text columns for proper sorting
        text_columns = ["Legal Description", "Grantee", "Grantor", "Document Type"]
        for col in text_columns:
            if col in self.df.columns:
                # Strip whitespace and ensure string type
                self.df[col] = self.df[col].astype(str).str.strip()
                # Replace empty strings with empty string (for consistent sorting)
                self.df[col] = self.df[col].replace("nan", "")

        # Ensure date columns are properly formatted for sorting
        date_columns = ["Document Date", "Received Date"]
        for col in date_columns:
            if col in self.df.columns:
                try:
                    # Convert to datetime for proper chronological sorting
                    original_values = self.df[col].copy()
                    self.df[col] = pd.to_datetime(self.df[col], errors="coerce")

                    # Check for any NaT values that might indicate conversion problems
                    nat_count = self.df[col].isna().sum()
                    if nat_count > 0:
                        # Show which original values became NaT
                        nat_mask = self.df[col].isna()
                        problem_values = original_values[nat_mask].tolist()

                except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime):
                    # Keep as string if conversion fails
                    self.df[col] = self.df[col].astype(str).str.strip()

    def _renumber_index(self) -> None:
        """Renumber the Index# column starting from 1 and incrementing by 1.

        Note: This method ONLY modifies the Index# column and leaves Original_Index
        unchanged, preserving the mapping needed for PDF bookmark processing.
        """
        if self.df is None:
            return

        if "Index#" in self.df.columns:
            # Renumber starting from 1, incrementing by 1
            # Original_Index column remains untouched to preserve PDF bookmark mapping
            self.df["Index#"] = range(1, len(self.df) + 1)
            self.processed_columns.add("Index#")

    def _handle_missing_values(self) -> None:
        """Handle null/missing values in sorting columns."""
        if self.df is None:
            return

        # Validate Received Date - REQUIRED for all rows
        if "Received Date" in self.df.columns:
            # Check for missing/null values
            missing_received_dates = self.df["Received Date"].isna()
            if missing_received_dates.any():
                missing_count = missing_received_dates.sum()
                missing_rows = self.df.index[missing_received_dates].tolist()
                raise ValueError(
                    f"Received Date is required for all rows. Found {missing_count} missing values in rows: {[r+1 for r in missing_rows]}"
                )

            # Check for invalid dates (NaT after conversion)
            invalid_dates = pd.isna(self.df["Received Date"])
            if invalid_dates.any():
                invalid_count = invalid_dates.sum()
                invalid_rows = self.df.index[invalid_dates].tolist()
                raise ValueError(
                    f"Received Date contains invalid date values. Found {invalid_count} invalid dates in rows: {[r+1 for r in invalid_rows]}"
                )

        # Fill empty strings for optional text columns
        text_columns = ["Legal Description", "Grantee", "Grantor", "Document Type"]
        for col in text_columns:
            if col in self.df.columns:
                # Only track as processed if we actually fill missing values
                original_missing = self.df[col].isna().sum()
                self.df[col] = self.df[col].fillna("")
                if original_missing > 0:
                    self.processed_columns.add(col)

        # Document Date is optional - leave as NaN for missing values
        # The na_position='last' parameter in sort_values() will handle sorting

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
        """Save Excel file preserving bookmark formulas and formatting using ExcelFormatter.

        Args:
            output_path (str): Path where the Excel file should be saved

        Returns:
            bool: True if file was saved successfully

        Raises:
            ValueError: If no DataFrame to save or save operation fails
            PermissionError: If unable to write to the specified path
            OSError: If file system error occurs
            ImportError: If required dependencies are missing
        """
        if self.df is None:
            raise ValueError("No DataFrame to save")

        try:
            # Create DataFrame with original column names for output
            output_df = self._create_output_dataframe()

            # Save DataFrame to Excel (basic save)
            output_df.to_excel(output_path, index=False)

            # Apply all formatting using ExcelFormatter
            formatter = ExcelFormatter(self.columns, self.bookmark_formula_column)
            formatter.apply_formatting(output_path, output_df)

            return True

        except (PermissionError, OSError) as e:
            raise ValueError(f"Failed to save Excel file - file access error: {str(e)}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to save Excel file - data error: {str(e)}")
        except ImportError as e:
            raise ValueError(
                f"Failed to save Excel file - missing dependencies: {str(e)}"
            )

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
        if self.df is None:
            return

        if "Index#" in self.df.columns:
            # Create Original_Index column with current Index# values
            self.df["Original_Index"] = self.df["Index#"].copy()
            self.processed_columns.add("Original_Index")

            # Add column info for Original_Index (will be hidden in final output)
            original_index_col_info = ColumnInfo(
                original_name="Original_Index",
                current_name="Original_Index",
                position=len(self.columns),  # Add at end
                width=0,  # Will be hidden
                horizontal_alignment="left",
                vertical_alignment="top",
                excel_letter="",  # Will be calculated
            )
            self.columns.append(original_index_col_info)

    def get_original_index_mapping(self) -> Dict[int, int]:
        """Get mapping from original index values to new index values.

        Returns:
            Dict[int, int]: Dictionary mapping original_index -> new_index
        """
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
