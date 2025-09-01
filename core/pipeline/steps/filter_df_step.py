#!/usr/bin/env python3
"""
FilterDfStep: Filter DataFrame rows by column values with conditional execution.
"""

import pandas as pd

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep


class FilterDfStep(BaseStep):
    """Pipeline step for filtering DataFrame rows by column values."""

    def should_execute(self, context: PipelineContext) -> bool:
        """Only execute if filtering is enabled."""
        return context.options.get("filter_enabled", False)

    def execute(self, context: PipelineContext) -> None:
        """Flag DataFrame rows for inclusion instead of removing them.

        This step adds an '_include' flag column to mark which rows should be processed:
        - Only executes if filter_enabled is True and filter values are provided
        - Flags rows that match filter criteria with _include=True
        - Preserves all rows to maintain DocumentUnit alignment
        - Works regardless of whether SortDfStep has run before or after

        Args:
            context: Pipeline context containing df to filter and filter options

        Raises:
            Exception: If filtering fails
        """
        filter_column = context.options.get("filter_column")
        filter_values = context.options.get("filter_values", [])

        # If filter values are not set, prompt the user with the merged DataFrame
        if not filter_column or not filter_values:
            self.logger.info("Filter enabled but no values selected - prompting user")

            # Show available values by source for user reference
            if (
                "Source" in context.df.columns
                and "Document Group" in context.df.columns
            ):
                source_groups = context.df.groupby("Source")["Document Group"].unique()
                for source, groups in source_groups.items():
                    # Filter out NaN values and convert to strings for sorting
                    clean_groups = [str(g) for g in groups if pd.notna(g)]
                    self.logger.info(
                        f"Available 'Document Group' values in {source}: {sorted(clean_groups)}"
                    )

            try:
                col, vals = self.ui.prompt_filter_selection(context.df)
                if col and vals:
                    filter_column = col
                    filter_values = vals
                    # Update context options for consistency
                    context.options["filter_column"] = col
                    context.options["filter_values"] = vals
                else:
                    self.logger.info(
                        "User cancelled filter selection - skipping filter"
                    )
                    return
            except Exception as e:
                self.logger.error(f"Failed to prompt for filter selection: {e}")
                return

        self.logger.info(
            f"Flagging DataFrame rows by column '{filter_column}' "
            f"with {len(filter_values)} values"
        )

        try:
            # Validate required data
            if context.df is None:
                raise ValueError("No Excel data loaded for filtering")

            if context.df.empty:
                raise ValueError("DataFrame is empty - no data to filter")

            # Validate filter configuration (already extracted above)

            if not filter_column:
                raise ValueError("Filter column name is empty or None")

            if not filter_values or len(filter_values) == 0:
                raise ValueError("Filter values list is empty")

            # Store original row count for logging
            total_rows = len(context.df)

            # Validate filter column exists in DataFrame
            if filter_column not in context.df.columns:
                available_columns = list(context.df.columns)
                raise ValueError(
                    f"Filter column '{filter_column}' not found in DataFrame. "
                    f"Available columns: {available_columns}"
                )

                # Apply filter by creating a proper boolean column
            try:
                # Create boolean mask for matching rows
                filter_mask = context.df[filter_column].isin(filter_values)

                # Create a new DataFrame with the _include column to avoid assignment issues
                context.df = context.df.copy()
                context.df["_include"] = pd.Series(
                    filter_mask.astype(bool), index=context.df.index, dtype=bool
                )

            except Exception as e:
                raise ValueError(
                    f"Failed to apply filter on column '{filter_column}': {e}"
                ) from e

        except Exception as e:
            self.logger.error(f"FilterDfStep execution failed: {e}")
            raise

        # Count flagged rows for logging
        included_rows = context.df["_include"].sum()
        excluded_rows = total_rows - included_rows

        self.logger.info(
            f"Filtering complete: {included_rows}/{total_rows} rows flagged for inclusion "
            f"({excluded_rows} rows excluded)"
        )

        # Show filter results by source for verification
        if "Source" in context.df.columns:
            source_results = context.df.groupby("Source")["_include"].agg(
                ["sum", "count"]
            )
            for source, (included, total) in source_results.iterrows():
                excluded = total - included
                self.logger.info(
                    f"  {source}: {included}/{total} included ({excluded} excluded)"
                )

        # Show applied filter for verification
        self.logger.info(f"Filter applied: {filter_column} in {filter_values}")

        # Warn if all rows were filtered out
        if included_rows == 0:
            self.logger.warning(
                "All rows were filtered out - no data flagged for processing"
            )
