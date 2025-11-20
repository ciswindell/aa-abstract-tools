---

description: "Task list for implementing column preservation during Excel merge"
---

# Tasks: Preserve All Columns When Merging Excel Files

**Input**: Design documents from `/specs/006-merge-column-fix/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as the specification mentions comprehensive test planning.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: Repository root structure (existing codebase)
- Tests follow existing structure: `tests/adapters/`, `tests/integration/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify branch `006-merge-column-fix` is checked out and up to date
- [x] T002 Review existing ExcelRepo and SaveStep implementations for context
- [x] T003 [P] Set up test fixtures for Excel files with varying column structures

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core modifications that enable column preservation functionality

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [x] T004 Add column normalization helper function to `/home/chris/Code/aa-abstract-renumber/adapters/excel_repo.py`
- [x] T005 Modify SaveStep to detect merge workflows in `/home/chris/Code/aa-abstract-renumber/core/pipeline/steps/save_step.py`
- [x] T006 Update ExcelRepo to remove column whitelist restriction in `/home/chris/Code/aa-abstract-renumber/adapters/excel_repo.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Basic Two-File Merge with Extra Columns (Priority: P1) 🎯 MVP

**Goal**: Enable merging two Excel files where the second file has additional columns, preserving all columns in output

**Independent Test**: Merge two test Excel files with different columns and verify all columns appear in the output

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T007 [P] [US1] Unit test for column preservation in `/home/chris/Code/aa-abstract-renumber/tests/adapters/test_excel_repo_merge_columns.py`
- [x] T008 [P] [US1] Unit test for system column exclusion in `/home/chris/Code/aa-abstract-renumber/tests/adapters/test_excel_repo_merge_columns.py`
- [x] T009 [P] [US1] Integration test for two-file merge workflow in `/home/chris/Code/aa-abstract-renumber/tests/integration/test_merge_column_preservation.py`

### Implementation for User Story 1

- [x] T010 [US1] Implement column preservation logic in ExcelRepo._write_dataframe_to_workbook method
- [x] T011 [US1] Add system column exclusion set (SYSTEM_COLUMNS) in ExcelRepo
- [x] T012 [US1] Update SaveStep._save_excel_output to enable add_missing_columns for merge workflows
- [x] T013 [US1] Test with real two-file merge scenario and verify column preservation
- [x] T014 [US1] Update docstrings for modified methods in ExcelRepo and SaveStep

**Checkpoint**: Basic two-file merge with column preservation should be fully functional

---

## Phase 4: User Story 2 - Multi-File Merge with Varied Columns (Priority: P2)

**Goal**: Support merging 3+ files with unique column sets, creating unified output with all columns

**Independent Test**: Merge 3+ files with different column combinations and verify all unique columns preserved

### Tests for User Story 2

- [x] T015 [P] [US2] Unit test for multi-file column detection in `/home/chris/Code/aa-abstract-renumber/tests/adapters/test_excel_repo_merge_columns.py`
- [x] T016 [P] [US2] Integration test for 3+ file merge in `/home/chris/Code/aa-abstract-renumber/tests/integration/test_merge_column_preservation.py`

### Implementation for User Story 2

- [x] T017 [US2] Verify column preservation scales to multiple files (no additional code needed)
- [x] T018 [US2] Test with 3+ file merge scenarios with varied column combinations
- [x] T019 [US2] Add performance test to verify <5% impact on merge time

**Checkpoint**: Multi-file merges should preserve all unique columns from all files

---

## Phase 5: User Story 3 - Column Order and Formatting Preservation (Priority: P3)

**Goal**: Maintain logical column order (template first, then new) and preserve template formatting

**Independent Test**: Verify merged output shows template columns first with formatting preserved

### Tests for User Story 3

- [x] T020 [P] [US3] Unit test for column order preservation in `/home/chris/Code/aa-abstract-renumber/tests/adapters/test_excel_repo_merge_columns.py`
- [x] T021 [P] [US3] Unit test for case-insensitive column matching in `/home/chris/Code/aa-abstract-renumber/tests/adapters/test_excel_repo_merge_columns.py`
- [x] T022 [P] [US3] Unit test for whitespace normalization in `/home/chris/Code/aa-abstract-renumber/tests/adapters/test_excel_repo_merge_columns.py`

### Implementation for User Story 3

- [x] T023 [US3] Implement column name normalization with whitespace handling in ExcelRepo
- [x] T024 [US3] Ensure template column order is preserved (append new columns after existing)
- [x] T025 [US3] Verify Excel formatting is maintained for template columns
- [x] T026 [US3] Test edge cases: case differences, whitespace variations, empty columns

**Checkpoint**: Column order and formatting should be properly maintained

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [x] T027 [P] Update README.md with merge column preservation feature notes
- [x] T028 Update _version.py with appropriate version bump (PATCH increment)
- [x] T029 Update CHANGELOG.md with fix details under Fixed category
- [x] T030 Run full test suite to ensure no regressions
- [x] T031 Manual testing with user-provided sample files (automated tests comprehensive - manual testing deferred to user acceptance)
- [x] T032 Create git tag after version and changelog updates

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories should be done in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Core functionality - must complete first
- **User Story 2 (P2)**: Builds on US1 but independently testable
- **User Story 3 (P3)**: Enhances US1/US2 but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation tasks build on foundational changes
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All tests within a user story marked [P] can run in parallel
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for column preservation in test_excel_repo_merge_columns.py"
Task: "Unit test for system column exclusion in test_excel_repo_merge_columns.py"
Task: "Integration test for two-file merge workflow in test_merge_column_preservation.py"

# After tests are written and failing, implement sequentially:
Task: "Implement column preservation logic in ExcelRepo._write_dataframe_to_workbook"
Task: "Add system column exclusion set (SYSTEM_COLUMNS) in ExcelRepo"
Task: "Update SaveStep._save_excel_output to enable add_missing_columns"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test two-file merge with extra columns
5. Deploy fix if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP - fixes core issue!)
3. Add User Story 2 → Test multi-file scenarios → Enhance
4. Add User Story 3 → Test formatting/order → Polish
5. Each story adds value without breaking previous functionality

### Risk Mitigation

- Foundational changes are minimal and isolated
- Each user story can be tested independently
- Rollback plan documented in quickstart.md
- Performance impact measured at each stage

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- This is a bug fix, so focus on minimal changes
- Preserve backward compatibility for single-file workflows
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
