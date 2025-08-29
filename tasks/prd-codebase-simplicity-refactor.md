# Codebase Simplicity Refactor PRD

## Introduction / Overview
Refactor selected modules to reduce branching and improve clarity without altering observable behavior. Focus areas: direct `Options` field access, merge-flow normalization, and robust PDF outline access. No UI changes, no format changes, and no PyPDF2 version changes. All existing tests must continue to pass.

## Goals
- Reduce incidental complexity and disjointed branching in `AppController` and `RenumberService`.
- Prefer precomputed merge inputs from the controller; keep a simple fallback for compatibility.
- Make the PDF adapter tolerant to `outline`/`outlines` attribute differences across PyPDF2 releases.
- Maintain existing behavior and interfaces; do not modify user-visible outputs.

## User Stories
- As a developer, I want fewer conditional branches so the flow is easier to read and maintain.
- As a developer, I want the merge logic standardized so the service consumes a single normalized structure.
- As a developer, I want the PDF adapter to be resilient to PyPDF2 outline attribute differences without upgrading dependencies.

## Functional Requirements
1. Replace `getattr(..., "merge_pairs", None)` and similar patterns with direct `Options` field access where appropriate.
   - Files: `core/app_controller.py`, `core/services/renumber.py`.
   - Preserve exact behavior for falsy/None cases using simple truthiness checks (e.g., `if options.merge_pairs:`).
2. Normalize merge handling in `RenumberService.run`:
   - Prefer `opts.merge_pairs_with_sheets` when present.
   - Fallback: if only `opts.merge_pairs` exists, pair each with `opts.sheet_name` (unchanged behavior).
   - Do not duplicate sheet resolution inside the service (the controller already resolves and sets `merge_pairs_with_sheets`).
3. Make `PdfPyPDF2Repo.read` robust to outline attribute names without changing PyPDF2 version:
   - Attempt `getattr(reader, "outlines", None)`; fallback to `getattr(reader, "outline", None)`.
   - If neither exists or resolves to an empty value, return `([], page_count)` as today.
   - Keep `_parse_outline` contract unchanged (accepts a list-like outline).
4. Refactor for readability only (no new public API):
   - Minimize nested branching in `RenumberService.run` using early local variables and straightforward conditional checks.
   - Keep method count the same; do not introduce additional public methods.
5. Style/constraints:
   - Adhere to PEP 8 and existing code style.
   - Keep imports at top-level only.
   - Do not delete existing comments.
   - No header-fill changes in Excel adapter (explicitly out of scope).
6. Deduplicate PDF reading in single-file flow:
   - Read pages once in the single-file path and reuse them; derive `total_pages = len(pages)` if needed.
   - Avoid a second call to retrieve pages later in the flow.
7. Centralize sheet-name resolution for merge:
   - Sheet selection/resolution for additional pairs must occur in the controller.
   - The service should consume `merge_pairs_with_sheets` when available and avoid per-file sheet discovery.

## Non-Goals (Out of Scope)
- No user-visible behavior changes.
- No PyPDF2 version change.
- No UI changes or new options.
- No changes to Excel header fill behavior.
- No changes to public interfaces (`Options`, `UIController`, repo Protocols`).

## Design Considerations (Optional)
- Continue using Protocol-based ports (`ExcelRepo`, `PdfRepo`, `UIController`) to keep core logic testable.
- Normalize merge inputs in the controller, and keep service tolerant to legacy callers by preserving a fallback path.

## Technical Considerations (Optional)
- PyPDF2 outline attribute differs across versions; use a tolerant getter for `outlines` vs `outline`.
- Maintain existing tests unchanged; any internal refactor must pass current suite.
- Avoid introducing helper methods that expand surface area; prefer small in-function cleanups.

## Success Metrics
- All existing tests pass with no modifications.
- Reduced conditional `getattr` usage in target files to zero (where fields are present on `Options`).
- Merge flow consumes pre-normalized pairs (`merge_pairs_with_sheets`) when available.
- PDF adapter handles both `outline` and `outlines` without errors.
- Single-file path performs only one PDF pages read.

## Open Questions
- None at this time; changes are strictly internal refactors with identical behavior.
