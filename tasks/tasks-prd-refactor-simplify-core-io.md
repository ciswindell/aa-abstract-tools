## Relevant Files

- `core/app_controller.py` - Remove duplicated load/validate; delegate I/O to service; use backup helpers; drop runtime filter prompt.
- `core/services/renumber.py` - Extract small helpers; unify merged/single flows; enforce single Document_ID pass; clean unused helpers.
- `core/transform/excel.py` - Import and use `core.config.DEFAULT_SORT_COLUMNS` when no sort is provided.
- `core/config.py` - Source of truth for `DEFAULT_SORT_COLUMNS`.
- `fileops/files.py` - Backup utilities to be used from controller.
- `adapters/ui_tkinter.py` - Ensure filter selection happens only via UI, no fallback prompts during processing (no behavior change expected).
- `tests/core/services/renumber_merge_test.py` - Validates merge flows; should pass unchanged.
- `tests/integration_test_document_id.py` - Validates end-to-end ID/sort/rename flow; should pass unchanged.
- `tests/core/transform/excel_test.py` - Validates transform behavior; should pass unchanged.

### Notes

- Run tests with: `python3 -m pytest -q` (or `pytest -q`).
- No user-visible behavior changes; all tests must pass unchanged.

## Tasks

- [x] 1.0 Streamline controller to delegate I/O and validation to service
  - [x] 1.1 Remove early Excel/PDF load and `ValidationService.run` calls from `core/app_controller.py`.
  - [x] 1.2 Keep only: path acquisition, options gathering, sheet resolution UI, backup toggle logic, and service invocation.
  - [x] 1.3 Replace `_generate_backup_filename` and `_create_backup_files` with `fileops.files.generate_backup_filename` / `create_backups`.
  - [x] 1.4 Remove runtime filter fallback prompt during processing; rely solely on UI state.

- [ ] 2.0 Centralize default sort columns in transforms via `core.config`
  - [x] 2.1 Import `DEFAULT_SORT_COLUMNS` in `core/transform/excel.sort_and_renumber`.
  - [x] 2.2 Use `DEFAULT_SORT_COLUMNS` when `sort_columns` is None; remove hardcoded list.
  - [x] 2.3 Ensure tests referencing sort behavior still pass.

- [ ] 3.0 Reduce duplication in `RenumberService` (helpers for titles/reorder)
  - [x] 3.1 Extract a helper to update bookmark titles from `titles_map` using `DocumentLink` mapping; support single and merged flows.
  - [x] 3.2 Extract a helper to reorder pages based on new Index# order for both single and merged flows.
  - [x] 3.3 Remove duplicated inline blocks and any unused local helpers (e.g., `with_suffix`).
  - [x] 3.4 Keep imports at top level; keep helpers small and readable.

- [ ] 4.0 Enforce merge semantics: no backups; outputs `merged.xlsx`/`merged.pdf` in input dir
  - [x] 4.1 Ensure controller forces `options.backup = False` when `merge_pairs` is present.
  - [x] 4.2 Confirm service writes outputs as `merged.xlsx` and `merged.pdf` alongside inputs for merge runs.
  - [x] 4.3 Confirm non-merge runs preserve current backup behavior.

- [ ] 5.0 Ensure single source of truth for `Document_ID` generation
  - [x] 5.1 Ensure `add_document_ids` is called once prior to any title mapping.
  - [x] 5.2 Allow `create_document_links` to use existing `Document_ID` if present; otherwise compute (maintain test parity).
  - [x] 5.3 Verify no duplicate hashing of the same row across flows.

- [ ] 6.0 Verify functional parity: run full test suite and smoke both single and merge flows
  - [x] 6.1 Run `pytest -q`; fix regressions while preserving behavior.
  - [ ] 6.2 Manual smoke: single-file flow end-to-end.
  - [ ] 6.3 Manual smoke: merge flow end-to-end with sorting and reorder toggles.


