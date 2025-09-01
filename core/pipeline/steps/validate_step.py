#!/usr/bin/env python3
"""
ValidateStep: Comprehensive input validation for DocumentUnit architecture.

This step performs fail-fast validation of all input files before expensive loading
and merging operations. It validates file existence, Excel data integrity, PDF
bookmark structure, and cross-references between Excel rows and PDF bookmarks.
"""

from pathlib import Path

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep


class ValidateStep(BaseStep):
    """Comprehensive input validation step for DocumentUnit architecture.

    Performs early validation to prevent processing failures and ensure data integrity
    before DocumentUnit creation and PDF merging operations begin.
    """

    def execute(self, context: PipelineContext) -> None:
        """Validate input files before loading to ensure fail-fast behavior.

        This step validates that all required files exist and are accessible
        before starting the expensive loading and merging process.

        Args:
            context: Pipeline context containing file paths to validate

        Raises:
            FileNotFoundError: If required files don't exist
            Exception: If files are not accessible or invalid
        """
        self.logger.info("Validating input files before loading")

        # Run all validation checks
        self._validate_file_existence(context)
        self._validate_excel_sheets(context)
        self._validate_excel_data_integrity(context)
        self._validate_pdf_bookmarks(context)
        self._validate_pdf_excel_cross_reference(context)

        file_count = len(context.file_pairs)
        self.logger.info(f"File validation passed: {file_count} file pairs validated")

    def _validate_file_existence(self, context: PipelineContext) -> None:
        """Validate that all files in file_pairs exist and are accessible."""
        self.logger.info("Validating file existence and accessibility")

        for i, (excel_path, pdf_path, _) in enumerate(context.file_pairs):
            self._validate_file_exists(excel_path, f"Excel file {i + 1}")
            self._validate_file_exists(pdf_path, f"PDF file {i + 1}")

    def _validate_excel_sheets(self, context: PipelineContext) -> None:
        """Validate Excel sheet names and update context with corrected names."""
        self.logger.info("Validating Excel sheet names")

        validated_pairs = []
        for excel_path, pdf_path, sheet_name in context.file_pairs:
            validated_sheet = self._validate_excel_sheet(excel_path, sheet_name)
            validated_pairs.append((excel_path, pdf_path, validated_sheet))

        # Update context with validated file pairs (in case sheet names changed)
        context.file_pairs = validated_pairs

    def _validate_excel_data_integrity(self, context: PipelineContext) -> None:
        """Validate Excel data integrity (duplicate Index# values, required columns, etc.)."""
        self.logger.info("Validating Excel data integrity")

        for i, (excel_path, _, sheet_name) in enumerate(context.file_pairs):
            excel_filename = Path(excel_path).name
            try:
                # Load Excel data to check integrity
                df = self.excel_repo.load(excel_path, sheet_name)

                if df.empty:
                    raise ValueError(
                        f"Excel sheet '{sheet_name}' is empty in file '{excel_filename}'"
                    )

                # Check for required Index# column
                if "Index#" not in df.columns:
                    raise ValueError(
                        f"Required column 'Index#' not found in sheet '{sheet_name}' of file '{excel_filename}'"
                    )

                # Check for duplicate Index# values (Index# is already string from ExcelRepo.load())
                index_col = df["Index#"]
                duplicates = index_col[index_col.duplicated()].unique()

                if len(duplicates) > 0:
                    duplicate_list = ", ".join(
                        f"'{dup}'" for dup in duplicates[:5]
                    )  # Show first 5
                    if len(duplicates) > 5:
                        duplicate_list += f" (and {len(duplicates) - 5} more)"

                    raise ValueError(
                        f"Duplicate Index# values found in '{excel_filename}' sheet '{sheet_name}': {duplicate_list}. "
                        f"Each Index# value must be unique for proper document linking."
                    )

                # Check for empty Index# values (Index# is already cleaned string from ExcelRepo.load())
                try:
                    empty_indices = (
                        index_col.isin(["", "nan", "None", "NaN"]) | index_col.isna()
                    )
                    empty_count = empty_indices.sum()
                except Exception as e:
                    raise ValueError(
                        f"Failed to check for empty Index# values in '{excel_filename}': {e}"
                    ) from e

                if empty_count > 0:
                    raise ValueError(
                        f"Found {empty_count} empty Index# values in '{excel_filename}' sheet '{sheet_name}'. "
                        f"All rows must have valid Index# values for document linking."
                    )

                self.logger.info(
                    f"Excel file {i + 1} data integrity passed: {len(df)} rows, {len(index_col.unique())} unique Index# values"
                )

            except Exception as e:
                raise Exception(
                    f"Excel data integrity validation failed for '{excel_filename}': {e}"
                ) from e

    def _validate_pdf_bookmarks(self, context: PipelineContext) -> None:
        """Validate PDF bookmark structure (proper Index# format, no duplicates, etc.)."""
        self.logger.info("Validating PDF bookmark structure")

        for i, (_, pdf_path, _) in enumerate(context.file_pairs):
            pdf_filename = Path(pdf_path).name
            try:
                # Load PDF bookmarks
                bookmarks, total_pages = self.pdf_repo.read(pdf_path)

                if total_pages <= 0:
                    raise ValueError(f"PDF '{pdf_filename}' has no pages")

                if not bookmarks:
                    raise ValueError(
                        f"PDF '{pdf_filename}' has no bookmarks. Bookmarks are required for document linking to Excel rows."
                    )

                # Extract bookmark indices and validate format
                bookmark_indices = []
                invalid_bookmarks = []

                for bookmark in bookmarks:
                    title = str(bookmark.get("title", "")).strip()

                    # Check if bookmark follows Index# pattern (e.g., "1-Document", "2-Something")
                    from core.transform.pdf import extract_original_index

                    original_index = extract_original_index(title)

                    if original_index:
                        bookmark_indices.append(original_index)
                    else:
                        invalid_bookmarks.append(title)

                # Check that all bookmarks have valid Index# format
                if invalid_bookmarks:
                    invalid_list = ", ".join(f"'{bm}'" for bm in invalid_bookmarks[:5])
                    if len(invalid_bookmarks) > 5:
                        invalid_list += f" (and {len(invalid_bookmarks) - 5} more)"

                    raise ValueError(
                        f"PDF '{pdf_filename}' has {len(invalid_bookmarks)} bookmarks that don't follow required Index# format: {invalid_list}. "
                        f"All bookmarks must start with a number followed by a dash (e.g., '1-Document', '2-Report') for proper document linking."
                    )

                # Check for duplicate bookmark indices
                if bookmark_indices:
                    from collections import Counter

                    index_counts = Counter(bookmark_indices)
                    duplicates = [
                        idx for idx, count in index_counts.items() if count > 1
                    ]

                    if duplicates:
                        duplicate_list = ", ".join(f"'{dup}'" for dup in duplicates[:5])
                        if len(duplicates) > 5:
                            duplicate_list += f" (and {len(duplicates) - 5} more)"

                        raise ValueError(
                            f"PDF '{pdf_filename}' has duplicate bookmark indices: {duplicate_list}. "
                            f"Each bookmark index must be unique for proper document linking."
                        )

                # Check for multiple bookmarks pointing to the same page (error)
                bookmark_pages = [
                    int(bookmark.get("page", 1)) for bookmark in bookmarks
                ]
                page_counts = Counter(bookmark_pages)
                duplicate_pages = [
                    page for page, count in page_counts.items() if count > 1
                ]

                if duplicate_pages:
                    # Create clear, organized error message by page
                    error_lines = [
                        "Multiple bookmarks point to the same pages.",
                        "Each bookmark must point to a unique page to avoid overlapping page ranges.",
                        "",
                        "Pages with multiple bookmarks:",
                    ]

                    # Sort pages for consistent output
                    for page in sorted(duplicate_pages):
                        bookmarks_on_page = [
                            str(bookmark.get("title", "")).strip()
                            for bookmark in bookmarks
                            if int(bookmark.get("page", 1)) == page
                        ]
                        error_lines.append(f"  Page {page}:")
                        for bookmark_title in bookmarks_on_page:
                            error_lines.append(f"    • {bookmark_title}")
                        error_lines.append("")  # Empty line between pages

                    error_lines.append(f"Total affected pages: {len(duplicate_pages)}")

                    raise ValueError("\n".join(error_lines))

                # Success logging
                valid_count = len(bookmark_indices)
                total_count = len(bookmarks)
                self.logger.info(
                    f"PDF file {i + 1} bookmark validation passed: {valid_count}/{total_count} bookmarks have valid Index# format, "
                    f"{total_pages} pages"
                )

            except Exception:
                # Re-raise the original exception without adding redundant context
                raise

    def _validate_file_exists(self, file_path: str, file_type: str) -> None:
        """Validate that a file exists and is accessible."""
        from pathlib import Path

        if not file_path:
            raise ValueError(f"{file_type} file path is empty")

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"{file_type} file not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"{file_type} path is not a file: {file_path}")

        # Try to check if file is readable
        try:
            with open(file_path, "rb") as f:
                f.read(1)  # Try to read first byte
        except Exception as e:
            raise Exception(
                f"{file_type} file is not readable: {file_path} - {e}"
            ) from e

    def _validate_excel_sheet(self, excel_path: str, sheet_name: str) -> str:
        """Validate sheet exists in Excel file, prompt user if not.

        Args:
            excel_path: Path to Excel file
            sheet_name: Sheet name to validate

        Returns:
            Validated sheet name (may be different if user selected a different sheet)

        Raises:
            Exception: If sheet validation fails or user cancels selection
        """
        try:
            # Get available sheet names
            available_sheets = self.excel_repo.get_sheet_names(excel_path)

            if not available_sheets:
                raise ValueError(f"No sheets found in Excel file: {excel_path}")

            # Check if requested sheet exists
            if sheet_name in available_sheets:
                self.logger.info(f"Sheet '{sheet_name}' found in {excel_path}")
                return sheet_name

            # Sheet doesn't exist - prompt user to select
            self.logger.warning(f"Sheet '{sheet_name}' not found in {excel_path}")
            self.logger.info(f"Available sheets: {', '.join(available_sheets)}")

            # Use UI callback to prompt user for sheet selection
            selected_sheet = self.ui.prompt_sheet_selection(
                file_path=excel_path,
                sheet_names=available_sheets,
                default_sheet=available_sheets[0] if available_sheets else None,
            )

            if not selected_sheet:
                raise ValueError(f"No sheet selected for Excel file: {excel_path}")

            self.logger.info(f"User selected sheet '{selected_sheet}' for {excel_path}")
            return selected_sheet

        except Exception as e:
            raise Exception(f"Sheet validation failed for {excel_path}: {e}") from e

    def _validate_pdf_excel_cross_reference(self, context: PipelineContext) -> None:
        """Validate that PDF bookmark indices have corresponding Excel rows."""
        self.logger.info("Validating PDF bookmark to Excel row cross-references")

        for i, (excel_path, pdf_path, sheet_name) in enumerate(context.file_pairs):
            excel_filename = Path(excel_path).name
            pdf_filename = Path(pdf_path).name

            try:
                # Load Excel data to get Index# values (Index# is already string from ExcelRepo.load())
                df = self.excel_repo.load(excel_path, sheet_name)
                excel_indices = set(df["Index#"])

                # Load PDF bookmarks to get bookmark indices
                bookmarks, _ = self.pdf_repo.read(pdf_path)

                # Extract bookmark indices
                from core.transform.pdf import extract_original_index

                bookmark_indices = []
                orphaned_bookmarks = []

                for bookmark in bookmarks:
                    title = str(bookmark.get("title", "")).strip()
                    original_index = extract_original_index(title)

                    if original_index:
                        if original_index in excel_indices:
                            bookmark_indices.append(original_index)
                        else:
                            orphaned_bookmarks.append((original_index, title))

                # Report orphaned bookmarks (PDF bookmarks without Excel rows)
                if orphaned_bookmarks:
                    orphaned_list = ", ".join(
                        f"'{idx}' ({title})" for idx, title in orphaned_bookmarks[:3]
                    )
                    if len(orphaned_bookmarks) > 3:
                        orphaned_list += f" (and {len(orphaned_bookmarks) - 3} more)"

                    raise ValueError(
                        f"PDF '{pdf_filename}' has {len(orphaned_bookmarks)} bookmark(s) without corresponding Excel rows: {orphaned_list}. "
                        f"Each PDF bookmark index must have a matching Index# value in Excel sheet '{sheet_name}'."
                    )

                # Success logging
                matched_count = len(bookmark_indices)
                total_bookmarks = len(
                    [
                        b
                        for b in bookmarks
                        if extract_original_index(str(b.get("title", "")).strip())
                    ]
                )
                self.logger.info(
                    f"Cross-reference validation passed for pair {i + 1}: {matched_count}/{total_bookmarks} PDF bookmarks have matching Excel rows"
                )

            except Exception as e:
                raise Exception(
                    f"Cross-reference validation failed between '{pdf_filename}' and '{excel_filename}': {e}"
                ) from e
