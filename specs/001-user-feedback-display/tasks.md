# Tasks: User Feedback Display

**Input**: Design documents from `/specs/001-user-feedback-display/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a single project at repository root with structure:
- `app/` - Application UI components
- `adapters/` - UI and I/O adapters
- `tests/` - Test files

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing project structure and confirm no additional setup needed

- [x] T001 Review existing GUI status area implementation in /home/chris/Code/aa-abstract-renumber/app/tk_app.py
- [x] T002 Confirm existing log_status() method signature in AbstractRenumberGUI class

**Checkpoint**: ✅ Existing structure verified - ready for foundational enhancements

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core message type system that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add message type constants (MSG_INFO, MSG_ERROR, MSG_SUCCESS, MSG_WARNING) in /home/chris/Code/aa-abstract-renumber/app/tk_app.py
- [x] T004 Configure tkinter Text widget tags for message types in AbstractRenumberGUI.setup_gui() method in /home/chris/Code/aa-abstract-renumber/app/tk_app.py
- [x] T005 Add msg_type optional parameter to AbstractRenumberGUI.log_status() method with default MSG_INFO in /home/chris/Code/aa-abstract-renumber/app/tk_app.py

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - See Processing Progress (Priority: P1) 🎯 MVP

**Goal**: Display real-time status messages with appropriate visual styling so users can see what the application is doing

**Independent Test**: Run any document processing operation and verify that status messages appear in different colors (black for info, green for success) showing each major step

### Implementation for User Story 1

- [x] T006 [P] [US1] Update AbstractRenumberGUI.log_status() to insert messages with specified tag in /home/chris/Code/aa-abstract-renumber/app/tk_app.py
- [x] T007 [P] [US1] Verify auto-scroll functionality with text.see(tk.END) works correctly in /home/chris/Code/aa-abstract-renumber/app/tk_app.py
- [x] T008 [P] [US1] Update TkinterUIAdapter.log_status() to accept optional msg_type parameter in /home/chris/Code/aa-abstract-renumber/adapters/ui_tkinter.py
- [x] T009 [US1] Test status message display by adding test messages to existing process_files workflow in /home/chris/Code/aa-abstract-renumber/core/app_controller.py
- [x] T010 [US1] Verify timestamp format remains HH:MM:SS in displayed messages in /home/chris/Code/aa-abstract-renumber/app/tk_app.py

**Checkpoint**: ✅ User Story 1 complete - users can see colored, timestamped status messages during processing

---

## Phase 4: User Story 2 - Understand Errors (Priority: P1)

**Goal**: Display clear, actionable error messages in plain language without technical jargon

**Independent Test**: Trigger various error conditions (missing files, invalid data) and verify each shows a user-friendly error message in red bold text

### Tests for User Story 2

- [x] T011 [P] [US2] Create test file tests/adapters/test_feedback_display.py with test structure
- [x] T012 [P] [US2] Write unit test for FileNotFoundError simplification in tests/adapters/test_feedback_display.py
- [x] T013 [P] [US2] Write unit test for PermissionError simplification in tests/adapters/test_feedback_display.py
- [x] T014 [P] [US2] Write unit test for generic error fallback in tests/adapters/test_feedback_display.py

### Implementation for User Story 2

- [x] T015 [US2] Implement simplify_error() helper function in /home/chris/Code/aa-abstract-renumber/adapters/ui_tkinter.py
- [x] T016 [US2] Update TkinterUIAdapter.show_error() to use simplify_error() and log with MSG_ERROR in /home/chris/Code/aa-abstract-renumber/adapters/ui_tkinter.py
- [x] T017 [US2] Add error message logging to log_status() calls in show_error() method in /home/chris/Code/aa-abstract-renumber/adapters/ui_tkinter.py
- [x] T018 [US2] Update existing error handling in pipeline steps to use plain language messages in /home/chris/Code/aa-abstract-renumber/core/pipeline/steps/
- [x] T019 [US2] Run pytest on tests/adapters/test_feedback_display.py to verify all error simplification tests pass

**Checkpoint**: ✅ User Story 2 complete - users see clear, actionable error messages in plain language

---

## Phase 5: User Story 3 - Clear Feedback History (Priority: P2)

**Goal**: Visually separate messages from different operations so users can distinguish current operation from previous ones

**Independent Test**: Process multiple document batches in sequence and verify that operations are visually separated by a gray line separator

### Implementation for User Story 3

- [x] T020 [US3] Add start_new_operation() method to AbstractRenumberGUI class in /home/chris/Code/aa-abstract-renumber/app/tk_app.py
- [x] T021 [US3] Implement separator line insertion with gray styling in start_new_operation() in /home/chris/Code/aa-abstract-renumber/app/tk_app.py
- [x] T022 [US3] Add message history limit check (MAX_MESSAGES=500, TRIM_AMOUNT=100) to log_status() in /home/chris/Code/aa-abstract-renumber/app/tk_app.py
- [x] T023 [US3] Call start_new_operation() at beginning of process_files() in AppController in /home/chris/Code/aa-abstract-renumber/core/app_controller.py
- [x] T024 [US3] Test visual separator display with multiple consecutive operations

**Checkpoint**: ✅ User Story 3 complete - operations are clearly separated with visual boundaries

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, manual testing, and improvements that affect multiple user stories

- [x] T025 [P] Add docstrings to new/modified methods in /home/chris/Code/aa-abstract-renumber/app/tk_app.py
- [x] T026 [P] Add docstrings to simplify_error() and updated methods in /home/chris/Code/aa-abstract-renumber/adapters/ui_tkinter.py
- [x] T027 [P] Add inline comments explaining message type system in /home/chris/Code/aa-abstract-renumber/app/tk_app.py
- [x] T028 Manual verification: Contract 1 - Messages appear within 1 second per /home/chris/Code/aa-abstract-renumber/specs/001-user-feedback-display/contracts/README.md
- [x] T029 Manual verification: Contract 2 - Message types have distinct visual styling per /home/chris/Code/aa-abstract-renumber/specs/001-user-feedback-display/contracts/README.md
- [x] T030 Manual verification: Contract 3 - Latest message always visible per /home/chris/Code/aa-abstract-renumber/specs/001-user-feedback-display/contracts/README.md
- [x] T031 Manual verification: Contract 4 - Operations visually separated per /home/chris/Code/aa-abstract-renumber/specs/001-user-feedback-display/contracts/README.md
- [x] T032 Manual verification: Contract 5 - Long operations continue feedback per /home/chris/Code/aa-abstract-renumber/specs/001-user-feedback-display/contracts/README.md
- [x] T033 Manual verification: Contract 6 - Auto-scroll works correctly per /home/chris/Code/aa-abstract-renumber/specs/001-user-feedback-display/contracts/README.md
- [x] T034 Review quickstart.md and verify all examples match implementation in /home/chris/Code/aa-abstract-renumber/specs/001-user-feedback-display/quickstart.md
- [x] T035 [P] Optional: Update TkLogger class to use message types in /home/chris/Code/aa-abstract-renumber/adapters/logger_tk.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1) and User Story 2 (P1) can proceed in parallel after Phase 2
  - User Story 3 (P2) can start after Phase 2, no dependency on US1/US2
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (parallel with US1)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- **US1**: Tasks T006-T010 can mostly run in parallel (T006, T007, T008 are [P]), then T009-T010 sequentially
- **US2**: Tests T011-T014 run in parallel first, then T015-T019 sequentially
- **US3**: Tasks T020-T024 run sequentially (shared file modifications)

### Parallel Opportunities

- **Phase 2**: Tasks T003, T004, T005 must run sequentially (same file, same method)
- **Phase 3 (US1)**: T006, T007, T008 can run in parallel (different methods/files)
- **Phase 4 (US2)**: T011-T014 (tests) can all run in parallel
- **Phase 5 (US3)**: Tasks modify same methods, must run sequentially
- **Phase 6**: T025, T026, T027 (documentation) can run in parallel; T028-T033 (manual tests) can run in parallel
- **Cross-Story**: US1 and US2 can be worked on in parallel by different developers after Phase 2 completes

---

## Parallel Example: Foundational + User Stories

```bash
# Sequential in Phase 2 (same file/method):
T003 → T004 → T005 (must complete before any user story)

# Parallel after Phase 2 completes:
# Developer A works on User Story 1:
T006: "Update log_status() to insert with tags"
T007: "Verify auto-scroll functionality"
T008: "Update TkinterUIAdapter.log_status()"

# Developer B works on User Story 2 (parallel with A):
T011: "Create test file"
T012: "Test FileNotFoundError simplification"
T013: "Test PermissionError simplification"
T014: "Test generic error fallback"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Both P1)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T005) - CRITICAL
3. Complete Phase 3: User Story 1 (T006-T010)
4. Complete Phase 4: User Story 2 (T011-T019)
5. **STOP and VALIDATE**: Test both P1 stories independently
6. Ready for user testing and feedback

### Incremental Delivery

1. Complete Setup + Foundational → Message type system ready
2. Add User Story 1 → Test independently → Users can see colored progress messages (MVP!)
3. Add User Story 2 → Test independently → Users get clear error messages
4. Add User Story 3 → Test independently → Operations visually separated
5. Polish phase → Documentation and final verification

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T005)
2. Once Foundational is done:
   - Developer A: User Story 1 (T006-T010)
   - Developer B: User Story 2 (T011-T019)
3. Developer A or B: User Story 3 (T020-T024)
4. Both: Polish phase (T025-T035) in parallel

---

## Task Summary

**Total Tasks**: 35 tasks

**By Phase**:
- Phase 1 (Setup): 2 tasks
- Phase 2 (Foundational): 3 tasks
- Phase 3 (US1 - P1): 5 tasks
- Phase 4 (US2 - P1): 9 tasks (4 tests + 5 implementation)
- Phase 5 (US3 - P2): 5 tasks
- Phase 6 (Polish): 11 tasks (3 docs + 6 manual tests + 2 verification)

**By User Story**:
- User Story 1 (See Processing Progress): 5 tasks
- User Story 2 (Understand Errors): 9 tasks
- User Story 3 (Clear Feedback History): 5 tasks
- Foundational/Shared: 16 tasks

**Parallel Opportunities**: 14 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**:
- US1: Run processing operation, verify colored messages appear
- US2: Trigger errors, verify plain language messages in red
- US3: Process multiple batches, verify visual separators

**Suggested MVP Scope**: Phases 1-4 (Setup + Foundational + US1 + US2)

---

## Notes

- [P] tasks = different files/methods, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests in US2 follow TDD approach (write first, verify fail, then implement)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Manual verification tasks (T028-T033) correspond to contracts in contracts/README.md
- Optional enhancement (T035) can be skipped if time constrained

