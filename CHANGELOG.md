# Changelog

All notable changes to Abstract Renumber Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Constitution updated to v1.1.1 with explicit version increment requirements

## [1.0.0] - 2025-11-20

### Added
- Version display system (Feature 005-version-display-system)
- Version shown in GUI window title: "Abstract Renumber Tool v1.0.0"
- Version shown in GUI footer at bottom-right in gray text
- Versioned executable naming: `AbstractRenumberTool-v1.0.0.exe`
- Single source of truth version management via `_version.py`
- Comprehensive version management documentation in README
- Semantic versioning rules (MAJOR.MINOR.PATCH)
- Version update workflow with examples
- 8 comprehensive tests for version system functionality
- Graceful fallback to "Unknown" when version file missing

### Technical Details
- Created `_version.py` module at project root
- Updated `app/tk_app.py` with version import and display logic
- Updated `build/build.py` to automatically read version for executable naming
- Added `tests/app/test_version_display.py` with full test coverage
- Fixed `.gitignore` to properly track test files
- Updated constitution to include Version Management quality standards

### Documentation
- Added "Version Management" section to README.md
- Created detailed quickstart guide in `specs/005-version-display-system/quickstart.md`
- Documented semantic versioning rules with examples
- Added version update workflow instructions

---

## Version History Format

Each version entry should include:
- **[Version]** - Release date in YYYY-MM-DD format
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements
- **Technical Details**: Implementation notes (optional)
- **Documentation**: Documentation updates (optional)

---

## Semantic Versioning Guide

- **MAJOR (X.0.0)**: Breaking changes affecting user workflows
  - UI redesigns that change how users interact with the application
  - Removed features or functionality
  - Changes that require users to modify their workflow

- **MINOR (x.Y.0)**: New features (backward compatible)
  - New buttons, options, or capabilities
  - Enhanced functionality that doesn't break existing workflows
  - Additional processing modes or features

- **PATCH (x.y.Z)**: Bug fixes and minor improvements
  - Error corrections
  - Performance improvements
  - Documentation updates
  - Minor UI tweaks that don't change functionality

