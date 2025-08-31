#!/usr/bin/env python3
"""
AddIdsStep: Wrap existing add_document_ids function with conditional execution.
"""

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.excel import add_document_ids


class AddIdsStep(BaseStep):
    """Pipeline step for adding Document IDs to Excel DataFrame."""

    def should_execute(self, context: PipelineContext) -> bool:
        """Only execute if Document_ID column doesn't already exist.

        For merge workflows, Document IDs are added in MergeStep before merging
        to prevent ID collisions. For single-file workflows, we add them here.

        Returns:
            True if Document_ID column is missing, False if it already exists
        """
        if context.df is None:
            return False

        has_document_ids = "Document_ID" in context.df.columns
        if has_document_ids:
            self.logger.info("Document IDs already exist - skipping AddIdsStep")

        return not has_document_ids

    def execute(self, context: PipelineContext) -> None:
        """Add Document IDs to DataFrame using existing add_document_ids function.

        This step adds unique Document IDs for single-file workflows.
        For merge workflows, this step is skipped since IDs are already added.

        Args:
            context: Pipeline context containing df and source path

        Raises:
            Exception: If Document ID generation fails
        """
        self.logger.info("Adding Document IDs to Excel DataFrame")

        # Ensure we have data to process
        if context.df is None:
            raise ValueError("No Excel data loaded for adding Document IDs")

        # Store original row count for verification
        original_rows = len(context.df)

        # Use existing add_document_ids function
        # For single-file workflows, use the primary excel_path
        context.df = add_document_ids(context.df, context.excel_path)

        # Verify we didn't lose any data and Document_ID was added
        if len(context.df) != original_rows:
            raise ValueError(
                f"Row count changed during Document ID generation: {original_rows} -> {len(context.df)}"
            )

        if "Document_ID" not in context.df.columns:
            raise ValueError("Document_ID column was not added to DataFrame")

        # Count unique Document IDs to verify uniqueness
        unique_ids = context.df["Document_ID"].nunique()
        total_rows = len(context.df)

        if unique_ids != total_rows:
            raise ValueError(
                f"Document ID collision detected: {unique_ids} unique IDs for {total_rows} rows"
            )

        self.logger.info(
            f"Document IDs added successfully: {unique_ids} unique IDs for {total_rows} rows"
        )
