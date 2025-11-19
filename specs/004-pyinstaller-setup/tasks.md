# Tasks: PyInstaller Windows Executable Setup

**Input**: Design documents from `/specs/004-pyinstaller-setup/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No test tasks included (not requested in specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Repository root: `/home/chris/Code/aa-abstract-renumber/`
- Build directory: `build/`
- Documentation directory: `docs/`
- Requirements file: `requirements.txt`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure for build tooling

- [x] T001 Create build/ directory in repository root
- [x] T002 Create docs/ directory in repository root (if not exists)
- [x] T003 [P] Add pyinstaller>=6.0.0,<7.0.0 to requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core build infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create PyInstaller spec file template in build/AbstractRenumberTool.spec with basic structure (Analysis, PYZ, EXE sections)
- [x] T005 Configure hidden imports in build/AbstractRenumberTool.spec for tkinter, pandas, openpyxl, pypdf, natsort, dateutil
- [x] T006 Configure module excludes in build/AbstractRenumberTool.spec for pandas.tests, matplotlib, IPython, jupyter, pytest
- [x] T007 Set windowed mode (console=False) and default app name in build/AbstractRenumberTool.spec

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Build Windows Executable (Priority: P1) 🎯 MVP

**Goal**: Enable developers to package the Abstract Renumber Tool as a standalone Windows executable with a simple build command

**Independent Test**: Run build script and verify that AbstractRenumberTool.exe is created in dist/ directory without errors

### Implementation for User Story 1

- [x] T008 [P] [US1] Create build script scaffolding in build/build.py with argument parsing (--mode, --optimize, --clean, --verbose, --spec, --help)
- [x] T009 [P] [US1] Implement prerequisite validation function in build/build.py (check Python version, PyInstaller installed, spec file exists, main.py exists, disk space)
- [x] T010 [US1] Implement BuildOrchestrator class in build/build.py with __init__, validate_prerequisites, build, get_build_info methods
- [x] T011 [US1] Implement BuildResult dataclass in build/build.py with success, executable_path, file_size_bytes, build_time_seconds, error_message, warnings fields
- [x] T012 [US1] Implement build execution logic in build/build.py (run PyInstaller subprocess, capture output, handle errors)
- [x] T013 [US1] Implement clean_build_directories function in build/build.py to remove dist/ and build/build/ if --clean flag set
- [x] T014 [US1] Implement post-build validation in build/build.py (check executable exists, verify file size reasonable, validate PE format)
- [x] T015 [US1] Implement build summary output in build/build.py (display executable path, size, build time, next steps)
- [x] T016 [US1] Add error message formatting in build/build.py following contract format ([ERROR] Category: Description, Details, Solution, Example)
- [x] T017 [US1] Add main() function and if __name__ == "__main__" block in build/build.py to wire CLI arguments to BuildOrchestrator

**Checkpoint**: At this point, User Story 1 should be fully functional - developer can run `python3 build/build.py` and get AbstractRenumberTool.exe

---

## Phase 4: User Story 2 - Test on Clean Windows Machine (Priority: P1)

**Goal**: Provide comprehensive testing documentation so QA can verify the executable works without Python on clean Windows machines

**Independent Test**: Follow testing checklist on a Windows machine without Python and verify all 9 test cases pass

### Implementation for User Story 2

- [x] T018 [P] [US2] Create testing checklist document in docs/testing-executable.md with test environment requirements section
- [x] T019 [P] [US2] Document smoke test (executable launches) in docs/testing-executable.md with expected behavior
- [x] T020 [P] [US2] Document GUI test (main window appears with all controls) in docs/testing-executable.md
- [x] T021 [P] [US2] Document file selection test (can browse and select Excel/PDF files) in docs/testing-executable.md
- [x] T022 [P] [US2] Document processing test (successfully processes valid input files) in docs/testing-executable.md
- [x] T023 [P] [US2] Document filter test (data filtering feature works correctly) in docs/testing-executable.md
- [x] T024 [P] [US2] Document merge test (multi-file merge feature works correctly) in docs/testing-executable.md
- [x] T025 [P] [US2] Document output test (processed files created with correct content) in docs/testing-executable.md
- [x] T026 [P] [US2] Document error handling test (invalid inputs show appropriate errors) in docs/testing-executable.md
- [x] T027 [P] [US2] Document shutdown test (application closes cleanly) in docs/testing-executable.md
- [x] T028 [US2] Add pass criteria section in docs/testing-executable.md (all 9 tests pass, no crashes, correct output, performance targets)
- [x] T029 [US2] Add VM/clean machine setup instructions in docs/testing-executable.md (VirtualBox, Hyper-V, or physical machine without Python)
- [x] T030 [US2] Add issue reporting template in docs/testing-executable.md (what to document when tests fail)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - developers can build and testers can validate on clean Windows

---

## Phase 5: User Story 3 - Configure Build Options (Priority: P2)

**Goal**: Document configuration options so developers can customize the executable (icon, console mode, included packages) without modifying build script

**Independent Test**: Modify spec file settings (e.g., add icon, change console mode), rebuild, and verify changes reflected in executable

### Implementation for User Story 3

- [ ] T031 [P] [US3] Create comprehensive build guide in docs/building-executable.md with prerequisites section (Python 3.7+, PyInstaller 6.x, optional UPX)
- [ ] T032 [P] [US3] Document basic build steps in docs/building-executable.md (install PyInstaller, run build script, find output)
- [ ] T033 [P] [US3] Document build script command-line options in docs/building-executable.md (--mode, --optimize, --clean, --verbose, --spec) with examples
- [ ] T034 [P] [US3] Document spec file structure and configuration section in docs/building-executable.md (APP_NAME, ENTRY_POINT, ICON_PATH, CONSOLE, UPX_ENABLED, HIDDEN_IMPORTS, EXCLUDES)
- [ ] T035 [P] [US3] Document how to add custom icon in docs/building-executable.md (create/obtain .ico file, set ICON_PATH in spec)
- [ ] T036 [P] [US3] Document console mode toggle in docs/building-executable.md (CONSOLE=True for debugging, False for release)
- [ ] T037 [P] [US3] Document how to add hidden imports in docs/building-executable.md (when needed, where to add, examples)
- [ ] T038 [P] [US3] Document how to include additional data files in docs/building-executable.md (datas parameter in Analysis section)
- [ ] T039 [P] [US3] Document onefile vs onedir modes in docs/building-executable.md (differences, use cases, how to choose)
- [ ] T040 [US3] Add configuration examples section in docs/building-executable.md (common customization scenarios with before/after spec file snippets)
- [ ] T041 [US3] Create build/ README.md with quick reference for spec file modification rules and safe vs risky changes

**Checkpoint**: All P1 and P2 user stories should now be independently functional - developers can build, configure, and testers can validate

---

## Phase 6: User Story 4 - Optimize Executable Size (Priority: P3)

**Goal**: Document optimization techniques so developers can reduce executable size and improve startup performance

**Independent Test**: Apply optimization techniques (exclude modules, use UPX, use onedir), measure file size, and verify at least 20% reduction

### Implementation for User Story 4

- [ ] T042 [P] [US4] Create troubleshooting guide in docs/troubleshooting.md with sections for build errors, runtime errors, performance issues, antivirus issues
- [ ] T043 [P] [US4] Document common build errors in docs/troubleshooting.md (PyInstaller not found, import errors, DLL issues) with solutions
- [ ] T044 [P] [US4] Document runtime errors in docs/troubleshooting.md (missing modules, DLL not found, GUI rendering problems) with solutions
- [ ] T045 [P] [US4] Document antivirus false positives in docs/troubleshooting.md (why they happen, whitelisting, code signing instructions)
- [ ] T046 [P] [US4] Document size optimization techniques in docs/troubleshooting.md (excluding unused modules, UPX compression, onedir mode)
- [ ] T047 [P] [US4] Add module exclusion recommendations in docs/troubleshooting.md (safe modules to exclude for size reduction: matplotlib, IPython, jupyter, notebook, pytest, setuptools)
- [ ] T048 [P] [US4] Document UPX compression setup and usage in docs/troubleshooting.md (installation, enabling in spec file, size/startup tradeoff)
- [ ] T049 [P] [US4] Document optimization levels (basic, medium, aggressive) in docs/troubleshooting.md with expected size reductions and risks
- [ ] T050 [US4] Add performance troubleshooting section in docs/troubleshooting.md (slow startup, large size, execution speed)
- [ ] T051 [US4] Add minimum Windows version compatibility documentation in docs/troubleshooting.md (Windows 10 1809+, VC++ redistributables)

**Checkpoint**: All user stories should now be independently functional - complete build tooling with full documentation

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final quality checks

- [ ] T052 [P] Update repository root README.md with PyInstaller build instructions (link to docs/building-executable.md)
- [ ] T053 [P] Add code signing instructions in docs/troubleshooting.md (obtaining certificate, signing process, Windows SmartScreen)
- [ ] T054 [P] Add distribution checklist in docs/building-executable.md (pre-distribution validation steps)
- [ ] T055 [P] Add performance expectations table in docs/building-executable.md (build time, size, startup time targets vs typical)
- [ ] T056 Verify all file paths in documentation are correct and relative to repository root
- [ ] T057 Run build script on Windows to validate it produces working executable
- [ ] T058 Validate quickstart.md commands work as documented (TL;DR section)
- [ ] T059 [P] Add .gitignore entries for dist/, build/build/, and *.spec.bak files
- [ ] T060 Final documentation review for typos, broken links, and completeness

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Build Executable**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1) - Testing Documentation**: Can start after Foundational (Phase 2) - Independent but references US1 build output
- **User Story 3 (P2) - Configure Options**: Can start after Foundational (Phase 2) - References US1 build process
- **User Story 4 (P3) - Optimize Size**: Can start after Foundational (Phase 2) - References US1 build and US3 configuration

### Within Each User Story

- Documentation tasks marked [P] can run in parallel (different files)
- Build script implementation follows logical order (scaffolding → validation → execution → output)
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 Setup**: All 3 tasks can run in parallel
- **Phase 2 Foundational**: Tasks T004-T007 can run in parallel (all modify same spec file, but different sections)
- **Phase 3 US1**: T008-T009 can run in parallel (different concerns in build.py)
- **Phase 4 US2**: T018-T027 can run in parallel (different test cases in same doc)
- **Phase 5 US3**: T031-T039 can run in parallel (different documentation sections)
- **Phase 6 US4**: T042-T049 can run in parallel (different troubleshooting sections)
- **Phase 7 Polish**: T052-T055, T059 can run in parallel (different files)
- **Different User Stories**: Once Phase 2 completes, different developers can work on US1, US2, US3, US4 simultaneously

---

## Parallel Example: User Story 1

```bash
# Launch parallel tasks for US1 build script (different concerns):
Task T008: "Create build script scaffolding in build/build.py with argument parsing"
Task T009: "Implement prerequisite validation function in build/build.py"

# Then sequential implementation (dependencies):
Task T010: "Implement BuildOrchestrator class" (uses T008, T009)
Task T011: "Implement BuildResult dataclass" (independent)
Task T012: "Implement build execution logic" (uses T010)
# ... and so on
```

## Parallel Example: User Story 2

```bash
# Launch all documentation tasks in parallel (different test cases):
Task T018: "Create testing checklist document"
Task T019: "Document smoke test"
Task T020: "Document GUI test"
Task T021: "Document file selection test"
Task T022: "Document processing test"
Task T023: "Document filter test"
Task T024: "Document merge test"
Task T025: "Document output test"
Task T026: "Document error handling test"
Task T027: "Document shutdown test"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only - Both P1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Build Executable)
4. Complete Phase 4: User Story 2 (Testing Documentation)
5. **STOP and VALIDATE**: Test build process on Windows and validate with testing checklist
6. Deploy/demo if ready - **This is a working MVP!**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 (both P1) → Test independently → **MVP Release** (basic build works)
3. Add User Story 3 (P2) → Test independently → **Enhanced Release** (customization supported)
4. Add User Story 4 (P3) → Test independently → **Optimized Release** (size/performance tuning)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Build Script)
   - Developer B: User Story 2 (Testing Docs)
   - Developer C: User Story 3 (Configuration Docs)
   - Developer D: User Story 4 (Optimization Docs)
3. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 60

**Tasks by User Story**:
- Setup: 3 tasks
- Foundational: 4 tasks
- User Story 1 (Build Executable): 10 tasks
- User Story 2 (Testing Documentation): 13 tasks
- User Story 3 (Configure Options): 11 tasks
- User Story 4 (Optimize Size): 10 tasks
- Polish: 9 tasks

**Parallel Opportunities**: 41 tasks marked [P] can run in parallel (68% parallelizable)

**Independent Test Criteria**:
- ✅ US1: Run build script and get working executable
- ✅ US2: Follow testing checklist on clean Windows
- ✅ US3: Modify spec file and verify changes in executable
- ✅ US4: Apply optimizations and measure size reduction

**Suggested MVP Scope**: Phase 1 + 2 + 3 + 4 (Setup + Foundation + US1 + US2) = 30 tasks
- This delivers a working build system with validation checklist
- Estimated effort: 2-3 days for one developer, 1 day for parallel team

---

## Format Validation

✅ All 60 tasks follow the checklist format:
- ✅ All start with `- [ ]` (checkbox)
- ✅ All have sequential Task IDs (T001-T060)
- ✅ 41 tasks marked [P] for parallel execution
- ✅ 44 tasks marked with story labels ([US1], [US2], [US3], [US4])
- ✅ All include file paths or clear descriptions
- ✅ Setup and Foundational phases have no story labels (correct)
- ✅ User Story phases all have story labels (correct)
- ✅ Polish phase has no story labels (correct)

---

## Notes

- [P] tasks = different files or independent concerns, no sequential dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No test tasks included (not requested in specification - this is tooling/documentation work)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- This is infrastructure work - no changes to core application code
- All new files are in build/ and docs/ directories

