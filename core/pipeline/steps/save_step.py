#!/usr/bin/env python3
"""
SaveStep: Save Excel and PDF outputs using existing repo methods.
"""

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from fileops.files import create_backups


class SaveStep(BaseStep):
    """Pipeline step for saving final Excel and PDF outputs."""

    def execute(self, context: PipelineContext) -> None:
        """Save Excel and PDF outputs using existing repository methods.

        This step handles the final output phase:
        - Creates backups if enabled (for single-file workflows only)
        - Saves Excel DataFrame back to template preserving formatting
        - Writes PDF with updated bookmarks and optionally reordered pages
        - Uses appropriate output paths for merge vs single-file workflows

        Args:
            context: Pipeline context containing processed data and options

        Raises:
            Exception: If saving fails
        """
        self.logger.info("Saving final Excel and PDF outputs")

        # Ensure we have data to save
        if context.df is None:
            raise ValueError("No Excel data available for saving")

        if context.pages is None or context.bookmarks is None:
            raise ValueError("No PDF data available for saving")

        # Get output paths
        excel_out_path, pdf_out_path = context.get_output_paths()

        # Create backups if enabled (skip for merge workflows)
        if context.options.backup and not context.is_merge_workflow():
            self.logger.info("Creating backup files before saving")
            create_backups(context.excel_path, context.pdf_path)

        # Save Excel output
        self._save_excel_output(context, excel_out_path)

        # Save PDF output
        self._save_pdf_output(context, pdf_out_path)

        self.logger.info(
            f"Output saved successfully to: {excel_out_path}, {pdf_out_path}"
        )

    def _save_excel_output(self, context: PipelineContext, excel_out_path: str) -> None:
        """Save Excel DataFrame back to template preserving formatting."""
        self.logger.info(f"Saving Excel output to: {excel_out_path}")

        # Determine target sheet name
        target_sheet = context.options.sheet_name or "Index"

        # Use existing ExcelRepo to save DataFrame back into template
        # This preserves all formatting, styles, other sheets, etc.
        self.excel_repo.save(
            df=context.df,
            template_path=context.excel_path,
            target_sheet=target_sheet,
            out_path=excel_out_path,
        )

        self.logger.info(
            f"Excel saved: {len(context.df)} rows to sheet '{target_sheet}'"
        )

    def _save_pdf_output(self, context: PipelineContext, pdf_out_path: str) -> None:
        """Save PDF with updated bookmarks and optionally reordered pages."""
        self.logger.info(f"Saving PDF output to: {pdf_out_path}")

        # Use existing PdfRepo to write pages and bookmarks
        # Pages may be reordered (if ReorderStep executed) or original order
        # Bookmarks have updated titles from BookmarkStep
        self.pdf_repo.write(
            pages=context.pages,
            bookmarks=context.bookmarks,
            out_path=pdf_out_path,
        )

        self.logger.info(
            f"PDF saved: {len(context.pages)} pages, {len(context.bookmarks)} bookmarks"
        )
