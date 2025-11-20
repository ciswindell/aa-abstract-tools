# Changelog

All notable changes to Abstract Renumber Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.2] - 2025-11-20

### Fixed
- **Merge Mode Validation**: Fixed critical bug where users could enable merge mode without selecting any file pairs
- System now prevents processing when merge enabled but no pairs selected
- Process button automatically disabled when invalid merge state detected
- Clear error message guides users to select pairs or disable merge mode
- Prevents inappropriate backup disable for single-file operations

### Technical Details
- Added three-layer validation: UI (Process button state), Adapter (Options validation), Controller (pre-processing check)
- Enhanced `_update_process_button_state()` method in GUI to check merge validity
- Modified `get_options()` to return None instead of empty list for merge_pairs when invalid
- Added backend validation in `AppController.process_files()` as safety net
- Comprehensive test suite: 4 tests covering validation and regression scenarios

## [1.0.1] - 2025-11-20

### Fixed
- **Column Preservation During Merge**: Fixed critical bug where columns unique to secondary files were lost during multi-file merge operations
- Merge operations now preserve all columns from all source files
- System columns (_include, _original_index, Document_ID) are properly excluded from output
- Column matching is now case-insensitive and whitespace-tolerant
- Template column order is preserved with new columns appended logically

### Technical Details
- Enhanced `ExcelRepo._write_dataframe_to_workbook()` to support dynamic column addition
- Added `_normalize_column_name()` helper for robust column matching
- Modified `SaveStep` to automatically enable column preservation for merge workflows
- Added comprehensive test suite: 12 tests covering unit and integration scenarios
- Zero data loss guarantee: 100% of columns from all source files preserved

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

