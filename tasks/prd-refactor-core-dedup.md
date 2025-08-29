# Introduction / Overview

Refactor the Abstract Renumber Tool to remove duplication and simplify over‑engineered areas while preserving existing behavior and outputs. The goal is to make the codebase easier to maintain and extend without changing Excel or PDF results.

# Goals

- Preserve outputs exactly (Excel cell values and PDF pages/bookmarks unchanged).
- Reduce duplication in page‑range computation and bookmark title mapping.
- Normalize merged flow to reuse the single‑file pipeline where feasible.
- Maintain PEP 8, SOLID/DRY principles, and top‑level imports.

# User Stories

- As a developer, I can work with a clearer, smaller codebase that avoids duplicate logic, so changes are safer and faster.
- As QA, I can run the existing test suite and verify no output changes.
- As an end user, I see identical Excel/PDF outputs and behavior to prior versions.

# Functional Requirements

1. Page‑range logic must be centralized using `core.transform.pdf.detect_page_ranges(...)` wherever ranges are needed (single and merged flows).
2. Bookmark title updating must be unified behind a single resolver‑based function that maps a bookmark to its `Document_ID`, then to a final title. The resolver may:
   - Use `DocumentLink` instances (single‑file path), or
   - Use an offset‑aware resolver for merged bookmarks, without changing outcomes.
3. Merged flow should, where possible, be normalized so that bookmark linking uses the same path as single‑file processing (e.g., combine and offset bookmarks/pages first, then create `DocumentLink`), avoiding special‑case branches. Behavior must remain identical.
4. Keep public interfaces unchanged (`ExcelRepo`, `PdfRepo`, `UIController`, service APIs) and avoid adding new methods “for the future”.
5. Maintain imports at module top level and PEP 8 style across touched files.
6. All existing tests must pass unchanged; add tests only if coverage gaps appear for the refactor, without altering expected outputs.

# Non‑Goals (Out of Scope)

- No UI/UX changes.
- No new PDF or Excel backends or file format changes.
- No behavioral changes to sorting, renumbering, bookmark titles, or page order.
- No performance‑driven rewrites beyond small incidental improvements.

# Design Considerations (Optional)

- Keep functions pure where they already are (e.g., transforms) and keep I/O in adapters.
- Favor small helpers (e.g., resolver function injection) to avoid branching.
- Preserve existing column names and schema.

# Technical Considerations (Optional)

- `pandas` and `pypdf` usage remains as-is; no backend swap.
- For merged normalization, compute page offsets once, then operate on a combined bookmark list to enable reuse of the single‑file link creation.
- Keep `Document_ID` generation stable; avoid any changes that would impact hashes.

# Success Metrics

- 100% of existing tests pass with zero modification.
- Output parity:
  - Excel: same cell values for intersecting columns; same worksheet targets.
  - PDF: identical page order and bookmark titles/levels/pages.
- Reduced duplication (e.g., removal of bespoke page‑range calculations; single title‑update path).
- Decreased code size in affected areas without reducing readability.

# Open Questions

- None at this time. Proceed under the constraint: no output changes.
