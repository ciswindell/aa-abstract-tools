#!/usr/bin/env python3
"""
LinkStep: Wrap existing create_document_links function in pipeline step.
"""

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.excel import create_document_links


class LinkStep(BaseStep):
    """Pipeline step for creating document links between Excel rows and PDF bookmarks."""

    def execute(self, context: PipelineContext) -> None:
        """Create DocumentLink objects mapping Excel rows to PDF bookmarks.

        This step creates the critical mapping between Excel data and PDF bookmarks
        using Document IDs. The links are used later for bookmark title updates
        and page reordering.

        Args:
            context: Pipeline context containing df with Document IDs and bookmarks

        Raises:
            Exception: If document linking fails
        """
        self.logger.info("Creating document links between Excel rows and PDF bookmarks")

        # Ensure we have the required data
        if context.df is None:
            raise ValueError("No Excel data loaded for document linking")

        if context.bookmarks is None:
            raise ValueError("No PDF bookmarks loaded for document linking")

        if "Document_ID" not in context.df.columns:
            raise ValueError(
                "Document_ID column missing - cannot create document links"
            )

        # Store counts for logging
        excel_rows = len(context.df)
        pdf_bookmarks = len(context.bookmarks)

        # Use existing create_document_links function
        # This creates DocumentLink objects that map Excel rows to PDF bookmarks
        context.document_links = create_document_links(context.df, context.bookmarks)

        linked_count = len(context.document_links)
        self.logger.info(
            f"Document linking complete: {linked_count} links created "
            f"from {excel_rows} Excel rows and {pdf_bookmarks} PDF bookmarks"
        )

        # Log statistics about linking success
        if linked_count == 0:
            self.logger.warning(
                "No document links created - check Index# matching between Excel and PDF"
            )
        elif linked_count < excel_rows:
            unlinked_excel = excel_rows - linked_count
            self.logger.info(
                f"{unlinked_excel} Excel rows could not be linked to PDF bookmarks"
            )
        elif linked_count < pdf_bookmarks:
            unlinked_bookmarks = pdf_bookmarks - linked_count
            self.logger.info(
                f"{unlinked_bookmarks} PDF bookmarks could not be linked to Excel rows"
            )

        # Store document links for later use in bookmark and reorder steps
        # The links contain the critical mapping information needed for:
        # - Updating bookmark titles with new sorted order
        # - Reordering PDF pages to match Excel sort order
