## Relevant Files

- `tasks/prd-codebase-architecture-refactor.md` - PRD (source) for SOLID/DRY refactor; all tasks trace to this.
- `abstract_renumber.py` - Current Tkinter UI and orchestration, to be thinned to a UI adapter.
- `core/` - New core package (pure logic, models, interfaces, services, transforms).
- `core/interfaces.py` - Protocols for Excel/PDF repositories and Logger.
- `core/models.py` - Dataclasses (Options, Result, Bookmark, PageRange, Record).
- `core/services/validate.py` - ValidationService composing Excel/PDF validators.
- `core/services/renumber.py` - RenumberService orchestrating load/validate/transform/save.
- `core/transform/excel.py` - Pure DataFrame transforms (clean, sort, renumber, mapping).
- `core/transform/pdf.py` - Pure bookmark/title transforms and page range detection.
- `adapters/` - New adapters package (IO implementations for Excel/PDF).
- `adapters/excel_repo.py` - Excel IO adapter using pandas/openpyxl and ExcelFormatter.
- `adapters/pdf_repo.py` - PDF IO adapter using PyPDF2.
- `adapters/logger_tk.py` - Logger adapter that writes to Tkinter status area.
- `utils/` - New utilities package (shared helpers).
- `utils/excel_utils.py` - Column index/letter helpers (single source of truth).
- `utils/dates.py` - Robust date parse/format helpers.
- `io/` - New IO helpers package.
- `io/files.py` - Backups and atomic save helpers.
- `excel_formatter.py` - Formatting-only; updated to use `utils/excel_utils`.
- `validators/input_sheet_validator.py` - Excel header/duplicate validation.
- `pdf_validator.py` - PDF bookmark conflict validation.
- `tests/core/transform/excel_test.py` - Unit tests for Excel transforms.
- `tests/core/transform/pdf_test.py` - Unit tests for PDF transforms.
- `tests/core/services/validate_test.py` - Unit tests for ValidationService.
- `tests/utils/excel_utils_test.py` - Unit tests for Excel utilities.
- `tests/utils/dates_test.py` - Unit tests for date helpers.
- `tests/io/files_test.py` - Unit tests for backup/atomic save helpers.
- `tests/adapters/excel_repo_smoke_test.py` - Smoke tests for Excel adapter with fixtures.
- `tests/adapters/pdf_repo_smoke_test.py` - Smoke tests for PDF adapter with fixtures.

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `module.py` and `module_test.py`).
- Use `pytest` to run tests. Running without a path executes all tests found by the pytest configuration.

## Tasks

- [ ] 1.0 Establish core architecture and interfaces (Protocols, models)
  - [x] 1.1 Create package layout: `core/`, `adapters/`, `utils/`, `io/` (and keep Tkinter UI).
  - [x] 1.2 Add `core/interfaces.py` with Protocols: `ExcelRepo`, `PdfRepo`, `Logger`.
  - [x] 1.3 Add `core/models.py` with `Options`, `Result`, `Bookmark`, `PageRange`, `Record` dataclasses.
  - [x] 1.4 Ensure all new modules use top-level imports, type hints, and docstrings.

- [ ] 2.0 Extract pure Excel transforms and adapters; update Excel formatting
  - [x] 2.1 Create `core/transform/excel.py` for: clean types, sort_and_renumber, original index mapping.
  - [x] 2.2 Implement `adapters/excel_repo.py` to load/save Excel and call `ExcelFormatter`.
  - [x] 2.3 Update `excel_formatter.py` to use `utils/excel_utils` and remain formatting-only.
  - [x] 2.4 Replace duplicate column/date logic with shared utils.
  - [x] 2.5 Verify output parity on fixture Excel (content-identical checks).

- [ ] 3.0 Extract PDF adapters and pure bookmark transforms
  - [x] 3.1 Create `core/transform/pdf.py` for: title generation, extract index, page range detection.
  - [x] 3.2 Implement `adapters/pdf_repo.py` for read/copy/write and outline handling.
  - [x] 3.3 Keep natural sort behavior in transforms; writer only writes.
  - [x] 3.4 Verify bookmark/title parity on fixture PDF (content-identical titles/order).

- [ ] 4.0 Implement ValidationService and integrate with orchestrator
  - [x] 4.1 Implement `core/services/validate.py` composing existing validators.
  - [x] 4.2 Treat required header and required-duplicate issues as hard errors.
  - [x] 4.3 Treat PDF bookmark page conflicts as hard errors.
  - [x] 4.4 Raise domain exceptions (no UI code); map to existing messages.

- [ ] 5.0 Implement RenumberService and thin Tkinter UI adapter
  - [x] 5.1 Implement `core/services/renumber.py` to orchestrate load/validate/transform/save.
  - [x] 5.2 Add a `Logger` adapter to pipe logs to Tkinter status area.
  - [x] 5.3 Refactor `abstract_renumber.py` to build `Options` and call `RenumberService`.
  - [x] 5.4 Preserve sheet selection UX and existing dialogs/messages.

- [ ] 6.0 Add DRY utilities (excel_utils, dates) and refactor call sites
  - [x] 6.1 Implement `utils/excel_utils.py` with index↔letter helpers.
  - [x] 6.2 Implement `utils/dates.py` with `parse_robust` and `format_mdy` helpers.
  - [x] 6.3 Remove duplicate implementations in existing modules.

- [ ] 7.0 Implement backups/atomic save helpers and integrate
  - [x] 7.1 Implement `io/files.py` for backups and atomic Excel save.
  - [x] 7.2 Update Excel adapter to use atomic save and backup helpers.

- [ ] 8.0 Ensure functional parity with golden fixtures; add unit tests
  - [x] 8.1 Add small Excel/PDF fixtures and expected outputs (goldens).
  - [x] 8.2 Add unit tests for `core/transform/*` and `core/services/validate.py`.
  - [x] 8.3 Add smoke tests for adapters against fixtures.
  - [x] 8.4 Achieve ≥ 80% coverage on core transforms/services.
