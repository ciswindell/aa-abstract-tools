#!/usr/bin/env python3
"""
ReorderStep: Reorder PDF pages with conditional execution based on options.
"""

from typing import Any, List, Mapping, Sequence, Tuple

import pandas as pd

from core.models import DocumentLink
from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep
from core.transform.pdf import detect_page_ranges


class ReorderStep(BaseStep):
    """Pipeline step for reordering PDF pages to match Excel sort order."""

    def should_execute(self, context: PipelineContext) -> bool:
        """Only execute if page reordering is enabled in options."""
        return context.options.reorder_pages

    def execute(self, context: PipelineContext) -> None:
        """Reorder PDF pages to match Excel sort order using existing logic.

        This step reorders PDF pages so they match the sorted Excel order.
        The logic differs for merge vs single-file workflows but both use
        the same underlying page range detection and reordering algorithms.

        Args:
            context: Pipeline context containing all required data

        Raises:
            Exception: If page reordering fails
        """
        self.logger.info("Reordering PDF pages to match Excel sort order")

        # Ensure we have all required data
        if context.df is None:
            raise ValueError("No Excel data available for page reordering")

        if context.pages is None or context.bookmarks is None:
            raise ValueError("No PDF pages or bookmarks available for reordering")

        if context.titles_map is None:
            raise ValueError("No titles map available for page reordering")

        # Store original counts for logging
        original_pages = len(context.pages)
        original_bookmarks = len(context.bookmarks)

        # Use different reordering logic based on workflow type
        if context.is_merge_workflow():
            new_pages, new_bookmarks = self._reorder_pages_merged(
                context.df,
                context.titles_map,
                context.pages,
                context.bookmarks,
                context.merged_links or [],
            )
        else:
            new_pages, new_bookmarks = self._reorder_pages_single(
                context.df,
                context.titles_map,
                context.pages,
                context.bookmarks,
                context.total_pages,
                context.document_links,
            )

        # Update context with reordered pages and bookmarks
        if new_pages and new_bookmarks:
            context.pages = new_pages
            context.bookmarks = new_bookmarks
            context.total_pages = len(new_pages)

            self.logger.info(
                f"Page reordering complete: {len(new_pages)} pages, {len(new_bookmarks)} bookmarks"
            )
        else:
            self.logger.warning(
                "Page reordering returned empty results - keeping original order"
            )

    def _reorder_pages_merged(
        self,
        df: pd.DataFrame,
        titles_map: Mapping[str, str],
        pages: Sequence[Any],
        bookmarks: Sequence[Mapping[str, Any]],
        links_with_offsets: Sequence[Tuple[DocumentLink, int]],
    ):
        """Return reordered pages and new bookmarks for merged flow.

        This is the same logic from the original RenumberService.
        """
        if not bookmarks or not pages:
            return [], []

        # Build synthetic unique titles to safely use detect_page_ranges
        synthetic_bookmarks: List[Mapping[str, Any]] = []
        for bm in bookmarks:
            t = str(bm.get("title", ""))
            p = int(bm.get("page", 1))
            synthetic_bookmarks.append({"title": f"{t}@@{p}", "page": p})

        ranges_by_synth_title = detect_page_ranges(synthetic_bookmarks, len(pages))

        # Map Document_ID to its synthetic key and level using original link + offset
        doc_id_to_synth_key: dict[str, str] = {}
        doc_id_to_level: dict[str, int] = {}
        for link, offset in links_with_offsets:
            synth_key = f"{link.original_bookmark_title}@@{int(link.original_bookmark_page) + int(offset)}"
            doc_id_to_synth_key[link.document_id] = synth_key
            doc_id_to_level[link.document_id] = int(link.original_bookmark_level)

        new_pages: List[Any] = []
        new_bookmarks: List[dict[str, Any]] = []
        current_start_page = 1

        for _, row in df.iterrows():
            doc_id = str(row.get("Document_ID", "")).strip()
            if not doc_id:
                continue
            synth_key = doc_id_to_synth_key.get(doc_id)
            if not synth_key:
                continue
            rng = ranges_by_synth_title.get(synth_key)
            if not rng:
                continue
            start, end = int(rng["start"]), int(rng["end"])
            for p in range(start, end + 1):
                if 1 <= p <= len(pages):
                    new_pages.append(pages[p - 1])
            new_title = titles_map.get(doc_id)
            if new_title:
                new_bookmarks.append(
                    {
                        "title": new_title,
                        "page": current_start_page,
                        "level": doc_id_to_level.get(doc_id, 0),
                    }
                )
            current_start_page += max(0, end - start + 1)

        return new_pages, new_bookmarks

    def _reorder_pages_single(
        self,
        df: pd.DataFrame,
        titles_map: Mapping[str, str],
        pages: Sequence[Any],
        bookmarks: Sequence[Mapping[str, Any]],
        total_pages: int,
        document_links: List[DocumentLink],
    ):
        """Return reordered pages and new bookmarks for single-file flow.

        This is the same logic from the original RenumberService.
        """
        if not bookmarks or not pages or int(total_pages) <= 0:
            return [], []

        original_ranges_by_title = detect_page_ranges(bookmarks, total_pages)

        doc_id_to_original_title: dict[str, str] = {}
        doc_id_to_level: dict[str, int] = {}

        # Use document links passed from context (created in LinkStep)

        for link in document_links:
            doc_id_to_original_title[link.document_id] = link.original_bookmark_title
            doc_id_to_level[link.document_id] = int(link.original_bookmark_level)

        new_pages: List[Any] = []
        new_bookmarks: List[dict[str, Any]] = []
        current_start_page = 1

        for _, row in df.iterrows():
            doc_id = str(row.get("Document_ID", "")).strip()
            if not doc_id:
                continue

            original_title = doc_id_to_original_title.get(doc_id)
            if not original_title:
                continue

            rng = original_ranges_by_title.get(original_title)
            if not rng:
                continue

            start, end = int(rng["start"]), int(rng["end"])

            for p in range(start, end + 1):
                if 1 <= p <= len(pages):
                    new_pages.append(pages[p - 1])

            new_title = titles_map.get(doc_id)
            if new_title:
                new_bookmarks.append(
                    {
                        "title": new_title,
                        "page": current_start_page,
                        "level": doc_id_to_level.get(doc_id, 0),
                    }
                )
            current_start_page += max(0, end - start + 1)

        return new_pages, new_bookmarks
