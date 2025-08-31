#!/usr/bin/env python3
"""
Pipeline context for passing data between pipeline steps.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Mapping, Optional, Tuple

import pandas as pd

from core.models import DocumentLink, Options


@dataclass
class PipelineContext:
    """Context object that carries data through the pipeline steps.

    This object is passed between pipeline steps and accumulates data
    as it flows through the processing pipeline.
    """

    # Input parameters
    excel_path: str
    pdf_path: str
    options: Options

    # Data accumulated during pipeline execution
    df: Optional[pd.DataFrame] = None
    bookmarks: Optional[List[Mapping[str, Any]]] = None
    pages: Optional[List[Any]] = None
    total_pages: int = 0
    document_links: Optional[List[DocumentLink]] = None
    titles_map: Optional[Mapping[str, str]] = None

    # For merge workflows - accumulated before merge
    merged_df_parts: Optional[List[pd.DataFrame]] = None
    merged_df_source_paths: Optional[List[str]] = (
        None  # Track source path for each DataFrame part
    )
    merged_pages: Optional[List[Any]] = None
    merged_bookmarks: Optional[List[Mapping[str, Any]]] = None
    merged_links: Optional[List[Tuple[DocumentLink, int]]] = None

    # Output paths (determined during processing)
    excel_out_path: Optional[str] = None
    pdf_out_path: Optional[str] = None

    def is_merge_workflow(self) -> bool:
        """Check if this is a merge workflow."""
        return bool(self.options.merge_pairs)

    def get_output_paths(self) -> Tuple[str, str]:
        """Get output paths, computing them if not already set."""
        if self.excel_out_path is None:
            if self.is_merge_workflow():
                self.excel_out_path = str(
                    Path(self.excel_path).with_name("merged.xlsx")
                )
            else:
                self.excel_out_path = self.excel_path

        if self.pdf_out_path is None:
            if self.is_merge_workflow():
                self.pdf_out_path = str(Path(self.pdf_path).with_name("merged.pdf"))
            else:
                self.pdf_out_path = self.pdf_path

        return self.excel_out_path, self.pdf_out_path
