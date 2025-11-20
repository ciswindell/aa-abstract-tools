# Tasks: Version Display System

**Input**: Design documents from `/specs/005-version-display-system/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/README.md, quickstart.md

**Tests**: Tests are included in this implementation to validate version handling and error cases.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a single project (Python GUI application) with the following structure:
- Root level: `_version.py` (new)
- Application: `app/tk_app.py` (modify)
- Build tooling: `build/build.py` (modify)
- Tests: `tests/app/test_version_display.py` (new)
- Documentation: `README.md` (update)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing project structure is ready for version system implementation

- [x] T001 Verify project structure matches plan.md expectations
- [x] T002 Verify Python 3.11 environment and tkinter availability
- [x] T003 Verify pytest is available for test execution

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the single source of truth version module that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create `_version.py` at project root with `__version__ = "1.0.0"` and module docstring
- [x] T005 Validate `_version.py` can be imported from project root: `python3 -c "from _version import __version__; print(__version__)"`

**Checkpoint**: Version module created and importable - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Version Visibility in Application (Priority: P1) 🎯 MVP

**Goal**: Display version in GUI window title and footer so users can identify their application version instantly

**Independent Test**: Launch application and verify version appears in both window title ("Abstract Renumber Tool v1.0.0") and footer ("Version 1.0.0")

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T006 [P] [US1] Create test file `tests/app/test_version_display.py` with test structure
- [x] T007 [P] [US1] Write test `test_version_import()` to verify `_version` module can be imported
- [x] T008 [P] [US1] Write test `test_version_format()` to validate semantic version format (regex: `^\d+\.\d+\.\d+$`)
- [x] T009 [P] [US1] Write test `test_version_fallback_on_missing_file()` using mock to simulate missing `_version.py`, verify fallback to "Unknown"
- [x] T010 [P] [US1] Write test `test_window_title_contains_version()` to verify window title includes version string

### Implementation for User Story 1

- [x] T011 [US1] Import version in `app/tk_app.py` `setup_window()` method with try/except fallback to "Unknown"
- [x] T012 [US1] Update window title in `app/tk_app.py` `setup_window()` to format: `f"Abstract Renumber Tool v{__version__}"`
- [x] T013 [US1] Create `_create_version_footer()` method in `app/tk_app.py` `AbstractRenumberGUI` class
- [x] T014 [US1] Implement footer label in `_create_version_footer()`: gray text, Arial 9, right-aligned, format `f"Version {__version__}"`
- [x] T015 [US1] Add footer to GUI layout: call `_create_version_footer()` in `setup_gui()` after status area (grid row 7)
- [x] T016 [US1] Run tests: `python3 -m pytest tests/app/test_version_display.py -v` - verify all pass

**Manual Verification**:
```bash
# Launch application
python3 main.py

# Verify:
# 1. Window title shows "Abstract Renumber Tool v1.0.0"
# 2. Footer at bottom-right shows "Version 1.0.0" in gray text
```

**Checkpoint**: User Story 1 complete - version is visible in GUI title and footer

---

## Phase 4: User Story 2 - Single Version Update Point (Priority: P1)

**Goal**: Ensure updating `_version.py` automatically propagates to all displays (GUI + executable naming) without manual edits

**Independent Test**: Change version in `_version.py`, rebuild, verify new version in executable filename, window title, and footer

### Tests for User Story 2

- [x] T017 [P] [US2] Write test `test_build_script_imports_version()` to verify build script can import version
- [x] T018 [P] [US2] Write test `test_executable_name_includes_version()` to verify build command uses versioned name

### Implementation for User Story 2

- [x] T019 [US2] Add project root to Python path in `build/build.py` at top of file: `sys.path.insert(0, str(Path(__file__).parent.parent))`
- [x] T020 [US2] Import version in `build/build.py` with try/except fallback to "dev" for development builds
- [x] T021 [US2] Update PyInstaller command in `build/build.py` to use versioned executable name: `exe_name = f"AbstractRenumberTool-v{__version__}"`
- [x] T022 [US2] Ensure `--name` flag uses `exe_name` variable in PyInstaller command construction
- [x] T023 [US2] Run tests: `python3 -m pytest tests/app/test_version_display.py::test_build_script_imports_version -v`

**Manual Verification**:
```bash
# Test single source of truth workflow:

# 1. Update version
echo '__version__ = "1.0.1"' > _version.py

# 2. Verify GUI picks up change
python3 main.py
# Window title should show "v1.0.1"
# Footer should show "Version 1.0.1"

# 3. Build executable
cd build
python3 build.py

# 4. Verify executable name
ls dist/ | grep "AbstractRenumberTool-v1.0.1"

# 5. Reset version
cd ..
echo '__version__ = "1.0.0"' > _version.py
```

**Checkpoint**: User Story 2 complete - single update in `_version.py` propagates to all displays

---

## Phase 5: User Story 3 - Semantic Version Understanding (Priority: P2)

**Goal**: Provide clear documentation on semantic versioning rules (MAJOR.MINOR.PATCH) for consistent version management

**Independent Test**: Review documentation and apply version increment rules to example changes, verify rules are clear and unambiguous

### Implementation for User Story 3

- [x] T024 [P] [US3] Add "Version Management" section to `README.md` documenting single source of truth (`_version.py`)
- [x] T025 [P] [US3] Document semantic versioning rules in `README.md`: MAJOR (breaking), MINOR (features), PATCH (fixes)
- [x] T026 [P] [US3] Add version update workflow to `README.md`: edit `_version.py` → commit → build → verify
- [x] T027 [P] [US3] Document where version appears (window title, footer, executable name) in `README.md`
- [x] T028 [US3] Add examples of version increments to `README.md`: bug fix (1.0.0 → 1.0.1), feature (1.0.1 → 1.1.0), breaking (1.1.0 → 2.0.0)
- [x] T029 [US3] Reference `specs/005-version-display-system/quickstart.md` for detailed version management guide in `README.md`

**Manual Verification**:
```bash
# Review documentation
cat README.md | grep -A 20 "Version Management"

# Verify covers:
# - Where _version.py is located
# - Semantic versioning rules (MAJOR.MINOR.PATCH)
# - When to increment each component
# - Update workflow steps
# - Examples of version changes
```

**Checkpoint**: User Story 3 complete - semantic versioning guidelines are documented

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge case handling, additional tests, and final validation

- [x] T030 [P] Write test `test_version_fallback_on_invalid_format()` to verify graceful handling of non-standard version strings
- [x] T031 [P] Write test `test_version_attribute_missing()` using mock to simulate `AttributeError`, verify "Unknown" fallback
- [x] T032 [P] Add inline comments in `_version.py` explaining semantic versioning format
- [x] T033 [P] Add docstring to `_create_version_footer()` method explaining purpose and styling
- [x] T034 Test error handling: Temporarily rename `_version.py` to `_version.py.bak`, launch app, verify "Unknown" displays, restore file
- [x] T035 Run full test suite: `python3 -m pytest tests/app/test_version_display.py -v` - all tests must pass
- [x] T036 Validate against quickstart.md: Follow all workflows in `specs/005-version-display-system/quickstart.md`, verify accuracy
- [x] T037 PEP 8 compliance check: Run linter on modified files (`_version.py`, `app/tk_app.py`, `build/build.py`, `tests/app/test_version_display.py`)
- [x] T038 Final manual test: Build executable, run on clean environment, verify version in all 3 locations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (Phase 3): Can start after Foundational - independently testable
  - User Story 2 (Phase 4): Can start after Foundational - builds on US1 GUI work but independently testable
  - User Story 3 (Phase 5): Can start after Foundational - pure documentation, no code dependencies
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Requires `_version.py` from Foundational phase - No other story dependencies
- **User Story 2 (P1)**: Requires `_version.py` from Foundational phase - Can leverage US1's GUI implementation but tests independently
- **User Story 3 (P2)**: Requires `_version.py` from Foundational phase - Pure documentation, no implementation dependencies

### Within Each User Story

**User Story 1**:
- Tests (T006-T010) can all run in parallel [P]
- GUI implementation tasks (T011-T015) must run sequentially (modifying same file)
- Test execution (T016) depends on all implementation tasks

**User Story 2**:
- Tests (T017-T018) can run in parallel [P]
- Build script tasks (T019-T022) must run sequentially (modifying same file)
- Test execution (T023) depends on implementation tasks

**User Story 3**:
- All documentation tasks (T024-T027) can run in parallel [P]
- Examples task (T028) and reference task (T029) run after initial docs

### Parallel Opportunities

- **Setup (Phase 1)**: All 3 tasks can run in parallel
- **User Story 1 Tests**: T006, T007, T008, T009, T010 can all run in parallel
- **User Story 2 Tests**: T017, T018 can run in parallel
- **User Story 3 Docs**: T024, T025, T026, T027 can run in parallel
- **Polish Tests**: T030, T031, T032, T033 can run in parallel
- **Across Stories**: After Foundational, all 3 user stories can be worked on in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create test file tests/app/test_version_display.py with test structure"
Task: "Write test test_version_import() to verify _version module can be imported"
Task: "Write test test_version_format() to validate semantic version format"
Task: "Write test test_version_fallback_on_missing_file() using mock"
Task: "Write test test_window_title_contains_version() to verify window title"

# These 5 tasks are all creating new test functions in the same file
# but can be written by different developers or AI agents simultaneously
# as long as there's no merge conflict (use different line ranges)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Both P1)

1. Complete Phase 1: Setup (verify environment)
2. Complete Phase 2: Foundational (create `_version.py`) - **CRITICAL**
3. Complete Phase 3: User Story 1 (GUI display)
4. Complete Phase 4: User Story 2 (build integration)
5. **STOP and VALIDATE**: Test both stories independently
6. Deploy/demo if ready (documentation can follow)

**Why this MVP**: User Stories 1 and 2 are both P1 and provide immediate value:
- Users can see version (US1)
- Developers have single update point (US2)
- Documentation (US3, P2) can be added incrementally

### Incremental Delivery

1. **Foundation**: Setup + Foundational → Version module created
2. **Increment 1**: Add User Story 1 → Test independently → **Users see version** ✓
3. **Increment 2**: Add User Story 2 → Test independently → **Build integration works** ✓
4. **Increment 3**: Add User Story 3 → Review docs → **Guidelines documented** ✓
5. **Polish**: Add comprehensive tests and validation → **Production ready** ✓

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup + Foundational (quick, ~10 minutes)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (GUI work in `app/tk_app.py`)
   - Developer B: User Story 2 (Build script work in `build/build.py`)
   - Developer C: User Story 3 (Documentation in `README.md`)
3. Stories complete and integrate independently (no conflicts)

---

## Task Summary

**Total Tasks**: 38

### Task Count by Phase:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 2 tasks
- Phase 3 (User Story 1): 11 tasks (5 tests + 6 implementation)
- Phase 4 (User Story 2): 7 tasks (2 tests + 5 implementation)
- Phase 5 (User Story 3): 6 tasks (documentation)
- Phase 6 (Polish): 9 tasks (tests + validation)

### Task Count by User Story:
- **User Story 1 (P1)**: 11 tasks - Version visibility in GUI
- **User Story 2 (P1)**: 7 tasks - Single source of truth integration
- **User Story 3 (P2)**: 6 tasks - Semantic versioning documentation
- **Infrastructure**: 14 tasks - Setup, foundational, polish

### Parallel Opportunities Identified:
- 3 tasks in Setup can run in parallel
- 5 test tasks in US1 can run in parallel
- 2 test tasks in US2 can run in parallel
- 4 documentation tasks in US3 can run in parallel
- 4 polish test tasks can run in parallel
- **Total parallelizable tasks**: 18 of 38 (47%)

### Independent Test Criteria:
- **US1**: Launch app → verify version in title and footer
- **US2**: Update `_version.py` → rebuild → verify version in executable name, title, footer
- **US3**: Review docs → apply rules to hypothetical changes → verify clarity

### Suggested MVP Scope:
**User Stories 1 & 2** (both P1) provide complete functional system:
- Version display for users (US1)
- Single update point for developers (US2)
- Combined: 18 tasks (Setup + Foundational + US1 + US2)
- Estimated time: 2-3 hours for experienced developer
- Documentation (US3) can follow as P2 priority

---

## Format Validation

✅ All tasks follow required format: `- [ ] [ID] [P?] [Story] Description with file path`
✅ All user story tasks include [US1], [US2], or [US3] labels
✅ All parallelizable tasks marked with [P]
✅ Task IDs sequential (T001-T038)
✅ File paths included in all implementation tasks
✅ Dependencies clearly documented

---

## Notes

- [P] tasks can run in parallel (different files or independent test functions)
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Tests are written first (TDD approach) to ensure they fail before implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Simple feature: Most complexity is in ensuring single source of truth pattern works correctly
- Error handling is critical: App must not crash if `_version.py` is missing

