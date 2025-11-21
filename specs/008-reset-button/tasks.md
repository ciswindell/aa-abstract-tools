# Tasks: Reset Button

**Input**: Design documents from `/specs/008-reset-button/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Included per specification requirements (8 test cases defined)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project uses single-project structure:
- **Application code**: `app/`, `adapters/`, `core/`
- **Tests**: `tests/` (mirrors source structure)
- **Version info**: `_version.py` (project root)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment verification and branch confirmation

- [x] T001 Verify Python 3.7+ installed and accessible via python3 command
- [x] T002 Verify pytest installed in current environment
- [x] T003 Confirm feature branch 008-reset-button is checked out
- [x] T004 Run existing app tests to establish baseline: python3 -m pytest tests/app/ -v

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**Status**: ✅ No foundational work needed - leveraging existing GUI infrastructure

**Rationale**: Feature extends existing `AbstractRenumberGUI` class and reuses existing `reset_gui()` method. All required infrastructure already exists.

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Quick State Reset After Processing (Priority: P1) 🎯 MVP

**Goal**: Provide one-click reset functionality that clears file selections, filter/merge configurations, and returns app to ready state after successful processing

**Independent Test**: Select files, configure options, click Reset button, verify all transient state cleared and app shows "No file selected"

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T005 [P] [US1] Create test file tests/app/test_reset_button.py with fixture for GUI instance
- [x] T006 [P] [US1] Test: Reset button exists and has correct text in tests/app/test_reset_button.py
- [x] T007 [P] [US1] Test: Reset clears file selections (excel_file, pdf_file) in tests/app/test_reset_button.py
- [x] T008 [P] [US1] Test: Reset clears filter state (enabled, column, values) in tests/app/test_reset_button.py
- [x] T009 [P] [US1] Test: Reset clears merge state (enabled, pairs) in tests/app/test_reset_button.py
- [x] T010 [P] [US1] Test: Reset disables Process button in tests/app/test_reset_button.py

### Implementation for User Story 1

- [x] T011 [US1] Add reset_button instance variable declaration to AbstractRenumberGUI.__init__ in app/tk_app.py (around line 56)
- [x] T012 [US1] Create button frame in setup_gui() to hold Process and Reset buttons horizontally in app/tk_app.py (replace line 115-121)
- [x] T013 [US1] Add Reset button widget creation with command=self._on_reset_clicked in app/tk_app.py
- [x] T014 [US1] Update Process button to use button frame layout in app/tk_app.py
- [x] T015 [US1] Implement _on_reset_clicked() event handler method in AbstractRenumberGUI class in app/tk_app.py (after line 541)
- [x] T016 [US1] Verify all US1 tests pass: python3 -m pytest tests/app/test_reset_button.py::test_reset_button_exists -v
- [x] T017 [US1] Verify all US1 tests pass: python3 -m pytest tests/app/test_reset_button.py -k "clears" -v

**Checkpoint**: At this point, User Story 1 should be fully functional - users can reset app state with one click

---

## Phase 4: User Story 2 - Recovery from Invalid State (Priority: P2)

**Goal**: Enable users to recover from configuration mistakes or invalid states without restarting application, including edge cases like resetting empty state

**Independent Test**: Configure wrong files and invalid options, click Reset, verify clean slate for new selections; also verify reset with no files selected is safe no-op

### Tests for User Story 2

- [x] T018 [P] [US2] Test: Reset with empty state is safe no-op in tests/app/test_reset_button.py
- [x] T019 [P] [US2] Test: Reset button always enabled (never disabled state) in tests/app/test_reset_button.py
- [x] T020 [P] [US2] Test: Reset preserves user preferences (backup, sort bookmarks) in tests/app/test_reset_button.py

### Implementation for User Story 2

- [x] T021 [US2] Add defensive None/empty checks in _on_reset_clicked() if needed in app/tk_app.py
- [x] T022 [US2] Verify reset_button state is always "normal" (never disabled) in app/tk_app.py
- [x] T023 [US2] Add inline comment documenting future enhancement for processing-state check in app/tk_app.py
- [x] T024 [US2] Verify all US2 tests pass: python3 -m pytest tests/app/test_reset_button.py -k "US2" -v

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - reset handles all edge cases safely

---

## Phase 5: User Story 3 - Visual Feedback on Reset (Priority: P3)

**Goal**: Provide clear visual confirmation that reset was successful through status messages and UI state changes

**Independent Test**: Click Reset and observe status area displays "GUI reset - ready for new files!" message with proper styling

### Tests for User Story 3

- [x] T025 [US3] Verify existing reset_gui() logs confirmation message (code inspection - already implemented)
- [x] T026 [US3] Verify existing reset_gui() updates file labels to "No file selected" (code inspection - already implemented)

### Implementation for User Story 3

**Status**: ✅ Already implemented in existing `reset_gui()` method (lines 622-675 in app/tk_app.py)

- [x] T027 [US3] Code review: Verify reset_gui() logs "GUI reset - ready for new files!" message
- [x] T028 [US3] Code review: Verify reset_gui() updates excel_label and pdf_label text to "No file selected"
- [x] T029 [US3] Code review: Verify reset_gui() clears status area except last 3 lines

**Checkpoint**: All user stories should now be independently functional with proper visual feedback

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, version management, and documentation

- [x] T030 [P] Run full test suite to ensure no regressions: python3 -m pytest tests/ -v
- [x] T031 [P] Manual verification following quickstart.md test scenarios (6 scenarios)
- [x] T032 [P] Check PEP 8 compliance: flake8 app/tk_app.py
- [x] T033 Read current version from _version.py and increment MINOR (new feature)
- [x] T034 Update _version.py with new version (e.g., 1.0.0 → 1.1.0)
- [x] T035 Update CHANGELOG.md: Add "Reset button for clearing app state" under [Unreleased] → Added section
- [ ] T036 Run application manually and verify Reset button appears and functions: python3 main.py
- [ ] T037 Commit changes: git commit -m "feat: add reset button for clearing app state"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: N/A - no foundational work needed
- **User Stories (Phase 3-5)**: Can start immediately after Setup
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup - No dependencies on other stories
- **User Story 2 (P2)**: Can start after US1 tests/implementation - Minimal dependency (tests same component)
- **User Story 3 (P3)**: Can start after US1 implementation - Already implemented in existing code

**Note**: All three user stories share the same implementation (Reset button + handler). They represent different use cases/scenarios rather than separate features. Tasks are organized to show incremental value delivery.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- UI components before event handlers
- Core implementation before edge case handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T001-T004) can run in sequence rapidly (verification only)
- All tests for User Story 1 (T006-T010) can run in parallel after test file created (T005)
- All tests for User Story 2 (T018-T020) can run in parallel
- Manual verification tasks in Polish phase can run in parallel
- PEP 8 check (T032) can run in parallel with manual verification (T031)

---

## Parallel Example: User Story 1 Tests

```bash
# After creating test file (T005), launch all US1 tests together:
Task T006: "Test: Reset button exists and has correct text"
Task T007: "Test: Reset clears file selections"
Task T008: "Test: Reset clears filter state"
Task T009: "Test: Reset clears merge state"
Task T010: "Test: Reset disables Process button"

# These can all be written simultaneously since they test different aspects
```

---

## Parallel Example: User Story 2 Tests

```bash
# Launch all US2 tests together:
Task T018: "Test: Reset with empty state is safe no-op"
Task T019: "Test: Reset button always enabled"
Task T020: "Test: Reset preserves user preferences"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify environment)
2. Skip Phase 2: Foundational (not needed)
3. Complete Phase 3: User Story 1 (T005-T017)
   - Write 6 tests that fail
   - Implement button and handler
   - Verify all tests pass
4. **STOP and VALIDATE**: Test US1 independently via manual testing
5. Deploy/demo if ready (users can reset state after processing)

### Incremental Delivery

1. Complete Setup → Environment verified
2. Add User Story 1 → Test independently → **MVP Deliverable** (core reset functionality)
3. Add User Story 2 → Test independently → **Enhanced** (edge case safety)
4. Add User Story 3 → Verify existing → **Complete** (visual feedback confirmed)
5. Polish → Version bump → **Release Ready**

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Developer A completes Setup (Phase 1)
2. Once Setup done:
   - Developer A: User Story 1 (Phase 3)
   - Developer B: User Story 2 tests (can prepare in parallel)
3. After US1 complete:
   - Developer A: User Story 3 verification
   - Developer B: User Story 2 implementation
4. Both: Polish phase together

---

## Task Summary

**Total Tasks**: 37 tasks across 6 phases

**Breakdown by Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 0 tasks (not needed)
- Phase 3 (US1 - MVP): 13 tasks (6 tests + 7 implementation)
- Phase 4 (US2): 6 tasks (3 tests + 3 implementation)
- Phase 5 (US3): 5 tasks (verification only - already implemented)
- Phase 6 (Polish): 9 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Select files → Reset → Files cleared, app ready
- US2: Reset with empty state → No errors, safe operation
- US3: Reset → Status message displayed with confirmation

**MVP Scope**: Phase 1 + Phase 3 (User Story 1) = 17 tasks for minimum viable feature

**Estimated Effort**: 2-3 hours total (per plan.md assessment)
- US1 (MVP): 1.5 hours
- US2: 30 minutes
- US3: 15 minutes (verification only)
- Polish: 45 minutes

---

## Notes

- [P] tasks = different test cases or verification steps with no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story delivers independently testable increment of value
- Tests written first (TDD approach) to ensure clear acceptance criteria
- Existing `reset_gui()` method provides 90% of functionality - only need UI button
- US3 is already implemented - tasks are verification/code review only
- Commit after each user story completion for atomic changes
- Stop at any checkpoint to validate story independently before proceeding

