# Product Requirements Document: DocumentUnit Architecture Refactor

## Introduction/Overview

The current pipeline architecture has a critical flaw: bookmarks and pages are stored as separate lists in `PipelineContext`, making it possible for pipeline steps to break the fundamental relationship between Excel rows, PDF bookmarks, and their corresponding page ranges. This fragility was exposed when the `ReorderStep` overwrote correctly processed bookmarks, causing data loss.

This PRD defines a refactor to replace the fragile separate lists with an atomic `DocumentUnit` data structure using a memory-efficient two-phase approach that makes it architecturally impossible to break the Excel row ↔ PDF page range relationship.

## Goals

1. **Eliminate Data Coupling Fragility**: Replace separate `bookmarks` and `pages` lists with atomic `DocumentUnit` objects that cannot be broken apart
2. **Establish Document ID as Single Source of Truth**: Make Document ID the immutable key that links Excel rows to PDF page ranges
3. **Maintain 100% Backward Compatibility**: Keep the exact same external API (`RenumberService.run` method signature and return type)
4. **Support Scalable Multi-File Merging**: Handle any number of Excel/PDF pairs (50+) efficiently without memory issues
5. **Implement Two-Phase Processing**: Separate merge complexity from sort complexity for better scalability and maintainability

## User Stories

1. **As a developer**, I want the bookmark-page relationship to be unbreakable so that pipeline steps cannot accidentally corrupt the data structure
2. **As a developer**, I want Document ID to be the permanent anchor that links Excel rows to PDF page ranges, regardless of sorting or filtering operations
3. **As a user**, I want the system to handle 50+ Excel/PDF file pairs efficiently without memory issues or performance degradation
4. **As a developer**, I want per-file linking to prevent Document ID collisions when merging multiple files with duplicate Index# values
5. **As a developer**, I want a two-phase approach that separates merge complexity from sort complexity for better maintainability

## Functional Requirements

### 1. Two-Phase Processing Architecture

#### Phase 1: Per-File Linking and Merging
1.1. **Per-File Processing**: Process each Excel/PDF pair individually to avoid Document ID collisions

1.2. **Document ID Generation**: Generate unique Document IDs for each Excel file using source file path

1.3. **Per-File Linking**: Link PDF bookmarks to Excel rows within each file pair before merging

1.4. **Sequential PDF Merging**: Merge all PDF pages into a single intermediate PDF in file order

1.5. **Page Offset Tracking**: Track page offsets so DocumentUnits know their position in merged PDF

#### Phase 2: Filter, Sort, and Rebuild
1.6. **DataFrame Filtering**: Apply user filters using `_include` flag column instead of removing rows
    - **ARCHITECTURAL DECISION**: Use boolean `_include` column to flag rows for processing
    - **Rationale**: Preserves DocumentUnit ↔ DataFrame alignment, enables reversible filtering
    - **Implementation**: FilterDfStep adds `_include=True/False` based on filter criteria

1.7. **Order-Agnostic Processing**: FilterDfStep and SortDfStep work regardless of execution order
    - **Design Goal**: Maximum flexibility to reorder pipeline steps without code changes
    - **FilterDfStep**: Flags rows with `_include` column, works on any DataFrame state
    - **SortDfStep**: Sorts only flagged rows, preserves unflagged rows in original positions

1.8. **Sorting**: Sort DocumentUnits by filtered DataFrame order using `_include` flag

1.9. **PDF Rebuilding**: Three-phase PyPDF-optimized reconstruction for maximum robustness
    - **Phase A: Page Filtering**: Extract only pages for flagged DocumentUnits (if enabled)
    - **Phase B: Page Reordering**: Arrange pages according to sorted DataFrame order (if enabled)  
    - **Phase C: Bookmark Creation**: Generate fresh outline using PyPDF's `add_outline_item()` API

1.10. **Immutable DocumentUnit Architecture**: DocumentUnit page ranges never change during processing
    - **Immutable Ranges**: `merged_page_range` always points to same location in intermediate PDF
    - **Dynamic Mapping**: Final PDF positions calculated during reconstruction, not stored
    - **Robust Filtering**: Simply exclude DocumentUnits from processing list, never modify ranges

### 2. DocumentUnit Data Structure
2.1. Create a `DocumentUnit` dataclass that atomically couples:
- Document ID (immutable hash key linking to Excel row)
- Page range in merged intermediate PDF
- Linked Excel row data (stored during Phase 1)
- Source file information for debugging

2.2. Document ID must be the permanent identifier that never changes during processing

2.3. Page ranges represent positions in the intermediate merged PDF, not original files

### 3. Memory-Efficient Implementation
3.1. **Sequential File Processing**: Open one PDF at a time during Phase 1, close immediately after processing

3.2. **Lazy Page Access**: Use PyPDF's lazy page loading - never store `list(reader.pages)`

3.3. **Intermediate PDF**: Use temporary merged PDF file instead of keeping all pages in memory

3.4. **DocumentUnit Metadata**: Store only lightweight metadata, not actual page objects

### 4. Pipeline Step Simplification
4.1. **LoadStep**: Handles entire Phase 1 (per-file linking, merging, DocumentUnit creation)

4.2. **FilterDfStep**: Filters DataFrame rows by column values (action_type_step naming)

4.3. **SortDfStep**: Sorts DataFrame rows and renumbers Index# column (action_type_step naming)

4.4. **RebuildPdfStep**: Handles PyPDF-optimized three-phase PDF reconstruction (action_type_step naming)

4.5. **Eliminated Steps**: MergeStep, LinkStep, AddIdsStep, BookmarkStep, ReorderStep become obsolete

### 5. Collision Prevention
5.1. **Per-File Linking**: Link bookmarks to Excel rows within each file before merging to prevent Index# collisions

5.2. **Unique Document IDs**: Use source file path in Document ID generation to ensure uniqueness across files

5.3. **Source Tracking**: Maintain source file information in DocumentUnits for debugging and validation

## Non-Goals (Out of Scope)

- Changing the external API of `RenumberService.run()`
- Modifying the Document ID generation algorithm (keep existing hash-based approach)
- Adding new features beyond architectural improvements
- UI changes or new user-facing functionality
- Changing PDF processing library (continue using PyPDF)

## Technical Considerations

### DocumentUnit Implementation
```python
@dataclass
class DocumentUnit:
    """Atomic unit linking Excel row to PDF page range in merged PDF."""
    document_id: str                           # Immutable hash key linking to Excel
    merged_page_range: Tuple[int, int]        # (start_page, end_page) in intermediate merged PDF
    excel_row_data: pd.Series                 # Linked Excel row (stored during Phase 1)
    source_info: str                          # "excel_path:pdf_path" for debugging
```

### Two-Phase Processing Flow
```python
# Phase 1: Per-File Linking and Merging
for excel_path, pdf_path in file_pairs:
    # Load and link this specific file pair
    pair_df = add_document_ids(load_excel(excel_path), excel_path)
    bookmarks, pages = load_pdf(pdf_path)
    
    # Link bookmarks to Excel rows within this file
    for bookmark in bookmarks:
        original_index = extract_original_index(bookmark['title'])
        matching_row = pair_df[pair_df['Index#'] == original_index]
        if not matching_row.empty:
            create_document_unit(matching_row.iloc[0], bookmark, page_offset)
    
    # Add pages to merged PDF, update offset
    merge_pdf_pages(pages)
    page_offset += len(pages)

# Phase 2: Filter, Sort, Rebuild (PyPDF-Optimized Design)
# FilterDfStep: Flag rows instead of removing them
df['_include'] = df['Document Type'].isin(['Deed', 'Assignment'])

# SortDfStep: Sort only flagged rows, preserve all rows
included_mask = df['_include']
df.loc[included_mask] = sort_and_renumber(df[included_mask])

# RebuildPdfStep: Three-phase PDF reconstruction
def rebuild_pdf_with_immutable_units(document_units, df_flagged, intermediate_pdf):
    # Phase A: Filter DocumentUnits (ranges never change!)
    flagged_doc_ids = set(df_flagged['Document_ID'])
    filtered_units = [u for u in document_units if u.document_id in flagged_doc_ids]
    
    # Phase B: Reorder by DataFrame order
    df_order = {doc_id: idx for idx, doc_id in enumerate(df_flagged['Document_ID'])}
    sorted_units = sorted(filtered_units, key=lambda u: df_order.get(u.document_id, 999))
    
    # Phase C: Create fresh PDF with PyPDF bookmarks
    writer = PdfWriter()
    writer.page_mode = "/UseOutlines"  # Show bookmark panel
    current_page = 0
    
    for unit in sorted_units:
        # Extract from IMMUTABLE intermediate PDF range
        start, end = unit.merged_page_range
        for page_idx in range(start-1, end):  # Convert to 0-based
            writer.add_page(intermediate_pdf.pages[page_idx])
        
        # Add bookmark pointing to final PDF position
        title = make_titles(df_flagged)[unit.document_id]
        writer.add_outline_item(title, current_page)
        current_page += (end - start + 1)
    
    return writer
```

### Memory Efficiency
- **No Page Objects Stored**: DocumentUnits contain only metadata, not page objects
- **Sequential Processing**: One PDF file open at a time during Phase 1
- **Intermediate File**: Use temporary merged PDF instead of in-memory page collections
- **Lazy Access**: Extract pages from intermediate PDF only when building final output

### Pipeline Simplification
- **Consolidated LoadStep**: Handles all of Phase 1 (linking, merging, DocumentUnit creation)
- **Simplified Steps**: FilterDfStep, SortDfStep, RebuildPdfStep replace complex multi-step pipeline
- **Eliminated Complexity**: No more merge-specific conditional logic or separate linking steps
- **Action_Type_Step Naming**: Clear naming convention (action + data type + step)
  - **FilterDfStep**: Filters DataFrame rows by column values
  - **SortDfStep**: Sorts DataFrame rows and renumbers Index# column  
  - **RebuildPdfStep**: Rebuilds PDF with three-phase PyPDF architecture

### Order-Agnostic Filter/Sort Design
- **Problem**: Traditional approach removes DataFrame rows, breaking DocumentUnit alignment
- **Solution**: Use `_include` flag column to mark rows for processing without removing them
- **Benefits**:
  - **DocumentUnit Integrity**: All DocumentUnits remain aligned with DataFrame rows
  - **Reversible Filtering**: Can easily toggle filters without data loss
  - **Order Independence**: FilterDfStep and SortDfStep work regardless of execution order
  - **Performance Flexibility**: Can optimize pipeline order without code changes
- **Implementation**:
  - **FilterDfStep**: Adds `_include=True/False` based on filter criteria
  - **SortDfStep**: Sorts only rows where `_include=True`, preserves others
  - **Later Steps**: Use `df[df['_include']]` to process only flagged rows

### PyPDF-Optimized PDF Reconstruction
- **Problem**: Traditional bookmark preservation is fragile and error-prone
- **Solution**: Three-phase reconstruction using PyPDF's native capabilities
- **Architecture**:
  - **Immutable DocumentUnits**: Page ranges never change, always point to intermediate PDF
  - **Dynamic Position Mapping**: Final PDF positions calculated during reconstruction
  - **Fresh Bookmark Generation**: Use `PdfWriter.add_outline_item()` for reliable bookmarks
- **Benefits**:
  - **Maximum Robustness**: Never fails due to bookmark corruption or format issues
  - **PyPDF Native**: Leverages library's strengths instead of fighting limitations
  - **Flexible Filtering**: Can exclude pages without complex range recalculation
  - **Optimal Performance**: Single-pass reconstruction with minimal memory usage
- **Three-Phase Process**:
  1. **Filter Pages**: Extract only DocumentUnits for flagged DataFrame rows
  2. **Reorder Pages**: Arrange according to sorted DataFrame order (if enabled)
  3. **Create Bookmarks**: Generate fresh outline pointing to final page positions

### Backward Compatibility
- External API (`RenumberService.run`) remains identical
- PipelineContext can provide computed properties if needed for compatibility
- Existing tests should pass without modification

## Success Metrics

1. **Zero Data Corruption**: Impossible to break bookmark-page relationships during pipeline execution
2. **Scalable Multi-File Processing**: Successfully handles 50+ Excel/PDF pairs without memory issues
3. **Collision Prevention**: No Document ID collisions when merging files with duplicate Index# values
4. **Test Compatibility**: All existing tests pass without modification
5. **Memory Efficiency**: Memory usage remains constant regardless of number of files processed
6. **Bug Resolution**: The ReorderStep bookmark loss issue is permanently resolved
7. **Code Simplification**: Significant reduction in pipeline complexity and conditional logic

## Open Questions

1. Should we implement progress tracking for long-running multi-file operations?
2. How should we handle PDF bookmarks that cannot be linked to Excel rows (orphaned bookmarks)?
3. What's the optimal temporary file cleanup strategy for the intermediate merged PDF?
4. Should we add validation to detect and report Document ID linking failures?

## Implementation Notes

This refactor addresses the root cause of the current bookmark loss bug by implementing a two-phase approach that:

1. **Eliminates Collision Risk**: Per-file linking prevents Document ID collisions that occur when multiple files have overlapping Index# values
2. **Ensures Atomic Relationships**: DocumentUnits make it architecturally impossible to break Excel row ↔ PDF page range relationships
3. **Scales Efficiently**: Memory-efficient design handles large numbers of files without performance degradation
4. **Simplifies Logic**: Two-phase separation eliminates complex conditional branching and merge-specific code paths

The architecture maintains backward compatibility while providing a robust foundation for reliable multi-file processing at scale.
