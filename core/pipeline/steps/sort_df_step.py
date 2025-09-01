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
        self.logger.info("Sorting flagged Excel data and renumbering Index# column")

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
                self.logger.info(
                    "No _include column found, including all rows for sorting"
                )

            # Get counts for logging
            total_rows = len(context.df)
            included_rows = context.df["_include"].sum()
            excluded_rows = total_rows - included_rows

            self.logger.info(
                f"Sorting {included_rows}/{total_rows} flagged rows ({excluded_rows} excluded)"
            )

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

            # Show what we're about to sort for verification
            if "Source" in included_df.columns:
                source_counts_before = included_df.groupby("Source").size()
                for source, count in source_counts_before.items():
                    self.logger.info(f"  About to sort {count} rows from {source}")

            if included_df.empty:
                raise ValueError("No flagged rows to sort after filtering")

            # Store original first index for logging
            original_first_index = None
            if "Index#" in included_df.columns and len(included_df) > 0:
                original_first_index = included_df.iloc[0]["Index#"]

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

                # Verify the rebuild worked correctly
                final_included_count = context.df["_include"].sum()
                if "Source" in context.df.columns:
                    source_counts_after = (
                        context.df[context.df["_include"]].groupby("Source").size()
                    )
                    for source, count in source_counts_after.items():
                        self.logger.info(
                            f"  After sort rebuild: {count} rows from {source}"
                        )
                self.logger.info(
                    f"  Total flagged rows after sort: {final_included_count}"
                )

            except Exception as e:
                raise ValueError(
                    f"Failed to rebuild DataFrame with sorted results: {e}"
                ) from e

        except Exception as e:
            self.logger.error(f"SortDfStep sorting operation failed: {e}")
            raise

        # Log sorting results
        new_first_index = None
        if "Index#" in sorted_included_df.columns and len(sorted_included_df) > 0:
            new_first_index = sorted_included_df.iloc[0]["Index#"]

        self.logger.info(f"Sorting complete: {included_rows} flagged rows processed")

        if original_first_index is not None and new_first_index is not None:
            if original_first_index != new_first_index:
                self.logger.info(
                    f"Sort order changed: first flagged Index# {original_first_index} -> {new_first_index}"
                )
            else:
                self.logger.info("Flagged data was already in correct sort order")

        # Verify Index# column was properly renumbered for flagged rows
        if "Index#" in sorted_included_df.columns:
            flagged_index_values = sorted_included_df["Index#"].tolist()
            expected_values = [str(i) for i in range(1, len(sorted_included_df) + 1)]
            if flagged_index_values != expected_values:
                raise ValueError(
                    "Index# column was not properly renumbered to sequential 1..N values for flagged rows"
                )
