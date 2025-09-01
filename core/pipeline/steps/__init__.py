#!/usr/bin/env python3
"""
DocumentUnit architecture pipeline steps with base protocols and utilities.

This module defines the pipeline step architecture that implements the DocumentUnit
design pattern. Steps operate on immutable DocumentUnits that maintain atomic
Excel row ↔ PDF page range relationships, preventing the data corruption issues
that existed in the previous fragile separate bookmarks/pages list architecture.
"""

from abc import ABC, abstractmethod
from typing import Protocol

from core.interfaces import ExcelRepo, Logger, PdfRepo, UIController
from core.pipeline.context import PipelineContext


class PipelineStep(Protocol):
    """Protocol for DocumentUnit architecture pipeline steps.

    All pipeline steps operate on PipelineContext containing immutable DocumentUnits
    that preserve Excel row ↔ PDF page range relationships throughout processing.
    """

    def execute(self, context: PipelineContext) -> None:
        """Execute the pipeline step with the given context.

        Args:
            context: Pipeline context containing all data

        Raises:
            Exception: If step execution fails
        """
        ...


class BaseStep(ABC):
    """Base class for DocumentUnit architecture pipeline steps.

    Provides common functionality and dependency injection for steps that operate
    on immutable DocumentUnits within the PipelineContext data flow.
    """

    def __init__(
        self,
        excel_repo: ExcelRepo,
        pdf_repo: PdfRepo,
        logger: Logger,
        ui: UIController,
    ) -> None:
        """Initialize step with dependencies."""
        self.excel_repo = excel_repo
        self.pdf_repo = pdf_repo
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
