## Relevant Files

- `core/app_controller.py` - Replace getattr-based `Options` access with direct fields; keep existing sheet resolution flow; ensure `merge_pairs_with_sheets` is set from controller.
- `core/services/renumber.py` - Prefer `merge_pairs_with_sheets`, fallback to `merge_pairs`; replace getattr-based `Options` access; simplify branching in `run` without behavior changes.
- `adapters/pdf_repo.py` - Tolerant outline retrieval (`outlines` vs `outline`) without changing PyPDF2 version; narrowed exception handling.
- `core/interfaces.py` - Verify Protocol contracts remain unchanged.
- `adapters/ui_tkinter.py` and `app/tk_app.py` - Sanity-check no changes needed; ensure `Options` construction unaffected.
- `tests/core/services/test_renumber_service.py` - Service behavior validation.
- `tests/core/services/renumber_merge_test.py` - Merge flow validation.
- `tests/core/services/validate_test.py` - Validation behavior remains unchanged.
- `tests/integration_test_document_id.py` - End-to-end IDs unchanged.
- `tests/test_excel_template_flow.py` - Excel write path remains unchanged.

### Notes

- Run tests with `python3 -m pytest -q` from the repo root.
- You can run a specific test file with `python3 -m pytest -q tests/path/to/test_file.py`.
- No public interfaces or user-visible behavior may change; all existing tests must pass unchanged.

## Tasks

- [x] 1.0 Replace getattr-based `Options` access with direct fields in controller and service
  - [x] 1.1 In `core/app_controller.py`, replace `getattr(options, ...)` checks with direct access (e.g., `if options.merge_pairs:`; `if options.filter_enabled and not options.filter_values:`). Preserve current logic.
  - [x] 1.2 In `core/services/renumber.py`, replace `getattr(opts, ...)` for `merge_pairs`, `merge_pairs_with_sheets`, `filter_column`, and `filter_values` with direct access while preserving truthiness behavior.
  - [x] 1.3 Run `python3 -m pytest -q` to confirm no regressions.

- [x] 2.0 Normalize merge handling to prefer `merge_pairs_with_sheets` with fallback
  - [x] 2.1 In `core/services/renumber.py`, build `pairs_iter` by preferring `opts.merge_pairs_with_sheets` when present.
  - [x] 2.2 Fallback: when only `opts.merge_pairs` exists, pair each with `opts.sheet_name` (current behavior). Do not resolve sheet names in the service.
  - [x] 2.3 Verify controller already sets `options.merge_pairs_with_sheets`; no duplicate logic in the service.
  - [x] 2.4 Run merge-related tests: `python3 -m pytest -q tests/core/services/renumber_merge_test.py`.

- [x] 3.0 Simplify `RenumberService.run` branching (readability only)
  - [x] 3.1 Reduce nested branching by using early local variables and straightforward conditionals; keep the method signature and public surface unchanged.
  - [x] 3.2 Avoid introducing new public methods; keep logic in-function per PRD (small cleanups only).
  - [x] 3.3 Re-run the full test suite.
  - [x] 3.4 Deduplicate PDF reading in single-file path by caching pages once and reusing.

- [x] 4.0 Make `PdfPyPDF2Repo.read` tolerant to outline attribute variants
  - [x] 4.1 Try `getattr(reader, "outlines", None)` first; fallback to `getattr(reader, "outline", None)`; if falsy, return `([], page_count)`.
  - [x] 4.2 Keep `_parse_outline` usage and flat bookmark contract unchanged.
  - [x] 4.3 Run PDF-related tests: `python3 -m pytest -q tests/adapters/pdf_repo_smoke_test.py` and full suite.

- [x] 5.0 Validate unchanged behavior and interfaces
  - [x] 5.1 Run `python3 -m pytest -q` and ensure all tests pass without modification.
  - [x] 5.2 Fix any linter issues introduced; do not change external behavior or public APIs.
  - [x] 5.3 Sanity-check sample flow manually if desired (no code changes required).
