## Introduction/Overview

This PRD covers the complete removal of the deprecated `PyPDF2` library from the codebase, consolidating on `pypdf` as the single PDF backend. We will retain a thin, clearly named selector to allow future backend swaps without code churn. No user-visible behavior may change.

## Goals

- Remove all `PyPDF2` dependencies, imports, references, and workarounds.
- Use `pypdf` exclusively for all PDF read/write/bookmark operations.
- Keep a minimal backend selector (renamed for clarity) for potential future engines.
- Enforce zero warnings in tests (remove the `PyPDF2` deprecation ignore).
- Update documentation and examples to reference only `pypdf`.

## User Stories

- As a maintainer, I want a single, modern PDF backend to reduce maintenance overhead and risk.
- As a developer, I want a clear backend interface so swapping future engines is low-effort.
- As QA, I want identical functional outputs after removal to ensure backward compatibility.

## Functional Requirements

1. Dependencies
   1.1 Remove `PyPDF2` from `requirements.txt`.
   1.2 Keep `pypdf` pinned (e.g., `== 4.2.0`) or a safe range (e.g., `>=4.2,<5`).

2. Backend/Config
   2.1 Rename the engine selector to a clearer name (e.g., `PDF_BACKEND`).
   2.2 Default to `pypdf`; if any other value is provided, raise a clear error.
   2.3 Rename/types: prefer `PdfBackend`/`get_pdf_backend()` terminology in code.

3. Code Cleanup
   3.1 Remove the `PyPDF2`-specific repository implementation.
   3.2 Consolidate adapter logic to the `pypdf` backend only.
   3.3 Ensure bookmark read/write behavior and page mode remain unchanged.

4. Tests
   4.1 Remove `PyPDF2` imports/usages in tests.
   4.2 Drop engine parametrization; tests run against the single `pypdf` backend.
   4.3 Keep smoke/parity tests validating bookmark round-trip and Excel/PDF flows.

5. Tooling/Policies
   5.1 Update `pytest.ini` to remove the `PyPDF2` deprecation ignore.
   5.2 Maintain zero-warnings policy for project deprecations.

6. Documentation
   6.1 Update `README.md` to reference `pypdf` only and the renamed backend selector.
   6.2 Provide guidance for future backend swaps through the selector.

## Non-Goals (Out of Scope)

- Introducing new PDF features or altering public behavior.
- Performance tuning unrelated to removal.
- Supporting alternative backends in this PRD (selector remains for future use only).

## Design Considerations (Optional)

- Keep the backend abstraction minimal and local to the PDF adapter to limit surface area.
- Use page indices for `pypdf` outline creation to maximize compatibility across versions.
- Fail fast with a clear message if `PDF_BACKEND` is set to an unsupported value.

## Technical Considerations (Optional)

- Grep for `PyPDF2` to ensure full removal across code, tests, and docs.
- Confirm no differences in produced PDFs that would affect tests or users.
- Decide on pinning strategy for `pypdf` to minimize breakage.

## Success Metrics

- No `PyPDF2` in dependencies, code, tests, or docs.
- `pytest -q` passes with zero warnings.
- No changes in functional outputs verified by existing tests.

## Open Questions

- Finalize naming: `PDF_BACKEND` env var and `PdfBackend`/`get_pdf_backend()` in code.
- Pin `pypdf` exactly vs. compatible range.


