#!/usr/bin/env python3
"""
SaveStep: Atomic save operations with backup support for DocumentUnit architecture.

This step handles final output with proper backup creation for single-file workflows
and direct saving for merge workflows. It saves filtered/sorted DataFrame data and
reconstructed PDF with fresh bookmarks generated from DocumentUnits.
"""

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from fileops.files import atomic_save_with_backup


class SaveStep(BaseStep):
    """Atomic save operations with backup support for DocumentUnit architecture.

    Handles final output phase with appropriate backup strategies for different
    workflow types (single-file vs merge) and atomic write operations.
    """

    def execute(self, context: PipelineContext) -> None:
        """Save Excel and PDF outputs using DocumentUnit-based architecture.

        This step handles the final output phase:
        - Creates backups if enabled (for single-file workflows only)
        - Saves flagged DataFrame rows back to Excel template preserving formatting
        - Writes PDF using PdfWriter from RebuildPdfStep (filtered/sorted pages with fresh bookmarks)
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

        if not hasattr(context, "final_pdf") or context.final_pdf is None:
            raise ValueError(
                "No PDF writer available for saving - RebuildPdfStep may not have executed"
            )

        # Get output paths
        excel_out_path, pdf_out_path = context.get_output_paths()

        # Determine backup settings
        should_backup = (
            context.options.get("backup", False) and not context.is_merge_workflow()
        )

        if should_backup:
            self.logger.info(
                "Saving with backup enabled (original files will be preserved)"
            )
        elif context.is_merge_workflow():
            self.logger.info(
                "Saving merged files (originals preserved, no backup needed)"
            )
        else:
            self.logger.info(
                "Saving without backup (original files will be overwritten)"
            )

        # Save Excel output with proper backup handling
        self._save_excel_output(context, excel_out_path, should_backup)

        # Save PDF output with proper backup handling
        self._save_pdf_output(context, pdf_out_path, should_backup)

        # Explicitly clear the PdfWriter to release memory immediately after saving
        # The PdfWriter object can hold hundreds of MB of PDF data in memory
        if context.final_pdf is not None:
            # Clear internal pages list to release memory
            if hasattr(context.final_pdf, "_pages"):
                context.final_pdf._pages = []
            if hasattr(context.final_pdf, "pages"):
                context.final_pdf.pages.clear()
            # Null out the reference
            context.final_pdf = None
            self.logger.info("Released PdfWriter memory after saving")

        # Clear the DataFrame to release memory
        if context.df is not None:
            context.df = None
            self.logger.info("Released DataFrame memory after saving")

        # Clear document units
        if context.document_units is not None:
            context.document_units = None
        if context.processed_document_units is not None:
            context.processed_document_units = None

        self.logger.info(
            f"Output saved successfully to: {excel_out_path}, {pdf_out_path}"
        )

    def _save_excel_output(
        self, context: PipelineContext, excel_out_path: str, should_backup: bool
    ) -> None:
        """Save Excel DataFrame back to template preserving formatting."""
        self.logger.info(f"Saving Excel output to: {excel_out_path}")

        # Determine target sheet name
        target_sheet = context.options.get("sheet_name") or "Index"

        # Save flagged rows (or all rows if no _include column exists)
        if "_include" in context.df.columns:
            df_to_save = context.df[context.df["_include"]].copy()
            # Show breakdown by source for verification
            if "Source" in context.df.columns:
                source_breakdown = df_to_save.groupby("Source").size()
                for source, count in source_breakdown.items():
                    self.logger.info(f"  Saving {count} rows from {source}")
        else:
            df_to_save = context.df.copy()

        saved_rows = len(df_to_save)
        total_rows = len(context.df)
        self.logger.info(f"Saving {saved_rows}/{total_rows} rows to Excel")

        # Define the write function for atomic save
        def write_excel(output_path: str) -> None:
            # Check if user wants to add missing columns (Document_Found)
            add_missing_columns = context.options.get("check_document_images", False)

            self.excel_repo.save(
                df=df_to_save,
                template_path=context.excel_path,
                target_sheet=target_sheet,
                out_path=output_path,
                add_missing_columns=add_missing_columns,
            )

        # Use atomic save with backup if needed
        backup_path = atomic_save_with_backup(
            original_path=excel_out_path,
            write_func=write_excel,
            create_backup=should_backup,
        )

        if backup_path:
            self.logger.info(f"Excel backup created: {backup_path}")
        self.logger.info(f"Excel saved: {saved_rows} rows to sheet '{target_sheet}'")

    def _save_pdf_output(
        self, context: PipelineContext, pdf_out_path: str, should_backup: bool
    ) -> None:
        """Save PDF using PdfWriter from RebuildPdfStep."""
        self.logger.info(f"Saving PDF output to: {pdf_out_path}")

        # Define the write function for atomic save
        def write_pdf(output_path: str) -> None:
            try:
                # Write the final PDF using the PdfWriter from RebuildPdfStep
                # This contains the filtered/sorted pages with fresh bookmarks
                with open(output_path, "wb") as output_file:
                    context.final_pdf.write(output_file)
            except Exception as e:
                raise Exception(f"Failed to write PDF to {output_path}: {e}") from e

        # Use atomic save with backup if needed
        backup_path = atomic_save_with_backup(
            original_path=pdf_out_path,
            write_func=write_pdf,
            create_backup=should_backup,
        )

        # Log statistics about the saved PDF
        page_count = len(context.final_pdf.pages)

        # Count bookmarks by checking outline
        bookmark_count = 0
        if hasattr(context.final_pdf, "outline") and context.final_pdf.outline:
            bookmark_count = len(context.final_pdf.outline)

        if backup_path:
            self.logger.info(f"PDF backup created: {backup_path}")
        self.logger.info(f"PDF saved: {page_count} pages, {bookmark_count} bookmarks")
