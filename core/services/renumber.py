#!/usr/bin/env python3
"""
RenumberService: orchestrates Excel/PDF load, validate, transform, and save.
"""

from typing import Any, Mapping, Sequence

import pandas as pd

from core.interfaces import ExcelRepo, Logger, PdfRepo
from core.models import Options, Result
from core.services.validate import ValidationService
from core.transform.excel import (
    clean_types,
    sort_and_renumber,
    build_original_index_mapping,
)
from core.transform.pdf import make_titles


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
            mapping = build_original_index_mapping(df2)

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
            self._pdf.write(pages=pages, bookmarks=updated_bookmarks, out_path=pdf_path)

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

    try:
        from natsort import natsorted, ns
    except Exception:
        natsorted = None  # type: ignore
        ns = None  # type: ignore

    updated = []
    for bm in bookmarks:
        title = str(bm.get("title", ""))
        original = title.split("-", 1)[0].strip() if "-" in title else None
        if original and original in titles_map:
            new_bm = dict(bm)
            new_bm["title"] = titles_map[original]
            updated.append(new_bm)
        else:
            updated.append(dict(bm))

    if sort_naturally and natsorted is not None and ns is not None:
        updated = natsorted(
            updated, key=lambda b: b.get("title", ""), alg=ns.IGNORECASE
        )

    return updated
