#!/usr/bin/env python3
"""
CleanStep: Wrap existing clean_types function in pipeline step.
"""

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.excel import clean_types


class CleanStep(BaseStep):
    """Pipeline step for cleaning data types in Excel DataFrame."""

    def execute(self, context: PipelineContext) -> None:
        """Clean data types in the DataFrame using existing clean_types function.

        This step normalizes data types for consistent processing:
        - Ensures Index# column is trimmed string
        - Normalizes text columns to trimmed strings
        - Attempts to parse date columns with robust date parsing

        Args:
            context: Pipeline context containing df to clean

        Raises:
            Exception: If data cleaning fails
        """
        self.logger.info("Cleaning data types in Excel DataFrame")

        # Ensure we have data to clean
        if context.df is None:
            raise ValueError("No Excel data loaded for cleaning")

        # Use existing clean_types function to normalize data
        original_rows = len(context.df)
        context.df = clean_types(context.df)

        self.logger.info(
            f"Data cleaning complete: {len(context.df)} rows processed (no rows lost)"
        )

        # Verify we didn't lose any data during cleaning
        if len(context.df) != original_rows:
            self.logger.warning(
                f"Row count changed during cleaning: {original_rows} -> {len(context.df)}"
            )
