## Relevant Files

- `core/services/renumber.py` - Main workflow; reorder functions and bookmark title update paths to unify/DRY.
- `core/transform/pdf.py` - `detect_page_ranges` used for centralized page-range logic; may add small helpers.
- `core/transform/excel.py` - `create_document_links` leveraged by unified linking path.
- `tests/core/services/renumber_merge_test.py` - Validates merge scenarios remain unchanged.
- `tests/core/services/test_renumber_service.py` - Validates single-file service behavior.
- `tests/core/transform/pdf_test.py` - Validates page-range detection and title generation behavior.
- `tests/integration_test_document_id.py` - Ensures Document_ID behavior remains unchanged.
- `tests/validation_test_document_id.py` - Guards against regressions in ID use paths.

### Notes

- Keep outputs identical (Excel and PDF). Do not modify expected values in tests; refactor only.
- Run tests with: `python3 -m pytest -q`.

## Tasks

- [x] 1.0 Centralize page-range computation across single and merged reorder paths
  - [x] 1.1 Update `_reorder_pages_single` to use `detect_page_ranges(bookmarks, total_pages)` exclusively.
  - [x] 1.2 Replace inline range logic in `_reorder_pages_merged` with `detect_page_ranges` (or delete if merged path is normalized under 3.0).
  - [x] 1.3 Add small guardrails for empty bookmarks/invalid pages while preserving behavior.
  - [x] 1.4 Add/adjust type hints and brief docstrings for readability (no functional change).
  - [x] 1.5 Run affected tests to confirm parity: `renumber_merge_test.py`, `pdf_test.py`.

- [x] 2.0 Unify bookmark title updates via a resolver-based mapping function
  - [x] 2.1 Introduce a private helper: `_update_bookmarks_with_titles(bookmarks, titles_map, resolver, sort_naturally)`.
  - [x] 2.2 Implement a resolver for single-file: map bookmark title → `Document_ID` via `DocumentLink`.
  - [x] 2.3 Implement a resolver for merged: map (title,page) → `Document_ID` with page offset awareness.
  - [x] 2.4 Replace `_merge_bookmarks_with_titles` and `_update_bookmarks_with_titles_merged` with the unified helper.
  - [x] 2.5 Ensure natural-sort option is preserved exactly (case-insensitive natsort).
  - [x] 2.6 Run service tests to confirm no title/output differences.

- [x] 3.0 Normalize merged processing to reuse the single-file linking pipeline
  - [x] 3.1 Combine and offset bookmarks/pages once; operate on this normalized set.
  - [ ] 3.2 Create `DocumentLink` objects from the normalized bookmarks and pre-ID DataFrame as in single-file flow.
  - [ ] 3.3 Reuse the single reorder path where possible; remove or minimize special merged-only branches.
  - [x] 3.4 Keep `Document_ID` generation and sort/renumber unchanged; verify outputs remain identical.
  - [x] 3.5 Validate with `renumber_merge_test.py` that behavior is unchanged.

- [x] 4.0 Preserve public interfaces and ensure 100% test parity (no output changes)
  - [x] 4.1 Avoid changing signatures of `ExcelRepo`, `PdfRepo`, `UIController`, and service APIs.
  - [x] 4.2 Run full test suite locally (`python3 -m pytest -q`) and ensure 100% pass with zero expected changes.
  - [x] 4.3 If needed, add narrowly scoped tests only to cover newly unified helpers without altering expectations.

- [x] 5.0 Update inline docs/type hints where touched to maintain clarity
  - [x] 5.1 Add precise types for tuples (e.g., `(DocumentLink, int)` for offset pairs if still used).
  - [x] 5.2 Add short docstrings for new helpers describing inputs/outputs and invariants.
  - [x] 5.3 Ensure imports stay at top level and code adheres to PEP 8.

### Decisions

- 3.2 and 3.3 cancelled: Creating links from fully merged bookmarks can misidentify cross-pair duplicate indices (validated only per pair), risking behavior change. Current merged resolvers preserve exact outputs without re-validating merged bookmarks.
