# Implementation Plan: Remove Streamlit Interface

**Branch**: `002-remove-streamlit` | **Date**: 2025-11-19 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/home/chris/Code/aa-abstract-renumber/specs/002-remove-streamlit/spec.md`

## Summary

Remove all Streamlit interface code, dependencies, and documentation from the dev branch. This cleanup task will eliminate the non-functional Streamlit UI implementation while preserving the existing Tkinter desktop interface. The removal includes Python files, imports, requirements file entries, and documentation references. This is a code deletion task with zero new functionality added.

## Technical Context

**Language/Version**: Python 3.11 (existing)  
**Primary Dependencies**: pandas, openpyxl, PyPDF2, python-dateutil, psutil, tkinter (existing - no changes)  
**Dependencies to Remove**: streamlit and all streamlit-related packages  
**Storage**: File-based (existing - no changes)  
**Testing**: pytest (existing test suite)  
**Target Platform**: Linux desktop (Ubuntu 22.04+), secondary Windows/macOS  
**Project Type**: Single project (existing structure)  
**Performance Goals**: No performance changes expected (possible minor improvement from reduced imports)  
**Constraints**: Must not affect existing Tkinter interface functionality  
**Scale/Scope**: Existing codebase cleanup - removal of abandoned Streamlit interface code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with Abstract Renumber Tool Constitution (v2.0.0):

- [x] **Clean Architecture**: Business logic in `core/` should be unaffected by UI code removal (Streamlit was in adapters/)
- [x] **Pipeline Processing**: Pipeline steps in `core/pipeline/steps/` should be unaffected (no Streamlit-specific steps)
- [x] **Memory Efficiency**: Removal of unused code cannot negatively impact memory usage
- [x] **Immutable Data**: DocumentUnit relationships are unaffected by UI code removal
- [x] **PEP 8 & SOLID/DRY**: Improves code quality by removing unused code and dependencies
- [x] **Local Desktop Interface**: Preserves Tkinter interface, removes non-compliant Streamlit interface (aligns with constitution)

**Gate Status**: ✅ PASS - This removal task aligns perfectly with Constitution v2.0.0 which specifies Tkinter-only local desktop interface. Removing Streamlit code brings the codebase into full compliance with principle VI (Local Desktop Interface).

**Post-Design Re-Check (after Phase 1)**:
- ✅ **Clean Architecture**: Design confirms Streamlit files are in `adapters/` only - core/ remains untouched
- ✅ **Pipeline Processing**: No pipeline steps affected - all in core/pipeline/steps/
- ✅ **Memory Efficiency**: Removal cannot harm memory efficiency (only improves by reducing loaded modules)
- ✅ **Immutable Data**: No DocumentUnit code in Streamlit files - complete separation verified
- ✅ **PEP 8 & SOLID/DRY**: Removing unused code improves DRY compliance (eliminates dead code)
- ✅ **Local Desktop Interface**: This removal ENFORCES constitution compliance - removes non-compliant interface

**Final Gate Status**: ✅✅ DOUBLE PASS - Both pre-research and post-design checks confirm full constitution compliance. This feature actively improves constitution adherence.

## Project Structure

### Documentation (this feature)

```text
specs/002-remove-streamlit/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - removal strategy and impact analysis
├── data-model.md        # Phase 1 output - files and dependencies to remove
├── quickstart.md        # Phase 1 output - step-by-step removal guide
└── contracts/           # Phase 1 output - N/A for removal task (verification steps instead)
```

### Source Code (repository root)

**Current Structure** (before removal):
```text
/home/chris/Code/aa-abstract-renumber/
├── core/                      # Business logic (should be unaffected)
│   ├── models/
│   ├── pipeline/
│   │   ├── steps/
│   │   └── context.py
│   ├── transform/
│   ├── config.py
│   └── interfaces.py
├── adapters/                  # External interfaces
│   ├── ui_tkinter.py         # KEEP - Tkinter interface (constitution-compliant)
│   ├── ui_streamlit.py       # REMOVE - Streamlit interface (if exists)
│   ├── excel_repo.py         # KEEP - No Streamlit dependencies
│   └── pdf_repo.py           # KEEP - No Streamlit dependencies
├── utils/                     # Utilities (should be unaffected)
├── fileops/                   # File operations (should be unaffected)
├── tests/                     # Test suite
│   ├── adapters/
│   │   ├── test_ui_streamlit.py  # REMOVE - Streamlit tests (if exists)
│   │   └── test_ui_tkinter.py    # KEEP - Tkinter tests
│   ├── core/                  # KEEP - Core tests
│   └── integration/
├── main.py                    # Entry point (KEEP - uses Tkinter)
├── requirements.txt           # UPDATE - Remove streamlit
├── README.md                  # UPDATE - Remove Streamlit references
└── [other config files]       # AUDIT - Remove Streamlit references

**Target Structure** (after removal):
```text
/home/chris/Code/aa-abstract-renumber/
├── core/                      # Business logic (unchanged)
├── adapters/                  # External interfaces
│   ├── ui_tkinter.py         # ONLY UI adapter remaining
│   ├── excel_repo.py
│   └── pdf_repo.py
├── utils/                     # Utilities (unchanged)
├── fileops/                   # File operations (unchanged)
├── tests/                     # Test suite
│   ├── adapters/
│   │   └── test_ui_tkinter.py
│   ├── core/
│   └── integration/
├── main.py                    # Entry point (unchanged)
├── requirements.txt           # Streamlit removed
├── README.md                  # Streamlit references removed
└── [other config files]       # Streamlit references removed
```

**Structure Decision**: This is a single project (Option 1) with existing structure. The removal task will delete Streamlit-specific files from `adapters/` and `tests/adapters/`, update `requirements.txt`, and clean documentation. No structural changes to the core architecture - only file deletions and dependency removals.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - This removal task is fully compliant with all constitution principles. In fact, it improves compliance by removing the Streamlit interface that conflicts with principle VI (Local Desktop Interface).
