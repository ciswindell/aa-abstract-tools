#!/usr/bin/env python3
"""
Unit tests for Pipeline class.
"""

from unittest.mock import Mock, patch

from core.models import Options
from core.pipeline.context import PipelineContext
from core.pipeline.pipeline import Pipeline
from core.pipeline.steps import BaseStep


class MockStep(BaseStep):
    """Mock pipeline step for testing."""

    def __init__(self, name="MockStep", should_execute_result=True, execute_error=None):
        # Initialize with mock dependencies
        super().__init__(Mock(), Mock(), Mock(), Mock())
        self.name = name
        self.should_execute_result = should_execute_result
        self.execute_error = execute_error
        self.execute_called = False
        self.should_execute_called = False

    def should_execute(self, context: PipelineContext) -> bool:
        self.should_execute_called = True
        return self.should_execute_result

    def execute(self, context: PipelineContext) -> None:
        self.execute_called = True
        if self.execute_error:
            raise self.execute_error


class TestPipeline:
    """Test cases for Pipeline class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.excel_repo = Mock()
        self.pdf_repo = Mock()

        self.logger = Mock()
        self.ui = Mock()

        self.pipeline = Pipeline(
            excel_repo=self.excel_repo,
            pdf_repo=self.pdf_repo,
            logger=self.logger,
            ui=self.ui,
        )

    def test_init(self):
        """Test Pipeline initialization."""
        assert self.pipeline.excel_repo is self.excel_repo
        assert self.pipeline.pdf_repo is self.pdf_repo
        assert self.pipeline.logger is self.logger
        assert self.pipeline.ui is self.ui
        assert self.pipeline.steps == []

    def test_add_step(self):
        """Test adding steps to pipeline."""
        step1 = MockStep("Step1")
        step2 = MockStep("Step2")

        self.pipeline.add_step(step1)
        assert len(self.pipeline.steps) == 1
        assert self.pipeline.steps[0] is step1

        self.pipeline.add_step(step2)
        assert len(self.pipeline.steps) == 2
        assert self.pipeline.steps[1] is step2

    @patch("core.pipeline.steps.validate_step.ValidateStep")
    @patch("core.pipeline.steps.load_step.LoadStep")
    @patch("core.pipeline.steps.filter_df_step.FilterDfStep")
    @patch("core.pipeline.steps.sort_df_step.SortDfStep")
    @patch("core.pipeline.steps.rebuild_pdf_step.RebuildPdfStep")
    @patch("core.pipeline.steps.save_step.SaveStep")
    @patch("core.pipeline.steps.format_excel_step.FormatExcelStep")
    def test_register_steps(
        self,
        mock_format,
        mock_save,
        mock_rebuild,
        mock_sort,
        mock_filter,
        mock_load,
        mock_validate,
    ):
        """Test step registration in correct order."""
        # Mock step constructors
        mock_validate_instance = Mock()
        mock_load_instance = Mock()
        mock_filter_instance = Mock()
        mock_sort_instance = Mock()
        mock_rebuild_instance = Mock()
        mock_save_instance = Mock()
        mock_format_instance = Mock()

        mock_validate.return_value = mock_validate_instance
        mock_load.return_value = mock_load_instance
        mock_filter.return_value = mock_filter_instance
        mock_sort.return_value = mock_sort_instance
        mock_rebuild.return_value = mock_rebuild_instance
        mock_save.return_value = mock_save_instance
        mock_format.return_value = mock_format_instance

        self.pipeline.register_steps()

        # Verify all steps were created with correct dependencies
        mock_validate.assert_called_once_with(
            self.excel_repo, self.pdf_repo, self.logger, self.ui
        )
        mock_load.assert_called_once_with(
            self.excel_repo, self.pdf_repo, self.logger, self.ui
        )
        mock_filter.assert_called_once_with(
            self.excel_repo, self.pdf_repo, self.logger, self.ui
        )
        mock_sort.assert_called_once_with(
            self.excel_repo, self.pdf_repo, self.logger, self.ui
        )
        mock_rebuild.assert_called_once_with(
            self.excel_repo, self.pdf_repo, self.logger, self.ui
        )
        mock_save.assert_called_once_with(
            self.excel_repo, self.pdf_repo, self.logger, self.ui
        )
        mock_format.assert_called_once_with(
            self.excel_repo, self.pdf_repo, self.logger, self.ui
        )

        # Verify steps were added in correct order
        assert len(self.pipeline.steps) == 7
        assert self.pipeline.steps[0] is mock_validate_instance
        assert self.pipeline.steps[1] is mock_load_instance
        assert self.pipeline.steps[2] is mock_filter_instance
        assert self.pipeline.steps[3] is mock_sort_instance
        assert self.pipeline.steps[4] is mock_rebuild_instance
        assert self.pipeline.steps[5] is mock_save_instance
        assert self.pipeline.steps[6] is mock_format_instance

    def test_execute_single_file_success(self):
        """Test successful execution with single file."""
        # Add mock steps
        step1 = MockStep("Step1")
        step2 = MockStep("Step2")
        self.pipeline.add_step(step1)
        self.pipeline.add_step(step2)

        options = Options(
            backup=True, sort_bookmarks=False, reorder_pages=False, sheet_name="Sheet1"
        )

        result = self.pipeline.execute("test.xlsx", "test.pdf", options)

        assert result.success is True
        assert result.message == "OK"
        assert step1.execute_called is True
        assert step2.execute_called is True
        # Pipeline-level info logs were removed in spec 003-reduce-info-logging.

    def test_execute_merge_workflow_with_pairs(self):
        """Test execution with merge pairs."""
        step = MockStep("Step1")
        self.pipeline.add_step(step)

        options = Options(
            backup=False,
            sort_bookmarks=True,
            reorder_pages=True,
            sheet_name="Sheet1",
            merge_pairs=[("file2.xlsx", "file2.pdf")],
        )

        result = self.pipeline.execute("file1.xlsx", "file1.pdf", options)

        assert result.success is True
        assert step.execute_called is True

    def test_execute_merge_workflow_with_sheets(self):
        """Test execution with merge pairs that include sheet names."""
        step = MockStep("Step1")
        self.pipeline.add_step(step)

        options = Options(
            backup=False,
            sort_bookmarks=False,
            reorder_pages=False,
            sheet_name="Sheet1",
            merge_pairs_with_sheets=[
                ("file1.xlsx", "file1.pdf", "Sheet1"),
                ("file2.xlsx", "file2.pdf", "Data"),
            ],
        )

        result = self.pipeline.execute("ignored.xlsx", "ignored.pdf", options)

        assert result.success is True
        assert step.execute_called is True

    def test_execute_step_conditional_execution(self):
        """Test conditional step execution based on should_execute."""
        step1 = MockStep("Step1", should_execute_result=True)
        step2 = MockStep("Step2", should_execute_result=False)  # Should be skipped
        step3 = MockStep("Step3", should_execute_result=True)

        self.pipeline.add_step(step1)
        self.pipeline.add_step(step2)
        self.pipeline.add_step(step3)

        options = Options(
            backup=False, sort_bookmarks=False, reorder_pages=False, sheet_name="Sheet1"
        )

        result = self.pipeline.execute("test.xlsx", "test.pdf", options)

        assert result.success is True
        assert step1.execute_called is True
        assert step2.execute_called is False  # Should be skipped
        assert step3.execute_called is True
        # "Skipping step" info log was removed in spec 003-reduce-info-logging.

    def test_execute_step_failure(self):
        """Test pipeline failure when step raises exception."""
        step1 = MockStep("Step1")
        step2 = MockStep("Step2", execute_error=ValueError("Test error"))
        step3 = MockStep("Step3")  # Should not be executed

        self.pipeline.add_step(step1)
        self.pipeline.add_step(step2)
        self.pipeline.add_step(step3)

        options = Options(
            backup=False, sort_bookmarks=False, reorder_pages=False, sheet_name="Sheet1"
        )

        result = self.pipeline.execute("test.xlsx", "test.pdf", options)

        assert result.success is False
        assert "Test error" in result.message
        assert step1.execute_called is True
        assert step2.execute_called is True
        assert step3.execute_called is False  # Should not be executed after failure

        # Verify error logging
        self.logger.error.assert_called_once()
        error_call = self.logger.error.call_args[0][0]
        assert "Pipeline failed at step MockStep" in error_call
        assert "Test error" in error_call

    def test_execute_auto_register_steps(self):
        """Test that steps are auto-registered if not already done."""
        options = Options(
            backup=False, sort_bookmarks=False, reorder_pages=False, sheet_name="Sheet1"
        )

        # Mock the register_steps method
        with patch.object(self.pipeline, "register_steps") as mock_register:
            # Add a mock step to avoid empty pipeline
            mock_step = MockStep("MockStep")
            self.pipeline.steps = [mock_step]

            result = self.pipeline.execute("test.xlsx", "test.pdf", options)

            # register_steps should not be called if steps already exist
            mock_register.assert_not_called()
            assert result.success is True

        # Test with empty pipeline
        self.pipeline.steps = []
        with patch.object(self.pipeline, "register_steps") as mock_register:
            mock_register.side_effect = lambda: self.pipeline.add_step(
                MockStep("AutoStep")
            )

            result = self.pipeline.execute("test.xlsx", "test.pdf", options)

            # register_steps should be called for empty pipeline
            mock_register.assert_called_once()
            assert result.success is True

    def test_execute_initialization_failure(self):
        """Test pipeline failure during initialization."""
        options = Options(
            backup=False, sort_bookmarks=False, reorder_pages=False, sheet_name="Sheet1"
        )

        # Mock register_steps to raise an exception
        with patch.object(
            self.pipeline, "register_steps", side_effect=RuntimeError("Init error")
        ):
            result = self.pipeline.execute("test.xlsx", "test.pdf", options)

            assert result.success is False
            assert "Pipeline initialization failed" in result.message
            assert "Init error" in result.message

            # Verify error logging
            self.logger.error.assert_called_once()

    def test_options_conversion_to_dict(self):
        """Test that Options object is correctly converted to dictionary."""
        step = MockStep("Step1")
        self.pipeline.add_step(step)

        options = Options(
            backup=True,
            sort_bookmarks=False,
            reorder_pages=True,
            sheet_name="CustomSheet",
            filter_enabled=True,
            filter_column="Type",
            filter_values=["A", "B"],
        )

        # Capture the context passed to the step
        original_execute = step.execute
        captured_context = None

        def capture_context(context):
            nonlocal captured_context
            captured_context = context
            return original_execute(context)

        step.execute = capture_context

        result = self.pipeline.execute("test.xlsx", "test.pdf", options)

        assert result.success is True
        assert captured_context is not None

        # Verify options dictionary conversion
        expected_options = {
            "backup": True,
            "sort_bookmarks": False,
            "reorder_pages": True,
            "check_document_images": False,
            "sheet_name": "CustomSheet",
            "filter_enabled": True,
            "filter_column": "Type",
            "filter_values": ["A", "B"],
        }
        assert captured_context.options == expected_options

    def test_file_pairs_creation_single_file(self):
        """Test file pairs creation for single file workflow."""
        step = MockStep("Step1")
        self.pipeline.add_step(step)

        options = Options(
            backup=False,
            sort_bookmarks=False,
            reorder_pages=False,
            sheet_name="TestSheet",
        )

        # Capture the context
        captured_context = None
        original_execute = step.execute

        def capture_context(context):
            nonlocal captured_context
            captured_context = context
            return original_execute(context)

        step.execute = capture_context

        result = self.pipeline.execute("single.xlsx", "single.pdf", options)

        assert result.success is True
        assert captured_context.file_pairs == [
            ("single.xlsx", "single.pdf", "TestSheet")
        ]

    def test_file_pairs_creation_merge_workflow(self):
        """Test file pairs creation for merge workflow."""
        step = MockStep("Step1")
        self.pipeline.add_step(step)

        options = Options(
            backup=False,
            sort_bookmarks=False,
            reorder_pages=False,
            sheet_name="Sheet1",
            merge_pairs=[("file2.xlsx", "file2.pdf"), ("file3.xlsx", "file3.pdf")],
        )

        # Capture the context
        captured_context = None
        original_execute = step.execute

        def capture_context(context):
            nonlocal captured_context
            captured_context = context
            return original_execute(context)

        step.execute = capture_context

        result = self.pipeline.execute("file1.xlsx", "file1.pdf", options)

        assert result.success is True
        expected_pairs = [
            ("file1.xlsx", "file1.pdf", "Sheet1"),
            ("file2.xlsx", "file2.pdf", "Sheet1"),
            ("file3.xlsx", "file3.pdf", "Sheet1"),
        ]
        assert captured_context.file_pairs == expected_pairs

    def test_step_without_should_execute_method(self):
        """Test handling of steps that don't have should_execute method."""

        # Create a step without should_execute method
        class SimpleStep(BaseStep):
            def __init__(self):
                super().__init__(Mock(), Mock(), Mock(), Mock())
                self.execute_called = False

            def execute(self, context):
                self.execute_called = True

        step = SimpleStep()
        self.pipeline.add_step(step)

        options = Options(
            backup=False, sort_bookmarks=False, reorder_pages=False, sheet_name="Sheet1"
        )

        result = self.pipeline.execute("test.xlsx", "test.pdf", options)

        # Step should be executed even without should_execute method
        assert result.success is True
        assert step.execute_called is True
