#!/usr/bin/env python3
"""
BookmarkStep: Update PDF bookmarks using existing logic.
"""

from typing import Any, Mapping, Sequence

from natsort import natsorted, ns

from core.pipeline.context import PipelineContext
from core.pipeline.steps import BaseStep


class BookmarkStep(BaseStep):
    """Pipeline step for updating PDF bookmark titles with new sorted titles."""

    def execute(self, context: PipelineContext) -> None:
        """Update PDF bookmark titles using existing bookmark update logic.

        This step updates bookmark titles to reflect the new sorted order:
        - Maps original bookmarks to Document IDs using document links
        - Updates bookmark titles using the titles_map from TitleStep
        - Optionally sorts bookmarks naturally if enabled in options

        Args:
            context: Pipeline context containing bookmarks, document_links, titles_map, and options

        Raises:
            Exception: If bookmark updating fails
        """
        self.logger.info("Updating PDF bookmark titles with new sorted order")

        # Ensure we have all required data
        if context.bookmarks is None:
            raise ValueError("No PDF bookmarks loaded for updating")

        if context.document_links is None:
            raise ValueError("No document links available for bookmark mapping")

        if context.titles_map is None:
            raise ValueError("No titles map available from TitleStep")

        # Store counts for logging
        original_bookmarks = len(context.bookmarks)

        # Create resolver function to map bookmarks to Document IDs
        # This uses the document links created in LinkStep
        title_to_doc_id = {
            link.original_bookmark_title: link.document_id
            for link in context.document_links
        }

        def bookmark_resolver(bm: Mapping[str, Any]) -> str | None:
            """Resolve bookmark to Document ID using original title."""
            return title_to_doc_id.get(str(bm.get("title", "")))

        # Update bookmarks using existing logic from RenumberService
        updated_bookmarks = self._update_bookmarks_with_titles_generic(
            context.bookmarks,
            context.titles_map,
            bookmark_resolver,
            context.options.sort_bookmarks,
        )

        # Replace bookmarks in context
        context.bookmarks = updated_bookmarks

        # Count how many bookmarks were actually updated
        updated_count = sum(
            1
            for bm in updated_bookmarks
            if bookmark_resolver({"title": bm.get("title", "")}) in context.titles_map
        )

        self.logger.info(
            f"Bookmark update complete: {updated_count}/{original_bookmarks} bookmarks updated"
        )

        if context.options.sort_bookmarks:
            self.logger.info("Bookmarks sorted naturally by title")

        if updated_count == 0:
            self.logger.warning("No bookmarks were updated - check document linking")
        elif updated_count < original_bookmarks:
            unchanged_count = original_bookmarks - updated_count
            self.logger.info(
                f"{unchanged_count} bookmarks remained unchanged (no matching Excel data)"
            )

    def _update_bookmarks_with_titles_generic(
        self,
        bookmarks: Sequence[Mapping[str, Any]],
        titles_map: Mapping[str, str],
        resolver: callable,
        sort_naturally: bool,
    ):
        """Generic bookmark title update using a resolver to get Document_ID.

        This is the same logic from the original RenumberService.

        Args:
            bookmarks: Original PDF bookmarks
            titles_map: Document_ID -> new title mapping
            resolver: Function to get Document_ID from bookmark
            sort_naturally: Whether to sort bookmarks by title

        Returns:
            List of updated bookmark dictionaries
        """
        updated = []
        for bm in bookmarks:
            doc_id = resolver(bm)
            if doc_id and doc_id in titles_map:
                new_bm = dict(bm)
                new_bm["title"] = titles_map[doc_id]
                updated.append(new_bm)
            else:
                updated.append(dict(bm))

        if sort_naturally:
            updated = natsorted(
                updated, key=lambda b: b.get("title", ""), alg=ns.IGNORECASE
            )

        return updated
