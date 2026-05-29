# Unformatted Bookmarks Handling — Design

**Issue:** #2 (Unformatted Bookmarks Handling)
**Date:** 2026-05-29
**Status:** Approved (pending spec review)

## Problem

When a PDF bookmark has no matching `Index#` row in the Excel sheet (an
"orphaned" bookmark — e.g. a generically named `"Merger 2014"`), the tool
**errors out and refuses to continue**. The error is raised in
`ValidateStep._validate_pdf_excel_cross_reference`:

```
N PDF bookmark(s) have no matching Excel row:
  • 'Merger 2014' — Merger 2014
Each PDF bookmark index must have a matching Index# value in the Excel sheet.
Please add the missing rows or remove the orphaned bookmarks.
```

The user must manually add rows to the Excel file before processing can
proceed. This feature lets the tool offer to add those rows automatically.

> Note on detection: an "orphaned/new" bookmark is defined as **any bookmark
> whose leading index token does not match an existing `Index#` value** in the
> sheet. This reuses the existing cross-reference check and covers both
> non-numeric names (`"Merger 2014"`) and numeric-but-missing indices
> (`"99-Foo"` when no row 99 exists).

## Scope

- **In scope:** single-file processing mode.
- **Out of scope:** multi-file merge mode. In merge mode the current
  error-out behavior is preserved unchanged and no prompt is shown.

## User experience

No new checkbox on the main GUI. The decision is made in the **existing error
dialog**, converted to a Yes/No prompt that includes a caution:

> *"These N PDF bookmark(s) have no matching row in the Excel file: … Add them
> to the Excel file as new rows?*
> *⚠️ Caution: adding rows can create duplicate entries if the bookmarks were
> not properly labeled. Use with caution.*
> *Choosing No will cancel processing."*

- **Yes** → add the rows and continue processing normally.
- **No** → raise the current error and abort (unchanged behavior).

The caution text is part of the prompt itself, so the user sees the warning
before choosing Yes.

When there is no interactive UI (headless runs, tests), the tool raises the
current error — existing behavior and tests are unchanged.

## Behavior of an added row

For each orphaned bookmark, one Excel row is appended:

| Column        | Value                                              |
|---------------|----------------------------------------------------|
| `Index#`      | Temporary placeholder = max numeric `Index#` + 1, incrementing per orphan (rows are renumbered after sorting anyway) |
| `Document Type` | The original bookmark title verbatim (e.g. `Merger 2014`) |
| `Received Date` | Blank                                            |
| all other columns | Blank                                          |

The bookmark's in-memory title is rewritten from `"<title>"` to
`"<next_idx>-<title>"` so the existing linking step
(`extract_original_index` → `Index#` match) connects the bookmark to the new
row.

After linking, processing continues unchanged:
- The row links to real PDF pages, so `Document_Found` resolves to `Yes`.
- Sorting / renumbering assigns the final `Index#`.
- `make_titles` regenerates the bookmark name as `"<final_idx>-<title>-N/A"`
  (blank `Received Date` already renders as `N/A` via `format_mdy`).

### Sorting is NOT modified

Sort behavior must not change in any way. New rows flow through the existing
sort exactly as current rows do. Their final position in the output is
whatever the current sort produces (in practice, near the top because their
sort-key columns are blank). No sort code is touched and no special-case
ordering is added for these rows.

### `Orphan` marker column

So the user can review which rows the tool auto-created (the caution warns
they may be duplicates), an `Orphan` column is written **only when orphans are
added in this run**.

- **Name:** `Orphan`. **Values:** `Yes` on each auto-added row, `No` on every
  other row (matching the existing `Document_Found` Yes/No convention).
- **Placement:** appended at the end of the sheet on the first run that adds
  orphans (via the writer's add-missing-columns path). On later runs the
  column already exists and is matched case/whitespace-tolerantly and
  overwritten in place — no duplicate column is created.
- **Overwrite reflects the current run:** every row is (re)written, so a row
  that was auto-added in a previous run but is a normal matched row this run
  shows `No`; only this run's additions show `Yes`. This overwrites any values
  loaded from a prior run.
- **No-orphan runs leave it untouched:** if this run adds no orphans, nothing
  sets the column. A pre-existing `Orphan` column in the input is read by
  `excel_repo.load` and round-tripped back to the output unchanged; if no such
  column exists, none is created.

Implementation: the row-injection helper sets `Orphan` (`No` for existing
rows, `Yes` for added rows) only when it runs; `SaveStep` enables
add-missing-columns when `context.new_bookmark_titles` is set so the new
column is written in single-file mode.

## Architecture & data flow

Single pass (no pipeline re-run), following the existing mid-pipeline UI
prompt pattern already used by `FilterDfStep`.

```
ValidateStep._validate_pdf_excel_cross_reference
    if orphans found:
        if merge workflow            -> raise (current error)         [out of scope]
        elif interactive UI present  -> ui.prompt_add_new_bookmarks(orphans)
                Yes -> context.new_bookmark_titles = {orphan titles}; continue
                No  -> raise (current error)
        else (no UI)                 -> raise (current error)

LoadStep._process_file_pair   (only when context.new_bookmark_titles is set)
    next_idx = max(numeric Index# in pair_df) + 1
    for each orphan bookmark in document order:
        append row {Index#: next_idx, Document Type: title, Received Date: blank, ...}
        rewrite bookmark title "<title>" -> "<next_idx>-<title>"
        next_idx += 1
    -> add_document_ids -> link_bookmarks_to_excel_rows -> (sort/renumber/rename unchanged)
```

## Components / files

| File | Change |
|------|--------|
| `core/interfaces.py` | Add `prompt_add_new_bookmarks(orphans) -> bool` to the `UIController` protocol |
| `adapters/ui_tkinter.py` | Implement the prompt via `messagebox.askyesno` |
| `core/pipeline/context.py` | Add field to carry orphaned bookmark titles (e.g. `new_bookmark_titles: set[str]`) |
| `core/pipeline/steps/validate_step.py` | In single-file mode with a UI, prompt instead of raising; record titles on Yes |
| `core/pipeline/steps/load_step.py` | When titles are recorded, inject rows + rewrite bookmark titles before linking |
| `core/transform/` (helper) | Small pure helper for row injection + title rewrite, to keep `LoadStep` lean and unit-testable |

## Edge cases

- **Multiple orphans:** handled in document order, each gets the next index.
- **Non-numeric existing `Index#` values:** ignored when computing the max;
  placeholder only needs to be unique and link the bookmark, since the final
  number comes from renumbering.
- **Merge mode:** prompt is never shown; current error preserved.
- **Headless / `None` UI:** current error preserved.
- **Bookmark title containing dashes** (e.g. `"Merger - 2014"`): becomes the
  `Document Type` verbatim; only the prepended index is used for linking
  (`extract_original_index` splits on the first dash), so linking is unaffected.

## Testing

- **Unit:** the row-injection helper — given a DataFrame and orphan titles,
  returns the DataFrame with correctly appended rows and the bookmark list
  with rewritten titles.
- **Integration (single-file):**
  - Stub UI returns **Yes** → output Excel contains the new row (Document Type
    = bookmark name, blank Received Date), output PDF bookmark named
    `"<n>-<name>-N/A"`, and the row is renumbered through the normal flow.
  - Stub UI returns **No** → raises the current orphaned-bookmark error.
- **Regression:**
  - Merge mode with an orphan still raises (no prompt).
  - Headless / `None` UI still raises.
  - Existing pipeline/validate tests remain green (no behavior change when no
    orphans are present).
