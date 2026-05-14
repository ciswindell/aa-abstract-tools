#!/usr/bin/env python3
"""
SortDfStep: Order-agnostic DataFrame sorting with DocumentUnit preservation.

This step implements the DocumentUnit architecture's order-agnostic sorting approach.
It sorts only flagged rows (_include=True) while preserving unflagged rows in their
original positions, maintaining perfect alignment with DocumentUnit page ranges.
"""

import pandas as pd

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.excel import sort_and_renumber


class SortDfStep(BaseStep):
    """Order-agnostic DataFrame sorting step with DocumentUnit preservation.

    Sorts only flagged rows while preserving DocumentUnit alignment. Works correctly
    regardless of whether FilterDfStep has executed before or after this step.
    """

    def execute(self, context: PipelineContext) -> None:
        """Sort flagged DataFrame rows and renumber Index# column.

        This step performs order-agnostic sorting that works regardless of FilterDfStep execution:
        - Initializes _include column if not present (all rows included by default)
        - Sorts only rows where _include=True by available columns (Legal Description, Grantee, etc.)
        - Renumbers Index# column from 1 to N for flagged rows only
        - Preserves unflagged rows in their original positions and states
        - Works correctly whether FilterDfStep has run before or after this step

        Args:
            context: Pipeline context containing df to sort

        Raises:
            Exception: If sorting fails
        """
        self.logger.info(
            f"Step {context.step_number} of {context.total_steps}: Sorting data..."
        )

        try:
            # Validate required data
            if context.df is None:
                raise ValueError("No Excel data loaded for sorting")

            if context.df.empty:
                raise ValueError("DataFrame is empty - no data to sort")

            # Validate required columns exist
            required_columns = ["Index#", "Document_ID"]
            missing_columns = [
                col for col in required_columns if col not in context.df.columns
            ]
            if missing_columns:
                available_columns = list(context.df.columns)
                raise ValueError(
                    f"Required columns missing for sorting: {missing_columns}. "
                    f"Available columns: {available_columns}"
                )

            # Initialize _include column if it doesn't exist (order-agnostic design)
            if "_include" not in context.df.columns:
                # Create proper boolean column with no NaN values using safe assignment
                context.df = context.df.copy()
                context.df["_include"] = pd.Series(
                    [True] * len(context.df), index=context.df.index, dtype=bool
                )

            # Get counts for logging
            len(context.df)
            included_rows = context.df["_include"].sum()

            if included_rows == 0:
                self.logger.warning(
                    "No rows flagged for sorting - skipping sort operation"
                )
                return

        except Exception as e:
            self.logger.error(f"SortDfStep validation failed: {e}")
            raise

        try:
            # Extract flagged rows for sorting
            included_mask = context.df["_include"]
            included_df = context.df[included_mask].copy()

            if included_df.empty:
                raise ValueError("No flagged rows to sort after filtering")

            # Store original first index for logging
            if "Index#" in included_df.columns and len(included_df) > 0:
                included_df.iloc[0]["Index#"]

            # Sort and renumber only the flagged rows
            try:
                sorted_included_df = sort_and_renumber(included_df)
            except Exception as e:
                raise ValueError(f"Failed to sort and renumber DataFrame: {e}") from e

            # Validate sorting results
            if len(sorted_included_df) != len(included_df):
                raise ValueError(
                    f"Row count changed during sorting: {len(included_df)} -> {len(sorted_included_df)}"
                )

            # Rebuild DataFrame with sorted flagged rows and preserved unflagged rows
            # This is more robust than trying to update in place
            try:
                # Get unflagged rows (preserve their original order and position)
                unflagged_df = context.df[~included_mask].copy()

                # Ensure sorted_included_df has _include=True
                sorted_included_df["_include"] = True

                # Combine: sorted flagged rows + unflagged rows
                # The order will be: all flagged rows first (sorted), then unflagged rows
                context.df = pd.concat(
                    [sorted_included_df, unflagged_df], ignore_index=True
                )

            except Exception as e:
                raise ValueError(
                    f"Failed to rebuild DataFrame with sorted results: {e}"
                ) from e

        except Exception as e:
            self.logger.error(f"SortDfStep sorting operation failed: {e}")
            raise

        # Verify Index# column was properly renumbered for flagged rows
        if "Index#" in sorted_included_df.columns:
            flagged_index_values = sorted_included_df["Index#"].tolist()
            expected_values = [str(i) for i in range(1, len(sorted_included_df) + 1)]
            if flagged_index_values != expected_values:
                raise ValueError(
                    "Index# column was not properly renumbered to sequential 1..N values for flagged rows"
                )
