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

            # Create backups if enabled
            if options.backup:
                self._create_backup_files(excel_file, pdf_file)

            # Build services
            logger = TkLogger(self.ui.log_status)
            excel_repo = ExcelOpenpyxlRepo()
            pdf_repo = PdfPyPDF2Repo()
            validator = ValidationService(self.required_columns)
            service = RenumberService(excel_repo, pdf_repo, validator, logger)

            # Run processing
            result = service.run(excel_file, pdf_file, options)
            if not result.success:
                raise RuntimeError(result.message or "Unknown error")

            # Show success
            message = f"Files processed successfully!\n\nSaved to: {os.path.dirname(excel_file)}"
            self.ui.show_success(message)

        except (ValueError, OSError, RuntimeError) as e:
            self.ui.show_error("Processing Error", f"Processing failed: {str(e)}")

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
        except Exception:
            return None

    def _prompt_user_select_sheet(self, file_path: str) -> Optional[str]:
        """Prompt user to select a sheet from available options."""
        try:
            wb = load_workbook(file_path, read_only=True, data_only=True)
            names = wb.sheetnames
            wb.close()

            if not names:
                return None

            return self.ui.prompt_sheet_selection(
                file_path, names, self.processing_sheet_name
            )

        except Exception as e:
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
