# Research: Version Display System

**Feature**: 005-version-display-system  
**Date**: 2025-11-20  
**Status**: Complete

## Overview

Research findings for implementing a single source of truth version system using semantic versioning, covering Python module patterns, GUI display strategies, build integration, and error handling approaches.

## Key Decisions

### Decision 1: Version Storage Location and Format

**Decision**: Use a root-level `_version.py` module with `__version__` string variable following PEP 440

**Rationale**:
- PEP 440 specifies Python version identification and dependency specification standard
- Root-level placement makes it accessible to all modules without import path complexity
- Leading underscore indicates private/internal module (not part of public API)
- Single `__version__` string is the minimal viable implementation
- Standard pattern used by major Python packages (requests, flask, django)

**Alternatives Considered**:
- **`setup.py` or `pyproject.toml`**: Requires parsing TOML/setup files at runtime, adds complexity, primarily for package distribution
- **`__init__.py` in app/**: Ties version to application module, harder to access from build scripts
- **JSON/YAML config file**: Requires file I/O and parsing at runtime, slower than Python import
- **Environment variable**: Not persistent, requires external configuration, unsuitable for distributed executables
- **Hardcoded in multiple files**: Violates DRY principle, error-prone, fails single-update requirement

**Implementation Notes**:
```python
# _version.py
"""Version information for Abstract Renumber Tool."""
__version__ = "1.0.0"
```

- Import as: `from _version import __version__`
- Format: "MAJOR.MINOR.PATCH" (semantic versioning 2.0.0)
- Optional additions for future: `__version_info__` tuple, `__build_date__` string

---

### Decision 2: Semantic Versioning Increment Rules

**Decision**: Follow Semantic Versioning 2.0.0 standard with application-specific interpretations

**Rationale**:
- Industry standard for version communication
- Clear contract: MAJOR = breaking changes, MINOR = new features, PATCH = bug fixes
- Users can assess update risk from version number alone
- Compatible with automated version comparison tools

**Application-Specific Rules**:

| Component | Increment When | Examples |
| --------- | -------------- | -------- |
| MAJOR     | Breaking UI changes, removed features, workflow incompatibilities | Redesigned GUI layout, removed "Merge Pairs" feature |
| MINOR     | New features, new options, added capabilities | New "Export to CSV" button, new checkbox option |
| PATCH     | Bug fixes, performance improvements, documentation updates | Fixed Windows warning, corrected error message typo |

**Pre-release Conventions** (if needed):
- `0.x.y`: Pre-1.0 development/testing versions
- `1.0.0`: First production-ready release
- `x.y.z-alpha`: Alpha testing (internal)
- `x.y.z-beta`: Beta testing (limited users)
- `x.y.z-rc.N`: Release candidate

**Implementation Notes**:
- Reset lower components when incrementing higher (e.g., 1.2.5 → 1.3.0, not 1.3.5)
- Document version changes in commit messages
- Consider adding CHANGELOG.md for user-facing release notes

---

### Decision 3: GUI Display Strategy

**Decision**: Display version in window title bar and fixed footer at bottom-right of main window

**Rationale**:
- **Window title**: Always visible in taskbar and window decorations, standard location for application identification
- **Footer**: Unobtrusive persistent display without disrupting main content, common pattern in desktop applications
- Dual display provides redundancy (title may be truncated on small screens)
- No additional user action required (no menu navigation, no About dialog)

**Alternatives Considered**:
- **About dialog only**: Requires user action (menu click), not instantly visible
- **Status bar**: Could conflict with existing status messages, adds UI complexity
- **Splash screen**: Only visible on startup, not persistent
- **Header banner**: Takes valuable vertical space, visually intrusive

**Implementation Details**:
- **Window title format**: "Abstract Renumber Tool v1.0.0"
- **Footer format**: "Version 1.0.0" (right-aligned, Arial 9, gray color)
- **Footer placement**: New grid row (row 7) below status area
- **Import location**: `from _version import __version__` in `setup_window()` and `_create_version_footer()`

**Visual Design**:
```python
# Window title
self.root.title(f"Abstract Renumber Tool v{__version__}")

# Footer (gray, small, right-aligned)
version_label = ttk.Label(
    footer_frame,
    text=f"Version {__version__}",
    foreground="gray",
    font=("Arial", 9)
)
version_label.pack(side=tk.RIGHT)
```

---

### Decision 4: Build Script Integration

**Decision**: Import version from `_version.py` in `build.py` and use for executable naming via `--name` flag

**Rationale**:
- Ensures executable filename matches application version automatically
- No manual string duplication in build script
- Version-stamped files enable side-by-side version comparisons
- Users can identify executable version from filename before running

**Alternatives Considered**:
- **Hardcoded version in build script**: Violates single source of truth, error-prone
- **Parse version from spec file**: Requires YAML/Markdown parsing, fragile to spec format changes
- **Git tags**: Requires git repository, doesn't work for internal testing builds
- **Build timestamp**: Doesn't communicate semantic versioning information

**Implementation Details**:
```python
# build/build.py
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
from _version import __version__

# Use in PyInstaller command
exe_name = f"AbstractRenumberTool-v{__version__}"
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--name", exe_name,  # Results in: AbstractRenumberTool-v1.0.0.exe
    # ... other flags
]
```

**Filename Convention**:
- Pattern: `AbstractRenumberTool-v{MAJOR}.{MINOR}.{PATCH}.exe`
- Example: `AbstractRenumberTool-v1.0.0.exe`, `AbstractRenumberTool-v1.2.1.exe`
- Consistent with spec file naming (005-version-display-system)

---

### Decision 5: Error Handling for Missing Version

**Decision**: Use try/except with fallback to "Unknown" version if `_version.py` is missing or malformed

**Rationale**:
- Application should not crash if version file is accidentally deleted
- "Unknown" clearly indicates a problem without exposing technical error messages to users
- Allows application to function normally despite version display issue
- Developer sees import error in logs during testing

**Alternatives Considered**:
- **Crash on missing version**: Too brittle, poor user experience
- **Empty string**: Confusing UI, looks like rendering bug
- **Raise error**: Prevents application launch, disproportionate to severity
- **Default to "0.0.0"**: Misleading, implies a valid version

**Implementation Pattern**:
```python
try:
    from _version import __version__
except (ImportError, AttributeError):
    __version__ = "Unknown"
    # Optionally log warning to console/logger
```

**Error Scenarios Covered**:
- File missing: `ImportError` caught
- Variable missing: `AttributeError` caught
- Invalid format (e.g., `__version__ = 123`): String formatting handles gracefully
- Extremely long version: Tkinter label truncates naturally

---

### Decision 6: Testing Strategy

**Decision**: Unit tests for version import, GUI display, and build script integration

**Rationale**:
- Ensures version system continues working after refactoring
- Validates fallback behavior for missing version file
- Confirms version appears in all required locations

**Test Cases**:
1. **test_version_import**: Import `_version.py` successfully, validate format
2. **test_version_format**: Regex validation of "X.Y.Z" format
3. **test_version_fallback**: Mock missing `_version.py`, verify "Unknown" fallback
4. **test_window_title_contains_version**: Launch GUI, check title contains version
5. **test_footer_displays_version**: Launch GUI, check footer label text
6. **test_build_script_reads_version**: Mock build process, verify executable name includes version

**Implementation Notes**:
- Tests in `tests/app/test_version_display.py`
- Use `unittest.mock` for simulating missing files
- GUI tests may require headless mode or actual Tk instance
- Build script tests can mock subprocess calls

---

## Best Practices

### Version Update Workflow
1. Determine change type (breaking, feature, fix)
2. Update `_version.py` with new version number
3. Commit change: `git commit -m "chore: bump version to X.Y.Z"`
4. Run build script: `python3 build/build.py`
5. Verify executable filename: `AbstractRenumberTool-vX.Y.Z.exe`
6. Test application launch: confirm version in title and footer
7. Distribute versioned executable to users

### Version Hygiene
- Update version before building release executables
- Never distribute multiple executables with same version
- Document version changes in git commit messages
- Consider maintaining CHANGELOG.md for user-facing changes

### Future Enhancements (Out of Scope)
- `__version_info__` tuple for programmatic version comparison
- `__build_date__` timestamp for build tracking
- About dialog with version, author, license information
- Automatic version bump scripts (e.g., `bump2version`)
- Pre-release version support (alpha, beta, rc)

---

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [PEP 440 – Version Identification](https://peps.python.org/pep-0440/)
- [Python Packaging User Guide - Single sourcing version](https://packaging.python.org/guides/single-sourcing-package-version/)
- [Tkinter Documentation - Window title](https://docs.python.org/3/library/tkinter.html)

