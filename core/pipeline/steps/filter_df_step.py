#!/usr/bin/env python3
"""
FilterDfStep: Filter DataFrame rows by column values with conditional execution.
"""

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep


class FilterDfStep(BaseStep):
    """Pipeline step for filtering DataFrame rows by column values."""

    def should_execute(self, context: PipelineContext) -> bool:
        """Only execute if filtering is enabled and filter values are provided."""
        return (
            context.options.get("filter_enabled", False)
            and context.options.get("filter_column") is not None
            and context.options.get("filter_values") is not None
            and len(context.options.get("filter_values", [])) > 0
        )

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

            # Initialize _include column if it doesn't exist (first time filtering)
            if "_include" not in context.df.columns:
                context.df["_include"] = True  # Default: include all rows

            # Validate filter column exists in DataFrame
            if filter_column not in context.df.columns:
                available_columns = list(context.df.columns)
                raise ValueError(
                    f"Filter column '{filter_column}' not found in DataFrame. "
                    f"Available columns: {available_columns}"
                )

            # Apply filter by flagging matching rows
            try:
                context.df["_include"] = context.df[filter_column].isin(filter_values)
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

        # Warn if all rows were filtered out
        if included_rows == 0:
            self.logger.warning(
                "All rows were filtered out - no data flagged for processing"
            )
