#!/usr/bin/env python3
"""
ValidateStep: Wrap existing ValidationService in pipeline step.
"""

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep


class ValidateStep(BaseStep):
    """Pipeline step for validating Excel and PDF data."""

    def execute(self, context: PipelineContext) -> None:
        """Validate Excel DataFrame and PDF bookmarks using existing ValidationService.

        This step validates the data after loading/merging but before any transformations.
        Uses the existing ValidationService which checks for required columns,
        duplicate bookmark indices, and other data integrity requirements.

        Args:
            context: Pipeline context containing df and bookmarks to validate

        Raises:
            Exception: If validation fails (propagated from ValidationService)
        """
        self.logger.info("Validating Excel and PDF data")

        # Ensure we have data to validate
        if context.df is None:
            raise ValueError("No Excel data loaded for validation")

        if context.bookmarks is None:
            raise ValueError("No PDF bookmarks loaded for validation")

        # Use existing ValidationService to validate data
        # This will raise exceptions if validation fails (fail-fast behavior)
        self.validator.run(df=context.df, bookmarks=context.bookmarks)

        self.logger.info(
            f"Validation passed: {len(context.df)} Excel rows, {len(context.bookmarks)} PDF bookmarks"
        )
