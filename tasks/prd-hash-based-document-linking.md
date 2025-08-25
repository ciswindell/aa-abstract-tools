# Product Requirements Document: Hash-Based Document Linking System

## Introduction/Overview

The current document renumbering system uses `Original_Index` to link Excel rows with PDF bookmarks. This approach fails when merging multiple Excel/PDF pairs because index values can collide (e.g., multiple files with "1", "2", "3"). 

This feature replaces the `Original_Index` system with a hash-based `Document_ID` that ensures unique identification across multiple files while maintaining all existing functionality for single-file workflows.

## Goals

1. Enable merging of multiple Excel/PDF pairs without ID collisions
2. Maintain backward compatibility for existing single-file workflows
3. Preserve all current sorting and renumbering functionality
4. Implement robust validation to catch data integrity issues early
5. Use type-safe dataclass structures for better maintainability

## User Stories

1. **As a user merging multiple files**, I want to combine 3 Excel/PDF pairs and have them renumbered sequentially (1-N) without any linking conflicts, so that all documents are processed correctly.

2. **As a user with existing single-file workflows**, I want my current processes to work exactly the same as before, so that I don't need to change my existing procedures.

3. **As a user with data quality issues**, I want the system to validate my data and warn me about duplicate indices or missing bookmarks before processing, so that I can fix issues upfront.

4. **As a developer maintaining this code**, I want clear, type-safe data structures that explicitly show the relationship between Excel rows and PDF bookmarks, so that the code is easier to understand and debug.

## Functional Requirements

1. **Hash Generation**: The system must generate unique `Document_ID` hashes using source file path, row position, and original index value.

2. **DocumentLink DataClass**: The system must use a dataclass with fields:
   - `document_id`: The unique hash identifier
   - `excel_row_index`: Position in the DataFrame
   - `original_bookmark_title`: Original PDF bookmark title
   - `original_bookmark_page`: Original PDF bookmark page number
   - `original_bookmark_level`: Original PDF bookmark level

3. **Validation**: The system must validate data before processing:
   - Excel `Index#` column values must be unique within each file
   - PDF bookmark leading numbers must be unique within each file
   - System must report validation errors clearly

4. **Backward Compatibility**: Single-file workflows must produce identical output to the current system.

5. **Original_Index Removal**: The system must completely replace `Original_Index` with `Document_ID` throughout the codebase.

6. **Error Handling**: The system must handle edge cases with strict data integrity:
   - If hash generation fails for a row, the system must fail with a clear error message
   - If multiple bookmarks match the same Excel row, the system must fail with a clear error message
   - If a bookmark cannot be linked to an Excel row, the system must fail with a clear error message
   - All data integrity issues must be fatal errors to prevent data loss

7. **Link Creation**: The system must create explicit `DocumentLink` objects that map Excel rows to PDF bookmarks before any renumbering occurs.

8. **Title Generation**: The system must generate new bookmark titles using sequential numbers (1, 2, 3...) after sorting, keyed by `Document_ID`.

## Non-Goals (Out of Scope)

1. **UI Changes**: No changes to the user interface or user-facing workflows
2. **File Format Changes**: No changes to Excel or PDF file formats
3. **Performance Optimization**: No specific performance improvements beyond maintaining current speed
4. **Merge UI**: This PRD covers the linking system only, not the merge feature UI
5. **Data Migration**: No migration of existing files - this is for new processing only

## Design Considerations

- **No Over-Engineering**: Keep changes minimal and focused - only replace the linking mechanism
- **Existing Architecture**: Integrate seamlessly with current SOLID/DRY architecture patterns
- **Hash Algorithm**: Use MD5 for speed and collision resistance (8-character truncation)
- **DataClass Location**: Add `DocumentLink` to `core/models.py` following existing patterns
- **Function Signatures**: Update existing functions to accept `source_path` parameter only where needed
- **Type Hints**: Maintain full type annotation coverage
- **DRY Principle**: Reuse existing validation and error handling patterns
- **Single Responsibility**: Each function should have one clear purpose in the linking process

## Technical Considerations

1. **Dependencies**: No new external dependencies required
2. **Integration Points**: 
   - `core/transform/excel.py` - Update `clean_types()` following existing patterns
   - `core/transform/pdf.py` - Update `make_titles()` and extraction functions using DRY principles
   - `core/services/renumber.py` - Update linking logic maintaining single responsibility
3. **Architecture Compliance**: Follow existing SOLID principles - no new abstractions unless necessary
4. **Testing**: Existing test suite must pass with minimal modifications - reuse existing test patterns
5. **Hash Collisions**: MD5 with 8 characters provides ~4 billion combinations, sufficient for typical use cases
6. **Code Reuse**: Leverage existing validation, error handling, and logging infrastructure

## Success Metrics

1. **Functionality**: All existing single-file test cases pass unchanged
2. **Uniqueness**: Zero hash collisions in test scenarios with up to 1000 documents
3. **Validation**: System catches and reports 100% of duplicate index scenarios
4. **Performance**: Processing time remains within 10% of current performance
5. **Code Quality**: No increase in cyclomatic complexity of core functions

## Open Questions

1. Should the hash length be configurable, or is 8 characters sufficient?
2. Do we need a migration utility to help users understand the change from `Original_Index`?
3. Should we add additional validation beyond the existing codebase requirements?

---

**Target Implementation Timeline**: 2-3 development days
**Risk Level**: Medium (core system changes, but well-defined scope)
**Dependencies**: None
