# Data Model: Streamlit Removal Artifacts

**Feature**: 002-remove-streamlit  
**Date**: 2025-11-19

## Overview

This document models the artifacts that need to be identified, verified, and removed as part of the Streamlit interface cleanup. Unlike typical data models that define entities and relationships, this removal task models the "removal artifacts" - files, dependencies, and references that constitute the Streamlit interface.

## Entity Definitions

### Entity 1: Streamlit Source File

**Definition**: A Python source file that is part of the Streamlit interface implementation

**Attributes**:
- **File Path** (string): Absolute or relative path to the file
- **File Type** (enum): `adapter` | `page` | `component` | `config`
- **Import Count** (integer): Number of `import streamlit` statements
- **Line Count** (integer): Total lines in file
- **Delete Status** (enum): `pending` | `deleted` | `verified`

**Identification Criteria**:
- File contains `import streamlit`
- File is in `adapters/` and named `*streamlit*`
- File is in `pages/` directory
- File is in `pages/components/` directory

**Known Instances**:
```
./adapters/ui_streamlit.py                      [adapter]
./pages/multi_file_merge.py                     [page]
./pages/mode_selection.py                       [page]
./pages/base_page.py                            [page]
./pages/single_file_processing.py               [page]
./pages/components/processing_options.py        [component]
./pages/components/file_upload.py               [component]
./pages/components/tabbed_workflow.py           [component]
./pages/components/state_management.py          [component]
./pages/components/styling.py                   [component]
./pages/components/downloads.py                 [component]
```

**Removal Action**: Delete file from repository

**Verification**: File no longer exists in working directory

---

### Entity 2: Streamlit Dependency Entry

**Definition**: A package dependency declaration for Streamlit or Streamlit-related packages

**Attributes**:
- **File Path** (string): Path to dependency file (e.g., `requirements.txt`)
- **Package Name** (string): Name of the package (e.g., `streamlit`)
- **Version Spec** (string): Version specification (e.g., `==1.49.0`)
- **Line Number** (integer): Line number in dependency file
- **Remove Status** (enum): `pending` | `removed` | `verified`

**Identification Criteria**:
- Line in `requirements.txt` contains `streamlit`
- Line in `setup.py` contains `streamlit`
- Line in `pyproject.toml` contains `streamlit`

**Known Instances**:
```
requirements.txt:streamlit==1.49.0
```

**Removal Action**: Delete line from dependency file

**Verification**: 
- Line removed from dependency file
- Fresh `pip install -r requirements.txt` does not install streamlit
- `pip list | grep streamlit` returns nothing

---

### Entity 3: Streamlit Import Statement

**Definition**: An import statement in Python code that imports Streamlit

**Attributes**:
- **File Path** (string): Path to file containing the import
- **Line Number** (integer): Line number of import statement
- **Import Style** (enum): `standard` | `alias` | `from_import`
- **Import Text** (string): Full text of import (e.g., `import streamlit as st`)
- **Resolution Status** (enum): `pending` | `file_deleted` | `import_removed`

**Identification Criteria**:
- Line matches pattern: `import streamlit`
- Line matches pattern: `import streamlit as st`
- Line matches pattern: `from streamlit import ...`

**Removal Strategy**:
- If file is Streamlit Source File → Delete entire file (import removed implicitly)
- If file is non-Streamlit file → Remove import line (should not occur if architecture is clean)

**Verification**: 
- `grep -r "import streamlit" --include="*.py" . | grep -v ".venv"` returns nothing

---

### Entity 4: Streamlit Documentation Reference

**Definition**: A reference to Streamlit in documentation, README, or code comments

**Attributes**:
- **File Path** (string): Path to file containing the reference
- **Line Number** (integer): Line number of reference
- **Context** (string): Surrounding text for context
- **Reference Type** (enum): `installation` | `usage` | `interface_option` | `comment` | `other`
- **Action** (enum): `remove` | `update` | `leave`

**Identification Criteria**:
- Case-insensitive match of "streamlit" in documentation files
- Case-insensitive match of "streamlit" in README.md
- Case-insensitive match of "streamlit" in code comments

**Known Locations** (to verify):
- `README.md`
- `docs/` directory (if exists)
- Python docstrings
- Inline comments

**Removal Strategy**:
- Installation instructions mentioning Streamlit → Remove
- Interface comparison (Streamlit vs Tkinter) → Update to note Tkinter-only
- Comments about Streamlit issues → Remove (no longer relevant)
- Historical notes → Leave or update to past tense ("Previously supported Streamlit...")

**Verification**:
- `grep -i streamlit README.md` returns nothing or only historical notes
- Documentation clearly states Tkinter-only interface

---

### Entity 5: Streamlit Directory

**Definition**: A directory containing exclusively Streamlit-related files

**Attributes**:
- **Directory Path** (string): Path to directory
- **File Count** (integer): Number of files in directory
- **Subdirectory Count** (integer): Number of subdirectories
- **Delete Status** (enum): `pending` | `deleted` | `verified`

**Identification Criteria**:
- Directory name suggests Streamlit usage (e.g., `pages/`)
- All files in directory are Streamlit Source Files

**Known Instances**:
```
./pages/                     [10+ files, 1 subdirectory]
./pages/components/          [5+ files]
```

**Removal Action**: Delete entire directory recursively

**Verification**: 
- Directory no longer exists in working directory
- `ls -la pages/` returns "No such file or directory"

---

## Relationships

### Containment Hierarchy

```
Streamlit Directory
  └─ Contains ─→ Streamlit Source File(s)
      └─ Contains ─→ Streamlit Import Statement(s)
```

**Implication**: Deleting a Streamlit Directory removes all contained Source Files and their Import Statements in one operation.

### Dependency Chain

```
Streamlit Dependency Entry
  └─ Causes Installation Of ─→ Streamlit Package
      └─ Enables ─→ Streamlit Import Statement
```

**Implication**: Removing Streamlit Dependency Entry will cause import errors if any Streamlit Import Statements remain (this validates complete removal).

### Documentation References

```
Streamlit Documentation Reference
  └─ Describes ─→ Streamlit Source File(s) OR Streamlit Dependency Entry
```

**Implication**: After removing files and dependencies, documentation references become outdated and must be updated or removed.

## State Transitions

### Streamlit Source File States

```
[Identified] → [Delete Requested] → [Deleted] → [Verified Absent]
                                        ↓
                                [Rollback: File Restored]
```

### Streamlit Dependency Entry States

```
[Present] → [Marked for Removal] → [Removed] → [Verified Not Installed]
                                        ↓
                                [Rollback: Re-added to requirements.txt]
```

### Overall Removal Progress States

```
[Initial State] → [Files Removed] → [Dependencies Removed] → [Documentation Updated] → [Complete]
       ↓                 ↓                    ↓                         ↓
   [Rollback]      [Rollback]          [Rollback]              [Rollback]
```

## Validation Rules

### Pre-Removal Validation

1. **File Existence**: All identified Streamlit Source Files must exist before removal
2. **No Shared Code**: Verify no non-Streamlit files import from Streamlit files
3. **Tkinter Independence**: Verify Tkinter interface does not depend on Streamlit files

### Post-Removal Validation

1. **Complete File Removal**: Zero Streamlit Source Files remain
2. **Complete Import Removal**: Zero Streamlit Import Statements in non-venv code
3. **Complete Dependency Removal**: `pip list` contains zero streamlit packages
4. **Documentation Cleanup**: Zero Streamlit installation/usage instructions remain (or updated to note historical)
5. **Tkinter Functionality**: Tkinter interface launches and operates correctly

### Verification Queries

**Count remaining Streamlit files**:
```bash
find . -name "*.py" -path "*/pages/*" -o -name "*streamlit*.py" | grep -v ".venv" | wc -l
# Expected: 0
```

**Count remaining Streamlit imports**:
```bash
grep -r "import streamlit" --include="*.py" . | grep -v ".venv" | wc -l
# Expected: 0
```

**Verify Streamlit not in requirements**:
```bash
grep -i streamlit requirements.txt | wc -l
# Expected: 0
```

**Verify Streamlit not installed**:
```bash
pip list | grep -i streamlit | wc -l
# Expected: 0
```

## Edge Cases

### Edge Case 1: Shared Utilities

**Scenario**: A utility function in `utils/` is used by both Streamlit and Tkinter interfaces

**Detection**: Check for imports from `utils/` in Streamlit files, then verify if Tkinter also imports same function

**Resolution**: 
- If Tkinter uses it: Keep the utility (it's not Streamlit-specific)
- If only Streamlit uses it: Delete or leave (won't hurt to keep generic utilities)

**Validation**: Tkinter interface still works after Streamlit removal

### Edge Case 2: Configuration Files

**Scenario**: Config file (e.g., `.streamlit/config.toml`) exists for Streamlit-specific settings

**Detection**: Look for `.streamlit/` directory or `*streamlit*.toml` files

**Resolution**: Delete entire `.streamlit/` directory if present

**Validation**: No `.streamlit/` directory remains

### Edge Case 3: Import in __init__.py

**Scenario**: `adapters/__init__.py` might import `ui_streamlit`

**Detection**: Check `adapters/__init__.py` for streamlit imports

**Resolution**: Remove import line from `__init__.py`

**Validation**: `python3 -c "import adapters"` succeeds without errors

### Edge Case 4: Conditional Imports

**Scenario**: Code uses try/except to conditionally import Streamlit

**Example**:
```python
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
```

**Detection**: Search for `try:` blocks containing `import streamlit`

**Resolution**: 
- If in Streamlit file: File will be deleted (no action needed)
- If in shared file: Remove try/except block or set `HAS_STREAMLIT = False` permanently

**Validation**: No conditional Streamlit imports remain

## Success Metrics

### Quantitative Metrics

- **Files Deleted**: 11+ files removed (1 adapter + 10+ pages)
- **Directories Deleted**: 2 directories removed (`pages/`, `pages/components/`)
- **Dependencies Removed**: 1 direct dependency (`streamlit==1.49.0`)
- **Import Statements Removed**: 10+ import statements (via file deletion)
- **Documentation References**: 0 installation/usage references remain

### Qualitative Metrics

- **Codebase Clarity**: No confusion about which UI to use (Tkinter only)
- **Installation Simplicity**: Faster installation, fewer dependencies
- **Constitution Compliance**: 100% compliant with Principle VI (Local Desktop Interface)
- **Maintenance Burden**: Reduced by eliminating unused interface code

## Summary

This data model defines five key artifact types for removal:
1. **Streamlit Source Files** - 11+ Python files to delete
2. **Streamlit Dependency Entries** - 1 requirement to remove
3. **Streamlit Import Statements** - Removed via file deletion
4. **Streamlit Documentation References** - To update or remove
5. **Streamlit Directories** - 2 directories to delete

The relationships and state transitions ensure a clean, verifiable removal process with clear success criteria.

