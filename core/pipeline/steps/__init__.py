#!/usr/bin/env python3
"""
Pipeline steps module with base Step protocol and common utilities.
"""

from abc import ABC, abstractmethod
from typing import Protocol

from core.interfaces import ExcelRepo, Logger, PdfRepo, UIController
from core.pipeline.context import PipelineContext
from core.services.validate import ValidationService


class PipelineStep(Protocol):
    """Protocol for pipeline steps."""

    def execute(self, context: PipelineContext) -> None:
        """Execute the pipeline step with the given context.

        Args:
            context: Pipeline context containing all data

        Raises:
            Exception: If step execution fails
        """
        ...


class BaseStep(ABC):
    """Base class for pipeline steps with common functionality."""

    def __init__(
        self,
        excel_repo: ExcelRepo,
        pdf_repo: PdfRepo,
        validator: ValidationService,
        logger: Logger,
        ui: UIController,
    ) -> None:
        """Initialize step with dependencies."""
        self.excel_repo = excel_repo
        self.pdf_repo = pdf_repo
        self.validator = validator
        self.logger = logger
        self.ui = ui

    @abstractmethod
    def execute(self, context: PipelineContext) -> None:
        """Execute the pipeline step with the given context.

        Args:
            context: Pipeline context containing all data

        Raises:
            Exception: If step execution fails
        """
        pass

    def should_execute(self, context: PipelineContext) -> bool:
        """Check if this step should be executed based on context/options.

        Override this method in steps that are conditionally executed.

        Args:
            context: Pipeline context

        Returns:
            True if step should execute, False to skip
        """
        return True


# Re-export the protocol for convenience
__all__ = ["PipelineStep", "BaseStep"]
