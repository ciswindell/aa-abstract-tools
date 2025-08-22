# PDF Bookmark Sorting Feature - Product Requirements Document

## Introduction/Overview

This feature adds an optional PDF bookmark sorting capability to the Abstract Renumber Tool. After the standard renumbering process, users can choose to sort PDF bookmarks alphabetically using a two-step process: first sorting the PDF outline/bookmarks while leaving pages in their original positions, then physically reordering the pages to match the sorted bookmark sequence. This makes the final processed PDF easier to navigate and search through.

## Goals

1. Provide users with an optional way to alphabetically sort PDF bookmarks after renumbering
2. Maintain page-to-bookmark relationships by moving page ranges together when physically reordering pages
3. Preserve the existing renumbering workflow while adding sorting as an optional post-process step
4. Improve PDF navigation experience for end users of the processed documents

## User Stories

- **As a user processing abstract documents**, I want to sort PDF bookmarks alphabetically so that the final output PDF is easier to navigate and find specific documents.
- **As a user**, I want to sort just the bookmarks without reordering pages when I only need to improve navigation without changing page structure.
- **As a user**, I want the option to physically reorder pages to match sorted bookmarks when I need the PDF structure to be completely reorganized.
- **As a user**, I want these options to be separate and optional so I can choose the level of reorganization based on my specific needs.

## Functional Requirements

1. **GUI Addition**: Add two checkboxes to the processing options section of the GUI:
   - "Sort PDF Bookmarks" - Controls bookmark outline sorting
   - "Reorder Pages to Match Bookmarks" - Controls physical page reordering
2. **Default State**: Both checkboxes must be unchecked by default
3. **Checkbox Dependency**: The "Reorder Pages" checkbox must only be enabled when "Sort PDF Bookmarks" is checked
4. **Processing Sequence**: Based on selected options, processing occurs after the standard renumbering process:
   - First: Validate that no multiple bookmarks point to the same page (before any other processing)
   - Second: Complete existing renumbering workflow (Excel sorting, PDF bookmark renaming)
   - Third: If "Sort PDF Bookmarks" is checked - Sort the PDF outline/bookmarks using natural sort order (pages remain in original positions)
   - Fourth: If "Reorder Pages to Match Bookmarks" is checked - Physically reorder PDF pages to match the sorted bookmark sequence
5. **Page Range Handling**: When a bookmark represents multiple consecutive pages, all pages in that range must move together as a unit
6. **Bookmark Scope**: All bookmarks are sorted alphabetically, regardless of whether they follow the expected Index# format
7. **Natural Sorting**: Bookmark sorting must use natural sort order (numbers before letters) and be case-insensitive, so "1-Assignment" comes before "Zoology"
8. **Error Detection**: System must detect and report errors when multiple bookmarks point to the same page number, and this validation must occur before any other processing begins

## Non-Goals (Out of Scope)

1. **Custom Sort Criteria**: Users cannot choose different sorting criteria (only alphabetical by full bookmark title)
2. **Partial Sorting**: Cannot sort only specific bookmarks or bookmark subsets
3. **Manual Reordering**: No drag-and-drop or manual bookmark reordering interface
4. **Sort Preview**: No preview of sorted order before processing
5. **Undo Functionality**: No ability to undo sorting after processing is complete

## Design Considerations

- Both checkboxes should be placed in the existing "Processing Options" section alongside the backup option
- Maintain consistent styling with existing GUI elements
- The checkboxes should have clear labeling and be visually grouped with other processing options
- The "Reorder Pages" checkbox should be visually indented or styled to show dependency on the first checkbox
- Clear visual feedback when the second checkbox is disabled/enabled based on first checkbox state

## Technical Considerations

- Must integrate with existing PDFProcessor class and bookmark handling logic
- Requires new methods for:
  - Early validation to detect multiple bookmarks pointing to the same page (before any processing)
  - Detecting page ranges associated with each bookmark
  - Natural sorting of bookmarks (numbers before letters, case-insensitive)
  - Two-step sorting process:
    1. Sort PDF outline/bookmarks (leaving pages in original positions)
    2. Physically reorder pages to match sorted bookmark sequence
  - Updating bookmark page references after page reordering
- Error validation must be performed at the very beginning of the process, before Excel processing or any other operations
- Preserve existing backup and file handling workflows

## Success Metrics

1. **Functionality**: PDF bookmarks are correctly sorted using natural sort order (numbers before letters, case-insensitive)
2. **Page Integrity**: Pages are reordered to match bookmark order without corruption or loss
3. **Error Detection**: System successfully identifies and reports bookmark conflicts before any processing begins
4. **User Experience**: Feature integrates seamlessly with existing workflow
5. **Backward Compatibility**: Existing functionality remains unchanged when sorting is disabled

## Open Questions

1. Should there be a progress indicator for the sorting process, especially for large PDFs?
2. How should the system handle edge cases where bookmark page detection fails?
3. Should the sorting operation be logged in the status area for user feedback? 