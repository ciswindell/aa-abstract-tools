#!/usr/bin/env python3
"""
RenumberService: orchestrates Excel/PDF load, validate, transform, and save.
"""

from typing import Any, Mapping, Sequence

from core.interfaces import ExcelRepo, Logger, PdfRepo
from core.models import Options, Result
from core.services.validate import ValidationService
from core.transform.excel import (
    clean_types,
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
            df2 = sort_and_renumber(df1)

            self._log.info("Generating PDF bookmark titles...")
            titles_map = make_titles(df2)

            # Save Excel back into template (in-place responsibility left to caller via backups)
            self._log.info("Saving Excel output...")
            target_sheet = opts.sheet_name or "Index"
            self._excel.save(
                df2,
                template_path=excel_path,
                target_sheet=target_sheet,
                out_path=excel_path,
            )

            # Recreate PDF output with updated bookmarks (no reordering here)
            self._log.info("Saving PDF output...")
            pages = self._pdf.pages(pdf_path)
            updated_bookmarks = _merge_bookmarks_with_titles(
                bookmarks, titles_map, opts.sort_bookmarks
            )

            if opts.reorder_pages:
                # Determine desired order by the DataFrame's Original_Index column
                desired_original_indices = [
                    str(x).strip() for x in df2.get("Original_Index", [])
                ]

                # Build ranges from original bookmarks (keyed by original title)
                original_ranges_by_title = detect_page_ranges(bookmarks, total_pages)
                # Map original index -> level and original title
                original_index_to_level: dict[str, int] = {}
                original_index_to_title: dict[str, str] = {}
                for bm in bookmarks:
                    orig_title = str(bm.get("title", ""))
                    orig_idx = extract_original_index(orig_title) or ""
                    if orig_idx:
                        original_index_to_level[orig_idx] = int(bm.get("level", 0))
                        original_index_to_title[orig_idx] = orig_title

                # Reorder physical pages by concatenating each bookmark's original page range
                new_pages: list[Any] = []
                new_bookmarks: list[dict[str, Any]] = []
                current_start_page = 1
                for orig_idx in desired_original_indices:
                    title_key = original_index_to_title.get(orig_idx)
                    if not title_key:
                        continue
                    rng = original_ranges_by_title.get(title_key)
                    if not rng:
                        continue
                    start, end = int(rng["start"]), int(rng["end"])
                    # Append page objects for this range (1-based to 0-based)
                    for p in range(start, end + 1):
                        if 1 <= p <= len(pages):
                            new_pages.append(pages[p - 1])

                    # Emit corresponding bookmark with updated title and new page start
                    new_title = titles_map.get(orig_idx)
                    if new_title:
                        new_bookmarks.append(
                            {
                                "title": new_title,
                                "page": current_start_page,
                                "level": original_index_to_level.get(orig_idx, 0),
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
):
    """Return updated bookmarks with new titles for those with mappable indices."""

    updated = []
    for bm in bookmarks:
        title = str(bm.get("title", ""))
        original = extract_original_index(title)
        if original and original in titles_map:
            new_bm = dict(bm)
            new_bm["title"] = titles_map[original]
            updated.append(new_bm)
        else:
            updated.append(dict(bm))

    if sort_naturally:
        updated = natsorted(
            updated, key=lambda b: b.get("title", ""), alg=ns.IGNORECASE
        )

    return updated
