### Introduction / Overview

Add filter and merge options to the existing single, canonical processing workflow. The workflow order is fixed; options gate whether specific steps execute. Filter lets a user select an Excel column and choose one or more values to keep; Excel and PDF outputs include only those records, removing filtered-out rows, pages, and bookmarks. Merge lets a user select multiple Excel/PDF pairs to combine into a single, renumbered Excel and a single PDF, honoring existing bookmark sorting and page reordering options. Merge does not modify the original inputs (backups are not created in merge mode).

### Goals

- Enable filtering by column with multi-select values and produce matched Excel/PDF outputs.
- Enable merging multiple Excel/PDF pairs into one renumbered Excel and one PDF.
- Preserve the single pipeline order; use options to include/exclude steps.
- Maintain data integrity: consistent Document_ID linkage, correct page/bookmark mappings, sequential Index#.
- Keep UI simple and guided: filter picker and merge-pairs selector dialogs.

### Guiding Principles

- Keep it simple: minimum code and UI necessary to achieve the outcomes.
- Follow SOLID: small, focused functions; clear interfaces; easy to extend steps without modifying existing ones.
- Avoid overengineering: no abstraction until needed; reuse existing repos/validators/transforms.
- DRY: share the single pipeline and gate steps via options rather than branching flows.

### User Stories

- As a user, I can select a column, pick one or more values from that column, and generate filtered Excel/PDF where only those records remain; removed records have their corresponding PDF pages and bookmarks omitted.
- As a user, I can select multiple Excel/PDF pairs to merge, confirm the list, and generate one combined, renumbered Excel and one PDF with bookmarks/titles sorted per existing options.
- As a user, I can use the existing options (sort bookmarks, reorder pages) with filter and with merge.

### Functional Requirements

1. Options and Modes
   1.1 The workflow remains a single fixed sequence; options determine which steps execute.
   1.2 Add filter options: `filter_column` (string) and `filter_values` (list of strings).
   1.3 Add merge option: user supplies N pairs of (Excel, PDF) inputs via a guided UI.
   1.4 When merge is enabled, disable the backup option (original files are not modified in merge mode).

2. UI: Filter
   2.1 Provide a dialog to select a column from the loaded Excel sheet.
   2.2 After the column is chosen, read distinct values from that column and present a multi-select list.
   2.3 Store the selected values into `filter_values` and proceed with processing.

3. UI: Merge
   3.1 If merge is selected, open a dialog to add one or more pairs of Excel/PDF files.
   3.2 Each pair requires both a valid Excel file and a matching PDF file; show validation errors if not provided.
   3.3 Allow users to add additional pairs, review the list, remove entries, and confirm.
   3.4 After confirmation, run processing across all selected pairs to produce one merged output.

4. Workflow Order (fixed)
   4.1 Load and validate inputs (for merge: for each pair).
   4.2 Clean types.
   4.3 Add Document_IDs.
   4.4 Merge data (optional; only when merge is enabled).
   4.5 Filter data (optional; only when filter is enabled).
   4.6 Sort and renumber (Index# sequential).
   4.7 Save Excel output.
   4.8 Write PDF output (apply existing options: sort bookmarks, reorder pages).

5. Filtering Behavior
   5.1 Filtering operates after Document_ID assignment (and after merging, if enabled).
   5.2 Excel output contains only rows where `filter_column` ∈ `filter_values`.
   5.3 PDF output omits pages and bookmarks that correspond to filtered-out rows; only remaining records are present.

6. Merging Behavior
   6.1 Load and validate each pair independently using existing validation.
   6.2 Combine DataFrames from all pairs; proceed with a single transform/renumber pass.
   6.3 Construct combined PDF by concatenating pages and bookmarks from all pairs; then apply existing sorting/bookmark title updates and optional page reordering according to the final renumbered order.

7. Outputs and Naming
   7.1 Renumber-only and Filter: do not overwrite originals by default; write to sibling files using a suffix (e.g., `_filtered` when filtering). If unchanged from today for renumber-only, retain current behavior.
   7.2 Merge: always write `merged.xlsx` and `merged.pdf` to the chosen output directory; originals remain untouched and backups are not created.
   7.3 If outputs already exist, prompt to overwrite or choose a different location.

8. Validation
   8.1 Use existing validation for Excel/PDF inputs.
   8.2 For merge: if required columns are missing in any pair, show a clear error and abort.
   8.3 If filtering yields zero rows, present a warning and allow the user to cancel or proceed to generate empty outputs.

### Non-Goals (Out of Scope)

- Advanced filtering operators (e.g., ranges, regex) beyond selecting exact values.
- Cross-sheet merging or filtering across multiple Excel sheets.
- Fuzzy matching of bookmarks to Excel rows beyond existing linkage logic.
- Automatic schema reconciliation beyond shared column names and required columns.
- Generic workflow engines, plugin systems, or needless abstractions beyond what’s required here.

### Design Considerations (Optional)

- UI
  - Add a small filter dialog (column dropdown, values multi-select, OK/Cancel).
  - Add a merge dialog with a pair list: (Excel, PDF) per row; add/remove rows; confirm.
- Workflow
  - Keep a single pipeline; use option-gated steps (`maybe(...)`).
  - Preserve existing repos, validators, and transforms; add minimal, pure filter/merge transforms.

### Technical Considerations (Optional)

- Ensure Document_ID creation runs before filter/merge to keep linkage intact.
- For merge, maintain per-source page ranges so page reordering can be applied after concatenation.
- Avoid touching input files in merge; write outputs to a chosen folder.
- Large PDFs: handle memory prudently (stream pages where repo supports it).

### Success Metrics

- Filtered outputs contain only selected values; PDF pages/bookmarks for removed rows are omitted.
- Merged outputs contain all input records; Index# is sequential from 1..N.
- Bookmark titles reflect renumbered order; optional natural sorting and page reordering work as before.
- No destructive changes to originals during merge; backups disabled in merge mode.
- Zero critical errors across representative datasets used today.

### Open Questions

- Output location defaults: where should filtered/merged files be written by default?
- Overwrite policy: auto-suffix vs. prompt for all modes?
- Maximum number of merge pairs supported in the UI?
- Case sensitivity/whitespace rules when matching filter values?
- Behavior when filter results are empty: proceed to empty outputs or force cancel?
- Any constraints on dataset size (rows, pages) that require guarding in UI?


