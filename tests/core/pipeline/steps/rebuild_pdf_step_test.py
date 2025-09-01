#!/usr/bin/env python3
"""
Unit tests for RebuildPdfStep.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from core.models import DocumentUnit
from core.pipeline.context import PipelineContext
from core.pipeline.steps.rebuild_pdf_step import RebuildPdfStep


class TestRebuildPdfStep:
    """Test RebuildPdfStep functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ui = Mock()
        self.mock_logger = Mock()
        self.step = RebuildPdfStep(
            excel_repo=Mock(),
            pdf_repo=Mock(),
            logger=self.mock_logger,
            ui=self.mock_ui,
        )

    def create_test_context(
        self, include_flags=None, reorder_pages=True, sort_bookmarks=True
    ):
        """Create a test context with DocumentUnits and DataFrame."""
        # Create test DataFrame with required columns for make_titles
        df = pd.DataFrame(
            {
                "Index#": [1, 2, 3],
                "Document_ID": ["id1", "id2", "id3"],
                "Document Type": ["Deed", "Assignment", "Deed"],
                "Received Date": ["1/1/2023", "2/1/2023", "3/1/2023"],
            }
        )

        if include_flags:
            df["_include"] = include_flags

        # Create test DocumentUnits
        document_units = [
            DocumentUnit(
                document_id="id1",
                merged_page_range=(1, 2),
                excel_row_data=df.iloc[0],
                source_info="file1.xlsx:file1.pdf",
            ),
            DocumentUnit(
                document_id="id2",
                merged_page_range=(3, 4),
                excel_row_data=df.iloc[1],
                source_info="file1.xlsx:file1.pdf",
            ),
            DocumentUnit(
                document_id="id3",
                merged_page_range=(5, 6),
                excel_row_data=df.iloc[2],
                source_info="file1.xlsx:file1.pdf",
            ),
        ]

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={"reorder_pages": reorder_pages, "sort_bookmarks": sort_bookmarks},
        )
        context.df = df
        context.document_units = document_units
        context.intermediate_pdf_path = "/tmp/test_intermediate.pdf"

        return context

    @patch("pathlib.Path")
    @patch("core.pipeline.steps.rebuild_pdf_step.PdfReader")
    @patch("core.pipeline.steps.rebuild_pdf_step.PdfWriter")
    def test_execute_full_workflow(
        self, mock_pdf_writer_class, mock_pdf_reader_class, mock_path_class
    ):
        """Test complete execute workflow."""
        context = self.create_test_context(include_flags=[True, False, True])

        # Mock Path.exists() to return True
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path_class.return_value = mock_path

        # Mock PDF reader and writer
        mock_reader = Mock()
        mock_reader.pages = [Mock() for _ in range(6)]  # 6 pages total
        mock_pdf_reader_class.return_value = mock_reader

        mock_writer = Mock()
        mock_pdf_writer_class.return_value = mock_writer

        # Execute the step
        self.step.execute(context)

        # Verify PDF reader was created
        mock_pdf_reader_class.assert_called_once_with(context.intermediate_pdf_path)

        # Verify PDF writer was created and stored in context
        mock_pdf_writer_class.assert_called_once()
        assert context.final_pdf == mock_writer

        # Verify pages were added (2 DocumentUnits with 2 pages each = 4 pages)
        assert mock_writer.add_page.call_count == 4

        # Verify bookmarks were added
        assert mock_writer.add_outline_item.call_count == 2

    def test_phase_a_filter_units_with_include_column(self):
        """Test Phase A filtering with _include column."""
        context = self.create_test_context(include_flags=[True, False, True])

        # Call Phase A directly
        filtered_units = self.step._phase_a_filter_units(context)

        # Should return only DocumentUnits for flagged rows
        assert len(filtered_units) == 2
        assert filtered_units[0].document_id == "id1"
        assert filtered_units[1].document_id == "id3"

    def test_phase_a_filter_units_without_include_column(self):
        """Test Phase A filtering without _include column."""
        context = self.create_test_context()  # No include_flags

        # Call Phase A directly
        filtered_units = self.step._phase_a_filter_units(context)

        # Should return all DocumentUnits
        assert len(filtered_units) == 3
        assert [u.document_id for u in filtered_units] == ["id1", "id2", "id3"]

    def test_phase_b_reorder_units_enabled(self):
        """Test Phase B reordering when enabled."""
        context = self.create_test_context(include_flags=[True, True, True])

        # Reorder DataFrame to test sorting
        context.df = context.df.sort_values("Document_ID", ascending=False).reset_index(
            drop=True
        )

        # Create filtered units (all units)
        filtered_units = list(context.document_units)

        # Call Phase B directly
        reordered_units = self.step._phase_b_reorder_units(context, filtered_units)

        # Should be reordered by DataFrame order (id3, id2, id1)
        expected_order = ["id3", "id2", "id1"]
        actual_order = [u.document_id for u in reordered_units]
        assert actual_order == expected_order

    def test_phase_b_reorder_units_disabled(self):
        """Test Phase B reordering when disabled."""
        context = self.create_test_context(reorder_pages=False)
        filtered_units = list(context.document_units)

        # Call Phase B directly
        reordered_units = self.step._phase_b_reorder_units(context, filtered_units)

        # Should maintain original order
        expected_order = ["id1", "id2", "id3"]
        actual_order = [u.document_id for u in reordered_units]
        assert actual_order == expected_order

    @patch("core.pipeline.steps.rebuild_pdf_step.PdfReader")
    @patch("core.pipeline.steps.rebuild_pdf_step.PdfWriter")
    def test_phase_c_create_pdf_with_bookmarks(
        self, mock_pdf_writer_class, mock_pdf_reader_class
    ):
        """Test Phase C PDF creation with bookmarks."""
        context = self.create_test_context()

        # Mock PDF reader and writer
        mock_reader = Mock()
        mock_reader.pages = [Mock() for _ in range(6)]
        mock_pdf_reader_class.return_value = mock_reader

        mock_writer = Mock()
        mock_pdf_writer_class.return_value = mock_writer

        # Create test units for Phase C
        test_units = context.document_units[:2]  # Use first 2 units

        # Call Phase C directly
        self.step._phase_c_create_pdf_with_bookmarks(context, test_units, mock_reader)

        # Verify pages were added correctly
        expected_page_calls = 4  # 2 units * 2 pages each
        assert mock_writer.add_page.call_count == expected_page_calls

        # Verify bookmarks were added
        assert mock_writer.add_outline_item.call_count == 2

    @patch("natsort.natsorted")
    @patch("core.pipeline.steps.rebuild_pdf_step.PdfWriter")
    def test_add_bookmarks_to_writer_with_sorting(
        self, mock_pdf_writer_class, mock_natsorted
    ):
        """Test bookmark addition with natural sorting."""
        mock_writer = Mock()
        mock_pdf_writer_class.return_value = mock_writer

        # Mock natsorted to return sorted order
        mock_natsorted.return_value = [
            {"title": "1-Title A", "page_num": 0},
            {"title": "2-Title B", "page_num": 2},
        ]

        bookmark_info = [
            {"title": "2-Title B", "page_num": 2},
            {"title": "1-Title A", "page_num": 0},
        ]  # Unsorted

        # Call method directly
        self.step._add_bookmarks_to_writer(
            mock_writer, bookmark_info, sort_bookmarks=True
        )

        # Verify natsorted was called
        mock_natsorted.assert_called_once()

        # Verify bookmarks were added in sorted order
        assert mock_writer.add_outline_item.call_count == 2

    @patch("core.pipeline.steps.rebuild_pdf_step.PdfWriter")
    def test_add_bookmarks_to_writer_without_sorting(self, mock_pdf_writer_class):
        """Test bookmark addition without sorting."""
        mock_writer = Mock()
        mock_pdf_writer_class.return_value = mock_writer

        bookmark_info = [
            {"title": "Title B", "page_num": 2},
            {"title": "Title A", "page_num": 0},
        ]  # Original order

        # Call method directly
        self.step._add_bookmarks_to_writer(
            mock_writer, bookmark_info, sort_bookmarks=False
        )

        # Verify bookmarks were added in original order
        expected_calls = [("Title B", 2), ("Title A", 0)]
        actual_calls = [
            call.args for call in mock_writer.add_outline_item.call_args_list
        ]
        assert actual_calls == expected_calls

    @patch("core.pipeline.steps.rebuild_pdf_step.Path")
    def test_cleanup_intermediate_pdf(self, mock_path_class):
        """Test intermediate PDF cleanup."""
        context = self.create_test_context()
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path_class.return_value = mock_path

        # Call cleanup method directly
        self.step._cleanup_intermediate_pdf(context)

        # Verify Path was created and unlink was called
        mock_path_class.assert_called_once_with("/tmp/test_intermediate.pdf")
        mock_path.unlink.assert_called_once()

    def test_execute_with_no_document_units(self):
        """Test execute with no DocumentUnits raises error."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = pd.DataFrame()
        context.document_units = []

        # Execute should raise ValueError
        with pytest.raises(ValueError, match="DocumentUnits list is empty"):
            self.step.execute(context)

    def test_execute_with_no_dataframe(self):
        """Test execute with no DataFrame raises error."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )
        context.df = None
        context.document_units = [Mock()]

        # Execute should raise ValueError
        with pytest.raises(ValueError, match="No DataFrame available"):
            self.step.execute(context)

    def test_execute_with_missing_intermediate_pdf(self):
        """Test execute with missing intermediate PDF path raises error."""
        context = self.create_test_context()
        context.intermediate_pdf_path = None

        # Execute should raise ValueError
        with pytest.raises(ValueError, match="No intermediate PDF path"):
            self.step.execute(context)

    @patch("pathlib.Path")
    @patch("core.pipeline.steps.rebuild_pdf_step.PdfReader")
    def test_execute_handles_pdf_reader_failure(
        self, mock_pdf_reader_class, mock_path_class
    ):
        """Test execute handles PDF reader failure gracefully."""
        context = self.create_test_context()

        # Mock Path.exists() to return True
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path_class.return_value = mock_path

        # Mock PDF reader to raise exception
        mock_pdf_reader_class.side_effect = Exception("Failed to read PDF")

        # Execute should raise exception with descriptive message
        with pytest.raises(Exception, match="Failed to read PDF"):
            self.step.execute(context)

    @patch("pathlib.Path")
    @patch("core.pipeline.steps.rebuild_pdf_step.Path")
    @patch("core.pipeline.steps.rebuild_pdf_step.PdfReader")
    @patch("core.pipeline.steps.rebuild_pdf_step.PdfWriter")
    def test_execute_cleanup_on_failure(
        self,
        mock_pdf_writer_class,
        mock_pdf_reader_class,
        mock_path_class,
        mock_pathlib_path,
    ):
        """Test execute cleans up intermediate PDF even on failure."""
        context = self.create_test_context()

        # Mock pathlib.Path for the existence check in execute()
        mock_pathlib_instance = Mock()
        mock_pathlib_instance.exists.return_value = True
        mock_pathlib_path.return_value = mock_pathlib_instance

        # Mock Path.exists() to return True and setup cleanup mock
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path_class.return_value = mock_path

        # Mock PDF reader
        mock_reader = Mock()
        mock_reader.pages = [Mock() for _ in range(6)]
        mock_pdf_reader_class.return_value = mock_reader

        # Mock PDF writer to raise exception during processing
        mock_writer = Mock()
        mock_writer.add_page.side_effect = Exception("Writer failed")
        mock_pdf_writer_class.return_value = mock_writer

        # Execute should raise exception
        with pytest.raises(Exception):
            self.step.execute(context)

        # Verify cleanup was still called
        mock_path.unlink.assert_called_once()
