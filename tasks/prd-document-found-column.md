# Product Requirements Document: Document Found Column Feature

## Introduction/Overview

The Document Found Column feature adds visibility into which Excel rows have corresponding PDF documents in the processing pipeline. Currently, users cannot easily identify which Excel entries are successfully linked to PDF bookmarks without manually cross-referencing files. This feature adds a "Document_Found" column to Excel outputs, enabling users to quickly audit document completeness, filter incomplete records, and generate reports on document availability.

The feature integrates seamlessly with the existing DocumentUnit architecture, leveraging the established linking mechanism between Excel rows and PDF bookmarks to provide accurate, real-time document status information.

## Goals

1. **Improve Document Auditing**: Enable users to quickly identify Excel rows that lack corresponding PDF documents
2. **Enhance Workflow Efficiency**: Allow users to filter and sort by document availability for targeted follow-up actions  
3. **Increase Data Transparency**: Provide clear visibility into the success rate of Excel-to-PDF linking
4. **Maintain User Control**: Offer the feature as an optional checkbox while ensuring existing columns are always updated
5. **Preserve Performance**: Implement with minimal impact on processing time using existing data structures

## User Stories

**As a document processor**, I want to see which Excel rows have corresponding PDF documents so that I can quickly identify missing documents that need follow-up.

**As a quality assurance reviewer**, I want to filter Excel output to show only rows without PDF documents so that I can generate a list of missing documents for the team.

**As a project manager**, I want to sort the Excel output by document availability so that I can assess completion rates and prioritize document collection efforts.

**As a data analyst**, I want the document status to be automatically calculated and updated so that I always have current information without manual cross-referencing.

**As a power user**, I want to control whether the column is added to new templates while ensuring existing columns are always updated with current data.

## Functional Requirements

1. **GUI Option**: The system must provide a checkbox labeled "Check for Document Images" in the Processing Options section
2. **Default State**: The checkbox must be checked by default for new sessions
3. **Reset Behavior**: GUI reset must return the checkbox to the default checked state (not remember previous setting)
4. **Column Addition**: When checkbox is checked and "Document_Found" column is missing from Excel template, the system must add it as the rightmost column
5. **Column Update**: When "Document_Found" column exists in Excel template, the system must always update it with current values regardless of checkbox state
6. **Data Calculation**: The system must always calculate document linking status in the DataFrame during LoadStep processing
7. **Value Format**: The system must store boolean values in DataFrame and display "Yes"/"No" values in Excel output
8. **Linking Logic**: The system must mark a row as "Yes" if a DocumentUnit was successfully created for that Excel row's Document_ID
9. **Statistics Logging**: The system must log document linking statistics (e.g., "Document linking: 85/100 Excel rows have corresponding PDF documents")
10. **Multi-file Support**: The system must work correctly with both single-file and merge workflows
11. **Template Preservation**: The system must preserve existing column positions when updating existing "Document_Found" columns
12. **Error Handling**: The system must handle edge cases gracefully (corrupted PDFs, missing bookmarks, duplicate indices)

## Non-Goals (Out of Scope)

1. **Document Source Identification**: Will not indicate which specific PDF file contains the document in merge scenarios
2. **Partial Match Detection**: Will not detect partial or fuzzy matches between Excel rows and PDF bookmarks
3. **Document Quality Assessment**: Will not evaluate PDF document quality, readability, or completeness
4. **Historical Tracking**: Will not maintain history of document status changes over time
5. **Custom Column Names**: Will not allow users to customize the "Document_Found" column name
6. **Advanced Filtering UI**: Will not add specialized filtering controls beyond standard Excel functionality
7. **Document Preview**: Will not provide preview or thumbnail capabilities for found documents

## Design Considerations

**GUI Integration**: The checkbox should be positioned in the existing "Processing Options" section after the "Reorder Pages" option, maintaining visual consistency with existing checkboxes.

**Info Text**: Include descriptive text below the checkbox: "📄 Adds 'Document_Found' column if missing (always updates if present)"

**Column Formatting**: The "Document_Found" column should use standard Excel boolean formatting with "Yes"/"No" values for maximum user comprehension.

**Visual Feedback**: Status log should provide clear feedback about column addition vs. update operations and linking statistics.

## Technical Considerations

**Architecture Integration**: Leverages existing DocumentUnit creation logic in LoadStep without requiring additional PDF parsing or bookmark analysis.

**Performance**: Minimal performance impact as it uses existing DocumentUnit data structures and adds only simple boolean operations.

**Data Flow**: Column calculation occurs during LoadStep, flows through FilterDfStep and SortDfStep naturally, and gets written during SaveStep.

**Excel Integration**: Extends existing ExcelRepo column handling with whitelist approach for controlled column addition.

**Memory Efficiency**: Uses existing DataFrame structures without additional memory overhead for document status tracking.

## Success Metrics

1. **User Adoption**: 70%+ of users keep the feature enabled (checkbox remains checked)
2. **Processing Performance**: No measurable increase in processing time for typical file sizes (100-500 rows)
3. **Data Accuracy**: 100% accuracy in document status reporting (matches actual DocumentUnit creation)
4. **User Feedback**: Positive user feedback on improved workflow efficiency and document auditing capabilities
5. **Error Reduction**: Reduction in user-reported issues related to missing or unlinked documents

## Open Questions

1. **Column Positioning**: For new columns, should "Document_Found" be added as the rightmost column or in a specific position (e.g., after "Index#")?
2. **Batch Processing**: Should we add progress indicators for very large files (1000+ rows) or is the existing logging sufficient?
3. **Export Formats**: Should the feature work with other potential export formats beyond Excel, or is Excel-only sufficient for current needs?
4. **Integration Testing**: What specific test scenarios should be prioritized for the various Excel template configurations users might have?
