## Introduction/Overview

This PRD defines work to eliminate current and future deprecation warnings by introducing support for the `pypdf` library alongside the existing `PyPDF2`, and by refactoring code/tests that rely on deprecated APIs (e.g., pandas `DataFrame.applymap`). The goal is to maintain identical behavior and outputs while ensuring the codebase is forward-compatible with newer library versions.

Baseline environment: Linux, Python 3.10.

## Goals

- Eliminate all pytest warnings in the suite (target: zero warnings).
- Add `pypdf` while retaining `PyPDF2` with an easy runtime/config switch between them.
- Maintain identical observable behavior and outputs between engines.
- Refactor tests to remove use of deprecated pandas APIs.
- Prepare a safe path to later remove `PyPDF2` after verification.

## User Stories

- As a maintainer, I want zero deprecation warnings so upgrades remain safe and predictable.
- As a developer, I want to toggle between `pypdf` and `PyPDF2` without code changes to validate parity.
- As a QA engineer, I want deterministic, identical outputs from either PDF engine to ensure backward compatibility.

## Functional Requirements

1. Dependency Management
   1.1 Add `pypdf` to `requirements.txt` (retain `PyPDF2` for now).
   1.2 Pin compatible versions and document the chosen versions.

2. PDF Engine Abstraction
   2.1 Introduce a simple PDF engine selector that allows choosing `pypdf` or `PyPDF2` via configuration (e.g., environment variable and/or `core/config.py`).
   2.2 Default to `pypdf` if available; allow override to `PyPDF2`.
   2.3 Wrap only the currently used PDF operations (no speculative methods), matching existing behavior.
   2.4 If the selected engine is unavailable, fail clearly with an actionable error message.

3. Adapter Integration
   3.1 Update `adapters/pdf_repo.py` to use the engine abstraction rather than importing `PyPDF2` directly.
   3.2 Preserve current public behavior and outputs, including any side effects (file contents, metadata, bookmarks).

4. Test Suite Updates
   4.1 Parametrize relevant PDF tests to run against both engines, unless explicitly skipped by configuration.
   4.2 Validate that outputs produced by both engines are functionally identical for the covered operations.
   4.3 Replace deprecated pandas `DataFrame.applymap` usage in tests with the recommended alternative (`DataFrame.map`).

5. Warnings Policy
   5.1 Ensure `pytest -q` runs with zero warnings in the current environment.
   5.2 Add or update a warnings policy (e.g., `pytest.ini` `filterwarnings`) to fail the build on new deprecations from project code.

6. Documentation
   6.1 Document how to select the PDF engine (config/env) in `README.md`.
   6.2 Document the rollback plan (switch back to `PyPDF2` via config) and later removal plan.

## Non-Goals (Out of Scope)

- Introducing new PDF features or altering user-facing functionality.
- Refactoring unrelated modules or adding unused abstraction layers.
- Performance optimization beyond ensuring no regressions.

## Design Considerations (Optional)

- Keep the engine abstraction minimal and localized to `adapters/pdf_repo.py` (and config) to reduce surface area.
- Prefer a simple configuration switch (env var like `PDF_ENGINE=pypdf|pypdf2` or key in `core/config.py`), defaulting to `pypdf`.
- Use a thin wrapper that normalizes differences in API names/behaviors used today (e.g., reading/writing, metadata/bookmarks) without adding future-looking methods.

## Technical Considerations (Optional)

- Some exception types or API signatures differ between `pypdf` and `PyPDF2`; normalize to existing expectations in the adapter.
- Ensure tests compare functional outcomes (e.g., saved PDF structure, bookmarks) rather than engine-specific details.
- Confirm the recommended pandas replacement for `DataFrame.applymap` is `DataFrame.map` and adjust imports/usages accordingly.
- Consider adding a small golden-file or checksum-based comparison for PDFs where practical, acknowledging that some metadata fields (timestamps) may differ and need normalization.

## Success Metrics

- `pytest -q` completes with 0 warnings and all tests passing.
- Both `pypdf` and `PyPDF2` modes pass the suite with identical functional outcomes for covered PDF operations.
- Documentation clearly explains switching engines and rollback steps.

## Open Questions

- Default engine: proceed with `pypdf` as default, with `PyPDF2` as a fallback via config?
- Exact location for engine selection: environment variable only, `core/config.py`, or both with precedence?
- Minimum supported pandas version to ensure `DataFrame.map` availability and consistent behavior?


