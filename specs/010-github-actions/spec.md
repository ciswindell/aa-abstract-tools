# GitHub Actions CI/CD + Slim Local Build

**Feature Branch**: `010-github-actions`
**Created**: May 14, 2026
**Status**: Implemented
**Input**: User decision to move releases off a local Windows machine. Previous flow required editing `_version.py`, running `python build/build.py` locally, and emailing the resulting `.exe` to clients — a friction-heavy process that depended on one developer's environment. Replace with tag-driven CI builds and GitHub Releases. Reference implementation: `aa-order-manager/.github/workflows/build.yml`.

## Goals

- Cut a release with one command: `git tag -a v1.2.3 -m "..." && git push origin v1.2.3`.
- PRs to `dev`/`main` must pass tests + lint before merge (enforceable via branch protection later).
- Local builds remain possible for developers without GitHub access.
- No secrets needed: `softprops/action-gh-release@v2` uses the default `GITHUB_TOKEN`.

## What changed

### Three workflows under `.github/workflows/`

- **`build.yml`** — Windows `.exe` build.
  - Triggers: `push` to tags `v*`, plus `workflow_dispatch` with a `version` input for ad-hoc builds.
  - Runs on `windows-latest`, Python 3.10 with pip cache.
  - Resolves the version (tag name stripped of leading `v`, or the manual input).
  - Writes `__version__ = "<resolved>"` to `_version.py` before building. CI never commits this change — the file is patched only inside the runner.
  - Runs `python build/build.py` which invokes PyInstaller against `build/AbstractRenumberTool.spec`. The spec names the executable `AbstractRenumberTool-v<version>.exe`.
  - Uploads the artifact (always) and creates a GitHub Release with auto-generated notes (only on tag push, gated by `if: github.event_name == 'push'`).
- **`ci.yml`** — pytest on PR and push to `dev`/`main`. `ubuntu-latest`, Python 3.10, pip cache, ~3s test suite (213 tests).
- **`lint.yml`** — `ruff check .` and `ruff format --check .` on PR and push to `dev`/`main`.

All three workflows use `actions/setup-python@v5` with `cache: 'pip'`. First run populates the cache; subsequent runs install in seconds.

### `build/build.py` slimmed from 550 to ~35 lines

Removed:

- `argparse` CLI (the spec file already controls mode/optimize/etc.).
- `BuildOrchestrator` class + `BuildResult` dataclass.
- `validate_prerequisites()` (Python version, PyInstaller install, disk space, spec file existence) — CI handles environment, and PyInstaller's own errors are clear enough on local runs.
- UPX detection.
- `_validate_build_output()` size heuristics and the verbose `print_build_summary()`.

What's left: import-version-with-fallback was already in the spec file, so build.py just runs `python -m PyInstaller --noconfirm <spec_path>` from the repo root and forwards the exit code. Local invocation unchanged: `python build/build.py`.

### README release flow rewritten

The old "Version Update Workflow" section instructed users to edit `_version.py`, commit, tag, and `cd build && python3 build.py`. The new section documents the tag-driven flow: update `CHANGELOG.md`, tag, push, watch the GitHub Action. `_version.py` no longer needs manual bumping for releases (CI injects from the tag); it remains the local development version.

A new "Manual / Ad-Hoc Build" subsection covers `workflow_dispatch` for one-off builds without a release, plus local-build instructions for developers.

## Verification

Before this branch can be merged, the following must hold:

- [x] `ruff check .` clean
- [x] `ruff format --check .` clean
- [x] `pytest` — 213 passed
- [ ] `lint.yml` and `ci.yml` succeed on the PR for this branch (proves the workflows themselves are valid)
- [ ] After merge: tag a no-op patch release (`v1.1.1`) and confirm `build.yml` produces a downloadable `.exe` on the Releases page

The last item is the only thing that can't be verified before merge — there's no way to test a tag-triggered workflow without pushing a tag against the actual main branch.

## Notes / Trade-offs

- **Version is *not* committed**. CI mutates `_version.py` inside the runner and discards it. This keeps the repo's `_version.py` as a stable "last-released" or "dev" marker without per-release commits. Trade-off: someone running locally on `main` after a release will see whatever's in `_version.py`, not the latest release tag. Acceptable since local builds are for developers, not clients.
- **`workflow_dispatch` does not create a Release**. Manual builds upload an artifact only — useful for testing the workflow or producing a build for QA without committing to a public release.
- **No Linux/macOS builds**. The application is Tkinter-based and ships as a Windows `.exe` to clients only. Adding cross-platform builds would require a matrix strategy and is out of scope until there's a real consumer.
- **Branch protection not enabled yet**. Workflows pass-or-fail status is informational until protections are configured in GitHub settings (`Require status checks: lint, test`). Recommended after this branch merges and one full PR cycle proves green.
- **Pip caching keys**. `cache: 'pip'` keys off `requirements.txt`. If we add a `requirements-dev.txt` or a `pyproject.toml` with deps, the cache key invalidates automatically.
