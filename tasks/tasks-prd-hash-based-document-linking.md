# Task List: Hash-Based Document Linking System

Based on PRD: `prd-hash-based-document-linking.md`

## Relevant Files

- `core/models.py` - Add DocumentLink dataclass following existing patterns
- `core/transform/excel.py` - Update clean_types() to generate Document_ID instead of Original_Index
- `core/transform/pdf.py` - Update make_titles() and extract functions to use Document_ID
- `core/services/renumber.py` - Update linking logic to use DocumentLink objects
- `core/services/validate.py` - Add validation for unique indices and bookmark linking
- `tests/core/transform/excel_test.py` - Update tests to use Document_ID
- `tests/core/transform/pdf_test.py` - Update tests to use Document_ID
- `tests/core/services/validate_test.py` - Add tests for new validation logic

### Notes

- All existing tests must pass with minimal modifications to ensure backward compatibility
- Use existing validation and error handling patterns to maintain SOLID/DRY principles
- Hash generation should be deterministic for testing purposes

## Tasks

- [x] 1.0 Create DocumentLink DataClass and Hash Generation Utilities
  - [x] 1.1 Add DocumentLink dataclass to core/models.py with required fields
  - [x] 1.2 Create generate_document_id() function using MD5 hash of file path + row position + original index
  - [x] 1.3 Add type hints and docstrings following existing code patterns
  - [x] 1.4 Write unit tests for hash generation function

- [x] 2.0 Update Excel Transform Functions to Use Document_ID
  - [x] 2.1 Modify clean_types() to accept optional source_path parameter
  - [x] 2.2 Replace Original_Index column creation with Document_ID generation
  - [x] 2.3 Ensure backward compatibility when source_path is None
  - [x] 2.4 Update existing tests to verify Document_ID column presence
  - [x] 2.5 Add new tests for hash generation with source_path

- [ ] 3.0 Update PDF Transform Functions to Use Document_ID
  - [ ] 3.1 Update make_titles() to use Document_ID column instead of Original_Index
  - [ ] 3.2 Rename extract_original_index() to extract_document_id() (keep same logic)
  - [ ] 3.3 Update function signatures and type hints
  - [ ] 3.4 Update existing tests to use new function names and Document_ID
  - [ ] 3.5 Ensure all PDF transform tests pass with new column name

- [ ] 4.0 Update Renumber Service Linking Logic
  - [ ] 4.1 Create create_document_links() function that returns List[DocumentLink]
  - [ ] 4.2 Update run() method to use DocumentLink objects for mapping
  - [ ] 4.3 Pass source_path to clean_types() when calling Excel transforms
  - [ ] 4.4 Update page reordering logic to use Document_ID from DocumentLink objects
  - [ ] 4.5 Add error handling for failed hash generation and duplicate mappings
  - [ ] 4.6 Update _merge_bookmarks_with_titles() to work with Document_ID

- [ ] 5.0 Remove Original_Index References and Update Tests
  - [ ] 5.1 Search codebase for all Original_Index references and replace with Document_ID
  - [ ] 5.2 Update all test files to use Document_ID instead of Original_Index
  - [ ] 5.3 Run full test suite to ensure no regressions
  - [ ] 5.4 Add integration test for single-file workflow producing identical output
  - [ ] 5.5 Add validation tests for duplicate indices and bookmark linking errors
