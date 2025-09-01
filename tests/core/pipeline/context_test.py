#!/usr/bin/env python3
"""
Unit tests for PipelineContext class.
"""

import pandas as pd
import pytest
from pypdf import PdfWriter

from core.models import DocumentUnit
from core.pipeline.context import PipelineContext


class TestPipelineContext:
    """Test cases for PipelineContext class."""

    def test_init_basic(self):
        """Test basic initialization of PipelineContext."""
        file_pairs = [("test.xlsx", "test.pdf", "Sheet1")]
        options = {"backup": True, "sort_bookmarks": False}

        context = PipelineContext(file_pairs=file_pairs, options=options)

        assert context.file_pairs == file_pairs
        assert context.options == options
        assert context.document_units is None
        assert context.df is None
        assert context.intermediate_pdf_path is None
        assert context.total_pages is None
        assert context.final_pdf is None
        assert context.processed_document_units is None
        assert context.excel_out_path is None
        assert context.pdf_out_path is None

    def test_init_with_data(self):
        """Test initialization with optional data fields."""
        file_pairs = [("test.xlsx", "test.pdf", "Sheet1")]
        options = {"backup": False}

        # Create test data
        test_df = pd.DataFrame({"Index#": [1, 2], "Type": ["A", "B"]})
        test_units = [
            DocumentUnit("id1", (1, 5), test_df.iloc[0], "test.xlsx:test.pdf")
        ]

        context = PipelineContext(
            file_pairs=file_pairs,
            options=options,
            document_units=test_units,
            df=test_df,
            intermediate_pdf_path="/tmp/test.pdf",
            total_pages=10,
        )

        assert context.document_units == test_units
        assert context.df.equals(test_df)
        assert context.intermediate_pdf_path == "/tmp/test.pdf"
        assert context.total_pages == 10

    def test_is_merge_workflow_single_file(self):
        """Test is_merge_workflow with single file."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )

        assert not context.is_merge_workflow()

    def test_is_merge_workflow_multiple_files(self):
        """Test is_merge_workflow with multiple files."""
        context = PipelineContext(
            file_pairs=[
                ("file1.xlsx", "file1.pdf", "Sheet1"),
                ("file2.xlsx", "file2.pdf", "Sheet1"),
            ],
            options={},
        )

        assert context.is_merge_workflow()

    def test_excel_path_property(self):
        """Test excel_path property returns first file pair's Excel path."""
        context = PipelineContext(
            file_pairs=[
                ("first.xlsx", "first.pdf", "Sheet1"),
                ("second.xlsx", "second.pdf", "Sheet1"),
            ],
            options={},
        )

        assert context.excel_path == "first.xlsx"

    def test_pdf_path_property(self):
        """Test pdf_path property returns first file pair's PDF path."""
        context = PipelineContext(
            file_pairs=[
                ("first.xlsx", "first.pdf", "Sheet1"),
                ("second.xlsx", "second.pdf", "Sheet1"),
            ],
            options={},
        )

        assert context.pdf_path == "first.pdf"

    def test_excel_path_empty_file_pairs(self):
        """Test excel_path raises error when no file pairs."""
        context = PipelineContext(file_pairs=[], options={})

        with pytest.raises(ValueError, match="No file pairs available"):
            _ = context.excel_path

    def test_pdf_path_empty_file_pairs(self):
        """Test pdf_path raises error when no file pairs."""
        context = PipelineContext(file_pairs=[], options={})

        with pytest.raises(ValueError, match="No file pairs available"):
            _ = context.pdf_path

    def test_get_output_paths_single_file(self):
        """Test get_output_paths for single file workflow."""
        context = PipelineContext(
            file_pairs=[("/path/to/test.xlsx", "/path/to/test.pdf", "Sheet1")],
            options={},
        )

        excel_out, pdf_out = context.get_output_paths()

        # Single file workflow should output to original paths
        assert excel_out == "/path/to/test.xlsx"
        assert pdf_out == "/path/to/test.pdf"
        assert context.excel_out_path == "/path/to/test.xlsx"
        assert context.pdf_out_path == "/path/to/test.pdf"

    def test_get_output_paths_merge_workflow(self):
        """Test get_output_paths for merge workflow."""
        context = PipelineContext(
            file_pairs=[
                ("/path/to/file1.xlsx", "/path/to/file1.pdf", "Sheet1"),
                ("/path/to/file2.xlsx", "/path/to/file2.pdf", "Sheet1"),
            ],
            options={},
        )

        excel_out, pdf_out = context.get_output_paths()

        # Merge workflow should use "_merged" suffix
        assert excel_out == "/path/to/file1_merged.xlsx"
        assert pdf_out == "/path/to/file1_merged.pdf"
        assert context.excel_out_path == "/path/to/file1_merged.xlsx"
        assert context.pdf_out_path == "/path/to/file1_merged.pdf"

    def test_get_output_paths_cached(self):
        """Test get_output_paths returns cached values on subsequent calls."""
        context = PipelineContext(
            file_pairs=[("/path/to/test.xlsx", "/path/to/test.pdf", "Sheet1")],
            options={},
        )

        # Set custom output paths
        context.excel_out_path = "/custom/excel.xlsx"
        context.pdf_out_path = "/custom/pdf.pdf"

        excel_out, pdf_out = context.get_output_paths()

        # Should return cached values, not generate new ones
        assert excel_out == "/custom/excel.xlsx"
        assert pdf_out == "/custom/pdf.pdf"

    def test_get_output_paths_complex_filenames(self):
        """Test get_output_paths with complex filenames and extensions."""
        context = PipelineContext(
            file_pairs=[
                ("/path/to/my.file.name.xlsx", "/path/to/my.file.name.pdf", "Sheet1"),
                ("/path/to/other.xlsx", "/path/to/other.pdf", "Sheet1"),
            ],
            options={},
        )

        excel_out, pdf_out = context.get_output_paths()

        # Should handle complex filenames correctly
        assert excel_out == "/path/to/my.file.name_merged.xlsx"
        assert pdf_out == "/path/to/my.file.name_merged.pdf"

    def test_dataclass_immutability(self):
        """Test that PipelineContext behaves as expected for a dataclass."""
        context1 = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={"backup": True}
        )

        context2 = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={"backup": True}
        )

        # Should be equal with same data
        assert context1.file_pairs == context2.file_pairs
        assert context1.options == context2.options

        # Should be able to modify fields
        context1.total_pages = 10
        assert context1.total_pages == 10
        assert context2.total_pages is None

    def test_with_pypdf_writer(self):
        """Test PipelineContext with PdfWriter object."""
        context = PipelineContext(
            file_pairs=[("test.xlsx", "test.pdf", "Sheet1")], options={}
        )

        # Should be able to store PdfWriter
        writer = PdfWriter()
        context.final_pdf = writer

        assert context.final_pdf is writer
        assert isinstance(context.final_pdf, PdfWriter)
