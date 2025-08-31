#!/usr/bin/env python3
"""
MergeStep: Merge multiple file pairs into single DataFrame/PDF early in process.
"""

from typing import Any, List, Mapping

import pandas as pd

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.excel import add_document_ids


class MergeStep(BaseStep):
    """Pipeline step for merging multiple file pairs into single workflow."""

    def should_execute(self, context: PipelineContext) -> bool:
        """Only execute if this is a merge workflow."""
        return context.is_merge_workflow()

    def execute(self, context: PipelineContext) -> None:
        """Merge multiple file pairs into single DataFrame and PDF data.

        This step consolidates all loaded file pairs into a single workflow,
        eliminating the need for complex conditional branching in later steps.

        Args:
            context: Pipeline context containing loaded merge data

        Raises:
            Exception: If merging fails
        """
        self.logger.info("Merging multiple file pairs into single workflow")

        # Merge DataFrames
        self._merge_dataframes(context)

        # Merge PDF data with page offset tracking
        self._merge_pdf_data(context)

        # Clear merge-specific data to save memory
        self._cleanup_merge_data(context)

        self.logger.info(
            f"Merge complete: {len(context.df)} rows, {context.total_pages} pages"
        )

    def _merge_dataframes(self, context: PipelineContext) -> None:
        """Merge all DataFrame parts into a single DataFrame.

        CRITICAL: Add Document IDs BEFORE merging to prevent ID collisions.
        Each DataFrame gets unique IDs based on its original source path.
        """
        if not context.merged_df_parts or not context.merged_df_source_paths:
            context.df = pd.DataFrame()
            return

        self.logger.info(
            f"Adding Document IDs to {len(context.merged_df_parts)} DataFrames before merge"
        )

        # Add Document IDs to each DataFrame part individually to preserve uniqueness
        df_parts_with_ids = []
        for i, (df_part, source_path) in enumerate(
            zip(context.merged_df_parts, context.merged_df_source_paths)
        ):
            self.logger.info(f"Adding Document IDs for {source_path}")
            df_with_ids = add_document_ids(df_part, source_path)
            df_parts_with_ids.append(df_with_ids)

        # Now merge DataFrames that already have unique Document IDs
        self.logger.info(
            f"Merging {len(df_parts_with_ids)} DataFrames with unique Document IDs"
        )
        context.df = pd.concat(df_parts_with_ids, ignore_index=True)

    def _merge_pdf_data(self, context: PipelineContext) -> None:
        """Merge PDF data with proper page offset tracking."""
        if not context.merged_pages or not context.merged_bookmarks:
            context.pages = []
            context.bookmarks = []
            context.total_pages = 0
            context.merged_links = []
            return

        # Set merged pages and bookmarks
        context.pages = context.merged_pages
        context.bookmarks = self._adjust_bookmark_pages(context.merged_bookmarks)
        context.total_pages = len(context.merged_pages)

        # Initialize merged_links for later use in bookmark processing
        # This will be populated by LinkStep after document IDs are added
        context.merged_links = []

    def _adjust_bookmark_pages(
        self, bookmarks: List[Mapping[str, Any]]
    ) -> List[Mapping[str, Any]]:
        """Adjust bookmark page numbers for merged PDF.

        Since LoadStep already accumulated bookmarks from multiple PDFs,
        we need to adjust page numbers to account for the merged structure.
        This is handled by tracking page offsets during the load process.

        Args:
            bookmarks: List of bookmark dictionaries

        Returns:
            List of adjusted bookmark dictionaries
        """
        # For now, return bookmarks as-is since LoadStep should handle page offsets
        # This method is a placeholder for future enhancements if needed
        return [dict(bm) for bm in bookmarks]

    def _cleanup_merge_data(self, context: PipelineContext) -> None:
        """Clear merge-specific data to save memory."""
        context.merged_df_parts = None
        context.merged_df_source_paths = None
        context.merged_pages = None
        context.merged_bookmarks = None
