## Relevant Files

- `core/models.py` - Add check_document_images option to Options dataclass
- `app/tk_app.py` - Add GUI checkbox and related methods for "Check for Document Images" feature
- `adapters/ui_tkinter.py` - Update UI adapter to pass new option from GUI to pipeline
- `core/pipeline/steps/load_step.py` - Add Document_Found column calculation during DocumentUnit creation
- `adapters/excel_repo.py` - Enhance Excel repository to handle new column addition and Yes/No formatting
- `core/pipeline/steps/save_step.py` - Pass GUI option to Excel repository for conditional column addition
- `tests/core/models_test.py` - Unit tests for Options dataclass changes
- `tests/app/tk_app_test.py` - Unit tests for GUI checkbox functionality (if test file exists)
- `tests/adapters/ui_tkinter_test.py` - Unit tests for UI adapter option handling
- `tests/core/pipeline/steps/load_step_test.py` - Unit tests for Document_Found column calculation
- `tests/adapters/excel_repo_test.py` - Unit tests for enhanced Excel column handling
- `tests/integration_document_found_workflow_test.py` - Integration tests for end-to-end Document_Found feature

### Notes

- Unit tests should be placed alongside the code files they are testing where possible
- Integration tests should verify the complete workflow from GUI option to Excel output
- The feature leverages existing DocumentUnit architecture, minimizing new code requirements
- Boolean values should be stored in DataFrame but displayed as "Yes"/"No" in Excel output

## Tasks

- [ ] 1.0 Add GUI Option for Document Found Feature
  - [ ] 1.1 Add check_document_images_enabled BooleanVar to AbstractRenumberGUI.__init__ with default value True
  - [ ] 1.2 Create checkbox widget in _create_backup_options method after reorder_pages_checkbox
  - [ ] 1.3 Add checkbox label "Check for Document Images" with info text "📄 Adds 'Document_Found' column if missing (always updates if present)"
  - [ ] 1.4 Implement get_check_document_images_enabled() method to return checkbox state
  - [ ] 1.5 Add _on_check_document_images_option_changed() callback method with status logging
  - [ ] 1.6 Update reset_gui() method to reset checkbox to default True state (not remember previous setting)
- [ ] 2.0 Update Data Models and Options Handling
  - [ ] 2.1 Add check_document_images: bool = False field to Options dataclass in core/models.py
  - [ ] 2.2 Update TkinterUIAdapter.get_options() method to include check_document_images from GUI
  - [ ] 2.3 Verify Options dataclass handles the new field correctly in pipeline context creation
- [ ] 3.0 Implement Document_Found Column Calculation in LoadStep
  - [ ] 3.1 Add Document_Found column calculation logic in LoadStep._process_file_pair() after DocumentUnit creation
  - [ ] 3.2 Implement logic: linked_document_ids = {unit.document_id for unit in document_units}
  - [ ] 3.3 Add boolean column: pair_df_with_ids["Document_Found"] = pair_df_with_ids["Document_ID"].isin(linked_document_ids)
  - [ ] 3.4 Add statistics logging: "Document linking: X/Y Excel rows have corresponding PDF documents"
  - [ ] 3.5 Ensure column flows correctly through merge_dataframes() for multi-file workflows
- [ ] 4.0 Enhance Excel Repository for New Column Support
  - [ ] 4.1 Add ADDABLE_COLUMNS whitelist constant with "Document_Found" in _write_dataframe_to_workbook()
  - [ ] 4.2 Implement new column detection logic for missing columns that are in whitelist
  - [ ] 4.3 Add new columns to Excel template header row when add_missing_columns=True
  - [ ] 4.4 Add add_missing_columns parameter to save() method and pass to _write_dataframe_to_workbook()
  - [ ] 4.5 Implement boolean to "Yes"/"No" conversion in DataFrame values before writing to Excel
  - [ ] 4.6 Update SaveStep._save_excel_output() to pass context.options.get("check_document_images", False) as add_missing_columns
  - [ ] 4.7 Add logging for new column addition: "Added X new columns: [column_names]"
- [ ] 5.0 Create Comprehensive Unit and Integration Tests
  - [ ] 5.1 Add test for Options dataclass with check_document_images field in core/models_test.py
  - [ ] 5.2 Create tests for GUI checkbox functionality and state management in LoadStep tests
  - [ ] 5.3 Test Document_Found column calculation with various DocumentUnit scenarios (all linked, none linked, partial)
  - [ ] 5.4 Test Excel repository new column addition and boolean formatting ("Yes"/"No" conversion)
  - [ ] 5.5 Test existing column update behavior (always updates regardless of checkbox state)
  - [ ] 5.6 Create integration test for complete workflow: GUI option → LoadStep calculation → Excel output
  - [ ] 5.7 Test multi-file merge scenarios with Document_Found column
  - [ ] 5.8 Test edge cases: empty DataFrames, corrupted PDFs, missing bookmarks
  - [ ] 5.9 Verify GUI reset behavior returns checkbox to default True state
  - [ ] 5.10 Test performance impact with large files (100-500 rows) to ensure no measurable slowdown
