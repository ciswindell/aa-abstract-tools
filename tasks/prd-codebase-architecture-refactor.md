# Codebase Architecture Refactor PRD

## Introduction/Overview
Refactor the current Abstract Renumber Tool codebase to follow SOLID/DRY principles and a modular, layered architecture. The goal is to decouple UI (Tkinter) from core logic, separate IO from pure transformations, centralize validations, and organize modules for clarity and future extensibility. After refactor, the tool must behave exactly the same from the user’s perspective (no feature changes), while preparing the codebase for future features such as merging Excel/PDF sources and alternative UIs (Streamlit/Django).

## Goals
- Maintain identical user-facing behavior with the existing Tkinter GUI.
- Decouple UI from business logic via a single application service entrypoint.
- Separate IO adapters (PyPDF2/openpyxl/pandas) from pure data transforms.
- Centralize validation into a composable validation pipeline.
- Remove duplication (column letter conversion, date formatting, etc.).
- Introduce thin, explicit interfaces (Protocols) and small domain models.
- Improve testability; add unit tests for pure transforms and validators.
- Organize files into a clear package layout to aid junior developer maintenance.

## User Stories
- As a user, I can run the Tkinter app and get the exact same results before and after the refactor.
- As a junior developer, I can read the codebase and quickly find where to change validation rules without touching UI or IO code.
- As a junior developer, I can add a new UI (e.g., Streamlit) by wiring it to the application service without changing core logic.
- As a junior developer, I can write unit tests for transforms without needing real PDFs or Excel files.
- As a junior developer, I can later implement “merge Excel and PDF then renumber” by extending a dedicated service rather than modifying the UI.

## Functional Requirements
1. Retain Tkinter UI functionality and behavior with no user-visible changes.
2. Introduce a single application orchestration service `RenumberService` that:
   1. Accepts paths (Excel/PDF) and an `Options` dataclass.
   2. Invokes validations and pure transforms, then delegates to adapters for IO and formatting.
   3. Emits logs via a `Logger` interface (no direct UI calls).
3. Define Protocol-based interfaces in `core/interfaces.py`:
   1. `ExcelRepo`: load DataFrame from Excel (sheet optional), save DataFrame into an existing workbook/template and sheet.
   2. `PdfRepo`: read bookmarks and page count, write pages and bookmarks.
   3. `Logger`: minimal `info` and `error` methods decoupled from UI.
4. Split Excel logic:
   1. `adapters/excel_repo.py`: IO only (pandas + openpyxl + `ExcelFormatter`).
   2. `core/transform/excel.py`: pure transforms (type cleaning, sort order, renumbering, original index mapping).
5. Split PDF logic:
   1. `adapters/pdf_repo.py`: IO only (PyPDF2 outline extraction, page copying, writing, page mode).
   2. `core/transform/pdf.py`: pure bookmark transforms (title generation, natural sort, page range detection).
6. Centralize validations in `core/services/validate.py` composing:
   1. Excel required headers (case-insensitive) and required-duplicate detection: hard errors.
   2. PDF bookmark page conflicts: hard errors.
7. Extract file operations into `io/files.py`:
   1. Optional timestamped backups for Excel and PDF.
   2. Atomic Excel save pattern (temp file → replace) reused by the Excel adapter.
8. DRY utilities:
   1. `utils/excel_utils.py`: index↔letter conversion used everywhere (no duplicate implementations).
   2. `utils/dates.py`: robust date parse/format helpers used by transforms and title formatting.
9. Keep `excel_formatter.py` strictly formatting-only; use `excel_utils` for column letter logic; do not mutate DataFrame.
10. `abstract_renumber.py` becomes a thin Tkinter adapter:
    1. Builds `Options` from UI state.
    2. Invokes `RenumberService.run(...)` and handles exceptions and dialogs.
    3. Uses a `Logger` adapter to forward service logs into the UI.
11. Preserve current sorting, renumbering, bookmark update logic, output paths, and backup semantics—results must remain identical.
12. Add unit tests (pytest) for pure modules (`core/transform/*`, `core/services/validate.py`) and basic adapter smoke tests.

## Non-Goals (Out of Scope)
- Implementing the Excel/PDF merge feature or page reordering strategy changes beyond current behavior.
- Replacing Tkinter with Streamlit/Django now (the architecture should enable it later).
- Changing file formats, inputs, or outputs beyond refactoring internals.
- Introducing a CLI or migration guide at this stage.

## Design Considerations (Optional)
- Architecture: hexagonal/clean layering with `core` (pure, testable) at the center, `adapters` for IO, `ui` for presentation, and `io/utils` for cross-cutting helpers.
- Dependency direction: UI and adapters depend on `core` interfaces; `core` does not import UI/adapters.
- Small domain models (`Record`, `Bookmark`, `Options`) and constrained interfaces to clarify APIs for junior developers.
- Keep exception types domain-specific to simplify UI error handling and testing.

## Technical Considerations (Optional)
- Language & style: Python 3, PEP 8, type hints for public APIs, minimal methods and no future placeholders. No imports outside of toplevel. Docstrings everywhere.
- Dependencies: continue using pandas, openpyxl, PyPDF2, natsort; no new heavy dependencies.
- Testing: pytest, focus on unit tests for transforms/validators; light adapter smoke tests; fixture files minimal.
- Performance: unchanged; transforms operate on DataFrames in-memory as today.
- Atomic file operations for Excel writes are preserved; backups use timestamped filenames.

## Success Metrics
- Functional parity: End-to-end runs produce the same Excel and PDF outputs as before (golden test on sample fixtures).
- Test coverage: ≥ 80% on `core/transform/*` and `core/services/validate.py`.
- Modularity: No UI imports in `core`; no duplication of column/date helpers across modules.
- Maintainability: New developer can locate validation logic and transform code within minutes (directory clarity, short files).
- Stability: All existing tests (and new unit tests) pass; manual smoke test with current UI succeeds.

## Open Questions
- Final names for domain exceptions (e.g., `ValidationError`, `BookmarkConflictError`)—align with existing error messages.
- Minimum set of golden fixtures to assert parity (sample Excel/PDF pairs to snapshot outputs).
