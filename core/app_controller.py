#!/usr/bin/env python3
"""
Application controller that orchestrates processing using UI abstraction.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from openpyxl import load_workbook

from adapters.excel_repo import ExcelOpenpyxlRepo
from adapters.logger_tk import TkLogger
from adapters.pdf_repo import PdfPyPDF2Repo
from core.config import DEFAULT_REQUIRED_COLUMNS, DEFAULT_SHEET_NAME
from core.interfaces import UIController
from core.services.renumber import RenumberService
from core.services.validate import ValidationService


class AppController:
    """Application controller that orchestrates processing via UI abstraction."""

    def __init__(self, ui: UIController) -> None:
        """Initialize with UI controller."""
        self.ui = ui
        self.required_columns = list(DEFAULT_REQUIRED_COLUMNS)
        self.processing_sheet_name = DEFAULT_SHEET_NAME

    def process_files(self) -> None:
        """Main processing function."""
        try:
            excel_file, pdf_file = self.ui.get_file_paths()
            if not excel_file or not pdf_file:
                self.ui.show_error(
                    "Missing Files", "Please select both Excel and PDF files."
                )
                return

            # Resolve processing sheet name
            target_sheet = self._resolve_processing_sheet_name(excel_file)
            if target_sheet is None:
                target_sheet = self._prompt_user_select_sheet(excel_file)
                if target_sheet is None:
                    return

            # Get options from UI
            options = self.ui.get_options()
            options.sheet_name = target_sheet

            # If merging, disable backups regardless of checkbox (originals untouched)
            if getattr(options, "merge_pairs", None):
                options.backup = False

            # Build services for early validation
            logger = TkLogger(self.ui.log_status)
            excel_repo = ExcelOpenpyxlRepo()
            pdf_repo = PdfPyPDF2Repo()
            validator = ValidationService(self.required_columns)

            # Load and validate data BEFORE creating backups
            logger.info("Loading and validating files...")
            df = excel_repo.load(excel_file, target_sheet)
            bookmarks, _ = pdf_repo.read(pdf_file)
            validator.run(df=df, bookmarks=bookmarks)
            logger.info("Validation passed.")

            # If filter is enabled and no values chosen yet, prompt now
            try:
                if (
                    getattr(options, "filter_enabled", False)
                    and not options.filter_values
                ):
                    col, vals = self.ui.prompt_filter_selection(df)
                    if col and vals:
                        options.filter_column = col
                        options.filter_values = vals
            except Exception:
                # Non-fatal: continue without filter if prompt fails
                pass

            # Create backups if enabled (only after validation passes)
            if options.backup:
                self._create_backup_files(excel_file, pdf_file)

            # If merging, resolve sheet names for each pair using the same selection flow
            if getattr(options, "merge_pairs", None):
                # Always include the primary selection as the first pair
                pairs_with_sheets = [(excel_file, pdf_file, target_sheet)]
                seen = {(excel_file, pdf_file)}

                # Append additional pairs, resolving sheet names per file
                for x_path, p_path in options.merge_pairs or []:
                    if (x_path, p_path) in seen:
                        continue
                    sheet_name = self._resolve_processing_sheet_name(x_path)
                    if sheet_name is None:
                        sheet_name = self._prompt_user_select_sheet(x_path)
                        if sheet_name is None:
                            continue
                    pairs_with_sheets.append((x_path, p_path, sheet_name))
                    seen.add((x_path, p_path))

                options.merge_pairs_with_sheets = pairs_with_sheets

            # Run processing
            service = RenumberService(excel_repo, pdf_repo, validator, logger)
            result = service.run(excel_file, pdf_file, options)
            if not result.success:
                raise RuntimeError(result.message or "Unknown error")

            # Show success
            message = f"Files processed successfully!\n\nSaved to: {os.path.dirname(excel_file)}"
            self.ui.show_success(message)

        except (ValueError, OSError, RuntimeError) as e:
            self.ui.show_error("Processing Error", str(e))

    def _resolve_processing_sheet_name(self, file_path: str) -> Optional[str]:
        """Resolve the processing sheet name, case-insensitively."""
        try:
            wb = load_workbook(file_path, read_only=True, data_only=True)
            desired = (self.processing_sheet_name or "").lower()
            names = wb.sheetnames
            lower_to_name = {n.lower(): n for n in names}
            wb.close()
            if desired and desired in lower_to_name:
                return lower_to_name[desired]
            return None
        except (OSError, ValueError, PermissionError):
            return None

    def _prompt_user_select_sheet(self, file_path: str) -> Optional[str]:
        """Prompt user to select a sheet from available options, or auto-select if only one sheet."""
        try:
            wb = load_workbook(file_path, read_only=True, data_only=True)
            names = wb.sheetnames
            wb.close()

            if not names:
                return None

            # If there's only one sheet, automatically use it
            if len(names) == 1:
                return names[0]

            return self.ui.prompt_sheet_selection(
                file_path, names, self.processing_sheet_name
            )

        except (OSError, ValueError, PermissionError) as e:
            self.ui.show_error("Sheet Selection Error", str(e))
            return None

    def _generate_backup_filename(self, original_path: str) -> str:
        """Generate backup filename with timestamp."""
        original_file = Path(original_path)
        file_stem = original_file.stem
        file_suffix = original_file.suffix
        file_dir = original_file.parent

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{file_stem}_backup_{timestamp}{file_suffix}"

        return str(file_dir / backup_filename)

    def _create_backup_files(self, excel_path: str, pdf_path: str) -> Tuple[str, str]:
        """Create backup copies with timestamp suffix."""
        excel_backup_path = self._generate_backup_filename(excel_path)
        pdf_backup_path = self._generate_backup_filename(pdf_path)

        shutil.copy2(excel_path, excel_backup_path)
        shutil.copy2(pdf_path, pdf_backup_path)

        return excel_backup_path, pdf_backup_path
