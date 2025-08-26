# Task List: Alphanumeric Index# Support

## Relevant Files

- `excel_processor.py` - Contains the main Excel processing logic that needs to be updated to handle alphanumeric Index# values
- `pdf_processor.py` - Contains PDF bookmark processing logic that needs to be updated for string-based index mapping
- `main.py` - Main application file that may need minor updates for error handling
- `test_excel_processor.py` - Unit tests for Excel processor functionality
- `test_pdf_processor.py` - Unit tests for PDF processor functionality
- `test_integration.py` - Integration tests for the complete workflow with alphanumeric Index# values

### Notes

- Unit tests should be placed alongside the code files they are testing
- Focus on testing both backward compatibility (numeric-only) and new functionality (alphanumeric)
- Integration tests should cover mixed format scenarios (A1, B5, 8, 13, AGH42)
- Use `python3 -m pytest` to run tests

## Tasks

- [x] 1.0 Update Excel Processor for String-Based Index# Handling
  - [x] 1.1 Modify `_process_data_types()` method to treat Index# as string instead of numeric
  - [x] 1.2 Update `get_original_index_mapping()` to return `Dict[str, int]` instead of `Dict[int, int]`
  - [x] 1.3 Ensure `_add_original_index_column()` preserves Index# values as strings
  - [x] 1.4 Update `_renumber_index()` to work with string-based Index# column
  - [x] 1.5 Add string cleaning and validation for Index# column values
  - [x] 1.6 Update type hints throughout ExcelProcessor class for string-based Index# handling

- [x] 2.0 Update PDF Processor for String-Based Index Mapping
  - [x] 2.1 Modify `generate_new_bookmark_titles()` to accept `Dict[str, int]` mapping
  - [x] 2.2 Update `extract_original_index_from_bookmark()` to return string instead of int
  - [x] 2.3 Modify `update_bookmarks_with_new_titles()` to handle string-based mapping
  - [x] 2.4 Update `_create_bookmark_page_mapping()` for string-based index keys
  - [x] 2.5 Update `get_bookmark_update_summary()` method signature and implementation
  - [x] 2.6 Add string comparison logic for bookmark matching instead of integer conversion
  - [x] 2.7 Update type hints throughout PDFProcessor class for string-based index handling

- [ ] 3.0 Implement Backward Compatibility Testing
  - [ ] 3.1 Create test cases for numeric-only Index# values (1, 2, 3, etc.)
  - [ ] 3.2 Verify existing functionality works unchanged with numeric Index# values
  - [ ] 3.3 Test mixed format scenarios (A1, B5, 8, 13, AGH42)
  - [ ] 3.4 Validate that final Index# column always contains sequential numbers (1, 2, 3, etc.)
  - [ ] 3.5 Test PDF bookmark mapping with various Index# formats
  - [ ] 3.6 Ensure Original_Index column preserves original values regardless of format

- [ ] 4.0 Add Error Handling for Edge Cases
  - [ ] 4.1 Handle empty or null Index# values gracefully
  - [ ] 4.2 Add validation for Index# values with special characters or spaces
  - [ ] 4.3 Implement proper error messages for Index# processing failures
  - [ ] 4.4 Add logging for Index# format conversion process
  - [ ] 4.5 Handle edge cases where Index# values are extremely long or complex
  - [ ] 4.6 Add validation to ensure Index# values are unique within the dataset

- [ ] 5.0 Create Comprehensive Test Suite
  - [ ] 5.1 Create unit tests for ExcelProcessor Index# handling methods
  - [ ] 5.2 Create unit tests for PDFProcessor string-based mapping methods
  - [ ] 5.3 Create integration tests for complete workflow with alphanumeric values
  - [ ] 5.4 Add test cases for backward compatibility with numeric-only Index# values
  - [ ] 5.5 Create test data files with various Index# formats (numeric, alphanumeric, mixed)
  - [ ] 5.6 Add performance tests for large files with complex Index# formats
  - [ ] 5.7 Create test cases for error conditions and edge cases 