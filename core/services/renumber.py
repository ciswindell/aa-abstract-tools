#!/usr/bin/env python3
"""
RenumberService: orchestrates Excel/PDF load, validate, transform, and save.
"""

from typing import Any, Mapping, Sequence, List, Tuple
from pathlib import Path
from fileops.files import create_backups
import pandas as pd

from core.interfaces import ExcelRepo, Logger, PdfRepo
from core.models import Options, Result
from core.services.validate import ValidationService
from core.transform.excel import (
    add_document_ids,
    clean_types,
    create_document_links,
    sort_and_renumber,
    filter_df,
)
from core.transform.pdf import make_titles, detect_page_ranges
from natsort import natsorted, ns


class RenumberService:
    """Single entrypoint for the renumber workflow."""

    def __init__(
        self,
        excel_repo: ExcelRepo,
        pdf_repo: PdfRepo,
        validator: ValidationService,
        logger: Logger,
    ) -> None:
        """Initialize with repositories, validator, and logger."""

        self._excel = excel_repo
        self._pdf = pdf_repo
        self._validator = validator
        self._log = logger

    def run(self, excel_path: str, pdf_path: str, opts: Options) -> Result:
        """Execute the end-to-end renumber process."""

        try:
            # Handle merge or single-file flow
            merged = bool(getattr(opts, "merge_pairs", None))

            if merged:
                self._log.info("Loading and validating multiple pairs for merge...")
                combined_pages: List[Any] = []
                combined_bookmarks: List[Mapping[str, Any]] = []
                combined_links: List[Any] = []  # DocumentLink objects
                df_parts: List[Any] = []
                page_offset = 0

                # Each pair: load → validate → clean → link → add IDs → accumulate
                # Prefer per-pair sheet if provided
                pairs_iter = []
                if getattr(opts, "merge_pairs_with_sheets", None):
                    for x, p, s in getattr(opts, "merge_pairs_with_sheets", []):
                        pairs_iter.append((x, p, s))
                else:
                    for x, p in getattr(opts, "merge_pairs", []):
                        pairs_iter.append((x, p, opts.sheet_name))

                for pair_excel, pair_pdf, pair_sheet in pairs_iter:
                    df_i = self._excel.load(pair_excel, pair_sheet)
                    bms_i, total_pages_i = self._pdf.read(pair_pdf)

                    # Validate inputs for this pair
                    self._validator.run(df=df_i, bookmarks=bms_i)

                    # Clean and link before IDs for stable mapping
                    clean_i = clean_types(df_i)
                    links_i = create_document_links(clean_i, bms_i, pair_excel)

                    # Add IDs per pair to keep IDs consistent with linking
                    df_ids_i = add_document_ids(clean_i, pair_excel)
                    df_parts.append(df_ids_i)

                    # Accumulate pages and offset bookmarks
                    pages_i = list(self._pdf.pages(pair_pdf))
                    combined_pages.extend(pages_i)
                    for bm in bms_i:
                        new_bm = dict(bm)
                        new_bm["page"] = int(bm.get("page", 1)) + page_offset
                        combined_bookmarks.append(new_bm)

                    # Store links and remember offset for later mapping via page
                    for link in links_i:
                        # Attach offset info by creating a light tuple mapping
                        combined_links.append((link, page_offset))

                    page_offset += int(total_pages_i)

                # Combine DataFrames
                if df_parts:
                    df = pd.concat(df_parts, ignore_index=True)
                else:
                    df = pd.DataFrame()
                bookmarks = combined_bookmarks
                pages = combined_pages
                total_pages = len(combined_pages)
            else:
                self._log.info("Loading Excel and PDF...")
                df = self._excel.load(excel_path, opts.sheet_name)
                bookmarks, total_pages = self._pdf.read(pdf_path)

                self._log.info("Validating inputs...")
                self._validator.run(df=df, bookmarks=bookmarks)

            self._log.info("Transforming Excel data...")
            # Clean
            df = clean_types(df)
            # Option-gated filter (keeps behavior identical when not set)
            if getattr(opts, "filter_column", None) and getattr(
                opts, "filter_values", None
            ):
                df = filter_df(df, opts.filter_column, opts.filter_values)
            # Preserve pre-ID/renumber snapshot for document link creation
            pre_id_df = df
            # Add IDs and sort/renumber
            if merged:
                # IDs already added per pair to keep consistency with links
                pass
            else:
                df = add_document_ids(df, excel_path)
            df = sort_and_renumber(df)

            self._log.info("Generating PDF bookmark titles...")
            titles_map = make_titles(df)

            # Determine output paths

            if merged:
                excel_out_path = str(Path(excel_path).with_name("merged.xlsx"))
                pdf_out_path = str(Path(pdf_path).with_name("merged.pdf"))
            else:
                excel_out_path = excel_path
                pdf_out_path = pdf_path

            # Create backups if enabled (skip when merging), only after validation passes
            if opts.backup and not merged:
                create_backups(excel_path, pdf_path)

            # Save Excel back into template (in-place responsibility left to caller via backups)
            self._log.info("Saving Excel output...")
            target_sheet = opts.sheet_name or "Index"
            self._excel.save(
                df,
                template_path=excel_path,
                target_sheet=target_sheet,
                out_path=excel_out_path,
            )

            # Recreate PDF output with updated bookmarks
            self._log.info("Saving PDF output...")
            if merged:
                # Non-reorder path: update titles in-place on combined bookmarks
                updated_bookmarks = _update_bookmarks_with_titles_merged(
                    bookmarks, titles_map, combined_links  # type: ignore[name-defined]
                )
                # Respect 'sort_bookmarks' option in merge mode
                if opts.sort_bookmarks:
                    updated_bookmarks = natsorted(
                        updated_bookmarks,
                        key=lambda b: b.get("title", ""),
                        alg=ns.IGNORECASE,
                    )
            else:
                pages = self._pdf.pages(pdf_path)
                # Create DocumentLink objects for bookmark title mapping
                document_links = create_document_links(pre_id_df, bookmarks, excel_path)

                updated_bookmarks = _merge_bookmarks_with_titles(
                    bookmarks, titles_map, opts.sort_bookmarks, document_links
                )

            if opts.reorder_pages:
                if merged:
                    new_pages, new_bookmarks = _reorder_pages_merged(
                        df, titles_map, pages, bookmarks, combined_links  # type: ignore[name-defined]
                    )
                else:
                    new_pages, new_bookmarks = _reorder_pages_single(
                        df,
                        titles_map,
                        pages,
                        bookmarks,
                        total_pages,
                        pre_id_df,
                        excel_path,
                    )

                self._pdf.write(
                    pages=new_pages or pages,
                    bookmarks=new_bookmarks or updated_bookmarks,
                    out_path=pdf_out_path,
                )
            else:
                self._pdf.write(
                    pages=pages, bookmarks=updated_bookmarks, out_path=pdf_out_path
                )

            self._log.info("Complete.")
            return Result(success=True, message="OK")

        except (ValueError, OSError, RuntimeError) as exc:
            self._log.error(str(exc))
            return Result(success=False, message=str(exc))


def _merge_bookmarks_with_titles(
    bookmarks: Sequence[Mapping[str, Any]],
    titles_map: Mapping[str, str],
    sort_naturally: bool,
    document_links: Sequence[Any],  # DocumentLink objects
):
    """Return updated bookmarks with new titles using DocumentLink mapping.

    Args:
        bookmarks: Original PDF bookmarks
        titles_map: Map from Document_ID to new title
        document_links: DocumentLink objects that map bookmarks to Excel rows
        sort_naturally: Whether to sort bookmarks naturally
    """

    # Create mapping from original bookmark title to Document_ID
    title_to_doc_id = {}
    for link in document_links:
        title_to_doc_id[link.original_bookmark_title] = link.document_id

    updated = []
    for bm in bookmarks:
        original_title = str(bm.get("title", ""))
        doc_id = title_to_doc_id.get(original_title)

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


def _update_bookmarks_with_titles_merged(
    bookmarks: Sequence[Mapping[str, Any]],
    titles_map: Mapping[str, str],
    links_with_offsets: Sequence[Tuple[Any, int]],  # (DocumentLink, offset)
):
    """Update bookmark titles for merged flows using (title,page) mapping.

    Uses original bookmark title and page (with offset) to resolve Document_ID
    and then titles_map for the final label.
    """
    title_page_to_doc: dict[Tuple[str, int], str] = {}
    for link, offset in links_with_offsets:
        key = (
            link.original_bookmark_title,
            int(link.original_bookmark_page) + int(offset),
        )
        title_page_to_doc[key] = link.document_id

    out: List[Mapping[str, Any]] = []
    for bm in bookmarks:
        key = (str(bm.get("title", "")), int(bm.get("page", 1)))
        doc_id = title_page_to_doc.get(key)
        if doc_id and doc_id in titles_map:
            new_bm = dict(bm)
            new_bm["title"] = titles_map[doc_id]
            out.append(new_bm)
        else:
            out.append(dict(bm))
    return out


def _reorder_pages_merged(
    df: pd.DataFrame,
    titles_map: Mapping[str, str],
    pages: Sequence[Any],
    bookmarks: Sequence[Mapping[str, Any]],
    links_with_offsets: Sequence[Tuple[Any, int]],
):
    ordered = sorted(bookmarks, key=lambda b: int(b.get("page", 1)))
    ranges_list: List[Tuple[int, int]] = []
    for i, bm in enumerate(ordered):
        start = int(bm.get("page", 1))
        if i + 1 < len(ordered):
            end = int(ordered[i + 1].get("page", start)) - 1
        else:
            end = len(pages)
        if end < start:
            end = start
        ranges_list.append((start, end))

    key_to_index: dict[Tuple[str, int], int] = {}
    for idx, bm in enumerate(ordered):
        key_to_index[(str(bm.get("title", "")), int(bm.get("page", 1)))] = idx

    doc_id_to_index: dict[str, int] = {}
    doc_id_to_level: dict[str, int] = {}
    for link, offset in links_with_offsets:
        key = (
            link.original_bookmark_title,
            int(link.original_bookmark_page) + int(offset),
        )
        idx = key_to_index.get(key)
        if idx is not None:
            doc_id_to_index[link.document_id] = idx
            doc_id_to_level[link.document_id] = int(link.original_bookmark_level)

    new_pages: List[Any] = []
    new_bookmarks: List[dict[str, Any]] = []
    current_start_page = 1

    for _, row in df.iterrows():
        doc_id = str(row.get("Document_ID", "")).strip()
        if not doc_id:
            continue
        idx = doc_id_to_index.get(doc_id)
        if idx is None:
            continue
        start, end = ranges_list[idx]
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
    df: pd.DataFrame,
    titles_map: Mapping[str, str],
    pages: Sequence[Any],
    bookmarks: Sequence[Mapping[str, Any]],
    total_pages: int,
    pre_id_df: pd.DataFrame,
    excel_path: str,
):
    original_ranges_by_title = detect_page_ranges(bookmarks, total_pages)

    doc_id_to_original_title: dict[str, str] = {}
    doc_id_to_level: dict[str, int] = {}

    document_links = create_document_links(pre_id_df, bookmarks, excel_path)
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
