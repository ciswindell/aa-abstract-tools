#!/usr/bin/env python3
"""
LoadStep: Load Excel/PDF files based on merge vs single file options.
"""

from typing import List

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep


class LoadStep(BaseStep):
    """Pipeline step for loading Excel and PDF files."""

    def execute(self, context: PipelineContext) -> None:
        """Load Excel/PDF files based on merge vs single file workflow.

        For single file workflow: Load the primary Excel/PDF files directly.
        For merge workflow: Load all file pairs and store them for merging.

        Args:
            context: Pipeline context containing file paths and options

        Raises:
            Exception: If file loading fails
        """
        if context.is_merge_workflow():
            self._load_merge_files(context)
        else:
            self._load_single_files(context)

    def _load_single_files(self, context: PipelineContext) -> None:
        """Load single Excel and PDF files."""
        self.logger.info(f"Loading single Excel file: {context.excel_path}")
        context.df = self.excel_repo.load(
            context.excel_path, context.options.sheet_name
        )

        self.logger.info(f"Loading single PDF file: {context.pdf_path}")
        context.bookmarks, context.total_pages = self.pdf_repo.read(context.pdf_path)
        context.pages = list(self.pdf_repo.pages(context.pdf_path))

    def _load_merge_files(self, context: PipelineContext) -> None:
        """Load multiple file pairs for merge workflow."""
        self.logger.info("Loading multiple file pairs for merge workflow")

        # Initialize merge collections
        context.merged_df_parts = []
        context.merged_df_source_paths = []  # Track source paths for Document ID generation
        context.merged_pages = []
        context.merged_bookmarks = []

        # Track page offset for bookmark adjustment
        merged_page_offset = 0

        # Get pair descriptors (with per-pair sheet names if available)
        pair_descriptors = self._get_pair_descriptors(context)

        for i, (excel_path, pdf_path, sheet_name) in enumerate(pair_descriptors):
            self.logger.info(
                f"Loading pair {i + 1}/{len(pair_descriptors)}: {excel_path}, {pdf_path}"
            )

            # Load Excel file for this pair
            pair_df = self.excel_repo.load(excel_path, sheet_name)
            context.merged_df_parts.append(pair_df)
            context.merged_df_source_paths.append(
                excel_path
            )  # Track source for Document ID generation

            # Load PDF file for this pair
            pair_bookmarks, pair_total_pages = self.pdf_repo.read(pdf_path)
            pair_pages = list(self.pdf_repo.pages(pdf_path))

            # Accumulate pages
            context.merged_pages.extend(pair_pages)

            # Adjust bookmark page numbers for merged PDF
            for bm in pair_bookmarks:
                adjusted_bm = dict(bm)
                adjusted_bm["page"] = int(bm.get("page", 1)) + merged_page_offset
                context.merged_bookmarks.append(adjusted_bm)

            # Update page offset for next pair
            merged_page_offset += int(pair_total_pages)

    def _get_pair_descriptors(self, context: PipelineContext) -> List[tuple]:
        """Get list of (excel_path, pdf_path, sheet_name) tuples for merge workflow."""
        # Always include the primary selection as the first pair
        pairs_with_sheets = [
            (context.excel_path, context.pdf_path, context.options.sheet_name)
        ]
        seen = {(context.excel_path, context.pdf_path)}

        # Use per-pair sheet names if available, otherwise fall back to merge_pairs
        if context.options.merge_pairs_with_sheets:
            for (
                excel_path,
                pdf_path,
                sheet_name,
            ) in context.options.merge_pairs_with_sheets:
                if (excel_path, pdf_path) not in seen:
                    pairs_with_sheets.append((excel_path, pdf_path, sheet_name))
                    seen.add((excel_path, pdf_path))
        elif context.options.merge_pairs:
            for excel_path, pdf_path in context.options.merge_pairs:
                if (excel_path, pdf_path) not in seen:
                    pairs_with_sheets.append(
                        (excel_path, pdf_path, context.options.sheet_name)
                    )
                    seen.add((excel_path, pdf_path))

        return pairs_with_sheets
