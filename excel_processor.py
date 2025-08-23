#!/usr/bin/env python3
"""
Excel processing module for the Abstract Renumber Tool.
Handles Excel file loading, validation, and data operations.
"""

from collections import Counter
from typing import Dict, List, Optional

import pandas as pd


class ExcelProcessor:
    """Handles Excel file operations and validation.

    This class processes Excel files with support for alphanumeric Index# values.
    Index# values are treated as strings throughout the processing pipeline to support
    formats like "A1", "B5", "AGH42", etc., while maintaining backward compatibility
    with numeric-only Index# values.
    """

    def __init__(self, required_columns: List[str]):
        self.required_columns = required_columns
        self.df: Optional[pd.DataFrame] = None
        self.original_file_path: Optional[str] = None
        self.processed_columns = set()
        self.bookmark_formula_column: Optional[str] = None

    def load_file(self, file_path: str, sheet_name: Optional[str] = None) -> bool:
        """Load Excel file with basic validation.

        Args:
            file_path: Path to the Excel file
            sheet_name: Optional sheet name to load (case-sensitive exact as in file)
        """
        try:
            # Load Excel file
            self.df = pd.read_excel(file_path, dtype=str, sheet_name=sheet_name)
            self.original_file_path = file_path

            if self.df.empty:
                raise ValueError("Excel file contains no data")

            # Minimal load only; transforms and validators handle processing

            return True

        except Exception as e:
            raise ValueError(f"Failed to load Excel file: {str(e)}")

    # Parsing/transform concerns are handled in core/transform/excel.py

    def check_duplicate_columns(self) -> List[str]:
        """Check for duplicate column names in the loaded DataFrame."""
        return self.df.columns[self.df.columns.duplicated()].tolist()

    def get_missing_columns(self) -> List[str]:
        """Check for required columns and return list of missing ones."""
        if self.df is None:
            return self.required_columns
        present_lower = {str(c).lower() for c in self.df.columns}
        missing = [
            col
            for col in self.required_columns
            if str(col).lower() not in present_lower
        ]
        return missing

    def get_required_duplicate_columns(self) -> List[str]:
        """Return required column names that appear more than once (case-insensitive)."""
        if self.df is None:
            return []
        required_lower = {str(c).lower() for c in self.required_columns}
        counts = Counter(
            str(c).lower() for c in self.df.columns if str(c).lower() in required_lower
        )
        return [
            rc for rc in self.required_columns if counts.get(str(rc).lower(), 0) > 1
        ]

    # Removed: column mapping (template headers + validation are authoritative)

    def get_column_info(self) -> Dict[str, any]:
        """Get information about the loaded DataFrame."""
        if self.df is None:
            return {}
        return {"rows": len(self.df), "columns": len(self.df.columns)}

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the loaded DataFrame.

        Returns:
            Optional[pd.DataFrame]: The loaded pandas DataFrame, or None if no file loaded
        """
        return self.df

    # Sorting/renumbering/type prep/missing-value handling are in transforms

    # Removed: processed/unprocessed columns accessors (unused)

    # Removed deprecated save_with_formulas; adapter is the write path

    # Removed export helpers; adapter handles template-preserving writes

    # Removed: update of column positions (adapter resolves headers)

    def get_bookmark_formula_column(self) -> Optional[str]:
        """Return the name of the bookmark formula column if detected.

        Returns:
            Optional[str]: Name of the detected bookmark formula column, or None if not found
        """
        return self.bookmark_formula_column

    def _add_original_index_column(self) -> None:
        """Add Original_Index column to preserve original Index# values for PDF bookmark mapping."""
        if "Index#" in self.df.columns:
            # Ensure Index# values are preserved as strings for alphanumeric support
            self.df["Original_Index"] = self.df["Index#"].astype(str).copy()
            self.processed_columns.add("Original_Index")

            # Column metadata no longer tracked

    def get_original_index_mapping(self) -> Dict[str, int]:
        """Get mapping from original index values to new index values.

        Returns:
            Dict[str, int]: Mapping from original index (as string) to new index (as int)
        """
        if (
            self.df is None
            or "Original_Index" not in self.df.columns
            or "Index#" not in self.df.columns
        ):
            return {}

        # Create mapping: original_index (as string) -> new_index (as int)
        mapping = {}
        for _, row in self.df.iterrows():
            original_idx = str(row["Original_Index"]).strip()
            new_idx = int(row["Index#"])
            mapping[original_idx] = new_idx

        return mapping
