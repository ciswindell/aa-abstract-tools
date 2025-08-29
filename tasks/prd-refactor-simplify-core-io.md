## Introduction / Overview

Internal refactor to simplify core I/O orchestration and reduce duplication while preserving existing behavior. The tool currently performs simple Excel/PDF renumbering but carries redundant loads, validations, and branching. This change streamlines responsibilities, applies DRY configuration, and clarifies control flow. There are no user‑visible behavior changes.

## Goals

- Eliminate duplicated I/O and validation between controller and service.
- Enforce that filter selection is UI‑only (no runtime fallback prompts).
- Disable backups when merging (inputs are never modified in merge).
- Keep merged outputs as `merged.xlsx` and `merged.pdf` in the same directory as inputs.
- Centralize default sort columns in `core.config` only; remove hardcoded lists in transforms.
- Reuse existing backup helpers in `fileops.files` and remove duplicates in controller.
- Reduce branching/duplication in `RenumberService.run` with small helpers.
- Keep a single source of truth for `Document_ID` generation.
- Maintain 100% functional parity (no user‑visible changes); all tests must pass.

## User Stories

- As a developer, I want the controller to delegate I/O to the service so there’s one place to reason about loading/validation.
- As a developer, I want default sort columns defined in one module so sorting behavior is consistent across the app and tests.
- As a developer, I want fewer branches in the service so changes are safer and easier to test.

## Functional Requirements

1) Controller delegates I/O and validation
   - Remove pre‑loading of Excel/PDF and calls to `ValidationService` in `core/app_controller.py`.
   - The controller gathers paths/options and calls the service; the service performs all loading and validation.

2) Filter selection is UI‑only
   - Remove/disable any runtime fallback prompting for filter values during processing.
   - If no filter chosen in the UI, processing proceeds unfiltered (no extra prompts).

3) Backups behavior on merge
   - When merging, backups are always disabled regardless of the checkbox (inputs are not modified).
   - Maintain current behavior for non‑merge runs (backups enabled if selected).

4) Output naming/location for merges
   - Keep `merged.xlsx` and `merged.pdf` filenames in the same directory as the selected inputs.

5) DRY default sorting
   - Move default column list to `core.config.DEFAULT_SORT_COLUMNS` (already present) and remove hardcoded defaults from `core/transform/excel.sort_and_renumber`.
   - `sort_and_renumber` must import and use `DEFAULT_SORT_COLUMNS` when `sort_columns` is not provided.

6) Reuse backup utilities
   - Replace `_generate_backup_filename` and `_create_backup_files` in `core/app_controller.py` with `fileops.files.generate_backup_filename` and `fileops.files.create_backups`.

7) Reduce duplication in `RenumberService`
   - Extract small helpers (module‑level functions) to unify the merged vs. single‑file paths:
     - Bookmark title update: extend the existing `_merge_bookmarks_with_titles` to support both single and merged flows (with optional (title,page) keying), or add a second small helper for the merged mapping. Keep imports at top level.
     - Page reordering: factor the two reorder blocks into one helper that accepts either bookmark ranges or link/index mapping.
   - Remove unused local helpers (e.g., `with_suffix`) if present.

8) Single source of truth for `Document_ID`
   - Ensure `add_document_ids` is called once per DataFrame before any bookmark title mapping.
   - Allow `create_document_links` to read existing `Document_ID` values if present; otherwise it may compute them as needed to preserve current tests and behavior.

9) Sheet selection
   - Keep the existing sheet‑name resolution flow and UI dialog behavior unchanged (no new UI). No additional runtime prompts beyond current sheet selection dialog.

## Non‑Goals (Out of Scope)

- No new UI elements, CLI flags, or behavior changes visible to users.
- No change to output formats/structures beyond the existing merged filenames.
- No change to validation rules or error messages beyond moving call sites.
- No performance guarantees beyond removing redundant I/O.

## Design Considerations

- Respect existing adapter boundaries (`ExcelRepo`, `PdfRepo`, `UIController`) and keep imports at top level.
- Maintain PEP 8 and current typing patterns; avoid future‑proofing methods that are not used.
- Prefer pure, small helpers in `core/services/renumber.py` to reduce duplication; keep logic readable and well‑named.
- Keep `DEFAULT_SORT_COLUMNS` as the only source of truth; transforms import from config.

## Technical Considerations

- Controller: remove duplicated load/validate logic; use `fileops.files.create_backups`.
- Transforms: `sort_and_renumber` imports `DEFAULT_SORT_COLUMNS` from `core.config`.
- Service: extract concise helpers for bookmark updates and page reordering; remove duplicate code paths.
- Tests: existing test suite must pass unchanged.

## Success Metrics / Acceptance Criteria

- All existing tests pass with no changes.
- No user‑visible behavior changes (manual smoke on typical flow and merge flow).
- `core/transform/excel.sort_and_renumber` no longer hardcodes default sort list.
- `core/app_controller.py` no longer loads/validates prior to calling the service.
- When `merge_pairs` is set, backups are disabled; outputs are `merged.xlsx`/`merged.pdf` in the input directory.
- Code health: reduced duplicated branches in `RenumberService.run` (measurable LOC reduction in the two large reorder/update blocks).

## Open Questions

- None at this time.


