## Introduction/Overview

This feature introduces an “input-as-template” Excel handling flow to ensure exported workbooks retain exactly the same sheets, columns, column order, and formatting (including widths, number formats, styles, filters, freeze panes, validations, conditional formatting, hidden flags, row heights, and merged cells) as the input. It addresses prior fragility in column width computation and formatting replication by avoiding re-creation of layouts. The existing renumbering logic and formula handling must remain unchanged; this work focuses solely on improving input/output handling reliability while keeping naming and functionality consistent with the current codebase.

## Goals

1. Preserve the full workbook structure and formatting from input to output for .xlsx files only.
2. Ensure exported data retains all original columns (including extra/unexpected ones) and their order and formatting.
3. Use the designated processing sheet by name; if not found, prompt the user via GUI to select the sheet.
4. Validate required columns (case-insensitive) based on the existing list in code; hard fail with a GUI message when any are missing.
5. Do not change existing processing logic, data mutation rules, or formula handling.
6. Maintain current naming conventions and integration points.
7. Perform output writes atomically to avoid partial files, preserve originals, and respect existing backup options.
8. Adhere to SOLID and DRY principles across design and implementation.
9. Replace column mapping with simple validation; remove the mapping module and UI.

## User Stories

1. As a user, I want the exported workbook to look the same as my input (all sheets, formatting, column widths) so I don’t need to fix formatting after processing.
2. As a user, I want the tool to automatically use the designated sheet for renumbering by its name, or let me choose the correct sheet if it isn’t found, so I can continue without editing my file.
3. As a user, I want a clear error if a required column is missing, so I can correct the input and rerun.

## Functional Requirements

1. Input Format
   1.1 The system must accept .xlsx files only.
   1.2 The system must support single-row headers.
   1.3 The system must support multiple sheets in the workbook.

2. Sheet Selection
   2.1 The system must target a specific sheet name for processing (exact name, case-sensitive match unless existing code specifies otherwise).
   2.2 If the target sheet is not found, the system must show a GUI to let the user select which sheet contains the data to process.
   2.3 All non-target sheets must be preserved unchanged in the output.

3. Required Columns
   3.1 The list of required columns must come from the existing codebase and remain the single source of truth.
   3.2 Required column name checks must be case-insensitive.
   3.3 Column order does not matter for validation.
   3.4 There must be no duplicate column names among the required set (case-insensitive). Duplicates outside the required set are allowed.
   3.5 If any required column is missing, the system must hard fail and show a GUI message listing missing columns. No auto-creation of columns. No column-mapping UI.

4. Output Preservation
   4.1 The system must preserve all sheets from the input workbook in the output workbook.
   4.2 The system must preserve the exact column order from the input on the processing sheet.
   4.3 The system must preserve all formatting and layout, including (but not limited to) column widths, number formats, styles, alignments, filters, freeze panes, data validations, conditional formatting, hidden states, row heights, merged cells, named ranges, and tables.
   4.4 Any additional/unexpected columns present in the input must be preserved in the output with their formatting and values.

5. Processing Constraints
   5.1 The existing processing logic must remain unchanged.
   5.2 The existing formula handling must remain unchanged.
   5.3 Data mutations must occur only within the current processing flow and only on the target sheet.

6. Performance and Scale
   6.1 The system should handle up to ~1,000 data rows comfortably.

7. Error Handling and UX
   7.1 If the required sheet is missing, the system must present a GUI sheet picker.
   7.2 If required columns are missing, the system must present a GUI error listing missing columns and abort.
   7.3 Error messages should be concise and reference exact sheet/column names as seen in the workbook.
   7.4 On any error during export, no partial or temporary files should remain in the user’s directory.
   7.5 The original input file must never be modified; treat it as read-only.
   7.6 Respect existing backup options/behavior; do not disable or alter them.

## Non-Goals (Out of Scope)

1. Supporting file formats other than .xlsx.
2. Changing existing processing or renumbering functionality.
3. Changing or adding formula handling logic.
4. Enforcing layout checks beyond preserving what exists (no new checks for freeze panes, filters, widths, etc.).
5. Reordering or renaming columns.
7. Restoring or maintaining the column-mapping UI/logic.
6. Validating column widths or other layout metrics.

## Design Considerations (Optional)

1. Input-as-template flow: open the input workbook, immediately save a copy as the output workbook, then perform in-place data updates on the designated sheet only. This avoids rebuilding formatting programmatically.
2. The GUI required for sheet selection and missing-required-columns errors should match the current project’s UX conventions and naming patterns.
3. Continue to leverage the current validation mechanisms in the codebase; add only the case-insensitive required column check where necessary without altering existing validation semantics.
4. Keep any public API signatures, naming conventions, and entry points consistent with the current codebase to avoid downstream changes.
5. SOLID/DRY guidance: separate responsibilities (e.g., SheetSelectionUI, RequiredColumnsValidator, WorkbookExporter), inject dependencies (e.g., sheet name provider, backup policy), and avoid duplicated formatting logic by reusing the input-as-template approach. Remove `ColumnMapper` entirely to simplify control flow; use a small `InputSheetValidator`.

## Technical Considerations (Optional)

1. Library Choice
   1.1 Any Python library that supports .xlsx read/write with full preservation of styles and workbook features is acceptable (e.g., openpyxl), provided it aligns with existing project dependencies.

2. Preservation Strategy
   2.1 Prefer workbook-level copy (input-as-template) over reconstructing formatting.
   2.2 Ensure operations target only the designated sheet and intended cell ranges to avoid unintended style normalization.
   2.3 Do not modify the input file; all writes target a separate output path.

3. Validation
   3.1 Use the existing required column list in the codebase; enforce case-insensitive presence checks.
   3.2 Do not add layout validations or width checks.

4. Integration
   4.1 Keep the same naming conventions and functionality as the current codebase.
   4.2 Integrate the sheet selection GUI and missing-column GUI at the points where the current code determines the working sheet and validates headers.
   4.3 Ensure compatibility with existing backup options (e.g., prior backup/rollback settings) without changing their semantics.

5. Performance
   5.1 Typical datasets are <1,000 rows; performance optimizations beyond the preservation approach are not required.

6. Atomic and Safe File Handling
   6.1 Use an atomic write pattern: write to a temporary file (preferably in the same directory), ensure data is flushed/synced, then rename/move to the final output path.
   6.2 If the process fails at any point before atomic rename, delete the temporary file and do not alter the target output file.
   6.3 If an output file already exists, follow current project conventions (e.g., prompt, unique suffix, or respect backup option) before overwrite; never silently overwrite unless existing behavior specifies it.
   6.4 Temporary files must use a clear, hidden or distinctive naming pattern and be cleaned up on both success and failure paths.

## Success Metrics

1. The output workbook is visually and structurally identical to the input, except for the intended data mutations on the target sheet.
2. All extra columns and all other sheets are present and formatted identically in the output.
3. If the target sheet is absent, a GUI sheet picker appears and a valid selection proceeds.
4. If required columns are missing, a GUI error shows exactly which ones, and processing aborts.
5. No changes to the renumbering results or formula behavior compared to the current implementation when given the same valid input.

## Open Questions

1. What is the exact configured name of the processing sheet, and where is it defined in code? Should it be configurable via settings/CLI/GUI?
2. What is the default output file naming/location and overwrite policy (e.g., suffix with “_renumbered” vs. user prompt)?
3. Should the GUI allow remembering a sheet choice (per session or per file) if the named sheet is not present?
4. Are there any named ranges/tables that the processing relies on and must be preserved during writes (e.g., avoid resizing or re-creating them)?
5. Do we need optional logging/telemetry for sheet selection and missing required columns to aid support?


