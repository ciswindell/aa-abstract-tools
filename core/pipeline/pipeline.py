#!/usr/bin/env python3
"""
DocumentUnit architecture pipeline orchestrator with immutable data flow.

This orchestrator implements the DocumentUnit architecture's two-phase processing
approach that prevents data corruption by maintaining immutable Excel row ↔ PDF
page range relationships throughout the pipeline execution.
"""

from typing import List

from core.interfaces import ExcelRepo, Logger, PdfRepo, UIController
from core.models import Options, Result
from core.pipeline.context import PipelineContext
from core.pipeline.steps import PipelineStep


class Pipeline:
    """DocumentUnit architecture pipeline orchestrator with immutable data flow.

    Orchestrates the two-phase DocumentUnit processing pipeline that maintains atomic
    Excel row ↔ PDF page range relationships and prevents the data corruption issues
    of the previous fragile separate bookmarks/pages list architecture.
    """

    def __init__(
        self,
        excel_repo: ExcelRepo,
        pdf_repo: PdfRepo,
        logger: Logger,
        ui: UIController,
    ) -> None:
        """Initialize pipeline with dependencies."""
        self.excel_repo = excel_repo
        self.pdf_repo = pdf_repo
        self.logger = logger
        self.ui = ui
        self.steps: List[PipelineStep] = []

    def add_step(self, step: PipelineStep) -> None:
        """Add a step to the pipeline."""
        self.steps.append(step)

    def register_steps(self) -> None:
        """Register all pipeline steps in the correct order.

        This method defines the hardcoded pipeline step order as specified in the PRD.
        Steps are conditionally executed based on options within each step's should_execute() method.
        """

        from core.pipeline.steps.filter_df_step import FilterDfStep
        from core.pipeline.steps.format_excel_step import FormatExcelStep
        from core.pipeline.steps.load_step import LoadStep
        from core.pipeline.steps.rebuild_pdf_step import RebuildPdfStep
        from core.pipeline.steps.save_step import SaveStep
        from core.pipeline.steps.sort_df_step import SortDfStep
        from core.pipeline.steps.validate_step import ValidateStep

        # Register steps in simplified DocumentUnit architecture order
        self.add_step(
            ValidateStep(self.excel_repo, self.pdf_repo, self.logger, self.ui)
        )
        self.add_step(LoadStep(self.excel_repo, self.pdf_repo, self.logger, self.ui))
        self.add_step(
            FilterDfStep(self.excel_repo, self.pdf_repo, self.logger, self.ui)
        )
        self.add_step(SortDfStep(self.excel_repo, self.pdf_repo, self.logger, self.ui))
        self.add_step(
            RebuildPdfStep(self.excel_repo, self.pdf_repo, self.logger, self.ui)
        )
        self.add_step(SaveStep(self.excel_repo, self.pdf_repo, self.logger, self.ui))
        self.add_step(
            FormatExcelStep(self.excel_repo, self.pdf_repo, self.logger, self.ui)
        )

    def execute(self, excel_path: str, pdf_path: str, options: Options) -> Result:
        """Execute the pipeline with fail-fast error handling.

        Args:
            excel_path: Path to Excel file
            pdf_path: Path to PDF file
            options: Processing options

        Returns:
            Result indicating success or failure
        """
        try:
            # Register pipeline steps if not already done
            if not self.steps:
                self.register_steps()

            # Convert Options to dictionary and create file pairs
            options_dict = {
                "backup": options.backup,
                "sort_bookmarks": options.sort_bookmarks,
                "reorder_pages": options.reorder_pages,
                "sheet_name": options.sheet_name,
                "filter_enabled": options.filter_enabled,
                "filter_column": options.filter_column,
                "filter_values": options.filter_values,
            }

            # Create file pairs list
            if options.merge_pairs_with_sheets:
                # Use the pre-built pairs with sheets (already includes primary pair)
                file_pairs = list(options.merge_pairs_with_sheets)
            elif options.merge_pairs:
                # Legacy merge pairs - add primary pair first, then merge pairs
                file_pairs = [(excel_path, pdf_path, options.sheet_name or "Sheet1")]
                for excel, pdf in options.merge_pairs:
                    file_pairs.append((excel, pdf, options.sheet_name or "Sheet1"))
            else:
                # Single file processing
                file_pairs = [(excel_path, pdf_path, options.sheet_name or "Sheet1")]

            # Create simplified pipeline context
            context = PipelineContext(file_pairs=file_pairs, options=options_dict)

            self.logger.info(f"Starting pipeline with {len(self.steps)} steps")

            # Execute each step in sequence with conditional execution
            executed_steps = 0
            for i, step in enumerate(self.steps):
                step_name = step.__class__.__name__

                # Check if step should be executed (conditional logic)
                if hasattr(step, "should_execute") and not step.should_execute(context):
                    self.logger.info(
                        f"Skipping step {i + 1}/{len(self.steps)}: {step_name} (conditions not met)"
                    )
                    continue

                executed_steps += 1
                self.logger.info(
                    f"Executing step {i + 1}/{len(self.steps)}: {step_name}"
                )

                try:
                    step.execute(context)
                    self.logger.info(f"Completed step {step_name}")
                except Exception as e:
                    # Log the full error with context for debugging
                    full_error_msg = f"Pipeline failed at step {step_name}: {str(e)}"
                    self.logger.error(full_error_msg)

                    # Return clean error message for user display
                    return Result(success=False, message=str(e))

            self.logger.info(
                f"Pipeline completed successfully ({executed_steps} steps executed)"
            )
            return Result(success=True, message="OK")

        except Exception as e:
            error_msg = f"Pipeline initialization failed: {str(e)}"
            self.logger.error(error_msg)
            return Result(success=False, message=error_msg)
