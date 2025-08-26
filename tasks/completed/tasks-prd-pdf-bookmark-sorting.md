## Relevant Files

- `main.py` - Main GUI class needs new checkbox and integration with sorting workflow (COMPLETED: Added BooleanVar attributes, both checkboxes, dependency logic, getter methods, layout improvements, PDF validation integration, conditional sorting workflow)
- `pdf_processor.py` - Core PDF processing class needs natural sorting and page reordering methods (COMPLETED: Added sort_bookmarks_naturally using natsort library, page range detection, page reordering)
- `pdf_validator.py` - New validation class for bookmark conflict detection and PDF validation logic (COMPLETED: Clean static validation methods, no file I/O)
- `requirements.txt` - Added natsort>=8.0.0 for natural sorting functionality (ADDED)
- `excel_processor.py` - May need minor integration points for validation workflow

### Notes

- The sorting feature integrates with existing PDF and GUI processing workflows
- Early validation must occur before any existing processing begins
- Natural sorting requires custom implementation for mixed alphanumeric content

## Tasks

- [x] 1.0 Create Feature Branch for PDF Bookmark Sorting
  - [x] 1.1 Ensure local dev branch is up to date with origin/dev
  - [x] 1.2 Create new feature branch named `feature/pdf-bookmark-sorting` from dev
  - [x] 1.3 Checkout the new feature branch for development work

- [x] 2.0 Add GUI Controls for PDF Bookmark Sorting
  - [x] 2.1 Add two new BooleanVar attributes to AbstractRenumberGUI class: `sort_bookmarks_enabled` and `reorder_pages_enabled` (both default False)
  - [x] 2.2 Create first checkbox in `_create_backup_options` method labeled "Sort PDF Bookmarks"
  - [x] 2.3 Create second checkbox labeled "Reorder Pages to Match Bookmarks" (initially disabled)
  - [x] 2.4 Add event handler to enable/disable second checkbox based on first checkbox state
  - [x] 2.5 Add getter methods `get_sort_bookmarks_enabled()` and `get_reorder_pages_enabled()`
  - [x] 2.6 Update GUI layout to accommodate both checkboxes below backup option
  - [x] 2.7 Test GUI changes to ensure proper layout, functionality, and dependency logic

- [x] 3.0 Implement Early Bookmark Validation
  - [x] 3.1 Create new file `pdf_validator.py` with PDFValidator class
  - [x] 3.2 Add method `validate_bookmark_page_conflicts()` to PDFValidator class
  - [x] 3.3 Implement logic to detect multiple bookmarks pointing to same page number
  - [x] 3.4 Return detailed error information including conflicting bookmark titles and page numbers
  - [x] 3.5 Integrate PDFValidator in `process_files()` method before any other processing
  - [x] 3.6 Add error handling to display conflicts to user and halt processing if conflicts found
  - [x] 3.7 Add status logging for validation results

- [x] 4.0 Implement Natural Sorting Algorithm for Bookmarks
  - [x] 4.1 Add method `natural_sort_key()` to PDFProcessor class for generating sort keys
  - [x] 4.2 Implement logic to separate numeric prefixes from alphabetic suffixes
  - [x] 4.3 Ensure numbers are sorted numerically (1, 2, 10) not lexically (1, 10, 2)
  - [x] 4.4 Implement case-insensitive alphabetic sorting for non-numeric parts
  - [x] 4.5 Add method `sort_bookmarks_naturally()` that reorders PDF outline/bookmarks naturally (pages stay in original positions)
  - [x] 4.6 Test sorting with mixed content like "1-Assignment", "10-Document", "Zoology"

- [x] 5.0 Implement Page Range Detection and Mapping
  - [x] 5.1 Add method `detect_bookmark_page_ranges()` to PDFProcessor class
  - [x] 5.2 Implement logic to determine consecutive pages belonging to each bookmark
  - [x] 5.3 Handle edge cases where bookmarks are not consecutive or overlap
  - [x] 5.4 Create data structure mapping bookmark index to page range (start, end)
  - [x] 5.5 Add validation to ensure page ranges don't conflict between bookmarks
  - [x] 5.6 Test page range detection with various PDF bookmark configurations

- [x] 6.0 Implement PDF Page Reordering Based on Sorted Bookmarks
  - [x] 6.1 Add method `reorder_pages_by_bookmarks()` to PDFProcessor class
  - [x] 6.2 Physically reorder pages to match current bookmark sequence (after bookmark sorting)
  - [x] 6.3 Update bookmark page references to match new page positions
  - [x] 6.4 Ensure page ranges move together as units when reordering
  - [x] 6.5 Preserve all non-bookmark pages in appropriate positions
  - [x] 6.6 Integrate conditional workflow: sort bookmarks if first checkbox checked, reorder pages if second checkbox checked
  - [x] 6.7 Add status logging for reordering progress

- [ ] 7.0 Merge Feature Branch Back to Dev Branch
  - [x] 7.1 Test complete end-to-end functionality with sample Excel and PDF files (Fixed PyPDF2 outlines issue)
  - [ ] 7.2 Verify backward compatibility when sorting option is disabled
  - [ ] 7.3 Ensure all existing functionality still works as expected
  - [ ] 7.4 Commit all changes with descriptive commit messages
  - [ ] 7.5 Switch to dev branch and merge feature branch
  - [ ] 7.6 Delete feature branch after successful merge
  - [ ] 7.7 Push updated dev branch to origin 