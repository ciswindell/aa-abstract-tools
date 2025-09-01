#!/usr/bin/env python3
"""
Pipeline context for passing data between pipeline steps.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from pypdf import PdfWriter

from core.models import DocumentUnit


@dataclass
class PipelineContext:
    """Simplified context object that carries data through the pipeline steps.

    This object is passed between pipeline steps and accumulates data
    as it flows through the processing pipeline.
    """

    # Input configuration
    file_pairs: List[Tuple[str, str, str]]  # (excel_path, pdf_path, sheet_name)
    options: Dict[str, Any]  # Simple dictionary of options

    # Processing results (populated by pipeline steps)
    document_units: Optional[List[DocumentUnit]] = None
    df: Optional[pd.DataFrame] = None
    intermediate_pdf_path: Optional[str] = None
    total_pages: Optional[int] = None

    # Final outputs (populated by RebuildPdfStep)
    final_pdf: Optional[PdfWriter] = None
    processed_document_units: Optional[List[DocumentUnit]] = None

    # Output paths (determined during processing)
    excel_out_path: Optional[str] = None
    pdf_out_path: Optional[str] = None

    def is_merge_workflow(self) -> bool:
        """Check if this is a merge workflow (more than one file pair)."""
        return len(self.file_pairs) > 1

    @property
    def excel_path(self) -> str:
        """Get the primary Excel file path (first file pair)."""
        if not self.file_pairs:
            raise ValueError("No file pairs available")
        return self.file_pairs[0][0]

    @property
    def pdf_path(self) -> str:
        """Get the primary PDF file path (first file pair)."""
        if not self.file_pairs:
            raise ValueError("No file pairs available")
        return self.file_pairs[0][1]

    def get_output_paths(self) -> Tuple[str, str]:
        """Get output paths for Excel and PDF files.

        Returns:
            Tuple of (excel_out_path, pdf_out_path)
        """
        if self.excel_out_path is None or self.pdf_out_path is None:
            # Generate default output paths if not set
            from pathlib import Path

            excel_base = Path(self.excel_path)
            pdf_base = Path(self.pdf_path)

            if self.is_merge_workflow():
                # For merge workflows, use "merged" suffix (no backup needed)
                excel_out = excel_base.with_name(
                    f"{excel_base.stem}_merged{excel_base.suffix}"
                )
                pdf_out = pdf_base.with_name(f"{pdf_base.stem}_merged{pdf_base.suffix}")
            else:
                # For single-file workflows, output to original file names
                # (backup logic will handle preserving originals)
                excel_out = excel_base
                pdf_out = pdf_base

            self.excel_out_path = str(excel_out)
            self.pdf_out_path = str(pdf_out)

        return self.excel_out_path, self.pdf_out_path
