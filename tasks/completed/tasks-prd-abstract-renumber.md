# Tasks: Abstract Renumber Tool

## Relevant Files

- `abstract_renumber.py` - Main application class with tkinter GUI and core processing logic (created)
- `excel_processor.py` - Class for handling Excel file operations and data sorting
- `excel_formatter.py` - Class for handling Excel formatting operations (column widths, alignment, text wrapping, date formatting)
- `pdf_processor.py` - Class for handling PDF bookmark operations (created)
- `column_mapper.py` - Dialog class for mapping Excel columns to required fields
- `requirements.txt` - Project dependencies list (created)
- `README.md` - Project documentation and usage instructions (created)

### Notes

- This is a standalone Python application using tkinter for the GUI
- Use `python3 -m pip install -r requirements.txt` to install dependencies
- The application should be executable directly with `python3 abstract_renumber.py`

## Tasks

- [x] 1.0 Setup Project Structure and Dependencies
  - [x] 1.1 Create requirements.txt file with pandas, PyPDF2, and pathlib dependencies
  - [x] 1.2 Set up project directory structure and organize files
  - [x] 1.3 Create initial README.md with installation and usage instructions
  - [x] 1.4 Validate/create virtual environment and verify dependencies are installed correctly

- [x] 2.0 Implement GUI Interface with tkinter
  - [x] 2.1 Create main window with proper title, size, and layout
  - [x] 2.2 Add file selection section with labels and browse buttons for Excel and PDF files
  - [x] 2.3 Implement file dialogs that default to user's Downloads folder
  - [x] 2.4 Add status text area with scrollbar for logging messages
  - [x] 2.5 Create process button that remains disabled until both files are selected
  - [x] 2.6 Implement file selection state management and UI updates

- [x] 3.0 Add Column Validation and Mapping Features
  - [x] 3.1 Validate Excel file contains required columns: Index#, Document Type, Legal Description, Grantee, Grantor, Document Date, Received Date
  - [x] 3.2 Create ColumnMappingDialog class with tkinter interface for missing columns
  - [x] 3.3 Allow users to select existing columns from dropdown to map to required column names
  - [x] 3.4 Apply column mappings by renaming DataFrame columns
  - [x] 3.5 Handle validation errors and provide clear error messages to users

- [x] 4.0 Create Excel File Processing Logic
  - [x] 4.1 Load Excel file into pandas DataFrame with proper data type handling
  - [x] 4.2 Implement multi-column sorting: Legal Description, Grantee, Grantor, Document Type, Document Date, Received Date
  - [x] 4.3 Handle null/missing values in sorting columns by filling with empty strings
  - [x] 4.4 Renumber Index# column starting from 1 and incrementing by 1
  - [x] 4.5 Preserve original Excel formatting and formulas in non-processed columns
  - [x] 4.6 Add temporary Excel export for testing (create test output file with "_test_sorted" suffix)
  - [x] 4.7 Preserve or set appropriate column widths from source worksheet using openpyxl
  - [x] 4.8 Apply text wrapping to all cells for better content display
  - [x] 4.9 Format date columns (Document Date, Received Date) with M/D/YYYY column formatting
  - [x] 4.10 Preserve original cell alignment (horizontal: left/center/right, vertical: top/center/bottom) from source Excel file
  - [x] 4.11 Modify Excel processing workflow to preserve original index numbers for PDF bookmark mapping
    - [x] 4.11.1 Add new column "Original_Index" to store original Index# values before sorting
    - [x] 4.11.2 Populate Original_Index column with current Index# values during data loading
    - [x] 4.11.3 Modify sort_data() method to preserve Original_Index column during sorting operations
    - [x] 4.11.4 Update renumbering logic to only affect Index# column, keeping Original_Index unchanged

- [x] 5.0 Implement PDF Bookmark Management
  - [x] 5.1 Read existing PDF file and extract current bookmark structure using PyPDF2
  - [x] 5.2 Copy all PDF pages to new PdfWriter object
  - [x] 5.3 Generate new bookmark titles in format: "Index#-Document Type-Received Date"
  - [x] 5.4 Format dates as M/D/YYYY maintaining original date format from Excel
  - [x] 5.5 Add new bookmarks to PDF with appropriate page references

- [x] 6.0 Handle File Output Operations
  - [x] 6.1 Generate output filenames by adding "_renumbered" suffix before file extension
  - [x] 6.2 Save processed Excel file using pandas to_excel() preserving original formatting
  - [x] 6.3 Save updated PDF file with new bookmark structure
  - [x] 6.4 Provide user feedback showing successful file creation with output filenames
  - [x] 6.5 Handle file write permissions and errors gracefully with appropriate error messages
  - [x] 6.6 Remove temporary testing Excel export code from section 4.6
  - [x] 6.7 Ensure Original_Index column is excluded from final Excel output (remove after PDF processing)

- [x] 7.0 Fix PDF Bookmark Preservation Issue
  - [x] 7.1 Preserve existing bookmarks that don't match the expected format (Index#-Document Type-Date)
  - [x] 7.2 Only update bookmarks that match the expected format and have corresponding Excel data
  - [x] 7.3 Maintain original bookmark structure and hierarchy for non-matching bookmarks  
  - [x] 7.4 Enhance user feedback to show counts of updated vs preserved bookmarks
  - [x] 7.5 Handle edge case where no new bookmark titles are generated (preserve all existing)

- [x] 8.0 Fix Excel Data Sorting Issue  
  - [x] 8.1 Add proper data type preparation before sorting (dates as datetime, strings cleaned)
  - [x] 8.2 Implement _prepare_sorting_data_types() method to ensure proper sorting behavior
  - [x] 8.3 Enhanced _process_data_types() method to better handle text and date columns
  - [x] 8.4 Add comprehensive debugging output to verify sorting is working correctly
  - [x] 8.5 Ensure sort_data() properly reorders rows by Legal Description, Grantee, Grantor, Document Type, Document Date, Received Date 

- [x] 9.0 Code Cleanup and Optimization
  - [x] 9.1 Remove debug print statements (~25 occurrences across modules)
  - [x] 9.2 Remove unused traceback import in excel_processor.py
  - [x] 9.3 Clean up temporary fix comments and replace with professional documentation
  - [x] 9.4 Replace broad Exception catches with specific exception types
  - [x] 9.5 Remove unused methods and instance variables
  - [x] 9.6 Add comprehensive docstring validation and cleanup for all public methods
  - [x] 9.7 Validate all imports are actually used and remove unused ones
  - [x] 9.8 Add type hints validation for all function parameters and return values

- [x] 10.0 Enhanced File Naming with Backup System
  - [x] 10.1 Design backup file naming strategy with datetime stamps (format: filename_backup_YYYY-MM-DD_HH-MM-SS.ext)
  - [x] 10.2 Implement file backup functionality to rename original files before processing
  - [x] 10.3 Update output filename generation to use original filenames instead of "_renumbered" suffix
  - [x] 10.4 Add safe file operations with rollback capability in case of processing failure
  - [x] 10.5 Update user interface feedback to inform users about backup file creation
  - [x] 10.6 Add validation to ensure backup operations don't overwrite existing backup files
  - [x] 10.7 Add GUI checkbox for "Backup Files" (checked by default) to control backup creation and remove popup dialogs for better UX
  - [x] 10.8 Update file access validation to check backup file creation permissions
  - [x] 10.9 Implement error handling for backup file creation failures with user guidance 

- [x] 11.0 MAJOR SIMPLIFICATION: Reduce Codebase Complexity
  - [x] 11.1 Remove excessive file access validation - keep only basic file existence checks
  - [x] 11.2 Drastically reduce status logging - keep only essential user feedback (start, complete, errors)
  - [x] 11.3 Remove complex file permission checking and atomic operations
  - [x] 11.4 Remove backup system rollback complexity - simple copy with error handling
  - [x] 11.5 Keep modular architecture but simplify each class by removing over-validation
  - [x] 11.7 Remove comprehensive error recovery systems - basic try/catch sufficient
  - [x] 11.8 Remove detailed progress updates during processing steps
  - [x] 11.10 Consolidate similar validation methods into single functions
  - [x] 11.11 Remove defensive programming patterns that add complexity without value
  - [x] 11.12 Test simplified version maintains core functionality and user experience
