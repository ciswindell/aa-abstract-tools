# Test Suite Cleanup: Stale Assertions and Structural Layout

**Feature Branch**: `011-fix-stale-tests`
**Created**: May 14, 2026
**Status**: Implemented
**Input**: All 23 pre-existing test failures plus 2 collection errors on `dev` and `main` made `pytest` permanently red. The 010 (GitHub Actions) work requires a green baseline.

## Findings

Three root causes — not a single bug:

### Structural (`tests/app/__init__.py` package collision)

Two test files (`tests/app/test_reset_button.py` and `tests/app/test_tk_app_document_found.py`) failed to collect with `ModuleNotFoundError: No module named 'app.tk_app'`. Other tests in the same directory worked fine.

Cause: `tests/app/__init__.py` existed (no other test subdirectory had one). With it present, pytest's `prepend` import mode added `tests/` to `sys.path` and treated `tests.app` as a package. `import app.tk_app` then resolved `app` to `tests/app/` — which has no `tk_app.py`. The collision was between the source package `app/` and the test package `tests/app/`.

Fix: delete `tests/app/__init__.py`. Tests in that directory now use the same rootdir-mode discovery as every other `tests/<subdir>/`.

### Intentional behavior change per spec `003-reduce-info-logging`

Spec 003 (Nov 19, 2025) explicitly removed ~90% of info-level logging — commit `d89d38c` deleted log lines like `"PDF saved: N pages, M bookmarks"`, `"Excel backup created: ..."`, `"Starting pipeline with N steps"`, source-breakdown logs, etc. The same commit also dropped the `simplify_error` user-friendly fallback wrapper (`"An error occurred: X. Please check..."` → return raw error string).

The unit tests in `validate_step_test.py`, `save_step_test.py`, `sort_df_step_test.py`, `pipeline_test.py`, and `test_feedback_display.py` still asserted on those removed messages. Treatment by test shape:

- **Pure-logging tests** (entire test exists to verify a logger call): deleted with a comment pointing to spec 003. Three were removed (`test_save_excel_output_source_breakdown_logging`, `test_save_pdf_output_statistics_logging`, `test_save_pdf_output_no_bookmarks`, `test_execute_with_source_column_logging`).
- **Behavior tests with log-assertion riders**: kept the behavior assertion, stripped just the trailing `assert_any_call` lines.
- **Error-message text changes** (3 cases): the production error text changed (lowercase → titlecase, "without corresponding" → "have no matching", and one case where production stopped wrapping inner exceptions per a deliberate code comment). Updated the assertion strings to match production.

### Tkinter wrapper-vs-string assertions

`ttk.Button.cget("state")` and `ttk.Label.cget("foreground")` return `Tcl_Obj`-like wrappers, not Python `str`. Three tests compared the result directly to a string literal and failed type-mismatch. Fixed by wrapping the `cget` result in `str()`.

The `test_tk_app_document_found.py` test also referenced a `TkinterApp` class that doesn't exist. The real class is `AbstractRenumberGUI` (`app/tk_app.py:22`). Renamed the import and constructor call; also changed `tk.Checkbutton`/`tk.Label` isinstance checks to `ttk.Checkbutton`/`ttk.Label` to match the production widgets.

## Decision principles

- **Audit before edit.** Initial instinct to blanket-update "stale strings" was wrong. The user pushed back, and the spec-003 commit history turned out to explain almost all failures as intentional removals, not regressions. The `simplify_error` case in particular was bundled into the same intentional cleanup, not a separate accidental drift.
- **Preserve coverage where it exists.** When a test mixed real behavior assertions with log assertions, only the log assertions were stripped — the behavior assertions kept providing regression protection.
- **Delete pure-logging tests outright.** A test whose entire purpose is verifying a logger call that no longer exists is dead weight; updating it would create a test for behavior that production deliberately doesn't have.
- **Don't restore removed production behavior.** Spec 003 was explicit and deliberate. The audit explicitly considered whether the `simplify_error` fallback dropoff was a regression (it makes unknown errors show raw Python text to users), but the call was to keep current production behavior and adjust the test, with a note that re-evaluating the UX is a separate product decision.

## Result

Pre-fix: 23 failed, 175 passed, 2 collection errors.
Post-fix: **213 passed, 0 failures, 0 collection errors.**

Eight test files modified, ~150 lines net removed, zero production code changes.

## What this unblocks

The 010 GitHub Actions work can now add a `pytest` CI step that's green from day 1, rather than needing pre-existing-failure exclusions.
