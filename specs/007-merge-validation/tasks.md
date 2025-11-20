---

description: "Task list for implementing merge mode validation"
---

# Tasks: Prevent Single-File Processing with Merge Mode Enabled

**Input**: Design documents from `/specs/007-merge-validation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as this is a critical data safety fix requiring comprehensive validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: Repository root structure (existing codebase)
- Tests follow existing structure: `tests/app/`, `tests/adapters/`, `tests/integration/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification

- [x] T001 Verify branch `007-merge-validation` is checked out and up to date
- [x] T002 Review existing merge mode logic in app/tk_app.py and adapters/ui_tkinter.py
- [x] T003 [P] Review current Process button enable/disable logic

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core validation infrastructure that MUST be complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Add `_update_process_button_state()` method to `/home/chris/Code/aa-abstract-renumber/app/tk_app.py`
- [x] T005 Modify merge_pairs logic in `/home/chris/Code/aa-abstract-renumber/adapters/ui_tkinter.py` to return None for empty lists
- [x] T006 Add backend validation in `/home/chris/Code/aa-abstract-renumber/core/app_controller.py` process_files()

**Checkpoint**: Foundation ready - validation logic in place at all layers

---

## Phase 3: User Story 1 - Validation Error When Merge Enabled Without Pairs (Priority: P1) 🎯 MVP

**Goal**: Prevent processing when merge enabled but no pairs selected, showing clear error message

**Independent Test**: Enable merge mode, don't select pairs, click Process, verify error appears

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T007 [P] [US1] Unit test for backend validation error in `/home/chris/Code/aa-abstract-renumber/tests/app/test_merge_validation.py`
- [x] T008 [P] [US1] Integration test for error message display in `/home/chris/Code/aa-abstract-renumber/tests/app/test_merge_validation.py`
- [x] T009 [P] [US1] Regression test for valid merge operations in `/home/chris/Code/aa-abstract-renumber/tests/app/test_merge_validation.py`

### Implementation for User Story 1

- [x] T010 [US1] Implement backend validation check in AppController.process_files()
- [x] T011 [US1] Add clear error message with actionable guidance
- [x] T012 [US1] Test error message appears when attempting invalid merge
- [x] T013 [US1] Verify single-file mode still works correctly
- [x] T014 [US1] Update docstrings for modified validation methods

**Checkpoint**: Backend validation prevents invalid merge processing

---

## Phase 4: User Story 2 - Visual Feedback for Merge Pair Requirement (Priority: P2)

**Goal**: Disable Process button when merge enabled without pairs, providing proactive UX

**Independent Test**: Enable merge mode, verify Process button disabled until pairs selected

### Tests for User Story 2

- [x] T015 [P] [US2] Unit test for Process button state logic in `/home/chris/Code/aa-abstract-renumber/tests/app/test_merge_validation.py`
- [x] T016 [P] [US2] Integration test for button state changes in `/home/chris/Code/aa-abstract-renumber/tests/app/test_merge_validation.py`

### Implementation for User Story 2

- [x] T017 [US2] Implement Process button state update logic in app/tk_app.py
- [x] T018 [US2] Call update method from file selection callback
- [x] T019 [US2] Call update method from merge toggle callback
- [x] T020 [US2] Call update method from pairs selection callback
- [x] T021 [US2] Test Process button disabled when merge enabled without pairs
- [x] T022 [US2] Test Process button enabled when pairs selected
- [x] T023 [US2] Verify all merge state transitions update button correctly

**Checkpoint**: Process button state correctly reflects merge validity

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [x] T024 [P] Update README.md with merge validation feature notes (if needed)
- [x] T025 Update _version.py with version bump (PATCH increment to 1.0.2)
- [x] T026 Update CHANGELOG.md with fix details under Fixed category
- [x] T027 Run full test suite to ensure no regressions
- [x] T028 Manual testing: Try all merge state combinations
- [x] T029 Create git tag after version and changelog updates

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 must complete before US2 (UI depends on backend validation existing)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Backend validation - must complete first
- **User Story 2 (P2)**: Depends on US1 (UI prevention builds on backend safety)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Backend validation before UI prevention
- Core implementation before integration tests
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All tests within a user story marked [P] can run in parallel
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for backend validation error in test_merge_validation.py"
Task: "Integration test for error message display in test_merge_validation.py"
Task: "Regression test for valid merge operations in test_merge_validation.py"

# After tests are written and failing, implement sequentially:
Task: "Implement backend validation check in AppController.process_files()"
Task: "Add clear error message with actionable guidance"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Backend validation)
4. **STOP and VALIDATE**: Test that invalid merge attempts are blocked
5. Deploy if ready (provides data safety immediately)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test backend validation → Deploy (MVP - prevents data loss!)
3. Add User Story 2 → Test UI prevention → Enhance UX
4. Each story adds value without breaking previous functionality

### Risk Mitigation

- Foundational changes are minimal validation checks
- Each user story can be tested independently
- Regression tests ensure valid operations still work
- Clear rollback path if issues arise

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- This is a critical bug fix affecting data safety
- Focus on minimal, defensive changes
- Comprehensive testing required to prevent regressions
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
