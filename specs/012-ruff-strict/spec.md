# Strict Ruff Adoption

**Feature Branch**: `012-ruff-strict`
**Created**: May 14, 2026
**Status**: Implemented
**Input**: User decision to enforce a strict linting/formatting standard before adding GitHub Actions CI (010). "Make ruff strict so that everything is super clean before we ship."

## Goals

- Single, opinionated linter+formatter for the project (replaces ad-hoc style).
- Catch real defects (unused vars, bad regex patterns, ambiguous Unicode, modern-Python rewrites).
- Make CI lint enforceable: `ruff check .` and `ruff format --check .` both clean on `main`.

## Configuration

`pyproject.toml` is new in this branch. Highlights:

- `target-version = "py310"` — matches `.venv` (Python 3.10.12).
- `line-length = 88` (Black/ruff default).
- Ruleset: `E, F, W, I, B, UP, SIM, C4, N, RUF`. `E501` ignored because the formatter handles wrapping.
- Per-file ignores in `tests/**/*.py` for naming and `assert`/`with`-nesting rules that conflict with pytest idioms (`N802/N803/N806`, `B011/B017`, `SIM117`).
- Excludes: `.venv`, `build`, `dist`, `specs`, `docs`, `__pycache__`.

## What changed

Baseline: **299** lint violations, **21** files needing reformat. Final: **0** violations, **0** reformats, **213/213** tests still green.

### Auto-fixes (252 total)

Applied via `ruff check --fix` (179 safe) and `ruff check --fix --unsafe-fixes` (33 unsafe, hand-reviewed) plus `ruff format` (21 files):

- **`I` (isort)**: import reordering across most files.
- **`UP`**: `Optional[X]` → `X | None`, `List[X]` → `list[X]`, `Dict` → `dict`, etc.
- **`F`**: dropped unused imports.
- **`E712`**: `== True` / `== False` → truthiness (only in tests/integration\_\* — all dict bool lookups, no pandas Series involved).
- **`B007`**: unused loop variables renamed to `_`.
- **`RUF013`**: PEP 484 implicit `Optional` annotations made explicit.

### Hand-fixes (15 total)

| Rule | Where | Treatment |
|------|-------|-----------|
| `E402` (×25) | 6 test files | Removed `sys.path.insert(...)` blocks. `pytest.ini` now sets `pythonpath = . tests`, so tests no longer need to mutate `sys.path` to import `adapters.*`, `core.*`, or `fixtures.*`. Side benefit: fixed pre-existing collection errors on `tests/adapters/*_smoke_test.py`. |
| `RUF043` (×6) | `save_step_test.py`, `validate_step_test.py` | `pytest.raises(..., match="...test.pdf...")` → `match=r"...test\.pdf..."`. Either escaped literal dots or kept intentional `.*` with raw-string prefix. |
| `RUF002` (×3) | `core/transform/excel.py`, `core/transform/pdf.py`, `test_excel_repo_phantom_dimensions.py` | Non-breaking hyphens and multiplication sign in docstrings → ASCII `-` and `x`. |
| `SIM115` (×2) | `test_excel_repo_document_found.py`, `tests/fixtures/excel_fixtures.py` | `NamedTemporaryFile(delete=False)` wrapped in `with` (capture `.name` inside the block, use after). |
| `SIM105` (×2) | `test_merge_validation.py` | `try/except (X, Y): pass` → `contextlib.suppress(X, Y)`. |
| `N818` (×1) | `test_excel_repo_phantom_dimensions.py` | `_TestTimeout` → `_TimeoutError`. Bonus: avoids pytest's auto-collection heuristics for `Test*` classes. |
| `N806` (×1) | `adapters/excel_repo.py` | In-function `SYSTEM_COLUMNS` → `system_columns`. (Function-local; promoting to module constant is out of scope.) |

## Verification

```bash
.venv/bin/ruff check .          # All checks passed!
.venv/bin/ruff format --check .  # 0 files would be reformatted
.venv/bin/pytest                  # 213 passed
```

## Notes for future work

- `--unsafe-fixes` was used once; all 33 changes were reviewed before commit. Future cleanup runs should default to `--fix` only.
- The pytest.ini change (`pythonpath = . tests`) is small but load-bearing: it lets the smoke tests and the fixtures-importing tests collect without filesystem path gymnastics. CI invocations don't need `PYTHONPATH=.` anymore.
- Branch 010 (GitHub Actions) will add `ruff check .` and `ruff format --check .` to a `lint.yml` workflow; this branch is the prerequisite.
