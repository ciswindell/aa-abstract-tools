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

    # All parsing/transform concerns are handled in core/transform/excel.py

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

    def apply_column_mapping(self, mapping: Dict[str, str]) -> bool:
        """Apply column name mappings to the DataFrame."""
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

    # Sorting/renumbering now lives in core/transform.excel

    # Removed type prep; handled in transforms

    # Renumbering handled in transforms

    # Missing values handled in transforms

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

    def save_with_formulas(
        self, output_path: str, processing_sheet_name: Optional[str] = None
    ) -> bool:
        """Save Excel file preserving formatting.

        Writes values into the existing output workbook (a copy of the input)
        to retain all sheets and formatting. Only the active/processing sheet is modified.
        """
        try:
            # Create output DataFrame with original column names
            output_df = self._create_output_dataframe()

            # Open the copied workbook and select the processing sheet or fallback to active
            wb = load_workbook(output_path)
            # Require explicit processing sheet; no fallback to active sheet
            if not processing_sheet_name:
                wb.close()
                raise RuntimeError("Processing sheet name not provided")
            lower_to_name = {name.lower(): name for name in wb.sheetnames}
            match_name = lower_to_name.get(str(processing_sheet_name).lower())
            if not match_name:
                wb.close()
                raise RuntimeError(
                    f"Processing sheet '{processing_sheet_name}' not found in output workbook"
                )
            ws = wb[match_name]

            # Build a case-insensitive header map from the first row
            header_values = []
            for cell in ws[1]:
                header_values.append(
                    "" if cell.value is None else str(cell.value).strip()
                )
            header_to_col = {
                h.lower(): idx + 1 for idx, h in enumerate(header_values) if h != ""
            }

            # Write DataFrame values into matching columns by header name
            for df_col in output_df.columns:
                target_col_idx = header_to_col.get(str(df_col).strip().lower())
                if not target_col_idx:
                    # Skip columns that do not exist in the target sheet
                    continue

                values = output_df[df_col].tolist()
                for row_idx, value in enumerate(
                    values, start=2
                ):  # Start at row 2 (after header)
                    ws.cell(row=row_idx, column=target_col_idx, value=value)

            # Clear hard-coded fills (keep conditional formatting)
            empty_fill = PatternFill(fill_type=None)
            for row in ws.iter_rows(
                min_row=2, max_row=ws.max_row, max_col=ws.max_column
            ):
                for cell in row:
                    cell.fill = empty_fill

            # Keep the selected sheet as active for downstream formatting
            try:
                wb.active = wb.sheetnames.index(ws.title)
            except Exception:
                pass

            # Save workbook with updated values
            wb.save(output_path)
            wb.close()

            # Adapter handles formatting via template in refactor; legacy path ends here
            return True

        except Exception as e:
            raise RuntimeError(f"Failed to save Excel file: {str(e)}") from e

    def _create_output_dataframe(self) -> pd.DataFrame:
        """Create DataFrame with original column names for export, excluding internal columns."""
        output_df = self.df.copy()

        # Remove the Original_Index column - it's only used internally for PDF bookmark mapping
        # and should not appear in the final Excel output
        if "Original_Index" in output_df.columns:
            output_df = output_df.drop(columns=["Original_Index"])

        # No renaming here; headers in the template are authoritative

        return output_df

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
