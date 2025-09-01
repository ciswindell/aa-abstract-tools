#!/usr/bin/env python3
"""
RenumberService: DocumentUnit architecture orchestration with immutable data flow.

This service maintains the exact same external API while internally using the new
DocumentUnit architecture that prevents data corruption by maintaining immutable
Excel row ↔ PDF page range relationships throughout processing.
"""

from core.interfaces import ExcelRepo, Logger, PdfRepo, UIController
from core.models import Options, Result
from core.pipeline.pipeline import Pipeline
from core.services.validate import ValidationService


class RenumberService:
    """Single entrypoint for DocumentUnit architecture renumber workflow.

    Maintains backward compatibility while internally using the new DocumentUnit
    architecture that prevents the data corruption issues of the previous fragile
    separate bookmarks/pages list approach.
    """

    def __init__(
        self,
        excel_repo: ExcelRepo,
        pdf_repo: PdfRepo,
        validator: ValidationService,
        logger: Logger,
        ui: UIController,
    ) -> None:
        """Initialize with repositories, validator, logger, and UI."""
        self._excel = excel_repo
        self._pdf = pdf_repo
        self._validator = validator
        self._log = logger
        self._ui = ui

    def run(self, excel_path: str, pdf_path: str, opts: Options) -> Result:
        """Execute the end-to-end renumber process using DocumentUnit architecture.

        This method maintains the exact same signature and behavior as the original
        implementation, but now uses the DocumentUnit architecture that prevents data
        corruption by maintaining immutable Excel row ↔ PDF page range relationships.

        The two-phase processing approach:
        - Phase 1 (LoadStep): Per-file linking and merging with DocumentUnit creation
        - Phase 2 (Filter/Sort/Rebuild): Process DocumentUnits while preserving relationships

        Args:
            excel_path: Path to Excel file
            pdf_path: Path to PDF file
            opts: Processing options

        Returns:
            Result indicating success or failure with message
        """
        # Create and execute pipeline
        pipeline = Pipeline(
            excel_repo=self._excel,
            pdf_repo=self._pdf,
            validator=self._validator,
            logger=self._log,
            ui=self._ui,
        )

        return pipeline.execute(excel_path, pdf_path, opts)
