## Relevant Files

- `abstract_renumber.py` - Orchestrates processing; integrate input-as-template flow and UX hooks (SOLID/DRY).
- `excel_processor.py` - Excel read/write pipeline; adopt template-preserving operations and atomic writes.
- `excel_formatter.py` - Current formatting logic; adapt to preservation-first strategy, minimize width logic.
- `column_mapper.py` - To be removed; replace mapping with a simple validator.
- `validators/input_sheet_validator.py` - New lightweight validator for required columns (case-insensitive, duplicates check).
- `tests/test_excel_template_flow.py` - Integration tests for preservation, sheet selection, and atomic write behavior.
- `tests/test_required_columns_validation.py` - Unit tests for required-columns checks (case-insensitive, duplicates).

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `module.py` and `test_module.py` in the same directory or tests folder).
- Use `pytest -q [optional/path/to/test_file]` to run tests. Running without a path executes all discovered tests.

## Tasks

- [ ] 1.0 Implement input-as-template export preserving full workbook formatting and structure (SOLID/DRY)
  - [x] 1.1 Confirm current .xlsx library/API capabilities for style-preserving reads/writes.
  - [x] 1.2 Load input workbook read-only; immediately create output as a saved copy in target dir.
  - [x] 1.3 Ensure all sheets are retained; restrict mutations to the processing sheet only.
  - [x] 1.4 Write values without re-creating styles; preserve extra columns and input column order.
  - [x] 1.5 Update minimal code paths only; remove reliance on programmatic width calculations.
- [ ] 2.0 Add GUI-driven sheet selection when target processing sheet is not found (SOLID/DRY)
  - [x] 2.1 Read configured processing sheet name; attempt exact match per existing behavior.
  - [x] 2.2 If not found, present a GUI picker listing available sheet names; capture selection for this run.
  - [x] 2.3 Route processing to the chosen sheet; maintain current naming/UX conventions.
- [ ] 3.0 Enforce required columns validation (case-insensitive) with GUI error on missing (SOLID/DRY)
  - [x] 3.1 Retrieve the existing required columns list from code as single source of truth.
  - [x] 3.2 Implement case-insensitive presence checks; ignore header order.
  - [x] 3.3 Detect duplicates within the required set (case-insensitive); duplicates outside required set allowed.
  - [x] 3.4 On failure, show GUI with the missing required columns and abort processing.
- [ ] 4.0 Remove column mapping module and UI; introduce simple `InputSheetValidator` (SOLID/DRY)
  - [x] 4.1 Create `validators/input_sheet_validator.py` and port checks there.
  - [x] 4.2 Replace usages of `ColumnMapper` with validator calls.
  - [x] 4.3 Delete `column_mapper.py` and any mapping dialogs.
  - [x] 4.4 Update docs/README to reflect validator approach.
- [ ] 5.0 Implement atomic output write with temp-file cleanup respecting backup options (SOLID/DRY)
  - [x] 5.1 Write to a temporary file in the output directory; flush and fsync.
  - [x] 5.2 Atomically rename temp file to final output path.
  - [x] 5.3 Respect existing backup/overwrite policies; do not alter their semantics.
  - [x] 5.4 Ensure cleanup of temp files on both success and error paths.
- [ ] 6.0 Integrate preservation flow with existing processing without functional changes (SOLID/DRY)
  - [x] 6.1 Wire the template-preserving exporter into current pipeline entry points.
  - [x] 6.2 Verify no change to formula handling or renumbering results on valid inputs.
  - [ ] 6.3 Add integration tests (<1,000 rows) confirming identical formatting except intended data changes.
  - [ ] 6.4 Update README/usage notes only where behavior is clarified (no functional change).


