# Quickstart: Remove Streamlit Interface

**Feature**: 002-remove-streamlit  
**Date**: 2025-11-19  
**Estimated Time**: 15-20 minutes  
**Difficulty**: Easy (code deletion task)

## Prerequisites

- [x] Feature specification reviewed ([spec.md](spec.md))
- [x] Research completed ([research.md](research.md))
- [x] Data model understood ([data-model.md](data-model.md))
- [x] Branch `002-remove-streamlit` checked out
- [x] Clean git status (no uncommitted changes)

## Overview

This guide walks through the complete removal of the Streamlit interface in three phases:
1. **Phase A**: Delete Streamlit files
2. **Phase B**: Remove Streamlit dependencies
3. **Phase C**: Update documentation

Each phase includes verification steps to ensure correctness before proceeding.

---

## Phase A: Delete Streamlit Files

### Step A1: Verify Current State

Before deletion, confirm what files exist:

```bash
cd /home/chris/Code/aa-abstract-renumber

# List Streamlit files
echo "=== Streamlit Adapter ==="
ls -lh adapters/ui_streamlit.py 2>/dev/null || echo "Not found"

echo "=== Pages Directory ==="
ls -lh pages/ 2>/dev/null || echo "Not found"

echo "=== Streamlit Imports Count ==="
grep -r "import streamlit" --include="*.py" . 2>/dev/null | grep -v ".venv" | wc -l
```

**Expected Output**:
- `adapters/ui_streamlit.py` exists
- `pages/` directory exists with multiple files
- Import count: 10+ imports

### Step A2: Delete Streamlit Adapter File

```bash
# Delete the Streamlit adapter
rm adapters/ui_streamlit.py

# Verify deletion
test ! -f adapters/ui_streamlit.py && echo "✓ Deleted" || echo "✗ Still exists"
```

**Expected**: `✓ Deleted`

### Step A3: Delete Pages Directory

```bash
# Delete entire pages directory recursively
rm -rf pages/

# Verify deletion
test ! -d pages && echo "✓ Deleted" || echo "✗ Still exists"
```

**Expected**: `✓ Deleted`

### Step A4: Check for Additional Streamlit Files

```bash
# Search for any remaining files with 'streamlit' in the name (excluding .venv)
find . -name "*streamlit*" -type f ! -path "*/.venv/*" ! -path "*/.git/*" ! -path "*/specs/*"

# Expected: No output (all Streamlit files removed)
```

**Expected**: No files found (empty output)

### Step A5: Verify Import Cleanup

```bash
# Count remaining Streamlit imports (excluding .venv)
IMPORT_COUNT=$(grep -r "import streamlit" --include="*.py" . 2>/dev/null | grep -v ".venv" | wc -l)

echo "Remaining Streamlit imports: $IMPORT_COUNT"

# Expected: 0
```

**Expected**: `Remaining Streamlit imports: 0`

### Step A6: Check adapters/__init__.py

```bash
# Check if adapters/__init__.py imports ui_streamlit
if [ -f adapters/__init__.py ]; then
    echo "=== Checking adapters/__init__.py ==="
    grep -i streamlit adapters/__init__.py || echo "✓ No Streamlit imports"
else
    echo "✓ adapters/__init__.py does not exist"
fi
```

**Expected**: `✓ No Streamlit imports` or file doesn't exist

**If Streamlit import found**: Remove the import line manually:
```bash
# Edit adapters/__init__.py and remove the line importing ui_streamlit
nano adapters/__init__.py  # or use your preferred editor
```

### Step A7: Verify Python Syntax

```bash
# Verify no import errors in key files
python3 -c "import adapters.ui_tkinter; print('✓ Tkinter adapter OK')"
python3 -c "import main; print('✓ main.py OK')"
```

**Expected**:
- `✓ Tkinter adapter OK`
- `✓ main.py OK`

### ✅ Phase A Complete

**Verification Checklist**:
- [x] `adapters/ui_streamlit.py` deleted
- [x] `pages/` directory deleted
- [x] Zero Streamlit imports remain (excluding .venv)
- [x] No import errors in Tkinter adapter or main.py

**Git Checkpoint** (optional):
```bash
git add -A
git commit -m "Phase A: Remove Streamlit files

- Delete adapters/ui_streamlit.py
- Delete pages/ directory and all contents
- Remove all Streamlit source files from repository"
```

---

## Phase B: Remove Streamlit Dependencies

### Step B1: Backup requirements.txt

```bash
# Create backup
cp requirements.txt requirements.txt.backup

echo "✓ Backup created: requirements.txt.backup"
```

### Step B2: Remove Streamlit from requirements.txt

```bash
# Remove streamlit line from requirements.txt
grep -v "^streamlit" requirements.txt > requirements.txt.tmp
mv requirements.txt.tmp requirements.txt

echo "=== Updated requirements.txt ==="
cat requirements.txt
```

**Verify**: `streamlit==1.49.0` line should be gone

### Step B3: Verify requirements.txt

```bash
# Confirm streamlit is not in requirements
grep -i streamlit requirements.txt && echo "✗ Streamlit still present" || echo "✓ Streamlit removed"
```

**Expected**: `✓ Streamlit removed`

### Step B4: Check Other Dependency Files

```bash
# Check if other dependency files exist
for file in setup.py pyproject.toml setup.cfg; do
    if [ -f "$file" ]; then
        echo "=== Checking $file ==="
        grep -i streamlit "$file" || echo "✓ No Streamlit in $file"
    fi
done
```

**Expected**: No Streamlit found in any additional files

### Step B5: Test Fresh Install (Optional)

**⚠️ Warning**: This creates a temporary virtual environment. Skip if you prefer to test later.

```bash
# Create test environment
python3 -m venv /tmp/test_venv
source /tmp/test_venv/bin/activate

# Install updated dependencies
pip install -r requirements.txt

# Check if streamlit installed
pip list | grep -i streamlit && echo "✗ Streamlit installed" || echo "✓ Streamlit not installed"

# Cleanup
deactivate
rm -rf /tmp/test_venv
```

**Expected**: `✓ Streamlit not installed`

### ✅ Phase B Complete

**Verification Checklist**:
- [x] `requirements.txt` does not contain `streamlit`
- [x] Other dependency files (if present) don't contain `streamlit`
- [x] Fresh install (if tested) does not install Streamlit

**Git Checkpoint**:
```bash
git add requirements.txt
git commit -m "Phase B: Remove Streamlit dependency

- Remove streamlit==1.49.0 from requirements.txt
- Verify no other dependency files reference Streamlit"
```

---

## Phase C: Update Documentation

### Step C1: Check README.md

```bash
# Search for Streamlit references in README
echo "=== Streamlit references in README.md ==="
grep -in streamlit README.md || echo "✓ No references found"
```

**If references found**: Proceed to Step C2  
**If no references found**: Skip to Phase C Complete

### Step C2: Update README.md (if needed)

```bash
# Open README.md for editing
nano README.md  # or your preferred editor
```

**Update Guidelines**:
- **Remove**: Installation instructions mentioning Streamlit
- **Remove**: Usage sections describing Streamlit interface
- **Remove**: Streamlit interface screenshots or examples
- **Update**: Interface options section to note "Tkinter desktop interface only"
- **Optional**: Add historical note like "Note: Streamlit interface was removed in v2.0 (2025-11-19)"

**Example Changes**:

**Before**:
```markdown
## Installation

pip install -r requirements.txt

This includes both Tkinter (desktop) and Streamlit (web) interfaces.

## Usage

### Desktop Interface (Tkinter)
python3 main.py

### Web Interface (Streamlit)
streamlit run streamlit_app.py
```

**After**:
```markdown
## Installation

pip install -r requirements.txt

## Usage

### Desktop Interface (Tkinter)
python3 main.py

Note: The application uses a local Tkinter desktop interface. Web interface (Streamlit) was removed as of 2025-11-19.
```

### Step C3: Check Other Documentation

```bash
# Search for Streamlit in other docs
find . -name "*.md" -type f ! -path "*/.venv/*" ! -path "*/.git/*" -exec grep -l -i streamlit {} \;
```

**For each file found**: Review and update similar to README.md

### Step C4: Search Code Comments

```bash
# Find Streamlit mentions in code comments
grep -r "streamlit" --include="*.py" . 2>/dev/null | grep -v ".venv" | grep -v "specs/"
```

**If found**: Review each instance:
- In deleted files: Already removed (no action)
- In remaining files: Remove or update comment

### ✅ Phase C Complete

**Verification Checklist**:
- [x] README.md updated (Streamlit references removed or noted as historical)
- [x] Other documentation files updated
- [x] Code comments reviewed and updated

**Git Checkpoint**:
```bash
git add README.md  # and any other updated docs
git commit -m "Phase C: Update documentation to remove Streamlit references

- Remove Streamlit installation instructions from README.md
- Update interface documentation to note Tkinter-only support
- Add historical note about Streamlit removal"
```

---

## Final Verification

Run all verification contracts from [contracts/README.md](contracts/README.md):

### Quick Verification Script

```bash
echo "=== Streamlit Removal Verification ==="
echo ""

# Contract 1: File System State
echo "Contract 1: File System State"
test ! -f ./adapters/ui_streamlit.py && echo "  ✓ ui_streamlit.py removed" || echo "  ✗ ui_streamlit.py still exists"
test ! -d ./pages && echo "  ✓ pages/ directory removed" || echo "  ✗ pages/ directory still exists"

# Contract 2: Dependency State
echo "Contract 2: Dependency State"
! grep -i streamlit requirements.txt && echo "  ✓ Streamlit removed from requirements.txt" || echo "  ✗ Streamlit still in requirements.txt"

# Contract 4: Import State
echo "Contract 4: Import State"
IMPORT_COUNT=$(grep -r "import streamlit" --include="*.py" . 2>/dev/null | grep -v ".venv" | wc -l)
[ $IMPORT_COUNT -eq 0 ] && echo "  ✓ No Streamlit imports remain" || echo "  ✗ $IMPORT_COUNT Streamlit imports remain"

# Contract 5: Tkinter Functionality
echo "Contract 5: Tkinter Functionality"
python3 -c "from adapters.ui_tkinter import AbstractRenumberGUI" 2>/dev/null && echo "  ✓ Tkinter adapter imports successfully" || echo "  ✗ Tkinter adapter import failed"
python3 -c "import main" 2>/dev/null && echo "  ✓ main.py imports successfully" || echo "  ✗ main.py import failed"

echo ""
echo "=== Verification Complete ==="
```

**Expected Output**: All checks show ✓ (pass)

### Manual Test (Recommended)

```bash
# Launch the Tkinter application
python3 main.py
```

**Verify**:
- Application launches without errors
- Tkinter window displays correctly
- File selection and processing work normally

---

## Completion Checklist

Before merging to dev:

- [ ] All Streamlit files deleted (Phase A complete)
- [ ] Streamlit dependency removed (Phase B complete)
- [ ] Documentation updated (Phase C complete)
- [ ] All verification contracts pass
- [ ] Tkinter application tested manually
- [ ] All changes committed to `002-remove-streamlit` branch

## Summary of Changes

**Files Deleted**:
- `adapters/ui_streamlit.py`
- `pages/` directory (10+ files)

**Files Modified**:
- `requirements.txt` (removed `streamlit==1.49.0`)
- `README.md` (removed Streamlit references)
- Any other documentation files with Streamlit references

**Total Impact**:
- ~11+ files deleted
- ~1-3 files modified
- 0 new files added

## Next Steps

After all verification passes:

1. **Merge to dev**:
   ```bash
   git checkout dev
   git merge 002-remove-streamlit --no-ff -m "Merge 002-remove-streamlit: Remove Streamlit interface"
   ```

2. **Delete feature branch**:
   ```bash
   git branch -d 002-remove-streamlit
   ```

3. **Push changes** (if using remote):
   ```bash
   git push origin dev
   ```

4. **Update your environment**:
   ```bash
   pip uninstall streamlit  # Remove from current environment if installed
   pip install -r requirements.txt  # Reinstall clean dependencies
   ```

## Troubleshooting

### Issue: Import errors after deletion

**Symptom**: `ImportError: cannot import name 'ui_streamlit'`

**Cause**: Some file still tries to import the deleted module

**Fix**:
```bash
# Find the offending import
grep -r "ui_streamlit" --include="*.py" . | grep -v ".venv"

# Remove or comment out the import in the found file
```

### Issue: Tkinter doesn't launch

**Symptom**: Application crashes or won't start

**Cause**: Possible shared code was deleted

**Fix**:
```bash
# Check error message for missing imports
python3 main.py 2>&1 | grep "ImportError\|ModuleNotFoundError"

# Restore specific files if needed
git checkout dev -- path/to/file
```

### Issue: Streamlit still in pip list

**Symptom**: `pip list | grep streamlit` shows Streamlit installed

**Cause**: Old environment still has Streamlit installed

**Fix**:
```bash
# Uninstall from current environment
pip uninstall streamlit -y

# Or create fresh environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Time Estimates

- **Phase A** (Delete files): 5 minutes
- **Phase B** (Remove dependencies): 3 minutes
- **Phase C** (Update docs): 5-10 minutes
- **Verification**: 5 minutes
- **Total**: 15-20 minutes

## References

- **Specification**: [spec.md](spec.md)
- **Research**: [research.md](research.md)
- **Data Model**: [data-model.md](data-model.md)
- **Verification Contracts**: [contracts/README.md](contracts/README.md)
- **Constitution**: [/home/chris/Code/aa-abstract-renumber/.specify/memory/constitution.md](../../.specify/memory/constitution.md)

