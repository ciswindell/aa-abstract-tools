#!/usr/bin/env python3
"""
RebuildPdfStep: Phase 2 final step - PyPDF-optimized DocumentUnit reconstruction.

This step implements the final phase of the DocumentUnit architecture using PyPDF's
native capabilities for maximum reliability and performance. It reconstructs the final
PDF from immutable DocumentUnits, ensuring that the Excel row ↔ PDF page range
relationships established in LoadStep are preserved throughout filtering and sorting.

Three-phase reconstruction process:
1. Filter: Extract only DocumentUnits for flagged DataFrame rows (_include=True)
2. Reorder: Arrange pages according to sorted DataFrame order (if enabled)
3. Rebuild: Create fresh PDF with new bookmarks pointing to final page positions
"""

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from core.models import DocumentUnit
from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.pdf import make_titles


class RebuildPdfStep(BaseStep):
    """Phase 2 final step: PyPDF-optimized DocumentUnit reconstruction.

    Reconstructs final PDF from immutable DocumentUnits while preserving the atomic
    Excel row ↔ PDF page range relationships established in LoadStep. Uses three-phase
    approach for optimal memory efficiency and reliability.
    """

    def should_execute(self, context: PipelineContext) -> bool:
        """Always execute - this step is required for final PDF generation."""
        return True

    def execute(self, context: PipelineContext) -> None:
        """Rebuild PDF using three-phase PyPDF-optimized reconstruction.

        This step performs robust PDF reconstruction with immutable DocumentUnits:
        - Phase A: Filter DocumentUnits based on _include flag (conditional)
        - Phase B: Reorder DocumentUnits by sorted DataFrame order (conditional)
        - Phase C: Create fresh PDF with PyPDF bookmarks (always)

        Args:
            context: Pipeline context containing DocumentUnits, DataFrame, and options

        Raises:
            Exception: If PDF reconstruction fails
        """
        self.logger.info(
            f"Step {context.step_number} of {context.total_steps}: Rebuilding PDF..."
        )

        # Validate required data
        if context.document_units is None:
            raise ValueError("No DocumentUnits available for PDF reconstruction")

        if not context.document_units:
            raise ValueError(
                "DocumentUnits list is empty - no PDF content to reconstruct"
            )

        if context.df is None:
            raise ValueError("No DataFrame available for PDF reconstruction")

        if context.df.empty:
            raise ValueError("DataFrame is empty - no data for PDF reconstruction")

        if context.intermediate_pdf_path is None:
            raise ValueError("No intermediate PDF path available for reconstruction")

        # Validate intermediate PDF file exists
        from pathlib import Path

        if not Path(context.intermediate_pdf_path).exists():
            raise FileNotFoundError(
                f"Intermediate PDF file not found: {context.intermediate_pdf_path}"
            )

        # Validate required columns in DataFrame
        required_columns = ["Document_ID", "Index#"]
        missing_columns = [
            col for col in required_columns if col not in context.df.columns
        ]
        if missing_columns:
            raise ValueError(f"Required DataFrame columns missing: {missing_columns}")

        intermediate_reader = None
        try:
            # Load intermediate PDF for page extraction
            intermediate_reader = PdfReader(context.intermediate_pdf_path)

            # Phase A: Filter DocumentUnits (conditional execution)
            filtered_units = self._phase_a_filter_units(context)

            # Phase B: Reorder DocumentUnits (conditional execution)
            sorted_units = self._phase_b_reorder_units(context, filtered_units)

            # Phase C: Create fresh PDF with bookmarks (always execute)
            final_writer = self._phase_c_create_pdf_with_bookmarks(
                context, sorted_units, intermediate_reader
            )

            # Store results in context for SaveStep
            context.final_pdf = final_writer
            context.processed_document_units = sorted_units

            # Explicitly release the intermediate reader to free memory
            # The pages have been copied to final_writer, so we don't need this anymore
            if intermediate_reader is not None:
                intermediate_reader = None

        except Exception as e:
            self.logger.error(f"PDF reconstruction failed: {e}")
            # Clean up any partial results
            if hasattr(context, "final_pdf"):
                delattr(context, "final_pdf")
            if hasattr(context, "processed_document_units"):
                delattr(context, "processed_document_units")
            raise Exception(f"PDF reconstruction failed: {e}") from e

        finally:
            # Clean up intermediate PDF file if it exists
            self._cleanup_intermediate_pdf(context)

    def _phase_a_filter_units(self, context: PipelineContext) -> list[DocumentUnit]:
        """Phase A: Filter DocumentUnits based on _include flag.

        Args:
            context: Pipeline context containing DocumentUnits and DataFrame

        Returns:
            List of DocumentUnits for flagged DataFrame rows
        """
        # Check if filtering is needed
        if "_include" not in context.df.columns:
            return list(context.document_units)

        # Get flagged Document IDs
        flagged_df = context.df[context.df["_include"]]
        flagged_doc_ids = set(flagged_df["Document_ID"])

        # Filter DocumentUnits (immutable - ranges never change!)
        filtered_units = [
            unit
            for unit in context.document_units
            if unit.document_id in flagged_doc_ids
        ]

        return filtered_units

    def _phase_b_reorder_units(
        self, context: PipelineContext, filtered_units: list[DocumentUnit]
    ) -> list[DocumentUnit]:
        """Phase B: Reorder DocumentUnits by sorted DataFrame order.

        Args:
            context: Pipeline context containing sorted DataFrame
            filtered_units: DocumentUnits from Phase A

        Returns:
            DocumentUnits sorted by DataFrame order
        """
        # Check if reordering is enabled
        if not context.options.get("reorder_pages", False):
            return filtered_units

        # Get flagged DataFrame in sorted order
        if "_include" not in context.df.columns:
            sorted_df = context.df
        else:
            sorted_df = context.df[context.df["_include"]]

        # Create mapping from Document ID to DataFrame position
        df_order = {doc_id: idx for idx, doc_id in enumerate(sorted_df["Document_ID"])}

        # Sort DocumentUnits by DataFrame order
        sorted_units = sorted(
            filtered_units,
            key=lambda unit: df_order.get(
                unit.document_id, 999
            ),  # Unknown IDs go to end
        )

        return sorted_units

    def _phase_c_create_pdf_with_bookmarks(
        self,
        context: PipelineContext,
        sorted_units: list[DocumentUnit],
        intermediate_reader: PdfReader,
    ) -> PdfWriter:
        """Phase C: Create fresh PDF with PyPDF bookmarks.

        Args:
            context: Pipeline context for bookmark generation
            sorted_units: DocumentUnits in final order
            intermediate_reader: Source PDF for page extraction

        Returns:
            PdfWriter with pages and fresh bookmarks
        """
        # Create new PDF writer
        writer = PdfWriter()
        writer.page_mode = "/UseOutlines"  # Show bookmark panel by default

        # Generate bookmark titles from flagged DataFrame
        if "_include" in context.df.columns:
            flagged_df = context.df[context.df["_include"]]
        else:
            flagged_df = context.df
        bookmark_titles = make_titles(flagged_df)

        # Collect bookmark information during page processing
        bookmark_info = []
        current_page = 0
        bookmarks_added = 0

        # Process each DocumentUnit in sorted order
        for unit in sorted_units:
            # Extract pages from intermediate PDF (immutable ranges!)
            start_page = unit.merged_page_range[0] - 1  # Convert to 0-based
            end_page = unit.merged_page_range[1]  # Exclusive end

            unit_start_page = current_page

            # Copy pages to final PDF
            for page_idx in range(start_page, end_page):
                if page_idx < len(intermediate_reader.pages):
                    writer.add_page(intermediate_reader.pages[page_idx])
                    current_page += 1

            # Collect bookmark info for this DocumentUnit
            if unit.document_id in bookmark_titles:
                title = bookmark_titles[unit.document_id]
                bookmark_info.append({"title": title, "page_num": unit_start_page})
                bookmarks_added += 1

        # Add bookmarks in the appropriate order
        self._add_bookmarks_to_writer(
            writer, bookmark_info, context.options.get("sort_bookmarks", False)
        )

        return writer

    def _add_bookmarks_to_writer(
        self, writer: PdfWriter, bookmark_info: list, sort_bookmarks: bool
    ) -> None:
        """Add bookmarks to the PDF writer in the appropriate order.

        Args:
            writer: PdfWriter to add bookmarks to
            bookmark_info: List of dicts with 'title' and 'page_num' keys
            sort_bookmarks: Whether to sort bookmarks naturally by title
        """
        if not bookmark_info:
            return

        try:
            if sort_bookmarks:
                from natsort import natsorted, ns

                # Sort bookmarks naturally by title
                sorted_bookmarks = natsorted(
                    bookmark_info,
                    key=lambda b: b["title"],
                    alg=ns.IGNORECASE,  # Case-insensitive natural sorting
                )

                bookmarks_to_add = sorted_bookmarks
            else:
                # Keep original order (follows DocumentUnit/DataFrame order)
                bookmarks_to_add = bookmark_info

            # Add bookmarks to writer
            for bookmark in bookmarks_to_add:
                writer.add_outline_item(bookmark["title"], bookmark["page_num"])

        except ImportError:
            self.logger.warning(
                "natsort library not available - adding bookmarks in document order"
            )
            # Fall back to original order
            for bookmark in bookmark_info:
                writer.add_outline_item(bookmark["title"], bookmark["page_num"])
        except Exception as e:
            self.logger.warning(
                f"Failed to sort bookmarks: {e} - adding in document order"
            )
            # Fall back to original order
            for bookmark in bookmark_info:
                writer.add_outline_item(bookmark["title"], bookmark["page_num"])

    def _cleanup_intermediate_pdf(self, context: PipelineContext) -> None:
        """Clean up intermediate PDF file to free disk space.

        Args:
            context: Pipeline context containing intermediate PDF path
        """
        if not context.intermediate_pdf_path:
            return

        try:
            intermediate_path = Path(context.intermediate_pdf_path)
            if intermediate_path.exists():
                intermediate_path.unlink()
                # Clear the path from context to prevent reuse
                context.intermediate_pdf_path = None
        except Exception:
            # Silently ignore cleanup failures (common on Windows due to file locking)
            # The temp file will be cleaned up by the OS eventually
            pass
