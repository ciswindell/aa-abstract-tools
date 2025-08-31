#!/usr/bin/env python3
"""
Main pipeline orchestrator that executes steps in sequence.
"""

from typing import List

from core.interfaces import ExcelRepo, Logger, PdfRepo
from core.models import Options, Result
from core.pipeline.context import PipelineContext
from core.pipeline.steps import PipelineStep
from core.services.validate import ValidationService


class Pipeline:
    """Main pipeline orchestrator that executes steps in sequence."""

    def __init__(
        self,
        excel_repo: ExcelRepo,
        pdf_repo: PdfRepo,
        validator: ValidationService,
        logger: Logger,
    ) -> None:
        """Initialize pipeline with dependencies."""
        self.excel_repo = excel_repo
        self.pdf_repo = pdf_repo
        self.validator = validator
        self.logger = logger
        self.steps: List[PipelineStep] = []

    def add_step(self, step: PipelineStep) -> None:
        """Add a step to the pipeline."""
        self.steps.append(step)

    def register_steps(self) -> None:
        """Register all pipeline steps in the correct order.

        This method defines the hardcoded pipeline step order as specified in the PRD.
        Steps are conditionally executed based on options within each step's should_execute() method.
        """
        from core.pipeline.steps.add_ids_step import AddIdsStep
        from core.pipeline.steps.bookmark_step import BookmarkStep
        from core.pipeline.steps.clean_step import CleanStep
        from core.pipeline.steps.filter_step import FilterStep
        from core.pipeline.steps.link_step import LinkStep
        from core.pipeline.steps.load_step import LoadStep
        from core.pipeline.steps.merge_step import MergeStep
        from core.pipeline.steps.reorder_step import ReorderStep
        from core.pipeline.steps.save_step import SaveStep
        from core.pipeline.steps.sort_step import SortStep
        from core.pipeline.steps.title_step import TitleStep
        from core.pipeline.steps.validate_step import ValidateStep

        # Register steps in hardcoded order (as per PRD requirements)
        self.add_step(
            LoadStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            MergeStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            ValidateStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            CleanStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            FilterStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            AddIdsStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            LinkStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            SortStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            TitleStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            BookmarkStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            ReorderStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
        )
        self.add_step(
            SaveStep(self.excel_repo, self.pdf_repo, self.validator, self.logger)
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

            # Create pipeline context
            context = PipelineContext(
                excel_path=excel_path, pdf_path=pdf_path, options=options
            )

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
                    error_msg = f"Pipeline failed at step {step_name}: {str(e)}"
                    self.logger.error(error_msg)
                    return Result(success=False, message=error_msg)

            self.logger.info(
                f"Pipeline completed successfully ({executed_steps} steps executed)"
            )
            return Result(success=True, message="OK")

        except Exception as e:
            error_msg = f"Pipeline initialization failed: {str(e)}"
            self.logger.error(error_msg)
            return Result(success=False, message=error_msg)
