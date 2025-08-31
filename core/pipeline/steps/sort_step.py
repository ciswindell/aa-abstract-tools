#!/usr/bin/env python3
"""
SortStep: Wrap existing sort_and_renumber function in pipeline step.
"""

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.excel import sort_and_renumber


class SortStep(BaseStep):
    """Pipeline step for sorting Excel data and renumbering Index# column."""

    def execute(self, context: PipelineContext) -> None:
        """Sort DataFrame and renumber Index# column using existing sort_and_renumber function.

        This step performs the core business logic of the application:
        - Sorts by available columns in ascending order (Legal Description, Grantee, etc.)
        - Renumbers Index# column from 1 to N based on new sort order
        - Resets DataFrame index to maintain consistency

        Args:
            context: Pipeline context containing df to sort

        Raises:
            Exception: If sorting fails
        """
        self.logger.info("Sorting Excel data and renumbering Index# column")

        # Ensure we have data to sort
        if context.df is None:
            raise ValueError("No Excel data loaded for sorting")

        # Store original row count and order info for logging
        original_rows = len(context.df)
        original_first_index = None
        if "Index#" in context.df.columns and len(context.df) > 0:
            original_first_index = context.df.iloc[0]["Index#"]

        # Use existing sort_and_renumber function
        # This sorts by default columns and renumbers Index# from 1..N
        context.df = sort_and_renumber(context.df)

        # Verify sorting completed successfully
        sorted_rows = len(context.df)
        if sorted_rows != original_rows:
            raise ValueError(
                f"Row count changed during sorting: {original_rows} -> {sorted_rows}"
            )

        # Log sorting results
        new_first_index = None
        if "Index#" in context.df.columns and len(context.df) > 0:
            new_first_index = context.df.iloc[0]["Index#"]

        self.logger.info(f"Sorting complete: {sorted_rows} rows processed")

        if original_first_index is not None and new_first_index is not None:
            if original_first_index != new_first_index:
                self.logger.info(
                    f"Sort order changed: first Index# {original_first_index} -> {new_first_index}"
                )
            else:
                self.logger.info("Data was already in correct sort order")

        # Verify Index# column was properly renumbered
        if "Index#" in context.df.columns:
            index_values = context.df["Index#"].tolist()
            expected_values = list(range(1, len(context.df) + 1))
            if index_values != expected_values:
                raise ValueError(
                    "Index# column was not properly renumbered to sequential 1..N values"
                )
