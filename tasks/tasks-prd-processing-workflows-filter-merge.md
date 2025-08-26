## Relevant Files

- `core/services/renumber.py` - Current workflow orchestration; will be refactored to option-gated pipeline.
- `core/services/validate.py` - Validation composed for Excel/PDF; reused without change.
- `core/interfaces.py` - Interfaces for repos and UI; may add small Options fields.
- `core/models.py` - `Options` dataclass to add filter/merge fields.
- `core/transform/excel.py` - Sort/renumber and link creation; add minimal filter/merge helpers.
- `core/transform/pdf.py` - Bookmark/page utilities; reused.
- `adapters/ui_tkinter.py` - UI adapter; add dialogs for filter and merge pairs.
- `adapters/excel_repo.py` - Excel IO; reused.
- `adapters/pdf_repo.py` - PDF IO; reused.
- `app/tk_app.py` - Wire UI to controller; extend for new dialogs and option wiring.
- `core/app_controller.py` - Backup handling tweaks (disable in merge), pass extended options.
- `tests/core/transform/excel_test.py` - Add tests for filtering/merging data frame behavior.
- `tests/integration_test_document_id.py` - Extend/duplicate for filter and merge flows.

### Notes

- Unit tests should typically be placed alongside the code files they are testing.
- Use `python3 -m pytest` to run tests.

## Tasks

- [ ] 1.0 Extend Options and single pipeline to support filter and merge
  - [ ] 1.1 Update `core/models.py::Options` to add `filter_column: Optional[str]`, `filter_values: Optional[list[str]]`, and `merge_pairs: Optional[list[tuple[str, str]]]`.
  - [ ] 1.2 Add `filter_df(df, column, values)` helper in `core/transform/excel.py` (pure, returns new DataFrame).
  - [ ] 1.3 Refactor `core/services/renumber.py::RenumberService.run` to a single pipeline with option-gated steps: load/validate → clean → add IDs → [merge?] → [filter?] → sort/renumber → save Excel → write PDF.
  - [ ] 1.4 Implement merge path in `RenumberService.run`: when `merge_pairs` is provided, load/validate each pair, concatenate DataFrames, and combine pages/bookmarks for later write.
  - [ ] 1.5 Keep existing behavior when no `merge_pairs` and no filter are provided.

- [ ] 2.0 Implement Filter UI and pipeline gating
  - [ ] 2.1 Extend `core/interfaces.UIController` with `prompt_filter_selection(df) -> tuple[Optional[str], list[str]] | None`.
  - [ ] 2.2 Add a small filter dialog in `adapters/ui_tkinter.py`: dropdown for column, multi-select for distinct values, returns selection.
  - [ ] 2.3 In `app/tk_app.py`, add a "Filter..." button in the options group to launch the dialog; store chosen column/values on the GUI instance.
  - [ ] 2.4 In `adapters/ui_tkinter.py::get_options`, include chosen filter column/values in `Options` (None if not set).
  - [ ] 2.5 In `core/app_controller.py::process_files`, ensure the filter prompt can be launched after the Excel is loaded (use the GUI-stored selection if already set, otherwise skip).

- [ ] 3.0 Implement Merge UI and data/PDF combination
  - [ ] 3.1 Extend `core/interfaces.UIController` with `prompt_merge_pairs() -> list[tuple[str, str]] | None`.
  - [ ] 3.2 Add a merge dialog in `adapters/ui_tkinter.py` to add/remove rows of (Excel, PDF) pairs; validate both paths per row.
  - [ ] 3.3 Add a "Merge..." button in `app/tk_app.py` to open the dialog; store resulting pairs on the GUI instance.
  - [ ] 3.4 In `adapters/ui_tkinter.py::get_options`, include selected `merge_pairs` (None if not set).
  - [ ] 3.5 Implement merge execution in `RenumberService.run`: loop pairs → load/validate → concat DataFrames; accumulate pages/bookmarks for final write; then proceed with sort/renumber/title mapping and optional page reordering.
  - [ ] 3.6 In `core/app_controller.py`, when `merge_pairs` is present, disable backups (ignore backup option).

- [ ] 4.0 Output handling, backups, and naming rules
  - [ ] 4.1 For filter-only runs, save Excel/PDF with a `_filtered` suffix; originals untouched if backups are enabled.
  - [ ] 4.2 For merge runs, always write `merged.xlsx` and `merged.pdf` to a chosen output directory (prompt if not set); never modify originals and do not create backups.
  - [ ] 4.3 Update `core/app_controller.py` to pass explicit output paths to the service where needed.

- [ ] 5.0 Tests: unit and integration for filter and merge
  - [ ] 5.1 Add unit tests for `filter_df` in `tests/core/transform/excel_test.py`.
  - [ ] 5.2 Add unit tests covering merge DataFrame concatenation order and renumbering.
  - [ ] 5.3 Add integration test for filter: rows removed in Excel, corresponding PDF pages/bookmarks omitted.
  - [ ] 5.4 Add integration test for merge: combined Excel with sequential Index#, single PDF with correct titles and optional page reordering.
  - [ ] 5.5 Ensure existing tests pass unchanged.


