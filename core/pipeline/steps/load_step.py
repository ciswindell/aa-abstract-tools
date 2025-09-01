#!/usr/bin/env python3
"""
LoadStep: Load and merge Excel/PDF files with DocumentUnit linking.

This step processes Excel/PDF file pairs and creates the foundation for processing:
1. Processes each Excel/PDF pair individually to prevent Document ID collisions
2. Creates DocumentUnits that link Excel rows to PDF page ranges
3. Merges all files into a single PDF and consolidated DataFrame
"""

import tempfile
from pathlib import Path
from typing import List

import pandas as pd
from pypdf import PdfWriter

from core.models import DocumentUnit
from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.document_unit import link_bookmarks_to_excel_rows
from core.transform.excel import add_document_ids


class LoadStep(BaseStep):
    """Load and merge Excel/PDF files with DocumentUnit linking."""

    def execute(self, context: PipelineContext) -> None:
        """Load and merge Excel/PDF files, creating DocumentUnits for linked data.

        Processes each Excel/PDF pair individually to prevent Document ID collisions,
        creates DocumentUnits that link Excel rows to PDF page ranges, and merges
        everything into a single PDF and consolidated DataFrame.

        Args:
            context: Pipeline context containing file paths and options

        Raises:
            ValueError: If no file pairs found or invalid file paths
            FileNotFoundError: If Excel or PDF files cannot be found
            Exception: If file loading, linking, or PDF merging fails
        """
        try:
            self.logger.info("Starting file loading and merging")

            # Get all file pairs to process
            file_pairs = context.file_pairs
            if not file_pairs:
                raise ValueError("No file pairs found to process")

            self.logger.info(f"Found {len(file_pairs)} file pairs to process")

            # Initialize collections for merging
            all_document_units = []
            all_df_parts = []
            merged_writer = PdfWriter()
            current_page_offset = 0

            # Process each file pair individually
            for i, (excel_path, pdf_path, sheet_name) in enumerate(file_pairs):
                try:
                    self.logger.info(
                        f"Processing pair {i + 1}/{len(file_pairs)}: {excel_path}, {pdf_path}"
                    )

                    # Process this specific file pair
                    pair_units, pair_df, pages_added = self._process_file_pair(
                        excel_path,
                        pdf_path,
                        sheet_name,
                        current_page_offset,
                        merged_writer,
                    )

                    # Validate results
                    if pair_df.empty:
                        self.logger.warning(f"Empty DataFrame from {excel_path}")
                    if not pair_units:
                        self.logger.warning(
                            f"No DocumentUnits created from {excel_path}:{pdf_path}"
                        )

                    # Accumulate results
                    all_document_units.extend(pair_units)
                    all_df_parts.append(pair_df)
                    current_page_offset += pages_added

                    self.logger.info(
                        f"Pair {i + 1} processed: {len(pair_units)} DocumentUnits, {pages_added} pages"
                    )

                except Exception as e:
                    self.logger.error(
                        f"Failed to process pair {i + 1} ({excel_path}, {pdf_path}): {e}"
                    )
                    raise Exception(
                        f"File processing failed on pair {i + 1}: {e}"
                    ) from e

            # Validate overall results
            if not all_document_units:
                raise ValueError("No DocumentUnits were created from any file pairs")
            if not all_df_parts:
                raise ValueError("No DataFrames were loaded from any file pairs")

            # Create intermediate merged PDF
            try:
                intermediate_pdf_path = self._create_intermediate_pdf(merged_writer)
            except Exception as e:
                self.logger.error(f"Failed to create intermediate PDF: {e}")
                raise Exception(f"PDF merging failed: {e}") from e

            # Merge all DataFrames
            try:
                merged_df = self._merge_dataframes(all_df_parts)
                if merged_df.empty:
                    raise ValueError("Merged DataFrame is empty")
            except Exception as e:
                self.logger.error(f"Failed to merge DataFrames: {e}")
                raise Exception(f"DataFrame merging failed: {e}") from e

            # Update context with merged results
            context.document_units = all_document_units
            context.df = merged_df
            context.intermediate_pdf_path = intermediate_pdf_path
            context.total_pages = current_page_offset

            self.logger.info(
                f"Loading complete: {len(all_document_units)} DocumentUnits, {current_page_offset} total pages"
            )

        except Exception as e:
            self.logger.error(f"LoadStep execution failed: {e}")
            # Clean up any partial results
            if (
                hasattr(context, "intermediate_pdf_path")
                and context.intermediate_pdf_path
            ):
                try:
                    Path(context.intermediate_pdf_path).unlink(missing_ok=True)
                except Exception:
                    pass
            raise

    def _process_file_pair(
        self,
        excel_path: str,
        pdf_path: str,
        sheet_name: str,
        page_offset: int,
        merged_writer: PdfWriter,
    ) -> tuple[List[DocumentUnit], pd.DataFrame, int]:
        """Process a single Excel/PDF pair and return DocumentUnits, DataFrame, and pages added.

        Prevents Document ID collisions by processing each file individually before merging.

        Returns:
            Tuple of (document_units, dataframe_with_ids, pages_added_count)

        Raises:
            FileNotFoundError: If Excel or PDF files don't exist
            ValueError: If files are invalid or empty
            Exception: If processing fails
        """
        # Validate file paths
        if not Path(excel_path).exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            # Load Excel file and add Document IDs using this file's path
            self.logger.info(f"Loading Excel: {excel_path}")
            pair_df = self.excel_repo.load(excel_path, sheet_name)

            if pair_df.empty:
                self.logger.warning(f"Excel file is empty: {excel_path}")
                # Continue processing even with empty DataFrame

            # Clean data types before generating Document IDs to ensure consistent ID generation
            from core.transform.excel import clean_types

            pair_df_cleaned = clean_types(pair_df)

            pair_df_with_ids = add_document_ids(pair_df_cleaned, excel_path)
            self.logger.info(f"Loaded {len(pair_df_with_ids)} rows from {excel_path}")

        except Exception as e:
            raise Exception(f"Failed to load Excel file {excel_path}: {e}") from e

        try:
            # Load PDF file
            self.logger.info(f"Loading PDF: {pdf_path}")
            pair_bookmarks, pair_total_pages = self.pdf_repo.read(pdf_path)

            if pair_total_pages <= 0:
                raise ValueError(f"PDF has no pages: {pdf_path}")

            self.logger.info(
                f"Loaded PDF with {pair_total_pages} pages, {len(pair_bookmarks)} bookmarks from {pdf_path}"
            )

        except Exception as e:
            raise Exception(f"Failed to load PDF file {pdf_path}: {e}") from e

        try:
            # Add all pages from this PDF to the merged writer (memory efficient - no list creation)
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            pages_added = 0
            for page in reader.pages:
                merged_writer.add_page(page)
                pages_added += 1

            if pages_added != pair_total_pages:
                self.logger.warning(
                    f"Page count mismatch in {pdf_path}: expected {pair_total_pages}, added {pages_added}"
                )

        except Exception as e:
            raise Exception(
                f"Failed to add pages from {pdf_path} to merged PDF: {e}"
            ) from e

        try:
            # Create DocumentUnits by linking bookmarks to Excel rows within this file
            source_info = f"{excel_path}:{pdf_path}"
            document_units = link_bookmarks_to_excel_rows(
                bookmarks=pair_bookmarks,
                excel_df=pair_df_with_ids,
                page_offset=page_offset,
                source_info=source_info,
                total_pages=pair_total_pages,
            )

            self.logger.info(
                f"Created {len(document_units)} DocumentUnits from {excel_path}:{pdf_path}"
            )

            # Log linking statistics
            if pair_bookmarks and not document_units:
                self.logger.warning(
                    f"No DocumentUnits created despite {len(pair_bookmarks)} bookmarks in {pdf_path}"
                )
            elif len(document_units) < len(pair_bookmarks):
                self.logger.info(
                    f"Linked {len(document_units)}/{len(pair_bookmarks)} bookmarks to Excel rows"
                )

        except Exception as e:
            raise Exception(
                f"Failed to create DocumentUnits for {excel_path}:{pdf_path}: {e}"
            ) from e

        return document_units, pair_df_with_ids, pages_added

    def _create_intermediate_pdf(self, merged_writer: PdfWriter) -> str:
        """Create intermediate merged PDF file and return its path."""
        # Create temporary file for intermediate PDF
        temp_fd, temp_path = tempfile.mkstemp(
            suffix=".pdf", prefix="intermediate_merged_"
        )

        try:
            with open(temp_path, "wb") as temp_file:
                merged_writer.write(temp_file)

            self.logger.info(f"Created intermediate PDF: {temp_path}")
            return temp_path
        except Exception:
            # Clean up temp file if creation failed
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass
            raise

    def _merge_dataframes(self, df_parts: List[pd.DataFrame]) -> pd.DataFrame:
        """Merge all DataFrame parts into a single DataFrame."""
        if not df_parts:
            return pd.DataFrame()

        if len(df_parts) == 1:
            return df_parts[0]

        # Concatenate all DataFrames (each already has unique Document IDs)
        merged_df = pd.concat(df_parts, ignore_index=True)
        self.logger.info(
            f"Merged {len(df_parts)} DataFrames into {len(merged_df)} total rows"
        )

        return merged_df
