# API Contracts: Version Display System

**Feature**: 005-version-display-system  
**Date**: 2025-11-20  
**Status**: Complete

## Overview

This document defines the contracts (interfaces) for the Version Display System. Since this is a simple feature with no HTTP APIs, databases, or complex protocols, the "contracts" are the Python module interfaces and the expected behavior of version-related functions.

---

## Contract 1: Version Module Interface

### Purpose
Define the structure and guarantees of the `_version.py` module that serves as the single source of truth for application versioning.

### Location
`/home/chris/Code/aa-abstract-renumber/_version.py`

### Module Signature

```python
"""Version information for Abstract Renumber Tool.

This module provides the canonical version number for the application.
All version displays (GUI, executable naming, documentation) MUST import
from this module to ensure consistency.
"""

__version__: str
"""
Semantic version string in format 'MAJOR.MINOR.PATCH'.

Examples:
    "0.1.0"  - Pre-release development version
    "1.0.0"  - First production release
    "1.2.3"  - Minor update with patches

Constraints:
    - MUST match regex: ^\d+\.\d+\.\d+$
    - Components MUST be non-negative integers
    - MUST follow Semantic Versioning 2.0.0 specification
"""
```

### Minimal Implementation

```python
# _version.py
"""Version information for Abstract Renumber Tool."""
__version__ = "1.0.0"
```

### Extended Implementation (Optional)

```python
# _version.py
"""Version information for Abstract Renumber Tool."""

__version__ = "1.0.0"
"""Current version string (semantic versioning)."""

__version_info__ = (1, 0, 0)
"""Version as tuple for programmatic comparison."""

__build_date__ = "2025-11-20"
"""ISO 8601 date of this version's release."""
```

### Contract Guarantees

**Stability**:
- Module MUST exist at `_version.py` in project root
- `__version__` variable MUST be defined as a string
- Module MUST NOT import external dependencies (stdlib only)
- Module MUST NOT perform side effects (no I/O, no logging, no computation)

**Versioning**:
- Format MUST be "MAJOR.MINOR.PATCH" (three dot-separated integers)
- Version MUST NOT contain pre-release suffixes in initial implementation (e.g., no "-alpha")
- Version string MUST be UTF-8 compatible

**Immutability**:
- Version MUST NOT change during application runtime
- Module MUST NOT provide functions to modify `__version__`
- Version is read-only constant from consumer perspective

### Consumer Contract

**GUI Components** (`app/tk_app.py`):

```python
# Contract: GUI must handle missing version gracefully
try:
    from _version import __version__
except (ImportError, AttributeError):
    __version__ = "Unknown"

# Contract: Display version in window title
self.root.title(f"Abstract Renumber Tool v{__version__}")

# Contract: Display version in footer (right-aligned, gray, small font)
version_label = ttk.Label(
    footer_frame,
    text=f"Version {__version__}",
    foreground="gray",
    font=("Arial", 9)
)
version_label.pack(side=tk.RIGHT)
```

**Build Script** (`build/build.py`):

```python
# Contract: Build script must add project root to Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Contract: Build script must handle missing version gracefully
try:
    from _version import __version__
except (ImportError, AttributeError):
    __version__ = "dev"  # Development build fallback

# Contract: Use version in executable naming
exe_name = f"AbstractRenumberTool-v{__version__}"

# Pass to PyInstaller --name flag
cmd = [..., "--name", exe_name, ...]
```

### Error Handling Contract

| Error Condition | Expected Behavior | Fallback Value |
|----------------|-------------------|----------------|
| `_version.py` missing | Catch `ImportError` | "Unknown" (GUI), "dev" (build) |
| `__version__` undefined | Catch `AttributeError` | "Unknown" (GUI), "dev" (build) |
| Invalid format (non-string) | String formatting handles | Display as-is (may be incorrect) |
| Empty string | No error raised | Display empty (poor UX, valid code) |

**Contract**: Consumers MUST NOT crash if version is unavailable. Graceful degradation is required.

---

## Contract 2: GUI Display Requirements

### Window Title Contract

**Requirement**: Main application window MUST display version in title bar.

**Format**: `"Abstract Renumber Tool v{__version__}"`

**Examples**:
- `"Abstract Renumber Tool v1.0.0"`
- `"Abstract Renumber Tool v2.3.1"`
- `"Abstract Renumber Tool vUnknown"` (fallback)

**Implementation Location**: `app/tk_app.py`, method `setup_window()`

**Test Verification**:
```python
def test_window_title_contains_version():
    """Verify window title includes version string."""
    root = tk.Tk()
    gui = AbstractRenumberGUI(root, controller=None)
    
    assert "v" in root.title()
    assert "Abstract Renumber Tool" in root.title()
    # Should match: "Abstract Renumber Tool v1.0.0"
```

---

### Footer Label Contract

**Requirement**: Main window footer MUST display version label.

**Format**: `"Version {__version__}"`

**Styling**:
- Font: Arial, size 9
- Color: Gray (foreground)
- Alignment: Right (packed with `side=tk.RIGHT`)
- Position: Grid row 7 (below status area)

**Examples**:
- `"Version 1.0.0"`
- `"Version 2.3.1"`
- `"Version Unknown"` (fallback)

**Implementation Location**: `app/tk_app.py`, method `_create_version_footer()`

**Test Verification**:
```python
def test_footer_displays_version():
    """Verify footer label exists and contains version."""
    root = tk.Tk()
    gui = AbstractRenumberGUI(root, controller=None)
    
    # Search for label widget containing "Version"
    version_labels = [w for w in root.winfo_children() 
                      if isinstance(w, ttk.Label) and "Version" in w.cget("text")]
    
    assert len(version_labels) > 0
    assert "Version" in version_labels[0].cget("text")
```

---

## Contract 3: Build Script Integration

### Executable Naming Contract

**Requirement**: PyInstaller build output MUST be named with version stamp.

**Format**: `"AbstractRenumberTool-v{__version__}.exe"`

**Examples**:
- Windows: `AbstractRenumberTool-v1.0.0.exe`
- Development: `AbstractRenumberTool-vdev.exe` (fallback)

**Implementation Location**: `build/build.py`

**Command Construction**:
```python
exe_name = f"AbstractRenumberTool-v{__version__}"

cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--name", exe_name,
    # ... other flags
    str(spec_path),
]
```

**Test Verification**:
```python
def test_build_script_reads_version(tmp_path):
    """Verify build script imports version and uses in naming."""
    # Mock _version module
    version_file = tmp_path / "_version.py"
    version_file.write_text('__version__ = "9.9.9"')
    
    # Import build script with mocked path
    import build.build
    
    # Verify executable name includes version
    assert "v9.9.9" in build.build.get_exe_name()
```

---

## Contract 4: Version Update Workflow

### Developer Contract

**Requirement**: Version updates MUST follow this exact workflow to ensure consistency.

**Steps**:
1. Edit `_version.py` and update `__version__` string
2. Commit change: `git commit -m "chore: bump version to X.Y.Z"`
3. Run build: `python3 build/build.py`
4. Verify executable name contains new version
5. Test application: launch and check title/footer display
6. Distribute versioned executable

**Example**:
```bash
# Update version
echo '__version__ = "1.0.1"' > _version.py

# Commit
git add _version.py
git commit -m "chore: bump version to 1.0.1"

# Build
cd build
python3 build.py

# Verify output
ls dist/  # Should see: AbstractRenumberTool-v1.0.1.exe
```

**Contract Violation Examples** (to avoid):
- ❌ Editing version in GUI code directly
- ❌ Editing version in build script directly
- ❌ Distributing executable with mismatched version
- ❌ Skipping git commit before building

---

## Non-Functional Contracts

### Performance

- Version import MUST complete in <1ms
- Version display MUST NOT delay GUI initialization
- Build script version read MUST NOT add >100ms to build time

### Compatibility

- Version module MUST be Python 3.7+ compatible
- No external dependencies beyond stdlib
- Compatible with PyInstaller bundling (no dynamic imports)

### Security

- Version module MUST NOT contain secrets or credentials
- Version string MUST NOT expose internal architecture details
- Safe to display in window title (visible in screenshots, recordings)

---

## Validation Tests

### Contract Compliance Test Suite

```python
# tests/app/test_version_display.py

class TestVersionContract:
    """Validate version system contracts."""
    
    def test_version_module_exists(self):
        """Contract: _version.py must exist."""
        import _version
        assert _version is not None
    
    def test_version_attribute_exists(self):
        """Contract: __version__ must be defined."""
        from _version import __version__
        assert __version__ is not None
    
    def test_version_is_string(self):
        """Contract: __version__ must be a string."""
        from _version import __version__
        assert isinstance(__version__, str)
    
    def test_version_format_valid(self):
        """Contract: Version must match MAJOR.MINOR.PATCH."""
        from _version import __version__
        import re
        pattern = r'^\d+\.\d+\.\d+$'
        assert re.match(pattern, __version__), \
            f"Version '{__version__}' does not match format X.Y.Z"
    
    def test_window_title_includes_version(self):
        """Contract: Window title must show version."""
        # ... GUI test
    
    def test_footer_displays_version(self):
        """Contract: Footer must show version."""
        # ... GUI test
    
    def test_build_script_uses_version(self):
        """Contract: Executable name includes version."""
        # ... Build script test
```

---

## Breaking Changes

Changes to these contracts that would break consumers:

**MAJOR Version Bump Required**:
- Renaming `_version.py` to different filename
- Renaming `__version__` to different variable name
- Changing version format (e.g., adding fourth component)
- Moving version module to different package

**MINOR Version Bump**:
- Adding optional `__version_info__` attribute
- Adding optional `__build_date__` attribute

**PATCH Version Bump**:
- Documentation updates
- Internal comment changes

---

## Future Extensions (Out of Scope)

### Pre-release Versions
```python
__version__ = "1.0.0-alpha.1"
__version__ = "2.0.0-rc.2"
```

### Build Metadata
```python
__git_hash__ = "abc123def456"
__build_number__ = 42
```

### Version Comparison API
```python
def compare_versions(v1: str, v2: str) -> int:
    """Return -1, 0, or 1 for version comparison."""
    pass
```

These are NOT part of the current contract and require separate specification.

---

## Summary

The Version Display System contract is intentionally minimal:
1. **One source file**: `_version.py` with `__version__` string
2. **Two display locations**: Window title and footer
3. **One build integration**: PyInstaller executable naming
4. **Graceful degradation**: Fallback to "Unknown" or "dev" if version missing

All consumers MUST import from `_version.py`. All consumers MUST handle import failures gracefully. No exceptions.

