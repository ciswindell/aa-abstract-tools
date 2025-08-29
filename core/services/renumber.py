#!/usr/bin/env python3
"""
RenumberService: orchestrates Excel/PDF load, validate, transform, and save.
"""

from typing import Any, Mapping, Sequence, List, Tuple
from pathlib import Path
from fileops.files import create_backups
import pandas as pd

from core.interfaces import ExcelRepo, Logger, PdfRepo
from core.models import Options, Result, DocumentLink
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
            merged = bool(opts.merge_pairs)

            # Predeclare shared variables to avoid conditional scope issues
            bookmarks: List[Mapping[str, Any]] = []
            pages: List[Any] = []
            total_pages: int = 0
            merged_links: List[Tuple[DocumentLink, int]] = []

            if merged:
                self._log.info("Loading and validating multiple pairs for merge...")
                merged_pages: List[Any] = []
                merged_bookmarks: List[Mapping[str, Any]] = []
                merged_links: List[Tuple[DocumentLink, int]] = []
                merged_df_parts: List[Any] = []
                merged_page_offset = 0

                # Each pair: load → validate → clean → link → add IDs → accumulate
                # Prefer per-pair sheet if provided
                pair_descriptors = []
                if opts.merge_pairs_with_sheets:
                    for (
                        excel_path_item,
                        pdf_path_item,
                        sheet_name_item,
                    ) in opts.merge_pairs_with_sheets:
                        pair_descriptors.append(
                            (excel_path_item, pdf_path_item, sheet_name_item)
                        )
                else:
                    for excel_path_item, pdf_path_item in opts.merge_pairs or []:
                        pair_descriptors.append(
                            (excel_path_item, pdf_path_item, opts.sheet_name)
                        )

                for pair_excel, pair_pdf, pair_sheet in pair_descriptors:
                    pair_df = self._excel.load(pair_excel, pair_sheet)
                    pair_bookmarks, pair_total_pages = self._pdf.read(pair_pdf)

                    # Validate inputs for this pair
                    self._validator.run(df=pair_df, bookmarks=pair_bookmarks)

                    # Clean and add IDs before linking
                    pair_clean_df = clean_types(pair_df)
                    pair_df_with_ids = add_document_ids(pair_clean_df, pair_excel)
                    pair_links = create_document_links(pair_df_with_ids, pair_bookmarks)
                    merged_df_parts.append(pair_df_with_ids)

                    # Accumulate pages and offset bookmarks
                    pair_pages = list(self._pdf.pages(pair_pdf))
                    merged_pages.extend(pair_pages)
                    for bm in pair_bookmarks:
                        new_bm = dict(bm)
                        new_bm["page"] = int(bm.get("page", 1)) + merged_page_offset
                        merged_bookmarks.append(new_bm)

                    # Store links and remember offset for later mapping via page
                    for link in pair_links:
                        # Attach offset info by creating a light tuple mapping
                        merged_links.append((link, merged_page_offset))

                    merged_page_offset += int(pair_total_pages)

                # Combine DataFrames
                if merged_df_parts:
                    df = pd.concat(merged_df_parts, ignore_index=True)
                else:
                    df = pd.DataFrame()
                bookmarks = merged_bookmarks
                pages = merged_pages
                total_pages = len(merged_pages)
            else:
                self._log.info("Loading Excel and PDF...")
                df = self._excel.load(excel_path, opts.sheet_name)
                bookmarks, total_pages = self._pdf.read(pdf_path)
                pages = list(self._pdf.pages(pdf_path))

                self._log.info("Validating inputs...")
                self._validator.run(df=df, bookmarks=bookmarks)

            self._log.info("Transforming Excel data...")
            # Clean
            df = clean_types(df)
            # Option-gated filter (keeps behavior identical when not set)
            if opts.filter_column and opts.filter_values:
                df = filter_df(df, opts.filter_column, opts.filter_values)
            # Add IDs and preserve a pre-renumber snapshot for linking
            if merged:
                # IDs already added per pair to keep consistency with links
                pre_id_df = df
            else:
                df = add_document_ids(df, excel_path)
                pre_id_df = df.copy()
            # Sort and renumber after IDs
            df = sort_and_renumber(df)

            self._log.info("Generating PDF bookmark titles...")
            titles_map = make_titles(df)

            # Determine output paths
            excel_out_path = (
                str(Path(excel_path).with_name("merged.xlsx")) if merged else excel_path
            )
            pdf_out_path = (
                str(Path(pdf_path).with_name("merged.pdf")) if merged else pdf_path
            )

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
                # Build resolver mapping for merged: (title, page) -> Document_ID
                title_page_to_doc: dict[Tuple[str, int], str] = {}
                for link, offset in merged_links:
                    key = (
                        link.original_bookmark_title,
                        int(link.original_bookmark_page) + int(offset),
                    )
                    title_page_to_doc[key] = link.document_id

                def merged_resolver(bm: Mapping[str, Any]) -> str | None:
                    key = (str(bm.get("title", "")), int(bm.get("page", 1)))
                    return title_page_to_doc.get(key)

                updated_bookmarks = _update_bookmarks_with_titles_generic(
                    bookmarks, titles_map, merged_resolver, opts.sort_bookmarks
                )
            else:
                # Create DocumentLink objects and resolver for single-file
                document_links = create_document_links(pre_id_df, bookmarks)
                title_to_doc_id = {
                    link.original_bookmark_title: link.document_id
                    for link in document_links
                }

                def single_resolver(bm: Mapping[str, Any]) -> str | None:
                    return title_to_doc_id.get(str(bm.get("title", "")))

                updated_bookmarks = _update_bookmarks_with_titles_generic(
                    bookmarks, titles_map, single_resolver, opts.sort_bookmarks
                )

            if opts.reorder_pages:
                if merged:
                    new_pages, new_bookmarks = _reorder_pages_merged(
                        df, titles_map, pages, bookmarks, merged_links
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


def _update_bookmarks_with_titles_generic(
    bookmarks: Sequence[Mapping[str, Any]],
    titles_map: Mapping[str, str],
    resolver: "callable",
    sort_naturally: bool,
):
    """Generic bookmark title update using a resolver to get Document_ID.

    resolver(bookmark_dict) -> str | None
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


def _reorder_pages_merged(
    df: pd.DataFrame,
    titles_map: Mapping[str, str],
    pages: Sequence[Any],
    bookmarks: Sequence[Mapping[str, Any]],
    links_with_offsets: Sequence[Tuple[DocumentLink, int]],
):
    """Return reordered pages and new bookmarks for merged flow.

    Uses synthetic unique bookmark keys ("title@@page") to compute ranges via
    detect_page_ranges, then maps DataFrame order to page ranges and titles.
    """
    if not bookmarks or not pages:
        return [], []
    # Build synthetic unique titles to safely use detect_page_ranges even when
    # bookmark titles repeat across merged inputs. Key format: "{title}@@{page}".
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
    df: pd.DataFrame,
    titles_map: Mapping[str, str],
    pages: Sequence[Any],
    bookmarks: Sequence[Mapping[str, Any]],
    total_pages: int,
    pre_id_df: pd.DataFrame,
    excel_path: str,
):
    """Return reordered pages and new bookmarks for single-file flow.

    Relies on detect_page_ranges and DocumentLink mapping to preserve
    associations from original bookmarks to new titles.
    """
    if not bookmarks or not pages or int(total_pages) <= 0:
        return [], []
    original_ranges_by_title = detect_page_ranges(bookmarks, total_pages)

    doc_id_to_original_title: dict[str, str] = {}
    doc_id_to_level: dict[str, int] = {}

    document_links = create_document_links(pre_id_df, bookmarks)
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
