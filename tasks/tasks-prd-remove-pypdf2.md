## Relevant Files

- `requirements.txt` - Remove `PyPDF2`; keep/pin `pypdf` only.
- `adapters/pdf_repo.py` - Remove PyPDF2 code paths; keep a renamed backend selector.
- `core/config.py` - Rename `PDF_ENGINE` to `PDF_BACKEND`; default to `pypdf` only.
- `tests/adapters/pdf_repo_smoke_test.py` - Remove engine parametrization; ensure pypdf-only path.
- `tests/conftest.py` - Drop `pdf_engine_env` fixture and any PyPDF2 dependencies.
- `pytest.ini` - Remove PyPDF2 deprecation ignore; keep zero-warnings policy for project.
- `README.md` - Update docs to reference pypdf only and the new selector name.

### Notes

- Run tests with `python3 -m pytest -q` from the repo root.
- Acceptance: 0 warnings, all tests pass; no `PyPDF2` references remain.

## Tasks

- [ ] 1.0 Remove `PyPDF2` from dependencies, imports, and code references
  - [x] 1.1 Remove `PyPDF2` from `requirements.txt`
  - [x] 1.2 Delete PyPDF2 imports and the `PdfPyPDF2Repo` implementation
  - [x] 1.3 Replace any remaining `PyPDF2` API usage with `pypdf` equivalents
  - [x] 1.4 Grep repo to confirm no `PyPDF2` references (code, tests, docs)
  - [x] 1.5 Run `python3 -m pytest -q` and ensure zero warnings

- [ ] 2.0 Rename and simplify the backend selector for future flexibility
  - [x] 2.1 In `core/config.py`, rename `PDF_ENGINE` -> `PDF_BACKEND` (default `pypdf`)
  - [x] 2.2 Remove Protocol/factory; collapse to single `PdfRepo` class
  - [x] 2.3 Restrict backend to `pypdf` only; raise clear error for others (not needed now)
  - [x] 2.4 Update call sites to use the new names

- [ ] 3.0 Refactor tests to pypdf-only and drop engine parametrization
  - [x] 3.1 Remove `pdf_engine_env` fixture and params from `tests/conftest.py`
  - [x] 3.2 Update `tests/adapters/pdf_repo_smoke_test.py` to be single-backend
  - [x] 3.3 Remove any PyPDF2-specific test imports or assumptions
  - [x] 3.4 Run full test suite and ensure all pass

- [ ] 4.0 Update pytest configuration to enforce zero warnings without PyPDF2 ignore
  - [x] 4.1 Remove the PyPDF2 deprecation ignore from `pytest.ini`
  - [x] 4.2 Keep project deprecations as errors and verify zero warnings

- [ ] 5.0 Update documentation and examples to pypdf-only usage
  - [x] 5.1 Update `README.md` requirements to list only `pypdf`
  - [x] 5.2 Replace engine selection docs with `PDF_BACKEND` (pypdf-only for now)
  - [x] 5.3 Remove references to PyPDF2 from examples and notes

- [ ] 6.0 Verify outputs and complete repository cleanup
  - [x] 6.1 Validate PDF outputs (bookmark titles/order) remain identical
  - [x] 6.2 Remove dead code/imports and run `pytest -q` once more
  - [ ] 6.3 Open PR with migration summary and risks/rollback (revert commit)


