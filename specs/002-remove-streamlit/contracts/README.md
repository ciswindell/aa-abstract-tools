# Contracts: Streamlit Removal Verification

**Feature**: 002-remove-streamlit  
**Date**: 2025-11-19

## Overview

This feature is a **code removal task**, not a feature addition. Therefore, there are no API contracts, endpoints, or schemas to define. Instead, this directory contains **verification contracts** - the criteria that must be met to confirm successful removal.

## Verification Contracts

### Contract 1: File System State

**Pre-Condition**: Streamlit files exist in repository

**Post-Condition**: Streamlit files completely removed

**Verification Steps**:
```bash
# No Streamlit adapter file
test ! -f ./adapters/ui_streamlit.py && echo "✓ PASS" || echo "✗ FAIL"

# No pages directory
test ! -d ./pages && echo "✓ PASS" || echo "✗ FAIL"

# No Streamlit Python files (excluding .venv)
[ $(find . -name "*.py" -type f ! -path "*/.venv/*" -exec grep -l "import streamlit" {} \; | wc -l) -eq 0 ] && echo "✓ PASS" || echo "✗ FAIL"
```

**Expected Result**: All checks return `✓ PASS`

---

### Contract 2: Dependency State

**Pre-Condition**: `streamlit==1.49.0` in requirements.txt

**Post-Condition**: Streamlit not in any dependency files

**Verification Steps**:
```bash
# Streamlit not in requirements.txt
! grep -i streamlit requirements.txt && echo "✓ PASS" || echo "✗ FAIL"

# Streamlit not in setup.py (if exists)
test ! -f setup.py || ! grep -i streamlit setup.py && echo "✓ PASS" || echo "✗ FAIL"

# Streamlit not in pyproject.toml (if exists)
test ! -f pyproject.toml || ! grep -i streamlit pyproject.toml && echo "✓ PASS" || echo "✗ FAIL"
```

**Expected Result**: All checks return `✓ PASS`

---

### Contract 3: Installation State

**Pre-Condition**: Streamlit may be installed in current environment

**Post-Condition**: Fresh installation does not include Streamlit

**Verification Steps**:
```bash
# Create fresh virtual environment
python3 -m venv /tmp/test_venv
source /tmp/test_venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify streamlit not installed
! pip list | grep -i streamlit && echo "✓ PASS" || echo "✗ FAIL"

# Cleanup
deactivate
rm -rf /tmp/test_venv
```

**Expected Result**: `✓ PASS` (streamlit not found in pip list)

---

### Contract 4: Import State

**Pre-Condition**: Multiple files import streamlit

**Post-Condition**: Zero non-venv Python files import streamlit

**Verification Steps**:
```bash
# Search for streamlit imports (excluding .venv)
IMPORT_COUNT=$(grep -r "import streamlit" --include="*.py" . 2>/dev/null | grep -v ".venv" | wc -l)

[ $IMPORT_COUNT -eq 0 ] && echo "✓ PASS: 0 imports found" || echo "✗ FAIL: $IMPORT_COUNT imports remain"
```

**Expected Result**: `✓ PASS: 0 imports found`

---

### Contract 5: Tkinter Functionality

**Pre-Condition**: Tkinter interface works before removal

**Post-Condition**: Tkinter interface still works after removal

**Verification Steps**:
```bash
# Syntax check
python3 -c "from adapters.ui_tkinter import AbstractRenumberGUI; print('✓ PASS: Import successful')"

# Entry point check
python3 -c "import main; print('✓ PASS: main.py imports correctly')"

# Visual test (requires manual verification)
# python3 main.py  # Launch application and verify it starts without errors
```

**Expected Result**: 
- `✓ PASS: Import successful`
- `✓ PASS: main.py imports correctly`
- Application launches and displays Tkinter window (manual verification)

---

### Contract 6: Documentation State

**Pre-Condition**: Documentation may reference Streamlit

**Post-Condition**: Documentation does not instruct users to install or use Streamlit

**Verification Steps**:
```bash
# Check README for Streamlit references
echo "README.md Streamlit references:"
grep -in streamlit README.md || echo "✓ PASS: No references found"

# Check for installation instructions mentioning Streamlit
echo "Installation instruction check:"
grep -A 3 -B 3 -in "install.*streamlit\|streamlit.*install" README.md || echo "✓ PASS: No installation instructions found"
```

**Expected Result**: 
- Either no references found (✓ PASS)
- Or references are historical/past-tense only (e.g., "Previously supported Streamlit")

---

## Test Execution Order

Execute verification contracts in this order:

1. **Contract 4: Import State** (fast, non-destructive)
2. **Contract 1: File System State** (fast, non-destructive)
3. **Contract 2: Dependency State** (fast, non-destructive)
4. **Contract 6: Documentation State** (fast, non-destructive)
5. **Contract 5: Tkinter Functionality** (medium, requires Python execution)
6. **Contract 3: Installation State** (slow, creates virtual environment)

**Stop Condition**: If any contract fails, stop and investigate before proceeding.

## Acceptance Criteria

**Feature Complete** when all 6 contracts return PASS:

- ✓ Contract 1: File System State
- ✓ Contract 2: Dependency State
- ✓ Contract 3: Installation State
- ✓ Contract 4: Import State
- ✓ Contract 5: Tkinter Functionality
- ✓ Contract 6: Documentation State

## Rollback Plan

If any contract fails and cannot be fixed:

```bash
# Discard all changes
git checkout dev

# Or discard specific files
git checkout dev -- path/to/file
```

The feature branch `002-remove-streamlit` can be deleted if removal causes unrecoverable issues.

## Notes

This feature intentionally has **no API contracts** because it removes code rather than adding it. The verification contracts above serve as acceptance tests, confirming that:

1. All Streamlit artifacts are removed
2. No broken imports remain
3. Tkinter interface continues to function
4. Fresh installations don't include Streamlit
5. Documentation is updated appropriately

These verification contracts replace traditional API contracts for this removal task.

