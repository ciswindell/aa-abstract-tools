# PRD: Refactored Architecture (SOLID/DRY)

## Introduction/Overview
Refactor the codebase to improve SOLID and DRY compliance, simplify the architecture, and make the system easier to maintain and test. The refactor focuses on removing legacy duplication, clarifying responsibilities across layers (core/services, core/transform, adapters, app), consolidating configuration and validation, and enforcing consistent coding standards. No user-visible behavior should change.

## Goals
- Establish a clean layered architecture with clear boundaries.
- Remove legacy/duplicate modules and unused code.
- Centralize configuration and validation.
- Enforce top-level imports and PEP 8 compliance.
- Increase unit test coverage for pure transforms and validation.
- Keep the GUI behavior identical while relocating controller code.

## User Stories
- As a maintainer, I want a clear separation of concerns so I can reason about changes without unexpected side effects.
- As a developer, I want reusable pure transforms and IO adapters so I can test logic without file dependencies.
- As a contributor, I want consistent config and validation sources so I don’t duplicate rules across modules.
- As a reviewer, I want linted code and tests so I can quickly validate changes.

## Functional Requirements
1. Remove legacy processors (after replacement)
   1. Replace all runtime usages in `abstract_renumber.py` with `RenumberService`, `ValidationService`, and adapters (`ExcelOpenpyxlRepo`, `PdfPyPDF2Repo`, `TkLogger`).
   2. Remove imports, attributes, and code paths relying on `ExcelProcessor` and `PDFProcessor`.
   3. Verify no references remain (repo-wide search) and run tests.
   4. Delete `excel_processor.py` and `pdf_processor.py`.
2. Centralize configuration
   1. Create `core/config.py` and move constants there (e.g., `DEFAULT_REQUIRED_COLUMNS`, default sort order, default processing sheet name).
   2. Inject config into services/controllers (do not hardcode in UI files like `abstract_renumber.py`).
3. Single source of validation
   1. Keep `validators/input_sheet_validator.py` as the single source for header checks.
   2. `core/services/validate.ValidationService` composes validators and raises on failures.
   3. Remove any duplicated header/duplicate checks elsewhere.
4. Service orchestration cleanup (`core/services/renumber.py`)
   1. Move all imports to top level (no imports inside functions); `natsort` is a hard dependency.
   2. Reuse `core/transform/pdf.extract_original_index` in place of ad-hoc parsing in `_merge_bookmarks_with_titles`.
   3. Remove unused computations (e.g., drop `build_original_index_mapping(...)` if unused).
5. UI/controller relocation
   1. Add `app/` directory and move Tkinter controller code from `abstract_renumber.py` into `app/tk_app.py`.
   2. Keep `abstract_renumber.py` as a minimal entrypoint that wires UI and services.
   3. Preserve all existing GUI behavior and strings.
6. Adapters and transforms boundaries
   1. Keep adapters (`adapters/excel_repo.py`, `adapters/pdf_repo.py`, `adapters/logger_tk.py`) strictly IO/adaptation only (no business rules).
   2. Keep transforms in `core/transform/` pure and side-effect free.
   3. Ensure `adapters/excel_repo.py` continues to use `fileops/files.atomic_write_with_template` for atomic saves.
7. Dependencies and imports
   1. `natsort` remains a hard dependency (already in `requirements.txt`), imported at module top where used.
   2. Enforce “no imports inside functions” across the repo.
8. Testing
   1. Add `pytest` config and tests for `core/transform/excel.py` and `core/transform/pdf.py` covering typical and edge cases (including alphanumeric indices and missing fields).
   2. Add tests for `core/services/validate.py` (missing headers, duplicate required headers, bookmark page conflicts).
   3. Add a service-level test for `RenumberService` using stub Protocol implementations (fake repos/loggers) to validate orchestration without IO.
9. Linting/formatting (PEP 8)
   1. Add `ruff` (lint + format) to the toolchain and project scripts.
   2. Ensure the codebase passes lint and formatting with default PEP 8-aligned rules.
10. Dead code removal
   1. Remove unused functions, classes, and variables identified during refactor.
   2. Ensure no references remain; builds/tests must pass post-removal.
11. Documentation (minimal for this PRD)
   1. Do not update `README.md` in this effort.

## Non-Goals (Out of Scope)
- Implementing new end-user features (e.g., merging datasets, filtering, new GUIs).
- Changing user-facing behavior or GUI text/flows.
- Broad documentation updates beyond minimal code comments.

## Design Considerations (Optional)
- Architecture layers:
  - `core/` (interfaces, models, config, services, pure transforms)
  - `adapters/` (Excel/PDF IO, logger adapters)
  - `app/` (UI/controller wiring only; Tkinter moved here)
  - `validators/`, `utils/`, `fileops/` remain as shared modules
- Protocols in `core/interfaces.py` continue to isolate core from adapters.
- Exceptions surface from `ValidationService` are handled by the app/controller layer; services may still return `Result` on success.

## Technical Considerations (Optional)
- Python: 3.10.12.
- Dependencies: `pandas`, `PyPDF2`, `openpyxl`, `natsort` (hard dependency).
- Testing: `pytest` with isolated unit tests for pure functions; service tests with stubs.
- Linting: `ruff` for lint and formatting; enforce “imports only at module top”.

## Success Metrics
- All tests pass (CI) with new unit tests added; target ≥ 80% coverage for `core/transform/*` and `core/services/validate.py`.
- `ruff` passes with no errors; no function-level imports remain.
- No references to `excel_processor.py` or `pdf_processor.py` remain; imports resolve.
- Existing GUI behavior is preserved (manual smoke test confirmed).

## Open Questions
- Should we also add type checks (e.g., `mypy`) in this effort or leave for a separate task?
- Do we want to enable `pre-commit` hooks for `ruff` and tests, or keep these in CI only?
