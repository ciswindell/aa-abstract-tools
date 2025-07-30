## Relevant Files

- `abstract_renumber.py` - Main GUI class needs new checkbox and integration with sorting workflow
- `pdf_processor.py` - Core PDF processing class needs natural sorting and page reordering methods
- `pdf_validator.py` - New validation class for bookmark conflict detection and PDF validation logic
- `excel_processor.py` - May need minor integration points for validation workflow

### Notes

- The sorting feature integrates with existing PDF and GUI processing workflows
- Early validation must occur before any existing processing begins
- Natural sorting requires custom implementation for mixed alphanumeric content

## Tasks

- [ ] 1.0 Create Feature Branch for PDF Bookmark Sorting
  - [ ] 1.1 Ensure local dev branch is up to date with origin/dev
  - [ ] 1.2 Create new feature branch named `feature/pdf-bookmark-sorting` from dev
  - [ ] 1.3 Checkout the new feature branch for development work

- [ ] 2.0 Add GUI Controls for PDF Bookmark Sorting
  - [ ] 2.1 Add two new BooleanVar attributes to AbstractRenumberGUI class: `sort_bookmarks_enabled` and `reorder_pages_enabled` (both default False)
  - [ ] 2.2 Create first checkbox in `_create_backup_options` method labeled "Sort PDF Bookmarks"
  - [ ] 2.3 Create second checkbox labeled "Reorder Pages to Match Bookmarks" (initially disabled)
  - [ ] 2.4 Add event handler to enable/disable second checkbox based on first checkbox state
  - [ ] 2.5 Add getter methods `get_sort_bookmarks_enabled()` and `get_reorder_pages_enabled()`
  - [ ] 2.6 Update GUI layout to accommodate both checkboxes below backup option
  - [ ] 2.7 Test GUI changes to ensure proper layout, functionality, and dependency logic

- [ ] 3.0 Implement Early Bookmark Validation
  - [ ] 3.1 Create new file `pdf_validator.py` with PDFValidator class
  - [ ] 3.2 Add method `validate_bookmark_page_conflicts()` to PDFValidator class
  - [ ] 3.3 Implement logic to detect multiple bookmarks pointing to same page number
  - [ ] 3.4 Return detailed error information including conflicting bookmark titles and page numbers
  - [ ] 3.5 Integrate PDFValidator in `process_files()` method before any other processing
  - [ ] 3.6 Add error handling to display conflicts to user and halt processing if conflicts found
  - [ ] 3.7 Add status logging for validation results

- [ ] 4.0 Implement Natural Sorting Algorithm for Bookmarks
  - [ ] 4.1 Add method `natural_sort_key()` to PDFProcessor class for generating sort keys
  - [ ] 4.2 Implement logic to separate numeric prefixes from alphabetic suffixes
  - [ ] 4.3 Ensure numbers are sorted numerically (1, 2, 10) not lexically (1, 10, 2)
  - [ ] 4.4 Implement case-insensitive alphabetic sorting for non-numeric parts
  - [ ] 4.5 Add method `sort_bookmarks_naturally()` that reorders PDF outline/bookmarks naturally (pages stay in original positions)
  - [ ] 4.6 Test sorting with mixed content like "1-Assignment", "10-Document", "Zoology"

- [ ] 5.0 Implement Page Range Detection and Mapping
  - [ ] 5.1 Add method `detect_bookmark_page_ranges()` to PDFProcessor class
  - [ ] 5.2 Implement logic to determine consecutive pages belonging to each bookmark
  - [ ] 5.3 Handle edge cases where bookmarks are not consecutive or overlap
  - [ ] 5.4 Create data structure mapping bookmark index to page range (start, end)
  - [ ] 5.5 Add validation to ensure page ranges don't conflict between bookmarks
  - [ ] 5.6 Test page range detection with various PDF bookmark configurations

- [ ] 6.0 Implement PDF Page Reordering Based on Sorted Bookmarks
  - [ ] 6.1 Add method `reorder_pages_by_bookmarks()` to PDFProcessor class
  - [ ] 6.2 Physically reorder pages to match current bookmark sequence (after bookmark sorting)
  - [ ] 6.3 Update bookmark page references to match new page positions
  - [ ] 6.4 Ensure page ranges move together as units when reordering
  - [ ] 6.5 Preserve all non-bookmark pages in appropriate positions
  - [ ] 6.6 Integrate conditional workflow: sort bookmarks if first checkbox checked, reorder pages if second checkbox checked
  - [ ] 6.7 Add status logging for reordering progress

- [ ] 7.0 Merge Feature Branch Back to Dev Branch
  - [ ] 7.1 Test complete end-to-end functionality with sample Excel and PDF files
  - [ ] 7.2 Verify backward compatibility when sorting option is disabled
  - [ ] 7.3 Ensure all existing functionality still works as expected
  - [ ] 7.4 Commit all changes with descriptive commit messages
  - [ ] 7.5 Switch to dev branch and merge feature branch
  - [ ] 7.6 Delete feature branch after successful merge
  - [ ] 7.7 Push updated dev branch to origin 