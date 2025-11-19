# Tasks: Remove Streamlit Interface

**Input**: Design documents from `/home/chris/Code/aa-abstract-renumber/specs/002-remove-streamlit/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md, contracts/ (all complete)

**Tests**: Per Constitution v2.0.0, tests are RECOMMENDED but not mandatory. This is a removal task with no new functionality, so no new tests are being created.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project uses the single project structure with:
- Core business logic in `core/`
- Adapters in `adapters/`
- Pages (Streamlit-specific) in `pages/`
- Utilities in `utils/`
- Tests in `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Branch verification and pre-removal state capture

**Status**: ✅ ALREADY COMPLETE (branch `002-remove-streamlit` created during /speckit.specify)

- [x] T001 Branch `002-remove-streamlit` created and checked out
- [x] T002 Feature specification complete in `/home/chris/Code/aa-abstract-renumber/specs/002-remove-streamlit/spec.md`
- [x] T003 Implementation plan complete in `/home/chris/Code/aa-abstract-renumber/specs/002-remove-streamlit/plan.md`
- [x] T004 Research document complete in `/home/chris/Code/aa-abstract-renumber/specs/002-remove-streamlit/research.md`
- [x] T005 Quickstart guide complete in `/home/chris/Code/aa-abstract-renumber/specs/002-remove-streamlit/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify current state and identify all Streamlit artifacts before removal

**⚠️ CRITICAL**: These verification tasks ensure we know exactly what to remove

**Status**: Ready to execute

- [ ] T006 [P] Verify `adapters/ui_streamlit.py` exists in `/home/chris/Code/aa-abstract-renumber/adapters/ui_streamlit.py`
- [ ] T007 [P] Verify `pages/` directory exists in `/home/chris/Code/aa-abstract-renumber/pages/`
- [ ] T008 [P] Count Streamlit imports with `grep -r "import streamlit" --include="*.py" . | grep -v ".venv" | wc -l`
- [ ] T009 [P] Verify `streamlit==1.49.0` in `/home/chris/Code/aa-abstract-renumber/requirements.txt`
- [ ] T010 [P] Verify Tkinter interface works by running `python3 -c "from adapters.ui_tkinter import AbstractRenumberGUI; print('✓ OK')"`

**Checkpoint**: All Streamlit artifacts identified - removal can begin

---

## Phase 3: User Story 1 - Simplified Codebase (Priority: P1) 🎯 MVP

**Goal**: Remove all Streamlit files and code from the repository to eliminate the non-functional interface

**Independent Test**: Verify no Streamlit imports exist in any Python file (excluding .venv) and that the Tkinter application launches without errors

**Why MVP**: This is the primary cleanup objective. Completing this story delivers immediate value by removing all non-functional Streamlit code and reducing codebase confusion.

### Implementation for User Story 1

- [ ] T011 [US1] Delete `/home/chris/Code/aa-abstract-renumber/adapters/ui_streamlit.py` file
- [ ] T012 [US1] Delete `/home/chris/Code/aa-abstract-renumber/pages/` directory recursively (entire directory with all subdirectories)
- [ ] T013 [US1] Verify adapters/ui_streamlit.py deleted with `test ! -f adapters/ui_streamlit.py`
- [ ] T014 [US1] Verify pages/ directory deleted with `test ! -d pages`
- [ ] T015 [US1] Count remaining Streamlit imports with `grep -r "import streamlit" --include="*.py" . | grep -v ".venv" | wc -l` (expect 0)
- [ ] T016 [US1] Check for Streamlit references in `/home/chris/Code/aa-abstract-renumber/adapters/__init__.py` and remove if present
- [ ] T017 [US1] Verify Tkinter imports still work with `python3 -c "from adapters.ui_tkinter import AbstractRenumberGUI; print('✓ OK')"`
- [ ] T018 [US1] Verify main.py imports still work with `python3 -c "import main; print('✓ OK')"`
- [ ] T019 [US1] Search for any remaining Streamlit files with `find . -name "*streamlit*" -type f ! -path "*/.venv/*" ! -path "*/.git/*" ! -path "*/specs/*"` (expect none)
- [ ] T020 [US1] Check for .streamlit/ configuration directory and delete if exists

**Checkpoint**: User Story 1 complete - all Streamlit files removed, Tkinter interface still works

**Success Criteria Verified**:
- ✅ No Streamlit-related imports exist in any Python files
- ✅ No Streamlit packages are listed in requirements files (verified in US2)
- ✅ No Streamlit-specific files exist in the repository
- ✅ Tkinter application continues to function without errors

---

## Phase 4: User Story 2 - Reduced Dependencies (Priority: P2)

**Goal**: Remove Streamlit from dependency files so fresh installations don't include unnecessary packages

**Independent Test**: Install application in a fresh virtual environment and verify `pip list | grep streamlit` returns nothing

**Note**: This user story builds on US1 (code removal) but is independently testable

### Implementation for User Story 2

- [ ] T021 [US2] Backup `/home/chris/Code/aa-abstract-renumber/requirements.txt` to `requirements.txt.backup`
- [ ] T022 [US2] Remove streamlit line from `/home/chris/Code/aa-abstract-renumber/requirements.txt` using `grep -v "^streamlit" requirements.txt > requirements.txt.tmp && mv requirements.txt.tmp requirements.txt`
- [ ] T023 [US2] Verify streamlit removed from requirements.txt with `! grep -i streamlit requirements.txt`
- [ ] T024 [US2] Check `/home/chris/Code/aa-abstract-renumber/setup.py` for Streamlit references (if file exists)
- [ ] T025 [US2] Check `/home/chris/Code/aa-abstract-renumber/pyproject.toml` for Streamlit references (if file exists)
- [ ] T026 [US2] Check `/home/chris/Code/aa-abstract-renumber/setup.cfg` for Streamlit references (if file exists)

### Verification for User Story 2 (Optional - can be done in Phase 6)

- [ ] T027 [P] [US2] Create fresh virtual environment and test installation (optional - time-consuming)
- [ ] T028 [P] [US2] Verify fresh install doesn't include Streamlit: `pip list | grep -i streamlit` (expect no output)

**Checkpoint**: User Story 2 verified - Streamlit removed from all dependency files

**Success Criteria Verified**:
- ✅ Streamlit is not listed in requirements.txt or any other dependency file
- ✅ Streamlit and its sub-dependencies are not installed in fresh environment
- ✅ Package count reduced by Streamlit-related packages

---

## Phase 5: User Story 3 - Cleaned Documentation (Priority: P3)

**Goal**: Update documentation to remove Streamlit references and clarify Tkinter-only interface

**Independent Test**: Search all documentation files for "streamlit" (case-insensitive) and verify results are either removed or historical notes only

**Note**: This user story is pure polish - can be done after US1 and US2 are complete

### Implementation for User Story 3

- [ ] T029 [US3] Search for Streamlit references in `/home/chris/Code/aa-abstract-renumber/README.md` with `grep -in streamlit README.md`
- [ ] T030 [US3] Update `/home/chris/Code/aa-abstract-renumber/README.md` to remove Streamlit installation instructions (if present)
- [ ] T031 [US3] Update `/home/chris/Code/aa-abstract-renumber/README.md` to note Tkinter-only interface (if Streamlit was documented)
- [ ] T032 [US3] Add historical note to README.md about Streamlit removal date (optional): "Note: Streamlit interface removed 2025-11-19"
- [ ] T033 [P] [US3] Search for Streamlit in code comments with `grep -r "streamlit" --include="*.py" . | grep -v ".venv" | grep -v "specs/" | grep "#"`
- [ ] T034 [P] [US3] Remove or update Streamlit-related code comments found in previous step
- [ ] T035 [P] [US3] Search for documentation files with `find . -name "*.md" -type f ! -path "*/.venv/*" ! -path "*/.git/*" ! -path "*/specs/*" -exec grep -l -i streamlit {} \;`
- [ ] T036 [US3] Update any additional documentation files found with Streamlit references

**Checkpoint**: User Story 3 complete - all documentation updated

**Success Criteria Verified**:
- ✅ README.md only documents the Tkinter interface
- ✅ Installation instructions omit Streamlit
- ✅ Streamlit-related comments are removed or updated

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, validation, and cleanup

- [ ] T037 [P] Run verification contract 1: File System State from `/home/chris/Code/aa-abstract-renumber/specs/002-remove-streamlit/contracts/README.md`
- [ ] T038 [P] Run verification contract 2: Dependency State from contracts/README.md
- [ ] T039 [P] Run verification contract 4: Import State from contracts/README.md
- [ ] T040 [P] Run verification contract 6: Documentation State from contracts/README.md
- [ ] T041 Run verification contract 5: Tkinter Functionality - launch application with `python3 main.py` (manual test)
- [ ] T042 [P] Delete backup file `requirements.txt.backup` if verification passes
- [ ] T043 Constitution v2.0.0 compliance review:
  - ✅ Clean Architecture: Removed adapter layer code only (core/ untouched)
  - ✅ Memory Efficiency: Reduced loaded modules
  - ✅ PEP 8 & SOLID/DRY: Removed dead code (improves DRY)
  - ✅ Local Desktop Interface: Enforces Tkinter-only principle
- [ ] T044 Run all verification contracts script (comprehensive validation)
- [ ] T045 Commit changes with descriptive message referencing all three user stories

**Optional**: Run verification contract 3 (Installation State) - creates fresh venv, time-consuming

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ✅ Complete - no dependencies
- **Foundational (Phase 2)**: Can start immediately - verification only
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion - MVP delivery
- **User Story 2 (Phase 4)**: Can start after US1 file deletion complete (independent but logical sequence)
- **User Story 3 (Phase 5)**: Can start after US1 complete (independent of US2)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies - can start after Phase 2
- **User Story 2 (P2)**: Logically follows US1 (remove code, then remove dependencies)
- **User Story 3 (P3)**: Can run in parallel with US2 or after US1

**Key Insight**: US2 and US3 can be executed in parallel after US1 completes, or sequentially in priority order.

### Within Each Phase

**Phase 2 (Foundational - Verification)**:
- T006-T010 can all run in parallel (independent verification checks)

**Phase 3 (US1 - File Deletion)**:
- T011-T012 are file deletions (sequential)
- T013-T015 are verification (can run in parallel after T011-T012)
- T016-T020 are cleanup checks (sequential, depend on T011-T012)

**Phase 4 (US2 - Dependency Removal)**:
- T021 (backup) must complete before T022
- T022 (edit requirements.txt) must complete before T023
- T023-T026 can run in parallel (different files)
- T027-T028 optional and can run in parallel if desired

**Phase 5 (US3 - Documentation)**:
- T029-T032 sequential (same file: README.md)
- T033-T036 can run in parallel with T029-T032 (different files)

**Phase 6 (Polish)**:
- T037-T040 can run in parallel (independent verification contracts)
- T041 must be manual (GUI launch)
- T042-T045 sequential (final cleanup and commit)

### Parallel Opportunities

```bash
# Phase 2: All verification checks (5 tasks in parallel)
Task: "T006 [P] Verify adapters/ui_streamlit.py exists"
Task: "T007 [P] Verify pages/ directory exists"
Task: "T008 [P] Count Streamlit imports"
Task: "T009 [P] Verify streamlit in requirements.txt"
Task: "T010 [P] Verify Tkinter interface works"

# Phase 3: Verification after deletion (3 tasks in parallel)
Task: "T013 [US1] Verify adapters/ui_streamlit.py deleted"
Task: "T014 [US1] Verify pages/ directory deleted"
Task: "T015 [US1] Count remaining Streamlit imports"

# Phase 4: Dependency file checks (4 tasks in parallel)
Task: "T023 [US2] Verify streamlit removed from requirements.txt"
Task: "T024 [US2] Check setup.py for Streamlit"
Task: "T025 [US2] Check pyproject.toml for Streamlit"
Task: "T026 [US2] Check setup.cfg for Streamlit"

# Phase 5: Documentation updates (2 parallel groups)
Group A: "T029-T032 [US3] README.md updates" (sequential within group)
Group B: "T033-T036 [US3] Code comments and other docs" (can run parallel to Group A)

# Phase 6: Final verification (4 tasks in parallel)
Task: "T037 [P] Verification contract 1: File System State"
Task: "T038 [P] Verification contract 2: Dependency State"
Task: "T039 [P] Verification contract 4: Import State"
Task: "T040 [P] Verification contract 6: Documentation State"
```

---

## Implementation Strategy

### Minimum Viable Product (MVP) - Fastest Path to Value

**Objective**: Remove all Streamlit code in ~10-15 minutes

1. ✅ **Phase 1**: Setup (already complete)
2. **Phase 2**: Foundational verification (T006-T010) - 2 minutes
3. **Phase 3**: User Story 1 core tasks (T011-T020) - 5-8 minutes
   - T011: Delete ui_streamlit.py
   - T012: Delete pages/ directory
   - T013-T020: Verification
4. **STOP and VALIDATE**: Verify Streamlit code removed and Tkinter works
5. **Optional**: Continue with US2 and US3 or commit MVP

**Result**: Streamlit code removed (US1 complete) in ~10-15 minutes

### Full Cleanup (All Three User Stories)

If you want complete cleanup including dependencies and documentation:

1. Complete MVP (Phase 1-3) - ~15 minutes
2. Add User Story 2 (Phase 4: T021-T026) - ~3 minutes
3. Add User Story 3 (Phase 5: T029-T036) - ~5-7 minutes
4. Complete polish (Phase 6: T037-T045) - ~5 minutes

**Time Estimate**: 25-30 minutes for complete cleanup

### Incremental Delivery Approach

**Commit Points**:
1. After T020: MVP complete (US1 - Streamlit code removed) - can ship this alone
2. After T026: US2 complete (dependencies removed) - can ship US1+US2
3. After T036: US3 complete (documentation cleaned) - full cleanup
4. After T045: Polish complete (all verification passed)

**Each commit delivers progressively more cleanup while maintaining working functionality**

---

## Code Changes Summary

### Files Deleted

1. **`adapters/ui_streamlit.py`**: Streamlit adapter file
2. **`pages/` directory**: Entire directory with 10+ Streamlit page files
   - `pages/multi_file_merge.py`
   - `pages/mode_selection.py`
   - `pages/base_page.py`
   - `pages/single_file_processing.py`
   - `pages/components/processing_options.py`
   - `pages/components/file_upload.py`
   - `pages/components/tabbed_workflow.py`
   - `pages/components/state_management.py`
   - `pages/components/styling.py`
   - `pages/components/downloads.py`

**Total**: 11+ files deleted

### Files Modified

1. **`requirements.txt`**: 1 line removed (`streamlit==1.49.0`)
2. **`README.md`**: Streamlit references removed/updated
3. **`adapters/__init__.py`**: Streamlit import removed (if present)
4. **Other documentation files**: Streamlit references updated (if present)

**Total**: 2-4 files modified

### Total Changes

- **Files deleted**: 11+ files
- **Directories deleted**: 2 directories (`pages/`, `pages/components/`)
- **Lines removed from dependencies**: 1 line
- **Documentation updated**: 1-3 files
- **Complexity**: Very low (deletion task, no new code)

---

## Verification Checklist

### Pre-Removal Verification (Phase 2)
- [ ] Streamlit adapter file exists
- [ ] Pages directory exists  
- [ ] Streamlit imports counted (10+ expected)
- [ ] Streamlit in requirements.txt
- [ ] Tkinter interface works before removal

### Post-Removal Verification (Phase 6)
- [ ] No Streamlit files remain
- [ ] Zero Streamlit imports (excluding .venv)
- [ ] Streamlit not in any dependency file
- [ ] Tkinter imports still work
- [ ] main.py imports still work
- [ ] Application launches successfully (manual test)
- [ ] Documentation updated appropriately

### Constitution Compliance
- [ ] Clean Architecture: Core business logic untouched
- [ ] Memory Efficiency: No negative impact
- [ ] PEP 8 & SOLID/DRY: Improved by removing dead code
- [ ] Local Desktop Interface: Enforced (Tkinter-only)

---

## Risk Mitigation

| Risk | Mitigation Task |
|------|----------------|
| Accidental deletion of needed files | T006-T010: Pre-removal verification identifies exact artifacts |
| Broken imports after deletion | T015-T018: Import verification catches issues immediately |
| Tkinter interface broken | T010, T017-T018, T041: Multiple verification points |
| Streamlit references remain | T008, T015, T039: Import count verification at multiple stages |
| Documentation outdated | T029-T036: Systematic documentation review and update |

---

## Success Metrics

- [ ] All Streamlit files removed (11+ files)
- [ ] All Streamlit imports removed (0 remaining, excluding .venv)
- [ ] Streamlit removed from requirements.txt
- [ ] Tkinter interface launches and works correctly
- [ ] Fresh install does not include Streamlit (optional verification)
- [ ] Documentation clearly states Tkinter-only interface
- [ ] All 6 verification contracts pass
- [ ] Constitution v2.0.0 compliance maintained/improved

---

## Notes

- **Simplicity**: This is intentionally a straightforward deletion task with extensive verification
- **Git Safety**: All changes on feature branch `002-remove-streamlit` (can be rolled back easily)
- **Quick Win**: MVP (US1 only) can be delivered in ~15 minutes
- **Comprehensive Verification**: 6 verification contracts ensure complete removal
- **No New Tests**: This is a removal task - existing tests verify Tkinter still works
- **No Breaking Changes**: Tkinter interface continues to work unchanged
- **Constitution Compliance**: This task actively improves compliance with Principle VI (Local Desktop Interface)

---

## Total Task Count

- **Setup/Foundational**: 10 tasks (5 complete, 5 verification)
- **User Story 1 (MVP)**: 10 tasks (file deletion and verification)
- **User Story 2**: 8 tasks (2 optional)
- **User Story 3**: 8 tasks
- **Polish**: 9 tasks

**Total**: 45 tasks (41 required, 4 optional)

**MVP Task Count**: 20 tasks (10 setup/foundational + 10 US1 implementation)

**Parallel Opportunities**: 18 tasks can run in parallel (marked with [P] or in parallel groups)

---

## Quick Reference: Task Execution Order

**For fastest MVP delivery** (US1 only):
```
Phase 2 → Phase 3 → Stop and test
(T006-T010) → (T011-T020) → Manual Tkinter test
Time: ~15 minutes
```

**For complete cleanup** (all 3 user stories):
```
Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
(T006-T010) → (T011-T020) → (T021-T028) → (T029-T036) → (T037-T045)
Time: ~25-30 minutes
```

**For parallel execution** (if multiple team members):
```
Phase 2 (everyone) → Phase 3 (Person A) → {
  Phase 4 (Person B, parallel to Phase 5)
  Phase 5 (Person C, parallel to Phase 4)
} → Phase 6 (everyone)
Time: ~20 minutes with 3 people
```

