#!/usr/bin/env python3
"""
Unit tests for FilterDfStep.
"""

from unittest.mock import Mock

import pandas as pd
import pytest

from core.pipeline.context import PipelineContext
from core.pipeline.steps.filter_df_step import FilterDfStep


class TestFilterDfStep:
    """Test FilterDfStep functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ui = Mock()
        self.mock_logger = Mock()
        self.step = FilterDfStep(
            excel_repo=Mock(),
            pdf_repo=Mock(),
            validator=Mock(),
            logger=self.mock_logger,
            ui=self.mock_ui,
        )

    def test_should_execute_when_filter_enabled(self):
        """Test should_execute returns True when filter is enabled."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={"filter_enabled": True},
        )

        assert self.step.should_execute(context) is True

    def test_should_execute_when_filter_disabled(self):
        """Test should_execute returns False when filter is disabled."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={"filter_enabled": False},
        )

        assert self.step.should_execute(context) is False

    def test_should_execute_when_filter_not_set(self):
        """Test should_execute returns False when filter option is not set."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )

        assert self.step.should_execute(context) is False

    def test_execute_with_existing_filter_values(self):
        """Test execute with pre-configured filter values."""
        # Create test DataFrame
        df = pd.DataFrame(
            {
                "Index#": ["1", "2", "3", "4"],
                "Document_ID": ["id1", "id2", "id3", "id4"],
                "Document Group": ["RS", "TS", "RS", "TS"],
                "Source": ["file1", "file1", "file1", "file1"],
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={
                "filter_enabled": True,
                "filter_column": "Document Group",
                "filter_values": ["RS"],
            },
        )
        context.df = df

        # Execute the step
        self.step.execute(context)

        # Verify _include column was added correctly
        assert "_include" in context.df.columns
        expected_include = [True, False, True, False]  # RS rows should be True
        assert context.df["_include"].tolist() == expected_include

        # Verify logging
        self.mock_logger.info.assert_called()

    def test_execute_with_filter_prompt(self):
        """Test execute when filter values need to be prompted."""
        # Create test DataFrame
        df = pd.DataFrame(
            {
                "Index#": ["1", "2", "3"],
                "Document_ID": ["id1", "id2", "id3"],
                "Document Group": ["RS", "TS", "RS"],
                "Source": ["file1", "file1", "file1"],
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={"filter_enabled": True},
        )
        context.df = df

        # Mock UI prompt response
        self.mock_ui.prompt_filter_selection.return_value = ("Document Group", ["RS"])

        # Execute the step
        self.step.execute(context)

        # Verify UI was called
        self.mock_ui.prompt_filter_selection.assert_called_once_with(df)

        # Verify _include column was added correctly
        assert "_include" in context.df.columns
        expected_include = [True, False, True]  # RS rows should be True
        assert context.df["_include"].tolist() == expected_include

        # Verify options were updated
        assert context.options["filter_column"] == "Document Group"
        assert context.options["filter_values"] == ["RS"]

    def test_execute_with_user_cancellation(self):
        """Test execute when user cancels filter selection."""
        df = pd.DataFrame(
            {
                "Index#": ["1", "2"],
                "Document_ID": ["id1", "id2"],
                "Document Group": ["RS", "TS"],
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={"filter_enabled": True},
        )
        context.df = df

        # Mock UI prompt response (user cancels)
        self.mock_ui.prompt_filter_selection.return_value = (None, [])

        # Execute the step
        self.step.execute(context)

        # Verify no _include column was added
        assert "_include" not in context.df.columns

    def test_execute_with_invalid_filter_column(self):
        """Test execute with invalid filter column raises error."""
        df = pd.DataFrame(
            {
                "Index#": ["1", "2"],
                "Document_ID": ["id1", "id2"],
                "Document Group": ["RS", "TS"],
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={
                "filter_enabled": True,
                "filter_column": "NonExistentColumn",
                "filter_values": ["RS"],
            },
        )
        context.df = df

        # Execute should raise ValueError
        with pytest.raises(
            ValueError, match="Filter column 'NonExistentColumn' not found"
        ):
            self.step.execute(context)

    def test_execute_with_empty_dataframe(self):
        """Test execute with empty DataFrame raises error."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={
                "filter_enabled": True,
                "filter_column": "Document Group",
                "filter_values": ["RS"],
            },
        )
        context.df = pd.DataFrame()  # Empty DataFrame

        # Execute should raise ValueError
        with pytest.raises(ValueError, match="DataFrame is empty"):
            self.step.execute(context)

    def test_execute_with_no_dataframe(self):
        """Test execute with no DataFrame raises error."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={
                "filter_enabled": True,
                "filter_column": "Document Group",
                "filter_values": ["RS"],
            },
        )
        context.df = None

        # Execute should raise ValueError
        with pytest.raises(ValueError, match="No Excel data loaded"):
            self.step.execute(context)

    def test_execute_with_mixed_data_types(self):
        """Test execute handles mixed data types in filter column."""
        df = pd.DataFrame(
            {
                "Index#": ["1", "2", "3", "4"],
                "Document_ID": ["id1", "id2", "id3", "id4"],
                "Mixed_Column": ["RS", 123, "RS", None],  # Mixed types
                "Source": ["file1", "file1", "file1", "file1"],
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={
                "filter_enabled": True,
                "filter_column": "Mixed_Column",
                "filter_values": ["RS"],
            },
        )
        context.df = df

        # Execute the step
        self.step.execute(context)

        # Verify _include column was added correctly
        assert "_include" in context.df.columns
        expected_include = [True, False, True, False]  # Only "RS" strings should match
        assert context.df["_include"].tolist() == expected_include

    def test_execute_preserves_dataframe_structure(self):
        """Test execute preserves original DataFrame structure."""
        df = pd.DataFrame(
            {
                "Index#": ["1", "2", "3"],
                "Document_ID": ["id1", "id2", "id3"],
                "Document Group": ["RS", "TS", "RS"],
                "Other_Column": ["A", "B", "C"],
            }
        )
        original_columns = df.columns.tolist()
        original_index = df.index.tolist()

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={
                "filter_enabled": True,
                "filter_column": "Document Group",
                "filter_values": ["RS"],
            },
        )
        context.df = df

        # Execute the step
        self.step.execute(context)

        # Verify original structure is preserved
        assert len(context.df) == 3  # Same number of rows
        assert context.df.index.tolist() == original_index  # Same index

        # Verify all original columns are still there
        for col in original_columns:
            assert col in context.df.columns

        # Verify _include column was added
        assert "_include" in context.df.columns
        assert len(context.df.columns) == len(original_columns) + 1
