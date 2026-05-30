# Unformatted Bookmarks Handling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let single-file processing offer (via a Yes/No prompt) to add Excel rows for PDF bookmarks that have no matching `Index#`, instead of erroring out.

**Architecture:** When `ValidateStep` finds orphaned bookmarks in single-file mode, it prompts the user through the existing UI. On Yes it records the orphaned titles on the pipeline context; `LoadStep` then appends a placeholder row per orphan and rewrites the bookmark title to `"<idx>-<title>"` so the existing linking/sort/rename flow handles it. Single pass; no sort changes; merge mode and headless runs keep the current error.

**Tech Stack:** Python 3.10, pandas, openpyxl, pypdf, pytest, ruff.

**Spec:** `docs/superpowers/specs/2026-05-29-unformatted-bookmarks-design.md`

---

## File Structure

| File | Responsibility | Change |
|------|----------------|--------|
| `core/pipeline/context.py` | Pipeline data carrier | Add `new_bookmark_titles` field |
| `core/transform/pdf.py` | Pure PDF/bookmark transforms | Add `add_rows_for_new_bookmarks` helper |
| `core/interfaces.py` | UI protocol | Add `prompt_add_new_bookmarks` |
| `adapters/ui_tkinter.py` | Tkinter UI | Implement `prompt_add_new_bookmarks` via `messagebox.askyesno` |
| `core/pipeline/steps/validate_step.py` | Input validation | Prompt instead of raise (single-file); record titles on Yes |
| `core/pipeline/steps/load_step.py` | Load + link | Inject rows via helper before linking |
| `tests/core/transform/pdf_new_bookmarks_test.py` | Unit test | New |
| `tests/core/pipeline/steps/validate_step_new_bookmarks_test.py` | Step test | New |
| `tests/integration/test_new_bookmarks_workflow.py` | Integration test | New |

---

## Task 1: Carry orphaned bookmark titles on the context

**Files:**
- Modify: `core/pipeline/context.py`

- [ ] **Step 1: Add the field**

In `core/pipeline/context.py`, inside the `PipelineContext` dataclass, add a new field directly after the existing `total_pages` field (currently line 41):

```python
    total_pages: int | None = None

    # New (orphaned) bookmark titles the user approved adding as Excel rows
    # (single-file mode only). None/empty means no new bookmarks to add.
    new_bookmark_titles: set[str] | None = None
```

- [ ] **Step 2: Verify it imports and constructs**

Run:
```bash
cd /home/chris/Code/aa-abstract-renumber && source .venv/bin/activate && \
python -c "from core.pipeline.context import PipelineContext; c=PipelineContext(file_pairs=[], options={}); print(c.new_bookmark_titles)"
```
Expected: prints `None`

- [ ] **Step 3: Commit**

```bash
git add core/pipeline/context.py
git commit -m "feat: add new_bookmark_titles to pipeline context (#2)"
```

---

## Task 2: Pure helper to inject rows and relabel bookmarks

**Files:**
- Create test: `tests/core/transform/pdf_new_bookmarks_test.py`
- Modify: `core/transform/pdf.py`

- [ ] **Step 1: Write the failing test**

Create `tests/core/transform/pdf_new_bookmarks_test.py`:

```python
#!/usr/bin/env python3
"""Tests for add_rows_for_new_bookmarks (issue #2)."""

import pandas as pd

from core.transform.pdf import add_rows_for_new_bookmarks


def _df():
    return pd.DataFrame(
        {
            "Index#": ["1", "2"],
            "Document Type": ["Deed", "Release"],
            "Received Date": ["2020-01-01", "2020-02-02"],
            "Legal Description": ["L1", "L2"],
        }
    )


def _bookmarks():
    return [
        {"title": "1-Deed-1/1/2020", "level": 0, "page": 1},
        {"title": "2-Release-2/2/2020", "level": 0, "page": 2},
        {"title": "Merger 2014", "level": 0, "page": 3},
    ]


def test_appends_row_and_relabels_bookmark():
    df, bookmarks = _df(), _bookmarks()
    new_df, new_bm = add_rows_for_new_bookmarks(df, bookmarks, {"Merger 2014"})

    # A row was appended for the orphan, with the next index.
    assert len(new_df) == 3
    row = new_df.iloc[-1]
    assert row["Index#"] == "3"
    assert row["Document Type"] == "Merger 2014"
    assert pd.isna(row["Received Date"])
    # Other (non-specified) columns are blank for the new row.
    assert pd.isna(row["Legal Description"])

    # Only the orphan bookmark is relabeled, in place/order.
    assert new_bm[0]["title"] == "1-Deed-1/1/2020"
    assert new_bm[1]["title"] == "2-Release-2/2/2020"
    assert new_bm[2]["title"] == "3-Merger 2014"

    # Inputs are not mutated.
    assert len(df) == 2
    assert bookmarks[2]["title"] == "Merger 2014"


def test_multiple_orphans_get_sequential_indices():
    df = pd.DataFrame({"Index#": ["5"], "Document Type": ["Deed"], "Received Date": ["x"]})
    bookmarks = [
        {"title": "5-Deed-1/1/2020", "level": 0, "page": 1},
        {"title": "Merger 2014", "level": 0, "page": 2},
        {"title": "Exhibit A", "level": 0, "page": 3},
    ]
    new_df, new_bm = add_rows_for_new_bookmarks(
        df, bookmarks, {"Merger 2014", "Exhibit A"}
    )
    assert list(new_df["Index#"]) == ["5", "6", "7"]
    assert new_bm[1]["title"] == "6-Merger 2014"
    assert new_bm[2]["title"] == "7-Exhibit A"


def test_no_matching_titles_returns_equivalent_data():
    df, bookmarks = _df(), _bookmarks()
    new_df, new_bm = add_rows_for_new_bookmarks(df, bookmarks, set())
    assert len(new_df) == 2
    assert [b["title"] for b in new_bm] == [b["title"] for b in bookmarks]
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
source .venv/bin/activate && pytest tests/core/transform/pdf_new_bookmarks_test.py -v
```
Expected: FAIL with `ImportError: cannot import name 'add_rows_for_new_bookmarks'`

- [ ] **Step 3: Implement the helper**

In `core/transform/pdf.py`, append this function at the end of the file (the module already imports `pandas as pd`, `Mapping`, and `Any`):

```python
def add_rows_for_new_bookmarks(
    df: pd.DataFrame,
    bookmarks: list[Mapping[str, Any]],
    new_bookmark_titles: set[str],
    index_col: str = "Index#",
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Append a placeholder Excel row for each approved new (orphaned) bookmark.

    For every bookmark whose title is in ``new_bookmark_titles``:
      * append a row to ``df`` with a unique ``Index#`` (max existing numeric
        index + 1, incrementing), ``Document Type`` set to the bookmark title,
        and a blank ``Received Date``; all other columns left blank.
      * rewrite the bookmark title to ``"<index>-<title>"`` so existing linking
        (``extract_original_index`` -> ``Index#`` match) connects it to the row.

    Returns a new (DataFrame, bookmarks) pair. Inputs are not mutated.
    """

    def _as_int(value: Any) -> int | None:
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return None

    existing = [
        n for n in (_as_int(v) for v in df.get(index_col, [])) if n is not None
    ]
    next_idx = (max(existing) + 1) if existing else 1

    new_rows: list[dict[str, Any]] = []
    new_bookmarks: list[dict[str, Any]] = []
    for bm in bookmarks:
        bm_copy = dict(bm)
        title = str(bm.get("title", ""))
        if title in new_bookmark_titles:
            bm_copy["title"] = f"{next_idx}-{title}"
            new_rows.append(
                {
                    index_col: str(next_idx),
                    "Document Type": title,
                    "Received Date": None,
                }
            )
            next_idx += 1
        new_bookmarks.append(bm_copy)

    if not new_rows:
        return df, new_bookmarks

    additions = pd.DataFrame(new_rows)
    new_df = pd.concat([df, additions], ignore_index=True)
    return new_df, new_bookmarks
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
source .venv/bin/activate && pytest tests/core/transform/pdf_new_bookmarks_test.py -v
```
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add core/transform/pdf.py tests/core/transform/pdf_new_bookmarks_test.py
git commit -m "feat: add_rows_for_new_bookmarks helper (#2)"
```

---

## Task 3: Add the prompt to the UI protocol and Tkinter adapter

**Files:**
- Modify: `core/interfaces.py:100-105`
- Modify: `adapters/ui_tkinter.py`

- [ ] **Step 1: Add the protocol method**

In `core/interfaces.py`, inside the `UIController` Protocol, append after `prompt_merge_pairs` (currently ends at line 104):

```python
    def prompt_add_new_bookmarks(self, bookmark_titles: list[str]) -> bool:
        """Ask whether to add new Excel rows for orphaned PDF bookmarks.

        Returns True if the user accepts (add the rows and continue), False to
        cancel (caller raises the standard orphaned-bookmark error).
        """
```

- [ ] **Step 2: Implement it in the Tkinter adapter**

In `adapters/ui_tkinter.py`, add this method to the UI controller class (place it next to the other `prompt_*` methods, e.g. after `prompt_merge_pairs`). `messagebox` is already imported at the top of the file:

```python
    def prompt_add_new_bookmarks(self, bookmark_titles: list[str]) -> bool:
        """Ask whether to add new Excel rows for orphaned PDF bookmarks."""
        preview = "\n".join(f"  • {t}" for t in bookmark_titles[:10])
        if len(bookmark_titles) > 10:
            preview += f"\n  (and {len(bookmark_titles) - 10} more)"
        message = (
            f"{len(bookmark_titles)} PDF bookmark(s) have no matching row in the "
            f"Excel file:\n{preview}\n\n"
            "Add them to the Excel file as new rows?\n\n"
            "⚠️ Caution: adding rows can create duplicate entries if the "
            "bookmarks were not properly labeled. Use with caution.\n\n"
            "Choosing No will cancel processing."
        )
        return bool(
            messagebox.askyesno("Add new bookmarks?", message, icon="warning")
        )
```

- [ ] **Step 3: Verify import/syntax**

Run:
```bash
source .venv/bin/activate && python -c "import adapters.ui_tkinter; import core.interfaces; print('ok')"
```
Expected: prints `ok`

- [ ] **Step 4: Commit**

```bash
git add core/interfaces.py adapters/ui_tkinter.py
git commit -m "feat: add prompt_add_new_bookmarks to UI (#2)"
```

---

## Task 4: ValidateStep prompts instead of erroring (single-file)

**Files:**
- Create test: `tests/core/pipeline/steps/validate_step_new_bookmarks_test.py`
- Modify: `core/pipeline/steps/validate_step.py:332-347`

- [ ] **Step 1: Write the failing test**

Create `tests/core/pipeline/steps/validate_step_new_bookmarks_test.py`:

```python
#!/usr/bin/env python3
"""ValidateStep behavior for orphaned bookmarks with the Yes/No prompt (#2)."""

import tempfile
from pathlib import Path

import pytest
from openpyxl import Workbook
from pypdf import PdfWriter

from adapters.excel_repo import ExcelOpenpyxlRepo
from adapters.pdf_repo import PypdfPdfRepo
from core.pipeline.context import PipelineContext
from core.pipeline.steps.validate_step import ValidateStep


class _Logger:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass


class _StubUI:
    """UI stub that records the prompt and returns a fixed answer."""

    def __init__(self, answer: bool):
        self.answer = answer
        self.asked_with: list[str] | None = None

    def prompt_add_new_bookmarks(self, bookmark_titles):
        self.asked_with = list(bookmark_titles)
        return self.answer


def _make_files(tmp: Path):
    xlsx = tmp / "in.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet"
    ws.append(
        ["Index#", "Document Type", "Received Date", "Legal Description",
         "Grantee", "Grantor", "Document Date"]
    )
    ws.append([1, "Deed", "2020-01-01", "L1", "A", "B", "2020-01-01"])
    ws.append([2, "Release", "2020-02-02", "L2", "C", "D", "2020-02-02"])
    wb.save(xlsx)

    pdf = tmp / "in.pdf"
    w = PdfWriter()
    for _ in range(3):
        w.add_blank_page(width=200, height=200)
    w.add_outline_item("1-Deed-1/1/2020", 0)
    w.add_outline_item("2-Release-2/2/2020", 1)
    w.add_outline_item("Merger 2014", 2)  # orphan
    with open(pdf, "wb") as fh:
        w.write(fh)
    return str(xlsx), str(pdf)


def _context(xlsx, pdf):
    return PipelineContext(
        file_pairs=[(xlsx, pdf, "Sheet")],
        options={"sheet_name": "Sheet", "backup": False},
    )


def test_yes_records_titles_and_does_not_raise():
    with tempfile.TemporaryDirectory() as d:
        xlsx, pdf = _make_files(Path(d))
        ctx = _context(xlsx, pdf)
        ui = _StubUI(answer=True)
        step = ValidateStep(ExcelOpenpyxlRepo(), PypdfPdfRepo(), _Logger(), ui)
        step.execute(ctx)
        assert ctx.new_bookmark_titles == {"Merger 2014"}
        assert ui.asked_with == ["Merger 2014"]


def test_no_raises_current_error():
    with tempfile.TemporaryDirectory() as d:
        xlsx, pdf = _make_files(Path(d))
        ctx = _context(xlsx, pdf)
        step = ValidateStep(ExcelOpenpyxlRepo(), PypdfPdfRepo(), _Logger(), _StubUI(False))
        with pytest.raises(ValueError, match="no matching Excel row"):
            step.execute(ctx)
        assert ctx.new_bookmark_titles is None


def test_no_ui_raises_current_error():
    with tempfile.TemporaryDirectory() as d:
        xlsx, pdf = _make_files(Path(d))
        ctx = _context(xlsx, pdf)
        step = ValidateStep(ExcelOpenpyxlRepo(), PypdfPdfRepo(), _Logger(), None)
        with pytest.raises(ValueError, match="no matching Excel row"):
            step.execute(ctx)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
source .venv/bin/activate && pytest tests/core/pipeline/steps/validate_step_new_bookmarks_test.py -v
```
Expected: `test_yes_records_titles_and_does_not_raise` FAILS (it currently raises ValueError); the two `*_raises_*` tests already pass.

- [ ] **Step 3: Modify the cross-reference check to prompt**

In `core/pipeline/steps/validate_step.py`, replace the orphaned-report block (currently lines 332-347, starting `# Report orphaned bookmarks` through the `raise ValueError(...)`) with:

```python
                # Report orphaned bookmarks (PDF bookmarks without Excel rows)
                if orphaned_bookmarks:
                    titles = [title for _, title in orphaned_bookmarks]

                    # Single-file mode with an interactive UI: offer to add rows.
                    if not context.is_merge_workflow() and hasattr(
                        self.ui, "prompt_add_new_bookmarks"
                    ):
                        if self.ui.prompt_add_new_bookmarks(titles):
                            existing = context.new_bookmark_titles or set()
                            context.new_bookmark_titles = existing | set(titles)
                            return

                    bullet_list = "\n".join(
                        f"  • '{idx}' — {title}"
                        for idx, title in orphaned_bookmarks[:10]
                    )
                    if len(orphaned_bookmarks) > 10:
                        bullet_list += f"\n  (and {len(orphaned_bookmarks) - 10} more)"

                    raise ValueError(
                        f"PDF File: '{pdf_filename}'\n"
                        f"Excel File: '{excel_filename}' (sheet '{sheet_name}')\n\n"
                        f"{len(orphaned_bookmarks)} PDF bookmark(s) have no matching Excel row:\n{bullet_list}\n\n"
                        f"Each PDF bookmark index must have a matching Index# value in the Excel sheet.\n"
                        f"Please add the missing rows or remove the orphaned bookmarks."
                    )
```

Note: `hasattr(self.ui, "prompt_add_new_bookmarks")` is `False` when `self.ui` is `None` or a UI without the method, so headless runs and merge mode keep the current error.

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
source .venv/bin/activate && pytest tests/core/pipeline/steps/validate_step_new_bookmarks_test.py -v
```
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add core/pipeline/steps/validate_step.py tests/core/pipeline/steps/validate_step_new_bookmarks_test.py
git commit -m "feat: prompt to add orphaned bookmarks in single-file validate (#2)"
```

---

## Task 5: LoadStep injects rows before linking

**Files:**
- Modify: `core/pipeline/steps/load_step.py` (imports, `execute` loop call, `_process_file_pair`)

- [ ] **Step 1: Add the import**

In `core/pipeline/steps/load_step.py`, add to the existing imports (after the `from core.transform.excel import add_document_ids` line, currently line 26):

```python
from core.transform.pdf import add_rows_for_new_bookmarks
```

- [ ] **Step 2: Pass the approved titles into `_process_file_pair`**

In `execute`, update the call (currently lines 72-78) to pass the titles:

```python
                    pair_units, pair_df, pages_added = self._process_file_pair(
                        excel_path,
                        pdf_path,
                        sheet_name,
                        current_page_offset,
                        merged_writer,
                        context.new_bookmark_titles,
                    )
```

- [ ] **Step 3: Update `_process_file_pair` signature**

Change the method signature (currently lines 140-147) to accept the titles:

```python
    def _process_file_pair(
        self,
        excel_path: str,
        pdf_path: str,
        sheet_name: str,
        page_offset: int,
        merged_writer: PdfWriter,
        new_bookmark_titles: set[str] | None = None,
    ) -> tuple[list[DocumentUnit], pd.DataFrame, int]:
```

- [ ] **Step 4: Reorder load/read and inject rows**

Replace the Excel-load + Document-ID block and the PDF-read block (currently lines 166-209) with the following. This loads Excel, reads the PDF, injects rows for approved orphans, then generates Document IDs:

```python
        try:
            # Load Excel file (Index# already cleaned to string by ExcelRepo.load)
            pair_df = self.excel_repo.load(excel_path, sheet_name)

            if pair_df.empty:
                self.logger.warning(f"Excel file is empty: {excel_path}")
                # Continue processing even with empty DataFrame
        except Exception as e:
            raise Exception(f"Failed to load Excel file {excel_path}: {e}") from e

        try:
            # Load PDF file
            pair_bookmarks, pair_total_pages = self.pdf_repo.read(pdf_path)

            if pair_total_pages <= 0:
                raise ValueError(f"PDF has no pages: {pdf_path}")
        except Exception as e:
            raise Exception(f"Failed to load PDF file {pdf_path}: {e}") from e

        # Inject placeholder rows for user-approved orphaned bookmarks, relabeling
        # each bookmark to "<index>-<title>" so normal linking picks it up.
        if new_bookmark_titles:
            pair_df, pair_bookmarks = add_rows_for_new_bookmarks(
                pair_df, pair_bookmarks, new_bookmark_titles
            )

        try:
            # Generate Document IDs from the (possibly augmented) DataFrame
            pair_df_with_ids = add_document_ids(pair_df, excel_path)
        except Exception as e:
            raise Exception(f"Failed to load Excel file {excel_path}: {e}") from e

        try:
            # Add all pages from this PDF to the merged writer
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            pages_added = 0
            for page in reader.pages:
                merged_writer.add_page(page)
                pages_added += 1

            if pages_added != pair_total_pages:
                self.logger.warning(
                    f"Page count mismatch in {pdf_path}: expected {pair_total_pages}, added {pages_added}"
                )
        except Exception as e:
            raise Exception(
                f"Failed to add pages from {pdf_path} to merged PDF: {e}"
            ) from e
```

- [ ] **Step 5: Run the existing LoadStep tests to confirm no regression**

Run:
```bash
source .venv/bin/activate && pytest tests/core/pipeline/steps/load_step_test.py -v
```
Expected: PASS (all existing load_step tests still pass)

- [ ] **Step 6: Commit**

```bash
git add core/pipeline/steps/load_step.py
git commit -m "feat: inject orphaned-bookmark rows in LoadStep (#2)"
```

---

## Task 6: End-to-end integration test (Validate → Load → naming)

**Files:**
- Create test: `tests/integration/test_new_bookmarks_workflow.py`

- [ ] **Step 1: Write the integration test**

Create `tests/integration/test_new_bookmarks_workflow.py`:

```python
#!/usr/bin/env python3
"""End-to-end: approving new bookmarks adds a linked, correctly-named row (#2)."""

import tempfile
from pathlib import Path

from openpyxl import Workbook
from pypdf import PdfWriter

from adapters.excel_repo import ExcelOpenpyxlRepo
from adapters.pdf_repo import PypdfPdfRepo
from core.pipeline.context import PipelineContext
from core.pipeline.steps.load_step import LoadStep
from core.pipeline.steps.validate_step import ValidateStep
from core.transform.pdf import make_titles


class _Logger:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass


class _YesUI:
    def prompt_add_new_bookmarks(self, bookmark_titles):
        return True


def _make_files(tmp: Path):
    xlsx = tmp / "in.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet"
    ws.append(
        ["Index#", "Document Type", "Received Date", "Legal Description",
         "Grantee", "Grantor", "Document Date"]
    )
    ws.append([1, "Deed", "2020-01-01", "L1", "A", "B", "2020-01-01"])
    ws.append([2, "Release", "2020-02-02", "L2", "C", "D", "2020-02-02"])
    wb.save(xlsx)

    pdf = tmp / "in.pdf"
    w = PdfWriter()
    for _ in range(3):
        w.add_blank_page(width=200, height=200)
    w.add_outline_item("1-Deed-1/1/2020", 0)
    w.add_outline_item("2-Release-2/2/2020", 1)
    w.add_outline_item("Merger 2014", 2)  # orphan
    with open(pdf, "wb") as fh:
        w.write(fh)
    return str(xlsx), str(pdf)


def test_approved_new_bookmark_is_added_linked_and_named():
    excel_repo, pdf_repo, logger = ExcelOpenpyxlRepo(), PypdfPdfRepo(), _Logger()
    with tempfile.TemporaryDirectory() as d:
        xlsx, pdf = _make_files(Path(d))
        ctx = PipelineContext(
            file_pairs=[(xlsx, pdf, "Sheet")],
            options={"sheet_name": "Sheet", "backup": False},
        )

        ValidateStep(excel_repo, pdf_repo, logger, _YesUI()).execute(ctx)
        assert ctx.new_bookmark_titles == {"Merger 2014"}

        LoadStep(excel_repo, pdf_repo, logger, None).execute(ctx)

        # The new row exists with the bookmark name as Document Type.
        merger_rows = ctx.df[ctx.df["Document Type"] == "Merger 2014"]
        assert len(merger_rows) == 1

        # All three bookmarks now link to rows (the orphan is no longer skipped).
        assert len(ctx.document_units) == 3

        # The bookmark name follows the convention with N/A for the blank date.
        titles = make_titles(ctx.df)
        new_doc_id = str(merger_rows.iloc[0]["Document_ID"])
        assert titles[new_doc_id] == "3-Merger 2014-N/A"
```

- [ ] **Step 2: Run the integration test**

Run:
```bash
source .venv/bin/activate && pytest tests/integration/test_new_bookmarks_workflow.py -v
```
Expected: PASS (1 passed)

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_new_bookmarks_workflow.py
git commit -m "test: end-to-end new-bookmark add workflow (#2)"
```

---

## Task 7: Full suite + lint, then verify nothing regressed

**Files:** none (verification only)

- [ ] **Step 1: Run the full test suite**

Run:
```bash
source .venv/bin/activate && pytest -q
```
Expected: all tests pass (previous total 218 + the new tests from this plan).

- [ ] **Step 2: Run ruff check and format check**

Run:
```bash
source .venv/bin/activate && ruff check . && ruff format --check .
```
Expected: `All checks passed!` and no files needing reformat. If `ruff format --check` reports files, run `ruff format <files>`, then re-run this step, then `git add` + commit with `style: apply ruff format (#2)`.

- [ ] **Step 3: Final confirmation commit (only if formatting changed)**

```bash
git add -A && git commit -m "style: ruff format for unformatted-bookmarks feature (#2)"
```

---

## Self-Review notes (filled during planning)

- **Spec coverage:** detection via existing cross-reference (Task 4); single-file-only gating via `is_merge_workflow()` (Task 4); Yes/No prompt with caution text (Tasks 3–4); No → current error (Task 4); row fields Index#/Document Type/blank date (Task 2); relabel-to-link (Task 2/5); `N/A` naming via existing `make_titles` (Task 6 assertion); sort untouched (no task modifies sort); headless/merge keep current error (Task 4 tests). All covered.
- **Type consistency:** `new_bookmark_titles: set[str] | None` used identically in context (Task 1), validate (Task 4), load (Task 5), helper arg (Task 2). `add_rows_for_new_bookmarks(df, bookmarks, set[str], index_col="Index#") -> (df, list[dict])` consistent across Tasks 2 and 5. `prompt_add_new_bookmarks(list[str]) -> bool` consistent across Tasks 3 and 4.
- **Placeholders:** none — every code step contains full code.
