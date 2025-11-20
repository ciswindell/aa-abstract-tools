# Data Model: Version Display System

**Feature**: 005-version-display-system  
**Date**: 2025-11-20  
**Status**: Complete

## Overview

This feature involves a single entity (Version) stored as a Python module constant. No databases, no complex relationships, no state transitions—just a string constant that flows through the application for display purposes.

## Entities

### Version

**Description**: A semantic version identifier following the MAJOR.MINOR.PATCH format that uniquely identifies a release of the Abstract Renumber Tool.

**Attributes**:

| Attribute | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| `__version__` | str | Yes | Regex: `^\d+\.\d+\.\d+$` | Semantic version string (e.g., "1.0.0") |
| `__version_info__` | tuple[int, int, int] | No | N/A | Optional: Parsed version components (e.g., (1, 0, 0)) |
| `__build_date__` | str | No | ISO 8601 date format | Optional: Build/release date (e.g., "2025-11-20") |

**Storage Location**: `/home/chris/Code/aa-abstract-renumber/_version.py`

**Example**:
```python
# Minimal (required)
__version__ = "1.0.0"

# Extended (optional, future enhancement)
__version__ = "1.2.3"
__version_info__ = (1, 2, 3)
__build_date__ = "2025-11-20"
```

**Validation Rules**:
- **Format**: Must match pattern `MAJOR.MINOR.PATCH` where each component is a non-negative integer
- **Components**: MAJOR, MINOR, PATCH are all integers ≥ 0
- **Increment**: When changing version, only one component should increment, and lower components reset to 0
- **String Type**: Must be a string (not int, float, list)
- **No Leading Zeros**: "1.01.0" is invalid; "1.1.0" is correct

**Semantic Constraints**:
- **MAJOR = 0**: Pre-release development versions (0.1.0, 0.2.0, ...)
- **MAJOR ≥ 1**: Production releases
- **Version Order**: 1.0.0 < 1.0.1 < 1.1.0 < 2.0.0 (lexicographic comparison for simplicity)

---

## Relationships

**No relationships**: Version is a standalone constant with no connections to other entities. It's consumed (read-only) by:
- GUI window title (`app/tk_app.py`)
- GUI footer label (`app/tk_app.py`)
- Build script executable naming (`build/build.py`)

**Flow Diagram**:
```
_version.py (__version__)
    ↓ (import)
    ├→ app/tk_app.py (setup_window)     → Window title: "Tool v1.0.0"
    ├→ app/tk_app.py (version_footer)   → Footer label: "Version 1.0.0"
    └→ build/build.py (build script)    → Executable: "Tool-v1.0.0.exe"
```

---

## State Transitions

**None**: Version is immutable at runtime. Changes occur only at development time:

1. **Initial State**: Version = "0.1.0" (or "1.0.0" for first production release)
2. **Update**: Developer edits `_version.py`, commits, pushes
3. **Build**: Build script reads updated version, generates versioned executable
4. **Distribution**: Users receive executable with version in filename
5. **Runtime**: Application imports and displays version (read-only, never modified)

**No runtime state changes**—version is constant for the lifetime of each executable.

---

## Access Patterns

### Read Operations

**Import by GUI**:
```python
# app/tk_app.py
try:
    from _version import __version__
except (ImportError, AttributeError):
    __version__ = "Unknown"

# Use in setup_window()
self.root.title(f"Abstract Renumber Tool v{__version__}")

# Use in _create_version_footer()
version_label = ttk.Label(footer_frame, text=f"Version {__version__}")
```

**Import by Build Script**:
```python
# build/build.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _version import __version__

exe_name = f"AbstractRenumberTool-v{__version__}"
```

**Frequency**: 
- GUI: Once per application launch (on module import)
- Build script: Once per build execution
- Performance: ~0.001ms (standard Python import)

### Write Operations

**Manual Edit**:
```bash
# Developer workflow
vim _version.py
# Change: __version__ = "1.0.0" → "1.0.1"
git commit -m "chore: bump version to 1.0.1"
python3 build/build.py
```

**No programmatic writes**—version updates are always manual developer actions.

---

## Error Scenarios

| Error | Cause | Handling | User Impact |
|-------|-------|----------|-------------|
| File Missing | `_version.py` deleted or not found | Catch `ImportError`, fallback to "Unknown" | Application runs, version shows "Unknown" |
| Attribute Missing | `__version__` variable not defined | Catch `AttributeError`, fallback to "Unknown" | Application runs, version shows "Unknown" |
| Invalid Format | `__version__ = "abc"` (non-numeric) | No validation at import, displays as-is | Version displays invalid string (non-breaking) |
| Type Mismatch | `__version__ = 123` (int instead of str) | String formatting handles via `f"{123}"` | Version displays "123" (works but violates format) |
| Empty String | `__version__ = ""` | No validation, displays empty | Footer/title missing version (confusing but non-breaking) |

**Recommended Validation** (future enhancement):
```python
import re

def validate_version(version_str: str) -> bool:
    """Validate semantic version format."""
    return bool(re.match(r'^\d+\.\d+\.\d+$', version_str))

# In GUI or build script
if not validate_version(__version__):
    logger.warning(f"Invalid version format: {__version__}")
    __version__ = "Unknown"
```

---

## Testing Data

### Valid Test Cases

```python
# tests/app/test_version_display.py

def test_valid_versions():
    assert validate_version("0.0.0") == True
    assert validate_version("1.0.0") == True
    assert validate_version("1.2.3") == True
    assert validate_version("10.20.30") == True
    assert validate_version("999.999.999") == True

def test_invalid_versions():
    assert validate_version("1.0") == False      # Missing PATCH
    assert validate_version("1.0.0.0") == False  # Extra component
    assert validate_version("abc") == False      # Non-numeric
    assert validate_version("1.0.0-beta") == False  # Pre-release suffix
    assert validate_version("") == False         # Empty string
```

### Mock Version Module

```python
# Test fallback behavior
def test_missing_version_file(monkeypatch):
    """Simulate missing _version.py."""
    monkeypatch.delattr("_version.__version__", raising=False)
    
    # Import GUI code
    from app.tk_app import AbstractRenumberGUI
    
    # Verify fallback
    assert __version__ == "Unknown"
```

---

## Future Enhancements (Out of Scope)

### Version Comparison

```python
__version_info__ = (1, 2, 3)

def compare_versions(v1: tuple, v2: tuple) -> int:
    """Return -1 if v1 < v2, 0 if equal, 1 if v1 > v2."""
    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    return 0
```

### Build Metadata

```python
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__build_date__ = "2025-11-20"
__git_hash__ = "abc123def456"  # From git rev-parse HEAD
__build_number__ = 42  # CI/CD build counter
```

### Pre-release Versions

```python
__version__ = "1.0.0-alpha"
__version__ = "1.0.0-beta.2"
__version__ = "1.0.0-rc.1"
```

*Not implemented in current scope—requires version comparison logic and parsing.*

---

## References

- [Semantic Versioning Specification](https://semver.org/)
- [PEP 440 Version Identification](https://peps.python.org/pep-0440/)

