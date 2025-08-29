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

            if merged:
                self._log.info("Loading and validating multiple pairs for merge...")
                combined_pages: List[Any] = []
                combined_bookmarks: List[Mapping[str, Any]] = []
                combined_links: List[Tuple[DocumentLink, int]] = []
                df_parts: List[Any] = []
                page_offset = 0

                # Each pair: load → validate → clean → link → add IDs → accumulate
                # Prefer per-pair sheet if provided
                pairs_iter = []
                if opts.merge_pairs_with_sheets:
                    for (
                        excel_path_item,
                        pdf_path_item,
                        sheet_name_item,
                    ) in opts.merge_pairs_with_sheets:
                        pairs_iter.append(
                            (excel_path_item, pdf_path_item, sheet_name_item)
                        )
                else:
                    for excel_path_item, pdf_path_item in opts.merge_pairs or []:
                        pairs_iter.append(
                            (excel_path_item, pdf_path_item, opts.sheet_name)
                        )

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
                pages = list(self._pdf.pages(pdf_path))

                self._log.info("Validating inputs...")
                self._validator.run(df=df, bookmarks=bookmarks)

            self._log.info("Transforming Excel data...")
            # Clean
            df = clean_types(df)
            # Option-gated filter (keeps behavior identical when not set)
            if opts.filter_column and opts.filter_values:
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
                # Build resolver mapping for merged: (title, page) -> Document_ID
                title_page_to_doc: dict[Tuple[str, int], str] = {}
                for link, offset in combined_links:  # type: ignore[name-defined]
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
                document_links = create_document_links(pre_id_df, bookmarks, excel_path)
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
    document_links: Sequence[DocumentLink],
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
    links_with_offsets: Sequence[Tuple[DocumentLink, int]],
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
