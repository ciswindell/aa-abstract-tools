# Task List: Excel Post-Processing Enhancement

## Relevant Files

- `core/pipeline/steps/format_excel_step.py` - New pipeline step for Excel post-processing formatting
- `tests/core/pipeline/steps/format_excel_step_test.py` - Unit tests for FormatExcelStep
- `core/pipeline/pipeline.py` - Pipeline orchestrator (modify to register new step)
- `tests/core/pipeline/pipeline_test.py` - Pipeline tests (update to include new step)

### Notes

- Unit tests should be placed alongside the code files they are testing
- Use `python3 -m pytest [optional/path/to/test/file]` to run tests
- The new step will integrate with existing pipeline architecture and logging

## Tasks

- [ ] 1.0 Create FormatExcelStep Pipeline Step
  - [ ] 1.1 Create `core/pipeline/steps/format_excel_step.py` file with basic class structure
  - [ ] 1.2 Implement `FormatExcelStep` class inheriting from `BaseStep`
  - [ ] 1.3 Add constructor with required dependencies (excel_repo, pdf_repo, logger, ui)
  - [ ] 1.4 Implement `execute(context: PipelineContext)` method with error handling
  - [ ] 1.5 Add comprehensive docstrings and type hints
  - [ ] 1.6 Implement graceful error handling that logs warnings but doesn't fail pipeline

- [ ] 2.0 Implement Date Column Detection and Formatting
  - [ ] 2.1 Create `_find_date_columns(worksheet)` method with robust case-insensitive pattern matching
  - [ ] 2.2 Implement pattern matching for variations like "Date", "DATE", "Document Date", "Received Date"
  - [ ] 2.3 Create `_apply_date_formatting(worksheet, date_columns, data_rows)` method
  - [ ] 2.4 Implement `M/D/YYYY` number format creation using openpyxl NamedStyle
  - [ ] 2.5 Apply date formatting to data rows plus 1000-row buffer
  - [ ] 2.6 Add logging for date columns found and formatted

- [ ] 3.0 Implement Auto-Filter Setup with Buffer
  - [ ] 3.1 Create `_setup_auto_filter(worksheet, data_rows)` method
  - [ ] 3.2 Calculate filter range from A1 to last column + 1000 rows
  - [ ] 3.3 Apply auto-filter using openpyxl `worksheet.auto_filter.ref`
  - [ ] 3.4 Handle edge cases (empty worksheets, single column, etc.)
  - [ ] 3.5 Add logging for auto-filter range applied

- [ ] 4.0 Integrate FormatExcelStep into Pipeline
  - [ ] 4.1 Import `FormatExcelStep` in `core/pipeline/pipeline.py`
  - [ ] 4.2 Add step registration in `register_steps()` method after `SaveStep`
  - [ ] 4.3 Ensure step receives proper dependencies (excel_repo, pdf_repo, logger, ui)
  - [ ] 4.4 Verify step executes only when `context.excel_out_path` exists
  - [ ] 4.5 Test integration with both single-file and merge workflows

- [ ] 5.0 Create Comprehensive Unit Tests
  - [ ] 5.1 Create `tests/core/pipeline/steps/format_excel_step_test.py` with test class setup
  - [ ] 5.2 Test date column detection with various header patterns
  - [ ] 5.3 Test date formatting application with mock openpyxl objects
  - [ ] 5.4 Test auto-filter setup with different worksheet sizes
  - [ ] 5.5 Test error handling scenarios (file not found, permission errors, corrupted Excel)
  - [ ] 5.6 Test integration with PipelineContext (valid/invalid excel_out_path)
  - [ ] 5.7 Test logging output for successful operations and error conditions
  - [ ] 5.8 Update pipeline tests to include FormatExcelStep in execution flow
  - [ ] 5.9 Create integration test to verify end-to-end Excel formatting
  - [ ] 5.10 Verify all tests pass and achieve good code coverage
