# Feature Specification: Fix Date Column Processing for Chronological Sorting

**Feature Branch**: `001-fix-date-sorting`  
**Created**: 2025-11-19  
**Status**: Draft  
**Input**: User description: "Fix date column processing to ensure proper chronological sorting when Excel cells are formatted as text"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Process Files with Text-Formatted Dates (Priority: P1)

When users upload Excel files where date columns (Document Date, Received Date) contain text-formatted date values instead of proper Excel date formatting, the system must correctly interpret these as dates and sort them chronologically rather than alphabetically.

**Why this priority**: This is the core issue causing incorrect output for users. Files are being sorted as "1/1/2024" before "12/31/2023" alphabetically, which breaks the entire chronological ordering that users depend on for their workflow.

**Independent Test**: Can be fully tested by uploading an Excel file with date columns formatted as text (e.g., "1/5/2024", "12/25/2023", "3/15/2024") and verifying the output file sorts them chronologically (12/25/2023, 1/5/2024, 3/15/2024).

**Acceptance Scenarios**:

1. **Given** an Excel file with Received Date column containing text values like "1/5/2024", "12/25/2023", "3/15/2024", **When** user processes the file with sort enabled, **Then** output file displays dates in chronological order (12/25/2023, 1/5/2024, 3/15/2024)
2. **Given** an Excel file with mixed date formatting (some cells as proper dates, some as text), **When** user processes the file, **Then** all dates sort correctly regardless of original cell format
3. **Given** an Excel file that previously sorted incorrectly due to text formatting, **When** user reprocesses it with the fix, **Then** the chronological order is correct

---

### User Story 2 - Handle Various Date Format Patterns (Priority: P2)

Users may have Excel files with dates written in different formats (M/D/YYYY, MM/DD/YYYY, YYYY-MM-DD, etc.). The system must recognize and correctly parse these common date patterns.

**Why this priority**: While the primary issue is text vs. date formatting, users work with various date formats. Supporting common patterns prevents future sorting issues and improves robustness.

**Independent Test**: Can be tested by processing files with dates in different formats (M/D/Y, MM-DD-YYYY, YYYY/MM/DD) and verifying all formats are recognized and sorted correctly.

**Acceptance Scenarios**:

1. **Given** an Excel file with dates in M/D/YYYY format (e.g., "1/5/2024", "12/25/2023"), **When** user processes the file, **Then** dates are sorted chronologically
2. **Given** an Excel file with dates in MM-DD-YYYY format (e.g., "01-05-2024", "12-25-2023"), **When** user processes the file, **Then** dates are sorted chronologically
3. **Given** an Excel file with dates in YYYY-MM-DD format (e.g., "2024-01-05", "2023-12-25"), **When** user processes the file, **Then** dates are sorted chronologically
4. **Given** an Excel file with dates in full text format (e.g., "January 5, 2024"), **When** user processes the file, **Then** dates are sorted chronologically

---

### User Story 3 - Preserve Data Integrity for Unparseable Values (Priority: P3)

When the system encounters values in date columns that cannot be parsed as dates (invalid formats, typos, null values), it must preserve the original value rather than causing errors or data loss.

**Why this priority**: Data integrity is critical, but this is a defensive scenario. Most valid date values should parse correctly (P1/P2), and unparseable values should be rare edge cases.

**Independent Test**: Can be tested by processing a file with intentionally invalid date values (empty cells, "N/A", "TBD") and verifying these values are preserved unchanged in the output.

**Acceptance Scenarios**:

1. **Given** an Excel file with some date cells empty or containing "N/A", **When** user processes the file, **Then** empty cells remain empty and "N/A" values are preserved
2. **Given** an Excel file with date cells containing unparseable text (e.g., "TBD", "UNKNOWN"), **When** user processes the file, **Then** the original text values are preserved in the output
3. **Given** an Excel file with only valid dates, **When** user processes the file, **Then** no data loss occurs and all dates are correctly formatted

---

### Edge Cases

- What happens when a date column contains only null/empty values?
- How does the system handle ambiguous date formats like "01/02/2024" (could be Jan 2 or Feb 1)?
- What happens when date values are extremely old (e.g., 1800s) or far in the future (e.g., 2100s)?
- How does the system handle dates that are Excel serial numbers stored as text (e.g., "44927")?
- What happens when the system encounters Unicode or non-ASCII characters in date fields?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect columns containing "date" in their name (case-insensitive) and apply date parsing to those columns
- **FR-002**: System MUST attempt to parse text values in date columns into proper datetime objects during file loading
- **FR-003**: System MUST support common date formats including M/D/YYYY, MM/DD/YYYY, M-D-YYYY, YYYY-MM-DD, and full text formats (e.g., "January 5, 2024")
- **FR-004**: System MUST preserve the original value when a date cannot be successfully parsed (no data loss)
- **FR-005**: System MUST handle null, empty, or NA values in date columns gracefully without errors
- **FR-006**: System MUST sort date columns chronologically (not alphabetically) after parsing
- **FR-007**: System MUST maintain backward compatibility - files with properly formatted Excel dates must continue to work correctly

### Architecture Requirements (per Constitution v2.0.0)

- **AR-001**: Date parsing logic MUST reside in data loading layer (`adapters/excel_repo.py`) to ensure all date conversion happens at the data boundary (Clean Architecture principle)
- **AR-002**: Date parsing MUST use existing `utils/dates.py` utilities to maintain DRY principles and consistent behavior across the codebase (Code Quality principle)
- **AR-003**: Date conversion MUST handle large files efficiently without excessive memory usage (Memory Efficiency principle)
- **AR-004**: Changes MUST follow PEP 8 style guidelines (Code Quality principle)
- **AR-005**: Existing unit tests SHOULD be updated to verify date parsing behavior, but tests are not mandatory (optional testing approach)

### Key Entities

- **Date Column**: Any Excel column with a name containing "date" (case-insensitive), such as "Document Date", "Received Date", "Date", etc. These columns require special parsing treatment.
- **Date Value**: A cell value within a date column that may be formatted as a proper Excel date, text string, or unparseable content. The system must handle all three cases.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can process Excel files with text-formatted date columns and receive correctly sorted output (chronological order) 100% of the time
- **SC-002**: System correctly parses at least 95% of common date formats (M/D/Y, MM-DD-YYYY, YYYY-MM-DD, full text dates) without requiring user intervention
- **SC-003**: Processing files with mixed date formatting (text and proper dates) produces the same output as files with consistent formatting
- **SC-004**: Zero data loss occurs during date parsing - unparseable values are preserved exactly as they appear in the input file
- **SC-005**: Users report zero new sorting issues related to date columns after the fix is deployed
- **SC-006**: Existing workflows using properly formatted Excel dates continue to work without any changes or degradation

## Assumptions

1. The primary date columns in user files are "Document Date" and "Received Date"
2. Most user files use U.S. date formats (M/D/Y) as the primary format
3. The existing `parse_robust()` function in `utils/dates.py` provides sufficient date parsing capabilities
4. Users expect dates to sort in ascending chronological order (oldest to newest)
5. The fix should apply automatically to all date columns without requiring user configuration

## Dependencies

- Existing `utils/dates.py` module with `parse_robust()` function
- pandas library for DataFrame operations
- openpyxl library for Excel file reading

## Out of Scope

- User interface for configuring date parsing behavior
- Support for non-standard or custom date formats beyond common patterns
- Automatic detection and correction of ambiguous date formats (e.g., 01/02/2024)
- Date validation against business rules (e.g., rejecting future dates)
- Localization support for non-U.S. date formats
