# PRD: Abstract Renumber Tool

## Introduction/Overview

The Abstract Renumber Tool is a class-based Python application that automates the process of sorting Excel data and renumbering corresponding PDF bookmarks. The tool addresses the manual effort required to maintain synchronized numbering between Excel worksheets and PDF bookmark references when documents need to be reordered based on multiple sorting criteria.

**Problem it solves:** Currently, when abstract documents need to be reordered based on legal descriptions, parties, and dates, both the Excel worksheet and PDF bookmarks must be manually updated to maintain consistency. This is time-consuming and error-prone.

**Goal:** Automate the sorting and renumbering process to ensure Excel data and PDF bookmarks remain synchronized after reordering.

**Process Overview:** 
1. Load Excel file and preserve original Index# values in an Original_Index column
2. Sort Excel data by multiple criteria and renumber Index# column sequentially  
3. Update PDF bookmarks using the mapping between original and new index numbers
4. Output final files with synchronized numbering (Original_Index column removed from Excel)

## Goals

1. **Automated Sorting:** Sort Excel data by multiple columns in specified priority order
2. **Index Renumbering:** Automatically renumber the Index# column starting from 1
3. **Bookmark Synchronization:** Update PDF bookmarks to match the new Excel order
4. **User-Friendly Interface:** Provide intuitive GUI for file selection and column mapping
5. **Data Validation:** Ensure Excel files contain required columns before processing
6. **Extensible Design:** Create class-based architecture for future enhancements

## User Stories

1. **As an abstract processor**, I want to select Excel and PDF files through a GUI so that I don't have to type file paths manually.

2. **As an abstract processor**, I want the tool to default to my Downloads folder so that I can quickly access recently downloaded files.

3. **As an abstract processor**, I want to sort my documents by legal description, then parties, then dates so that they follow the required filing order.

4. **As an abstract processor**, I want the Index# column to be automatically renumbered from 1 so that it reflects the new sort order while preserving the original numbers for bookmark mapping.

5. **As an abstract processor**, I want PDF bookmarks to be updated automatically using the mapping between original and new index numbers so that bookmarks correctly reference the reordered documents.

6. **As a data administrator**, I want to map Excel columns if they don't match expected names so that I can use files with different column structures.

## Functional Requirements

1. **GUI File Selection**
   - The system must provide a tkinter-based file selection interface
   - The system must default to the user's Downloads folder
   - The system must allow selection of one Excel file (.xlsx) and one PDF file

2. **Column Validation and Mapping**
   - The system must validate that the Excel file contains required columns: Index#, Document Type, Legal Description, Grantee, Grantor, Document Date, Received Date
   - The system must provide a column mapping interface if required columns are missing
   - The system must allow users to map existing columns to required column names

3. **Data Sorting**
   - The system must sort Excel data in the following priority order:
     1. Legal Description (alphabetical)
     2. Grantee (alphabetical) 
     3. Grantor (alphabetical)
     4. Document Type (alphabetical)
     5. Document Date (chronological)
     6. Received Date (chronological)

4. **Index Renumbering**
   - The system must preserve original Index# values in a temporary Original_Index column before sorting
   - The system must renumber the Index# column starting from 1 after sorting
   - The system must increment by 1 for each subsequent row
   - The system must maintain the Original_Index column until PDF processing is complete

5. **Bookmark Processing**
   - The system must read existing PDF bookmarks
   - The system must create a mapping from original Index# values to new Index# values
   - The system must locate PDF bookmarks using the original Index# numbers
   - The system must update bookmark titles with new Index# numbers and current data
   - The system must maintain the format: "Index#-Document Type-Received Date"
   - The system must preserve the M/D/YYYY date format in bookmarks

6. **File Output**
   - The system must create new files with modified names (not overwrite originals)
   - The system must remove the Original_Index column from the final Excel output
   - The system must preserve original file formatting and structure
   - The system must maintain Excel formulas and formatting in non-processed columns

## Non-Goals (Out of Scope)

1. **Column Processing:** Will not process or sort by Effective Date or Adjudicated Date columns
2. **PDF Content Modification:** Will not modify PDF page content, only bookmarks
3. **Multiple File Processing:** Will not process multiple Excel/PDF file pairs simultaneously
4. **Database Integration:** Will not store or retrieve data from external databases
5. **Advanced PDF Operations:** Will not merge, split, or perform other PDF manipulations

## Design Considerations

- **GUI Framework:** Use tkinter for cross-platform compatibility
- **Class Structure:** Implement separate classes for GUI, Excel processing, and PDF processing
- **Error Handling:** Provide clear error messages for file format issues, missing columns, etc.
- **Progress Indication:** Show progress for long-running operations

## Technical Considerations

- **Dependencies:** pandas (Excel processing), PyPDF2 or pymupdf (PDF processing), tkinter (GUI)
- **File Format Support:** Primary focus on .xlsx files, PDF bookmark manipulation
- **Memory Management:** Handle large Excel files efficiently
- **Cross-Platform:** Ensure compatibility across Windows, macOS, and Linux

## Success Metrics

1. **Accuracy:** 100% synchronization between Excel Index# and PDF bookmark numbers
2. **Usability:** Users can complete the process without technical documentation
3. **Performance:** Process typical files (50-100 rows) within 30 seconds
4. **Error Handling:** Clear error messages for all failure scenarios
5. **Extensibility:** New sorting criteria can be added without major refactoring

## Open Questions

1. Should the tool handle duplicate values in sorting columns?
2. How should missing/null values in sorting columns be handled?
3. Should the tool provide preview functionality before making changes?
4. What should happen if PDF bookmarks don't follow the expected format?
5. Should the tool maintain a log of changes made? 