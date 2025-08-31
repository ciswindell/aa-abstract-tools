#!/usr/bin/env python3
"""
TitleStep: Wrap existing make_titles function in pipeline step.
"""

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.pdf import make_titles


class TitleStep(BaseStep):
    """Pipeline step for generating new PDF bookmark titles from sorted Excel data."""

    def execute(self, context: PipelineContext) -> None:
        """Generate new bookmark titles using existing make_titles function.

        This step creates the mapping from Document IDs to new bookmark titles
        based on the sorted Excel data. The titles follow the format:
        "{Index#}-{Document Type}-{M/D/YYYY}"

        Args:
            context: Pipeline context containing sorted df with Document IDs

        Raises:
            Exception: If title generation fails
        """
        self.logger.info("Generating new PDF bookmark titles from sorted Excel data")

        # Ensure we have data to process
        if context.df is None:
            raise ValueError("No Excel data loaded for title generation")

        # Verify required columns exist
        required_columns = ["Document_ID", "Index#", "Document Type", "Received Date"]
        missing_columns = [
            col for col in required_columns if col not in context.df.columns
        ]
        if missing_columns:
            raise ValueError(
                f"Missing required columns for title generation: {missing_columns}"
            )

        # Store counts for logging
        total_rows = len(context.df)

        # Use existing make_titles function to generate title mapping
        # Returns dict mapping Document_ID -> new title string
        context.titles_map = make_titles(context.df)

        generated_titles = len(context.titles_map)
        self.logger.info(
            f"Title generation complete: {generated_titles} titles generated from {total_rows} rows"
        )

        # Log statistics about title generation success
        if generated_titles == 0:
            self.logger.warning(
                "No titles generated - check required columns and data quality"
            )
        elif generated_titles < total_rows:
            failed_rows = total_rows - generated_titles
            self.logger.info(
                f"{failed_rows} rows could not generate titles (missing required data)"
            )

        # Log sample titles for verification (first few)
        if context.titles_map:
            sample_titles = list(context.titles_map.values())[:3]
            self.logger.info(f"Sample generated titles: {sample_titles}")

        # The titles_map will be used by BookmarkStep to update PDF bookmark titles
        # Format: {document_id: "1-Deed-1/15/2024", document_id: "2-Assignment-2/1/2024", ...}
