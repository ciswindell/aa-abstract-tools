# Feature Specification: Bounded clear-loops in Excel save

**Feature Branch**: `009-excel-clear-fills-perf`
**Created**: May 14, 2026
**Status**: Implemented
**Input**: User report — "It gets stuck on step 5" on a specific Excel/PDF pair while working fine on others.

## Problem

`ExcelOpenpyxlRepo._write_dataframe_to_workbook` runs two clearing loops over `range(2, ws.max_row + 1)` and `ws.iter_rows(max_row=ws.max_row, max_col=ws.max_column)`. On templates whose used range reports phantom dimensions near Excel's hard limit (~1,048,576 rows), these loops iterate over tens of millions of cells. The pipeline's user-visible "Step 5 of 6: Saving outputs..." then appears to hang indefinitely (multi-hour projected runtime).

Diagnosis evidence:

- Triggered on `~/Downloads/test.{pdf,xlsx}` only. Other workbooks save in well under a second.
- `ws.max_row = 1,048,517`, `ws.max_column = 16` on the affected `Sheet` even though only 76 data rows exist. A single stray cell at row 1,048,517 col 13 (`value=None`, `has_style=True`) is enough for openpyxl to report the phantom max_row.
- 99% CPU during the hang; `SIGINT` produced a traceback pointing at `cell.fill = empty_fill` inside the fill-clearing loop (openpyxl `IndexedList.append` membership check).
- Probe: the existing approach projects to ≈25 000 s on this workbook; a bounded approach finishes in ≈1 s.

The user-visible "Step 5" is `SaveStep`, not `RebuildPdfStep`, because `FilterDfStep` is conditionally skipped when filtering is disabled — `context.step_number` is the position among non-skipped steps. This was an additional source of confusion during diagnosis.

## Behaviour to preserve

Both loops have a load-bearing role beyond performance:

1. **Value-clear (lines 159–164)** blanks template cells that fell outside the (possibly filtered) DataFrame. The filter pipeline produces a smaller `df_to_save` than the original template; the loop ensures dropped rows do not leak into the output.
2. **Fill-clear (lines 183–193)** removes background fills across the data area on output.

A correct fix must continue covering legitimate stale data rows in the template, not just the rows being written.

## Decision

Compute the real data extent of the loaded worksheet using openpyxl's populated-cell dictionary (`ws._cells`):

```python
data_col_indices = set(header_to_col.values())
real_max_row = max(
    (r for (r, c), cell in ws._cells.items()
     if c in data_col_indices and cell.value is not None),
    default=1,
)
clear_max_row = max(real_max_row, len(df) + 1)
```

This restricts the scan to data columns and to cells that actually carry a value, so a styled-but-empty phantom cell does not inflate the result. The cost is one pass over `ws._cells` (≤1 ms on the affected workbook). Both clearing loops use `clear_max_row` as the upper bound.

`max(real_max_row, len(df)+1)` covers both the filter case (`len(df) < real_max_row`, must clear stale rows) and the merge case (`len(df) > real_max_row`, must clear up through the new rows).

The fill-clear loop also bounds its column range to `max(header_to_col.values())`, the highest indexed header column. Cells outside the headers (e.g., the bookmark formula column on the right) are not in scope for this loop.

## Acceptance

Tests live in `tests/adapters/test_excel_repo_phantom_dimensions.py`:

1. `test_save_completes_quickly_on_workbook_with_phantom_dimensions` — synthetic template with `phantom_row=500_000`. Must complete in <5 s. Guarded by `SIGALRM(10)` so a regression fails fast.
2. `test_save_blanks_template_rows_beyond_smaller_dataframe` — template with 10 real rows, DataFrame with 4 rows. Asserts that output rows 2–5 contain new values and rows 6–11 are blank. Guards against a naïve `len(df)+1` bound regressing the filter path.

End-to-end verification on the reporting user's actual file pair: full pipeline runs to `RESULT success=True message=OK` in ~3 s; `SaveStep` finishes in ~1.1 s.

## Notes

- `ws._cells` is openpyxl's loaded-cell dictionary. It is not part of the public API but has been stable across the 3.x line. If a future openpyxl release removes it, both tests in this spec will fail loudly so the fix can be updated.
- This change does not touch `format_excel_step.py`, `atomic_save_with_backup`, or the PDF write path. Step 5 in the user's report has been disambiguated to `SaveStep`; no separate work is needed in `RebuildPdfStep`.
