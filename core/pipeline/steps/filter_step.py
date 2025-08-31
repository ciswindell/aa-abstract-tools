#!/usr/bin/env python3
"""
FilterStep: Wrap existing filter_df function with conditional execution.
"""

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.excel import filter_df


class FilterStep(BaseStep):
    """Pipeline step for optionally filtering Excel DataFrame."""

    def should_execute(self, context: PipelineContext) -> bool:
        """Only execute if filtering is enabled and filter values are provided."""
        return (
            context.options.filter_enabled
            and context.options.filter_column is not None
            and context.options.filter_values is not None
            and len(context.options.filter_values) > 0
        )

    def execute(self, context: PipelineContext) -> None:
        """Filter DataFrame using existing filter_df function.

        This step conditionally filters the DataFrame based on options:
        - Only executes if filter_enabled is True and filter values are provided
        - Uses existing filter_df function to filter by column values
        - Resets DataFrame index after filtering

        Args:
            context: Pipeline context containing df to filter and filter options

        Raises:
            Exception: If filtering fails
        """
        self.logger.info(
            f"Filtering DataFrame by column '{context.options.filter_column}' "
            f"with {len(context.options.filter_values)} values"
        )

        # Ensure we have data to filter
        if context.df is None:
            raise ValueError("No Excel data loaded for filtering")

        # Store original row count for logging
        original_rows = len(context.df)

        # Use existing filter_df function to filter data
        context.df = filter_df(
            context.df, context.options.filter_column, context.options.filter_values
        )

        filtered_rows = len(context.df)
        self.logger.info(
            f"Filtering complete: {original_rows} -> {filtered_rows} rows "
            f"({original_rows - filtered_rows} rows filtered out)"
        )

        # Warn if all rows were filtered out
        if filtered_rows == 0:
            self.logger.warning(
                "All rows were filtered out - no data remaining for processing"
            )
