## Relevant Files

- `requirements.txt` - Add `pypdf` while retaining `PyPDF2`; pin versions.
- `core/config.py` - Introduce a simple PDF engine selector (env/config-based).
- `adapters/pdf_repo.py` - Use the engine abstraction; preserve behavior/output.
- `tests/adapters/pdf_repo_smoke_test.py` - Validate PDF behavior; consider engine parametrization.
- `tests/core/transform/pdf_test.py` - PDF transform behavior checks (engine parity where applicable).
- `tests/core/transform/test_pdf.py` - Additional PDF behavior coverage.
- `tests/integration_test_document_id.py` - End-to-end document ID behavior, ensure parity.
- `tests/adapters/excel_repo_smoke_test.py` - Replace deprecated pandas `DataFrame.applymap` usage.
- `pytest.ini` - Configure warnings policy to fail on new deprecations from project code.
- `README.md` - Document engine selection, rollback, and zero-warnings policy.

### Notes

- Run tests with `python3 -m pytest -q` from the repo root.
- Target: zero warnings and all tests passing across selected engine.
- Allow switching engines via environment variable and/or config setting.

## Tasks

- [ ] 1.0 Add `pypdf` dependency and pin compatible versions
  - [x] 1.1 Audit `requirements.txt` for current `PyPDF2` constraints
  - [x] 1.2 Add `pypdf` with a compatible, pinned version; keep `PyPDF2`
  - [x] 1.3 Install deps and smoke-check imports: `python3 -c "import pypdf, PyPDF2"`
  - [x] 1.4 Run `python3 -m pytest -q` to ensure no regressions

- [ ] 2.0 Implement PDF engine selector and minimal abstraction layer
  - [x] 2.1 In `core/config.py`, add `pdf_engine` setting (env `PDF_ENGINE`, default `pypdf`)
  - [x] 2.2 Define a minimal engine contract (read, pages, write) in `adapters/pdf_repo.py`
  - [x] 2.3 Implement an internal factory to select `pypdf` or `PyPDF2` backend
  - [x] 2.4 Ensure clear error if selected engine is unavailable

- [ ] 3.0 Integrate abstraction into `adapters/pdf_repo.py` preserving existing behavior
  - [x] 3.1 Replace direct `PyPDF2` imports with calls through the selected engine
  - [x] 3.2 Map bookmark read APIs (outline/outlines differences) for both engines
  - [x] 3.3 Map bookmark write APIs, including fit/zoom behavior parity
  - [x] 3.4 Preserve `page_mode` behavior (`/UseOutlines`) when supported
  - [x] 3.5 Normalize exceptions and edge cases; keep current outputs identical
  - [x] 3.6 Fix pypdf outline writing to use page indices for stability

- [ ] 4.0 Update tests: parametrize engines and remove pandas deprecations
  - [x] 4.1 Add a fixture or parametrization to run PDF tests with both engines
  - [x] 4.2 Update `tests/adapters/excel_repo_smoke_test.py` to replace `DataFrame.applymap` with `DataFrame.map`
  - [x] 4.3 Adjust any other tests using deprecated APIs (search and replace)
  - [x] 4.4 Ensure all tests pass for both engines locally

- [ ] 5.0 Enforce zero-warnings policy in pytest configuration
  - [x] 5.1 Add `pytest.ini` with `filterwarnings` to error on project deprecations
  - [x] 5.2 Ignore known third-party deprecations if unavoidable, with rationale
  - [x] 5.3 Verify `python3 -m pytest -q` yields zero warnings

- [ ] 6.0 Update documentation for engine selection and rollback plan
  - [x] 6.1 Document `PDF_ENGINE` and default behavior in `README.md`
  - [x] 6.2 Document how to compare outputs across engines and rollback
  - [x] 6.3 Note zero-warnings policy and how to keep it enforced


