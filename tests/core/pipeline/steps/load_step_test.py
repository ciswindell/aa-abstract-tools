#!/usr/bin/env python3
"""
Unit tests for the refactored LoadStep implementing Phase 1 DocumentUnit architecture.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from core.models import DocumentUnit
from core.pipeline.context import PipelineContext
from core.pipeline.steps.load_step import LoadStep


class TestLoadStep:
    """Test cases for LoadStep Phase 1 implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock repositories and logger
        self.excel_repo = Mock()
        self.pdf_repo = Mock()

        self.logger = Mock()
        self.ui = Mock()

        # Create LoadStep instance
        self.load_step = LoadStep(
            excel_repo=self.excel_repo,
            pdf_repo=self.pdf_repo,
            logger=self.logger,
            ui=self.ui,
        )

    def test_single_file_workflow_success(self):
        """Test successful single file processing."""
        # Setup mock data
        excel_df = pd.DataFrame(
            {
                "Index#": ["1", "2"],
                "Document Type": ["Type1", "Type2"],
                "Received Date": ["2024-01-01", "2024-01-02"],
            }
        )

        bookmarks = [
            {"title": "1-Doc1", "page": 1, "level": 0},
            {"title": "2-Doc2", "page": 5, "level": 0},
        ]

        # Configure mocks
        self.excel_repo.load.return_value = excel_df
        self.pdf_repo.read.return_value = (bookmarks, 10)

        # Create context for single file workflow
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={
                "backup": False,
                "sort_bookmarks": False,
                "reorder_pages": False,
            },
        )

        # Mock the entire _process_file_pair method to avoid PDF complexity
        mock_document_units = [
            DocumentUnit(
                document_id="id1",
                merged_page_range=(1, 4),
                excel_row_data=excel_df.iloc[0],
                source_info="test.xlsx:test.pdf",
            ),
            DocumentUnit(
                document_id="id2",
                merged_page_range=(5, 10),
                excel_row_data=excel_df.iloc[1],
                source_info="test.xlsx:test.pdf",
            ),
        ]

        with (
            patch.object(self.load_step, "_process_file_pair") as mock_process,
            patch.object(self.load_step, "_create_intermediate_pdf") as mock_create_pdf,
            patch.object(self.load_step, "_merge_dataframes") as mock_merge_df,
        ):
            # Setup method mocks
            mock_process.return_value = (mock_document_units, excel_df.copy(), 10)
            mock_create_pdf.return_value = "/tmp/test.pdf"
            mock_merge_df.return_value = excel_df.copy()

            # Execute
            self.load_step.execute(context)

        # Verify results
        assert context.document_units is not None
        assert len(context.document_units) == 2
        assert context.df is not None
        assert len(context.df) == 2
        assert context.intermediate_pdf_path == "/tmp/test.pdf"
        assert context.total_pages == 10

    def test_merge_workflow_success(self):
        """Test successful merge workflow with multiple file pairs."""
        # Setup mock data for multiple files
        excel_df1 = pd.DataFrame(
            {"Index#": ["1", "2"], "Document Type": ["Type1", "Type2"]}
        )
        excel_df2 = pd.DataFrame(
            {"Index#": ["1", "2"], "Document Type": ["Type3", "Type4"]}
        )

        bookmarks1 = [{"title": "1-Doc1", "page": 1, "level": 0}]
        bookmarks2 = [{"title": "1-Doc3", "page": 1, "level": 0}]

        # Configure mocks for multiple calls
        self.excel_repo.load.side_effect = [excel_df1, excel_df2]
        self.pdf_repo.read.side_effect = [(bookmarks1, 5), (bookmarks2, 3)]

        # Create context for merge workflow
        context = PipelineContext(
            file_pairs=[
                ("file1.xlsx", "file1.pdf", "Sheet1"),
                ("file2.xlsx", "file2.pdf", "Sheet1"),
            ],
            options={
                "backup": False,
                "sort_bookmarks": False,
                "reorder_pages": False,
            },
        )

        # Mock dependencies
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("core.transform.excel.add_document_ids") as mock_add_ids,
            patch(
                "core.pipeline.steps.load_step.link_bookmarks_to_excel_rows"
            ) as mock_link,
            patch("pypdf.PdfReader") as mock_reader,
            patch("tempfile.mkstemp") as mock_mkstemp,
        ):
            # Setup mock returns
            mock_add_ids.side_effect = [excel_df1.copy(), excel_df2.copy()]

            # Create a mock function that respects the page_offset parameter
            def mock_link_function(
                bookmarks, excel_df, page_offset, source_info, total_pages
            ):
                if "file1" in source_info:
                    return [
                        DocumentUnit(
                            "id1",
                            (page_offset + 1, page_offset + 5),
                            excel_df.iloc[0],
                            source_info,
                        )
                    ]
                else:
                    return [
                        DocumentUnit(
                            "id2",
                            (page_offset + 1, page_offset + 3),
                            excel_df.iloc[0],
                            source_info,
                        )
                    ]

            mock_link.side_effect = mock_link_function

            # Create real PDF pages in memory for proper mocking
            from io import BytesIO

            from pypdf import PdfWriter as RealPdfWriter

            # Create mock PDF readers with real pages
            def create_mock_reader_with_real_pages(num_pages):
                # Create a real PDF in memory
                temp_writer = RealPdfWriter()
                for _ in range(num_pages):
                    temp_writer.add_blank_page(width=72, height=72)

                pdf_bytes = BytesIO()
                temp_writer.write(pdf_bytes)
                pdf_bytes.seek(0)

                # Create a real reader from the in-memory PDF
                from pypdf import PdfReader as RealPdfReader

                return RealPdfReader(pdf_bytes)

            mock_reader_instance1 = create_mock_reader_with_real_pages(5)
            mock_reader_instance2 = create_mock_reader_with_real_pages(3)

            mock_reader.side_effect = [mock_reader_instance1, mock_reader_instance2]

            mock_mkstemp.return_value = (1, "/tmp/merged.pdf")

            # Mock file operations with proper file-like objects
            mock_file = BytesIO()

            with patch("builtins.open", return_value=mock_file):
                # Execute
                self.load_step.execute(context)

        # Verify results - core functionality works
        assert context.document_units is not None
        assert len(context.document_units) == 2
        assert context.df is not None
        assert len(context.df) == 4  # Combined DataFrames
        assert context.intermediate_pdf_path == "/tmp/merged.pdf"

        # Verify DocumentUnits were created (page offsets are handled by the real implementation)
        assert context.document_units[0].document_id == "id1"
        assert context.document_units[1].document_id == "id2"
        assert "file1" in context.document_units[0].source_info
        assert "file2" in context.document_units[1].source_info

    def test_file_not_found_error(self):
        """Test handling of missing files."""
        context = PipelineContext(
            file_pairs=[("missing.xlsx", "missing.pdf", "Sheet1")],
            options={
                "backup": False,
                "sort_bookmarks": False,
                "reorder_pages": False,
            },
        )

        # Mock file not existing
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(Exception) as exc_info:
                self.load_step.execute(context)

            assert "FileNotFoundError" in str(exc_info.value) or "not found" in str(
                exc_info.value
            )

    def test_empty_excel_file_handling(self):
        """Test handling of empty Excel files."""
        # Setup empty DataFrame
        empty_df = pd.DataFrame()

        self.excel_repo.load.return_value = empty_df
        self.pdf_repo.read.return_value = ([], 1)

        context = PipelineContext(
            file_pairs=[("empty.xlsx", "test.pdf", "Sheet1")],
            options={
                "backup": False,
                "sort_bookmarks": False,
                "reorder_pages": False,
            },
        )

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("core.transform.excel.add_document_ids") as mock_add_ids,
            patch(
                "core.transform.document_unit.link_bookmarks_to_excel_rows"
            ) as mock_link,
            patch("pypdf.PdfReader") as mock_reader,
            patch("tempfile.mkstemp") as mock_mkstemp,
        ):
            mock_add_ids.return_value = empty_df
            mock_link.return_value = []

            from pypdf import PageObject

            mock_page = Mock(spec=PageObject)
            mock_page.__getitem__ = Mock(return_value="/Page")  # Mock PA.TYPE
            mock_page.pdf = None  # Required by pypdf
            mock_reader_instance = Mock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance

            mock_mkstemp.return_value = (1, "/tmp/test.pdf")

            # Empty DataFrame should raise an error because it lacks required columns
            with pytest.raises(Exception) as exc_info:
                self.load_step.execute(context)

            # Should fail because empty DataFrame doesn't have Index# column
            assert "Index column" in str(exc_info.value) or "Index#" in str(
                exc_info.value
            )

    def test_pdf_with_no_pages_error(self):
        """Test handling of PDF with no pages."""
        excel_df = pd.DataFrame({"Index#": ["1"]})

        self.excel_repo.load.return_value = excel_df
        self.pdf_repo.read.return_value = ([], 0)  # No pages

        context = PipelineContext(
            file_pairs=[("test.xlsx", "empty.pdf", "Sheet1")],
            options={
                "backup": False,
                "sort_bookmarks": False,
                "reorder_pages": False,
            },
        )

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("core.transform.excel.add_document_ids") as mock_add_ids,
        ):
            mock_add_ids.return_value = excel_df

            with pytest.raises(Exception) as exc_info:
                self.load_step.execute(context)

            assert "no pages" in str(exc_info.value).lower()

    def test_no_file_pairs_error(self):
        """Test handling when no file pairs are found."""
        context = PipelineContext(
            file_pairs=[],  # Empty file pairs
            options={
                "backup": False,
                "sort_bookmarks": False,
                "reorder_pages": False,
            },
        )

        # Should raise ValueError for empty file pairs
        with pytest.raises(ValueError) as exc_info:
            self.load_step.execute(context)

        assert "No file pairs found" in str(exc_info.value)

    def test_intermediate_pdf_creation_failure(self):
        """Test handling of intermediate PDF creation failure."""
        excel_df = pd.DataFrame({"Index#": ["1"]})
        bookmarks = [{"title": "1-Doc", "page": 1, "level": 0}]

        self.excel_repo.load.return_value = excel_df
        self.pdf_repo.read.return_value = (bookmarks, 1)

        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={
                "backup": False,
                "sort_bookmarks": False,
                "reorder_pages": False,
            },
        )

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("core.transform.excel.add_document_ids") as mock_add_ids,
            patch(
                "core.transform.document_unit.link_bookmarks_to_excel_rows"
            ) as mock_link,
            patch("pypdf.PdfReader") as mock_reader,
            patch("tempfile.mkstemp") as mock_mkstemp,
        ):
            mock_add_ids.return_value = excel_df
            mock_link.return_value = [
                DocumentUnit("id1", (1, 1), excel_df.iloc[0], "test.xlsx:test.pdf")
            ]

            from pypdf import PageObject

            mock_page = Mock(spec=PageObject)
            mock_page.__getitem__ = Mock(return_value="/Page")  # Mock PA.TYPE
            mock_page.pdf = None  # Required by pypdf
            mock_reader_instance = Mock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance

            mock_mkstemp.return_value = (1, "/tmp/test.pdf")

            # Mock file write failure
            with patch("builtins.open", side_effect=OSError("Write failed")):
                with pytest.raises(Exception) as exc_info:
                    self.load_step.execute(context)

                # The error should be about adding pages to merged PDF
                assert "add pages" in str(exc_info.value) or "merged PDF" in str(
                    exc_info.value
                )

    def test_cleanup_on_failure(self):
        """Test that intermediate files are cleaned up on failure."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")],
            options={
                "backup": False,
                "sort_bookmarks": False,
                "reorder_pages": False,
            },
        )

        # Set intermediate path to test cleanup
        context.intermediate_pdf_path = "/tmp/test_cleanup.pdf"

        with (
            patch("pathlib.Path.exists", return_value=False),
            patch("pathlib.Path.unlink") as mock_unlink,
        ):
            with pytest.raises(Exception):
                self.load_step.execute(context)

            # Verify cleanup was attempted
            mock_unlink.assert_called_once_with(missing_ok=True)

    def test_get_file_pairs_single_workflow(self):
        """Test file_pairs access for single file workflow."""
        context = PipelineContext(
            file_pairs=[("single.xlsx", "single.pdf", "Sheet1")],
            options={
                "backup": False,
                "sort_bookmarks": False,
                "reorder_pages": False,
            },
        )

        # File pairs are now directly accessible from context
        pairs = context.file_pairs

        assert len(pairs) == 1
        assert pairs[0] == ("single.xlsx", "single.pdf", "Sheet1")

    def test_get_file_pairs_merge_workflow(self):
        """Test file_pairs access for merge workflow."""
        context = PipelineContext(
            file_pairs=[
                ("file1.xlsx", "file1.pdf", "Sheet1"),
                ("file2.xlsx", "file2.pdf", "Sheet1"),
                ("file3.xlsx", "file3.pdf", "Sheet1"),
            ],
            options={
                "backup": False,
                "sort_bookmarks": False,
                "reorder_pages": False,
            },
        )

        # File pairs are now directly accessible from context
        pairs = context.file_pairs

        assert len(pairs) == 3
        assert pairs[0] == ("file1.xlsx", "file1.pdf", "Sheet1")
        assert pairs[1] == ("file2.xlsx", "file2.pdf", "Sheet1")
        assert pairs[2] == ("file3.xlsx", "file3.pdf", "Sheet1")

    def test_merge_dataframes_empty_input(self):
        """Test _merge_dataframes with empty input."""
        result = self.load_step._merge_dataframes([])
        assert result.empty

    def test_merge_dataframes_single_dataframe(self):
        """Test _merge_dataframes with single DataFrame."""
        df = pd.DataFrame({"col1": [1, 2]})
        result = self.load_step._merge_dataframes([df])
        pd.testing.assert_frame_equal(result, df)

    def test_merge_dataframes_multiple_dataframes(self):
        """Test _merge_dataframes with multiple DataFrames."""
        df1 = pd.DataFrame({"col1": [1, 2]})
        df2 = pd.DataFrame({"col1": [3, 4]})

        result = self.load_step._merge_dataframes([df1, df2])

        expected = pd.DataFrame({"col1": [1, 2, 3, 4]})
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)
