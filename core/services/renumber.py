#!/usr/bin/env python3
"""
RenumberService: orchestrates Excel/PDF load, validate, transform, and save.
"""

from typing import Any, Mapping, Sequence

from core.interfaces import ExcelRepo, Logger, PdfRepo
from core.models import Options, Result
from core.services.validate import ValidationService
from core.transform.excel import (
    add_document_ids,
    clean_types,
    create_document_links,
    sort_and_renumber,
)
from core.transform.pdf import make_titles, extract_original_index, detect_page_ranges
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
            self._log.info("Loading Excel and PDF...")
            df = self._excel.load(excel_path, opts.sheet_name)
            bookmarks, total_pages = self._pdf.read(pdf_path)

            self._log.info("Validating inputs...")
            self._validator.run(df=df, bookmarks=bookmarks)

            self._log.info("Transforming Excel data...")
            df1 = clean_types(df)
            df2 = add_document_ids(df1, excel_path)
            df3 = sort_and_renumber(df2)

            self._log.info("Generating PDF bookmark titles...")
            titles_map = make_titles(df3)

            # Save Excel back into template (in-place responsibility left to caller via backups)
            self._log.info("Saving Excel output...")
            target_sheet = opts.sheet_name or "Index"
            self._excel.save(
                df3,
                template_path=excel_path,
                target_sheet=target_sheet,
                out_path=excel_path,
            )

            # Recreate PDF output with updated bookmarks (no reordering here)
            self._log.info("Saving PDF output...")
            pages = self._pdf.pages(pdf_path)
            # Create DocumentLink objects for bookmark title mapping
            document_links = create_document_links(df1, bookmarks, excel_path)

            updated_bookmarks = _merge_bookmarks_with_titles(
                bookmarks, titles_map, opts.sort_bookmarks, document_links
            )

            if opts.reorder_pages:

                # Build ranges from original bookmarks (keyed by original title)
                original_ranges_by_title = detect_page_ranges(bookmarks, total_pages)

                # Create mapping from Document_ID to original bookmark info using DocumentLinks
                doc_id_to_original_title: dict[str, str] = {}
                doc_id_to_level: dict[str, int] = {}

                for link in document_links:
                    doc_id_to_original_title[link.document_id] = (
                        link.original_bookmark_title
                    )
                    doc_id_to_level[link.document_id] = link.original_bookmark_level

                # Reorder pages by the new sequential Index# order (1, 2, 3...)
                new_pages: list[Any] = []
                new_bookmarks: list[dict[str, Any]] = []
                current_start_page = 1

                # Iterate through df3 in order (which is already sorted 1, 2, 3...)
                for _, row in df3.iterrows():
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

                    # Append page objects for this range (1-based to 0-based)
                    for p in range(start, end + 1):
                        if 1 <= p <= len(pages):
                            new_pages.append(pages[p - 1])

                    # Get new title from titles_map using Document_ID
                    new_title = titles_map.get(doc_id)
                    if new_title:
                        new_bookmarks.append(
                            {
                                "title": new_title,
                                "page": current_start_page,
                                "level": doc_id_to_level.get(doc_id, 0),
                            }
                        )
                    # Advance current_start_page by the length of this segment
                    current_start_page += max(0, end - start + 1)

                self._pdf.write(
                    pages=new_pages or pages,
                    bookmarks=new_bookmarks or updated_bookmarks,
                    out_path=pdf_path,
                )
            else:
                self._pdf.write(
                    pages=pages, bookmarks=updated_bookmarks, out_path=pdf_path
                )

            self._log.info("Complete.")
            return Result(success=True, message="OK")

        except Exception as exc:  # noqa: BLE001
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
