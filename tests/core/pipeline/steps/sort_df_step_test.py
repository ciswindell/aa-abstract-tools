#!/usr/bin/env python3
"""
Unit tests for SortDfStep.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from core.pipeline.context import PipelineContext
from core.pipeline.steps.sort_df_step import SortDfStep


class TestSortDfStep:
    """Test SortDfStep functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ui = Mock()
        self.mock_logger = Mock()
        self.step = SortDfStep(
            excel_repo=Mock(),
            pdf_repo=Mock(),
            logger=self.mock_logger,
            ui=self.mock_ui,
        )

    def test_execute_with_include_column(self):
        """Test execute with existing _include column."""
        df = pd.DataFrame(
            {
                "Index#": [3, 1, 2],
                "Document_ID": ["id3", "id1", "id2"],
                "Document Group": ["RS", "TS", "RS"],
                "_include": [True, False, True],  # Only rows 0 and 2 should be sorted
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = df

        # Mock sort_and_renumber function
        with patch("core.pipeline.steps.sort_df_step.sort_and_renumber") as mock_sort:
            # Mock returns sorted DataFrame with renumbered Index#
            sorted_df = pd.DataFrame(
                {
                    "Index#": [1, 2],  # Renumbered
                    "Document_ID": ["id3", "id2"],  # Sorted order
                    "Document Group": ["RS", "RS"],
                    "_include": [True, True],
                }
            )
            mock_sort.return_value = sorted_df

            # Execute the step
            self.step.execute(context)

            # Verify sort_and_renumber was called with flagged rows only
            mock_sort.assert_called_once()
            called_df = mock_sort.call_args[0][0]
            assert len(called_df) == 2  # Only flagged rows
            assert called_df["Document_ID"].tolist() == ["id3", "id2"]

            # Verify DataFrame structure is preserved
            assert len(context.df) == 3  # Same total rows
            assert context.df["_include"].sum() == 2  # Same number of flagged rows

    def test_execute_without_include_column(self):
        """Test execute when _include column doesn't exist."""
        df = pd.DataFrame(
            {
                "Index#": [3, 1, 2],
                "Document_ID": ["id3", "id1", "id2"],
                "Document Group": ["RS", "TS", "RS"],
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = df

        # Mock sort_and_renumber function
        with patch("core.pipeline.steps.sort_df_step.sort_and_renumber") as mock_sort:
            sorted_df = pd.DataFrame(
                {
                    "Index#": [1, 2, 3],  # Renumbered
                    "Document_ID": ["id1", "id2", "id3"],  # Sorted order
                    "Document Group": ["TS", "RS", "RS"],
                    "_include": [True, True, True],
                }
            )
            mock_sort.return_value = sorted_df

            # Execute the step
            self.step.execute(context)

            # Verify _include column was created
            assert "_include" in context.df.columns
            assert context.df["_include"].all()  # All rows should be True

            # Verify sort_and_renumber was called with all rows
            mock_sort.assert_called_once()
            called_df = mock_sort.call_args[0][0]
            assert len(called_df) == 3  # All rows

    def test_execute_with_source_column_logging(self):
        """Test execute logs source breakdown correctly."""
        df = pd.DataFrame(
            {
                "Index#": [1, 2, 3, 4],
                "Document_ID": ["id1", "id2", "id3", "id4"],
                "Source": ["file1", "file1", "file2", "file2"],
                "_include": [True, False, True, True],
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = df

        # Mock sort_and_renumber function
        with patch("core.pipeline.steps.sort_df_step.sort_and_renumber") as mock_sort:
            sorted_df = pd.DataFrame(
                {
                    "Index#": [1, 2, 3],
                    "Document_ID": ["id1", "id3", "id4"],
                    "Source": ["file1", "file2", "file2"],
                    "_include": [True, True, True],
                }
            )
            mock_sort.return_value = sorted_df

            # Execute the step
            self.step.execute(context)

            # Verify logging was called for source breakdown
            self.mock_logger.info.assert_called()
            log_calls = [call.args[0] for call in self.mock_logger.info.call_args_list]

            # Should log "About to sort" and "After sort rebuild" messages
            assert any("About to sort" in call for call in log_calls)
            assert any("After sort rebuild" in call for call in log_calls)

    def test_execute_with_empty_flagged_rows(self):
        """Test execute with no flagged rows skips gracefully."""
        df = pd.DataFrame(
            {
                "Index#": [1, 2, 3],
                "Document_ID": ["id1", "id2", "id3"],
                "_include": [False, False, False],  # No rows flagged
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = df

        # Execute should complete without error (graceful skip)
        self.step.execute(context)

        # Verify warning was logged
        self.mock_logger.warning.assert_called_once_with(
            "No rows flagged for sorting - skipping sort operation"
        )

    def test_execute_with_missing_required_columns(self):
        """Test execute with missing required columns raises error."""
        df = pd.DataFrame(
            {
                "Document_ID": ["id1", "id2", "id3"],
                # Missing Index# column
                "_include": [True, True, True],
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = df

        # Execute should raise ValueError
        with pytest.raises(ValueError, match="Required columns missing"):
            self.step.execute(context)

    def test_execute_with_no_dataframe(self):
        """Test execute with no DataFrame raises error."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = None

        # Execute should raise ValueError
        with pytest.raises(ValueError, match="No Excel data loaded"):
            self.step.execute(context)

    def test_execute_preserves_unflagged_rows(self):
        """Test execute preserves unflagged rows in original positions."""
        df = pd.DataFrame(
            {
                "Index#": [3, 1, 2, 4],
                "Document_ID": ["id3", "id1", "id2", "id4"],
                "Document Group": ["RS", "TS", "RS", "TS"],
                "_include": [True, False, True, False],  # Only rows 0 and 2 flagged
            }
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = df

        # Mock sort_and_renumber function
        with patch("core.pipeline.steps.sort_df_step.sort_and_renumber") as mock_sort:
            # Return sorted flagged rows
            sorted_df = pd.DataFrame(
                {
                    "Index#": [1, 2],  # Renumbered
                    "Document_ID": ["id2", "id3"],  # Sorted order (id2 before id3)
                    "Document Group": ["RS", "RS"],
                    "_include": [True, True],
                }
            )
            mock_sort.return_value = sorted_df

            # Execute the step
            self.step.execute(context)

            # Verify total row count is preserved
            assert len(context.df) == 4

            # Verify flagged rows count is preserved
            assert context.df["_include"].sum() == 2

            # Verify unflagged rows still exist
            unflagged_rows = context.df[~context.df["_include"]]
            assert len(unflagged_rows) == 2

    def test_execute_handles_sort_failure(self):
        """Test execute handles sort_and_renumber failure gracefully."""
        df = pd.DataFrame(
            {"Index#": [1, 2], "Document_ID": ["id1", "id2"], "_include": [True, True]}
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = df

        # Mock sort_and_renumber to raise exception
        with patch("core.pipeline.steps.sort_df_step.sort_and_renumber") as mock_sort:
            mock_sort.side_effect = Exception("Sort failed")

            # Execute should raise ValueError with descriptive message
            with pytest.raises(
                ValueError, match="Failed to sort and renumber DataFrame"
            ):
                self.step.execute(context)

    def test_execute_validates_sort_results(self):
        """Test execute validates that sort doesn't change row count."""
        df = pd.DataFrame(
            {"Index#": [1, 2], "Document_ID": ["id1", "id2"], "_include": [True, True]}
        )

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = df

        # Mock sort_and_renumber to return wrong number of rows
        with patch("core.pipeline.steps.sort_df_step.sort_and_renumber") as mock_sort:
            # Return fewer rows than input
            sorted_df = pd.DataFrame(
                {
                    "Index#": [1],  # Only 1 row instead of 2
                    "Document_ID": ["id1"],
                    "_include": [True],
                }
            )
            mock_sort.return_value = sorted_df

            # Execute should raise ValueError
            with pytest.raises(ValueError, match="Row count changed during sorting"):
                self.step.execute(context)

    def test_execute_boolean_column_handling(self):
        """Test execute properly handles boolean _include column creation."""
        df = pd.DataFrame({"Index#": [1, 2, 3], "Document_ID": ["id1", "id2", "id3"]})

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = df

        # Mock sort_and_renumber function
        with patch("core.pipeline.steps.sort_df_step.sort_and_renumber") as mock_sort:
            sorted_df = pd.DataFrame(
                {
                    "Index#": [1, 2, 3],
                    "Document_ID": ["id1", "id2", "id3"],
                    "_include": [True, True, True],
                }
            )
            mock_sort.return_value = sorted_df

            # Execute the step
            self.step.execute(context)

            # Verify _include column is proper boolean type
            assert context.df["_include"].dtype == bool
            assert not context.df["_include"].isna().any()  # No NaN values
