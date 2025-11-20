# Feature Specification: Preserve All Columns When Merging Excel Files

**Feature Branch**: `006-merge-column-fix`  
**Created**: 2025-11-20  
**Status**: Draft  
**Input**: User description: "Fix to preserve all columns when merging Excel files"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Two-File Merge with Extra Columns (Priority: P1)

A user needs to merge two Excel/PDF pairs where the second file contains additional columns not present in the first file. They expect all columns from both files to appear in the merged output.

**Why this priority**: This is the core issue reported - users are losing data when merging files with different column structures. This must work for the feature to have any value.

**Independent Test**: Can be fully tested by merging two Excel files with different columns and verifying all columns appear in the output.

**Acceptance Scenarios**:

1. **Given** File A has columns [A, B, C] and File B has columns [A, B, C, D], **When** user merges the files, **Then** the output contains all columns [A, B, C, D] with data from both files preserved
2. **Given** File A has columns [Index#, Date, Name] and File B has columns [Index#, Date, Name, Status, Comments], **When** user merges the files, **Then** the output contains all five columns with no data loss

---

### User Story 2 - Multi-File Merge with Varied Columns (Priority: P2)

A user needs to merge three or more Excel/PDF pairs where each file may have a unique set of columns. The system should create a unified output with the superset of all columns.

**Why this priority**: While less common than two-file merges, multi-file merges are supported by the system and should preserve all unique columns from all files.

**Independent Test**: Can be tested by merging 3+ files with different column combinations and verifying the output contains all unique columns.

**Acceptance Scenarios**:

1. **Given** three files with columns [A,B], [B,C], and [A,C,D] respectively, **When** user merges all three files, **Then** the output contains columns [A, B, C, D] with appropriate data placement
2. **Given** files with overlapping and unique columns, **When** merged, **Then** rows from each file retain their original column data in the correct positions

---

### User Story 3 - Column Order and Formatting Preservation (Priority: P3)

When merging files with different columns, the system should maintain a logical column order and preserve any special formatting from the template file.

**Why this priority**: While data preservation is critical (P1), maintaining a logical presentation and formatting improves usability but isn't essential for data integrity.

**Independent Test**: Can be tested by checking column order in merged output matches a logical pattern (template columns first, then additional columns).

**Acceptance Scenarios**:

1. **Given** template file with formatted columns [A, B, C] and second file with [A, B, C, D, E], **When** merged, **Then** output shows columns in order [A, B, C, D, E] with template formatting preserved for A, B, C
2. **Given** files with different column orders, **When** merged, **Then** the primary file's column order is preserved with new columns appended at the end

---

### Edge Cases

- What happens when column names differ only in case (e.g., "Status" vs "status")?
- How does system handle completely disjoint column sets (no overlapping columns)?
- What happens when the same column name appears with different data types? (Resolved: auto-detect best common type)
- How does system handle empty columns or columns with all null values?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST preserve all columns from all files when performing merge operations
- **FR-002**: System MUST maintain data integrity - no cell values can be lost during merge
- **FR-003**: System MUST handle column name matching in a case-insensitive manner with whitespace normalization
- **FR-004**: System MUST append new columns after existing template columns to maintain logical order
- **FR-005**: System MUST preserve Excel formatting from the template file for existing columns
- **FR-006**: System MUST properly align data rows even when files have different column structures (shared columns contain vertically concatenated data from all files)
- **FR-007**: System MUST continue to respect existing filters and sorting during merge operations
- **FR-008**: System MUST maintain all existing functionality (document linking, page reordering, etc.) when columns are added
- **FR-009**: System MUST exclude internal columns (those starting with underscore and Document_ID) from being treated as new user data columns
- **FR-010**: System MUST intelligently handle data type conflicts by auto-detecting the most appropriate common type that preserves all data

### Key Entities *(include if feature involves data)*

- **Excel Column**: Represents a data field that may exist in one or more source files, identified by column header name
- **Column Mapping**: Tracks which columns from source files map to which columns in the merged output
- **Template Structure**: The column structure from the primary Excel file that serves as the base for formatting

## Clarifications

### Session 2025-11-20

- Q: When the same column name appears in multiple source files, how should the data be merged? → A: Concatenate all rows from all files with that column name
- Q: What should appear in cells for columns that don't exist in a source file? → A: Empty cells (null/blank)
- Q: Should internal system columns be excluded from merge column detection? → A: Yes, exclude internal system columns
- Q: How should whitespace in column names be handled during matching? → A: Trim and normalize spaces
- Q: How should the system handle data type conflicts in the same column across files? → A: Auto-detect best common type

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of columns from all source files appear in merged output (zero data loss)
- **SC-002**: Merge operations with different column structures complete without errors in 100% of cases
- **SC-003**: Performance impact of column preservation is negligible (merge time increases by less than 5%)
- **SC-004**: Users can identify source of each data column in merged output through visual inspection
- **SC-005**: All existing merge functionality continues to work correctly with column preservation enabled

## Assumptions

- Column matching is case-insensitive (following Excel conventions)
- New columns are appended to the right of existing columns
- The primary file's formatting takes precedence for shared columns
- Empty columns are preserved to maintain structure consistency
- Missing columns in source files result in empty cells (null values) in the merged output
- Document ID generation continues to work correctly with expanded column sets

## Out of Scope

- Column reordering or custom column mapping interfaces
- Automatic column type conversion or data transformation
- Handling of formula columns or calculated fields
- Column-level merge conflict resolution
- Preview of column differences before merge