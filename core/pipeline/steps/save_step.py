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
        self.logger.info(f"Step {context.step_number} of {context.total_steps}: Saving outputs...")

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

        # Save Excel output with proper backup handling
        self._save_excel_output(context, excel_out_path, should_backup)

        # Save PDF output with proper backup handling
        self._save_pdf_output(context, pdf_out_path, should_backup)

        # Explicitly clear the PdfWriter to release memory immediately after saving
        # The PdfWriter object can hold hundreds of MB of PDF data in memory
        if context.final_pdf is not None:
            # Clear internal pages list to release memory
            # Note: pypdf uses _VirtualList which doesn't have clear(), so just null the reference
            try:
                if hasattr(context.final_pdf, "_pages"):
                    context.final_pdf._pages = []
            except Exception:
                pass  # Ignore if we can't clear pages
            # Null out the reference to release memory
            context.final_pdf = None

        # Clear the DataFrame to release memory
        if context.df is not None:
            context.df = None

        # Clear document units
        if context.document_units is not None:
            context.document_units = None
        if context.processed_document_units is not None:
            context.processed_document_units = None

    def _save_excel_output(
        self, context: PipelineContext, excel_out_path: str, should_backup: bool
    ) -> None:
        """Save Excel DataFrame back to template preserving formatting."""
        # Determine target sheet name
        target_sheet = context.options.get("sheet_name") or "Index"

        # Save flagged rows (or all rows if no _include column exists)
        if "_include" in context.df.columns:
            df_to_save = context.df[context.df["_include"]].copy()
        else:
            df_to_save = context.df.copy()

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
        atomic_save_with_backup(
            original_path=excel_out_path,
            write_func=write_excel,
            create_backup=should_backup,
        )

    def _save_pdf_output(
        self, context: PipelineContext, pdf_out_path: str, should_backup: bool
    ) -> None:
        """Save PDF using PdfWriter from RebuildPdfStep."""
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
        atomic_save_with_backup(
            original_path=pdf_out_path,
            write_func=write_pdf,
            create_backup=should_backup,
        )
