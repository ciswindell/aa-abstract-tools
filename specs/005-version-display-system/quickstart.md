# Quickstart: Version Display System

**Feature**: 005-version-display-system  
**Audience**: Developers maintaining Abstract Renumber Tool  
**Time to Read**: 2 minutes

## What This Feature Does

- Displays application version in window title and footer
- Single source of truth: `_version.py` at project root
- Automatic versioned executable naming (e.g., `AbstractRenumberTool-v1.0.0.exe`)
- Follows semantic versioning: MAJOR.MINOR.PATCH

---

## Quick Reference

### Update Version for New Release

```bash
# 1. Edit version file
vim _version.py
# Change: __version__ = "1.0.0" to "1.0.1" (or appropriate version)

# 2. Commit
git add _version.py
git commit -m "chore: bump version to 1.0.1"

# 3. Build
cd build
python3 build.py

# 4. Verify
ls dist/  # Should see: AbstractRenumberTool-v1.0.1.exe

# 5. Test
./dist/AbstractRenumberTool-v1.0.1.exe
# Check window title shows "v1.0.1"
# Check footer shows "Version 1.0.1"
```

---

## Version Increment Rules

| Change Type | Example | Version Change |
|-------------|---------|----------------|
| **Bug fix** | Fixed Windows warning, typo correction | `1.0.0` → `1.0.1` (PATCH) |
| **New feature** | Added export button, new checkbox option | `1.0.1` → `1.1.0` (MINOR) |
| **Breaking change** | Removed feature, redesigned UI workflow | `1.1.0` → `2.0.0` (MAJOR) |

**Reset Rule**: When incrementing, reset lower components to 0
- `1.2.5` → `1.3.0` (added feature, reset PATCH)
- `1.3.7` → `2.0.0` (breaking change, reset MINOR and PATCH)

---

## Where Version Appears

1. **Window Title**: "Abstract Renumber Tool v1.0.0"
2. **Footer Label**: "Version 1.0.0" (bottom-right, gray text)
3. **Executable Name**: `AbstractRenumberTool-v1.0.0.exe`

---

## Files Modified

### Core Files (you'll edit these)

```text
_version.py              # UPDATE: Change __version__ string
```

### Implementation Files (already implemented)

```text
app/tk_app.py            # Reads version, displays in title and footer
build/build.py           # Reads version, names executable
```

---

## Common Tasks

### Check Current Version

```bash
# From code
python3 -c "from _version import __version__; print(__version__)"

# From git
git log --oneline | grep "bump version"

# From executable filename
ls dist/ | grep AbstractRenumberTool
```

### Create First Release

```bash
# Set to 1.0.0 (production-ready)
echo '__version__ = "1.0.0"' > _version.py
git commit -m "chore: set version to 1.0.0 for first release"
cd build && python3 build.py
```

### Pre-release Versions (0.x.y)

```bash
# Use 0.x.y for testing/development
echo '__version__ = "0.1.0"' > _version.py  # Alpha
echo '__version__ = "0.9.0"' > _version.py  # Release candidate
echo '__version__ = "1.0.0"' > _version.py  # First production release
```

---

## Troubleshooting

### Version shows "Unknown" in GUI

**Cause**: `_version.py` missing or `__version__` not defined  
**Fix**:
```bash
# Check file exists
ls _version.py

# Check content
cat _version.py
# Should see: __version__ = "X.Y.Z"

# Recreate if missing
echo '__version__ = "1.0.0"' > _version.py
```

### Executable name doesn't include version

**Cause**: Build script can't import `_version.py`  
**Fix**:
```bash
# Verify import works
python3 -c "from _version import __version__; print(__version__)"

# Rebuild
cd build && python3 build.py
```

### Version format invalid (X.Y instead of X.Y.Z)

**Cause**: Missing PATCH component  
**Fix**:
```bash
# Must have three components
echo '__version__ = "1.0.0"' > _version.py  # Correct
# NOT: __version__ = "1.0"                   # Incorrect
```

---

## Testing Version System

```bash
# Run version-related tests
cd /home/chris/Code/aa-abstract-renumber
python3 -m pytest tests/app/test_version_display.py -v

# Expected tests:
# ✓ test_version_import
# ✓ test_version_format
# ✓ test_version_fallback
# ✓ test_window_title_contains_version
# ✓ test_footer_displays_version
```

---

## Advanced: Extended Version Info (Optional)

For future enhancements, you can add optional metadata:

```python
# _version.py (extended)
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)      # Tuple for comparison
__build_date__ = "2025-11-20"     # ISO 8601 date
```

**Note**: GUI and build script currently only use `__version__` string.

---

## Semantic Versioning Quick Guide

### MAJOR (X.0.0) - Breaking Changes
- User workflows break or change significantly
- Features removed
- UI completely redesigned

**Example**: Changed from single-file mode to batch mode (workflow incompatible)

### MINOR (x.Y.0) - New Features
- New buttons, options, or capabilities
- Backward compatible (old workflows still work)
- No functionality removed

**Example**: Added "Export to CSV" button, users can ignore if they don't need it

### PATCH (x.y.Z) - Bug Fixes
- Fixed crashes, errors, or incorrect behavior
- Performance improvements
- Documentation/typo corrections
- No new features, no breaking changes

**Example**: Fixed Windows file locking warning, corrected error message spelling

---

## Related Documentation

- **Spec**: `specs/005-version-display-system/spec.md` (requirements)
- **Plan**: `specs/005-version-display-system/plan.md` (implementation design)
- **Research**: `specs/005-version-display-system/research.md` (design decisions)
- **Data Model**: `specs/005-version-display-system/data-model.md` (version structure)
- **Contracts**: `specs/005-version-display-system/contracts/README.md` (API details)

---

## Cheat Sheet

```bash
# Update version workflow (copy-paste ready)
vim _version.py                              # Edit version
git add _version.py && git commit -m "chore: bump version to X.Y.Z"
cd build && python3 build.py                 # Build
ls dist/AbstractRenumberTool-v*.exe          # Verify
```

**Remember**: Only edit `_version.py`, never edit version strings in GUI or build code!

