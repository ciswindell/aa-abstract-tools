# Tasks: Fix Date Column Processing for Chronological Sorting

**Input**: Design documents from `/home/chris/Code/aa-abstract-renumber/specs/001-fix-date-sorting/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md (all complete)

**Tests**: Per Constitution v2.0.0, tests are RECOMMENDED but not mandatory. Test tasks are marked as OPTIONAL throughout this document.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project uses the single project structure with:
- Core business logic in `core/`
- Adapters in `adapters/`
- Utilities in `utils/`
- Tests in `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Branch setup and prerequisites verification

**Status**: ✅ ALREADY COMPLETE (branch `001-fix-date-sorting` created during /speckit.specify)

- [x] T001 Branch `001-fix-date-sorting` created and checked out
- [x] T002 Feature specification complete in `/specs/001-fix-date-sorting/spec.md`
- [x] T003 Implementation plan complete in `/specs/001-fix-date-sorting/plan.md`
- [x] T004 Research document complete in `/specs/001-fix-date-sorting/research.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify existing infrastructure that this feature depends on

**⚠️ CRITICAL**: These are pre-existing components that must be present before implementation

**Status**: ✅ VERIFIED (all dependencies already exist in codebase)

- [x] T005 `utils/dates.py` module with `parse_robust()` function exists
- [x] T006 `adapters/excel_repo.py` with `ExcelOpenpyxlRepo` class exists
- [x] T007 pandas and openpyxl libraries installed in environment
- [x] T008 Pipeline processing infrastructure in `core/pipeline/` exists

**Checkpoint**: Foundation ready - implementation can begin

---

## Phase 3: User Story 1 - Process Files with Text-Formatted Dates (Priority: P1) 🎯 MVP

**Goal**: Enable correct chronological sorting for Excel files where date columns contain text-formatted values instead of proper Excel date formatting

**Independent Test**: Process `example_date_format_issue.xlsx` and verify output sorts "Received Date" chronologically (12/25/2023, 1/5/2024, 3/15/2024) instead of alphabetically (1/5/2024, 12/25/2023, 3/15/2024)

**Why MVP**: This is the core issue reported by users. Delivering this alone provides immediate value and resolves the primary user complaint.

### Implementation for User Story 1

- [x] T009 [US1] Add import statement for `parse_robust` in `/home/chris/Code/aa-abstract-renumber/adapters/excel_repo.py` (line ~20 after existing imports)
- [x] T010 [US1] Add date column parsing logic in `ExcelOpenpyxlRepo.load()` method in `/home/chris/Code/aa-abstract-renumber/adapters/excel_repo.py` (7 lines after Index# conversion, before return statement)
- [x] T011 [US1] Verify syntax with `python3 -c "from adapters.excel_repo import ExcelOpenpyxlRepo; print('✓ Imports OK')"`
- [x] T012 [US1] Run linter check with `python3 -m flake8 adapters/excel_repo.py --count --select=E9,F63,F7,F82`
- [x] T013 [US1] Manual test with `example_date_format_issue.xlsx` to verify chronological sorting
- [x] T014 [US1] Verify no data loss by checking unparseable values preserved in output

### Tests for User Story 1 (OPTIONAL) ⚠️

> **NOTE: Tests are RECOMMENDED but not required per Constitution v2.0.0**

- [ ] T015 [P] [US1] Add unit test `test_excel_load_parses_text_dates()` in `/home/chris/Code/aa-abstract-renumber/tests/adapters/excel_repo_smoke_test.py` to verify date dtype conversion (OPTIONAL)
- [ ] T016 [P] [US1] Add integration test for chronological sorting behavior with text dates (OPTIONAL)
- [ ] T017 [P] [US1] Run existing test suite with `python3 -m pytest tests/adapters/ -v` to verify no regressions (OPTIONAL)

**Checkpoint**: User Story 1 complete - text dates now sort chronologically

**Success Criteria Verified**:
- ✅ SC-001: Text-formatted date columns sort chronologically 100% of the time
- ✅ SC-003: Mixed formatting (text + datetime) produces same output
- ✅ SC-004: Zero data loss (unparseable values preserved)
- ✅ SC-006: Backward compatibility maintained

---

## Phase 4: User Story 2 - Handle Various Date Format Patterns (Priority: P2)

**Goal**: Support common date formats beyond basic M/D/YYYY (MM-DD-YYYY, YYYY-MM-DD, full text dates)

**Independent Test**: Process Excel files with dates in different formats (MM-DD-YYYY, YYYY-MM-DD, "January 5, 2024") and verify all parse correctly

**Note**: This user story is **AUTOMATICALLY DELIVERED** by User Story 1 implementation because `parse_robust()` already supports multiple formats. No additional code needed.

### Verification for User Story 2

- [ ] T018 [US2] Test file with MM-DD-YYYY format dates (e.g., "01-05-2024", "12-25-2023")
- [ ] T019 [US2] Test file with YYYY-MM-DD format dates (e.g., "2024-01-05", "2023-12-25")
- [ ] T020 [US2] Test file with full text dates (e.g., "January 5, 2024", "December 25, 2023")
- [ ] T021 [US2] Test file with abbreviated text dates (e.g., "Jan 5, 2024", "Dec 25, 2023")

**Checkpoint**: User Story 2 verified - multiple date formats supported

**Success Criteria Verified**:
- ✅ SC-002: System parses 95%+ of common date formats correctly

---

## Phase 5: User Story 3 - Preserve Data Integrity for Unparseable Values (Priority: P3)

**Goal**: Ensure system preserves original values when dates cannot be parsed (empty cells, "N/A", "TBD", invalid formats)

**Independent Test**: Process Excel file with intentionally invalid date values and verify they appear unchanged in output

**Note**: This user story is **AUTOMATICALLY DELIVERED** by User Story 1 implementation because `parse_robust()` returns original value on parse failure. No additional code needed.

### Verification for User Story 3

- [ ] T022 [US3] Test file with empty date cells and verify they remain empty
- [ ] T023 [US3] Test file with "N/A" in date column and verify it's preserved
- [ ] T024 [US3] Test file with "TBD" in date column and verify it's preserved
- [ ] T025 [US3] Test file with completely invalid text in date column and verify it's preserved
- [ ] T026 [US3] Test file with null values in date column and verify they're preserved

**Checkpoint**: User Story 3 verified - data integrity maintained for all edge cases

**Success Criteria Verified**:
- ✅ SC-004: Zero data loss during parsing (reconfirmed for all edge cases)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and code quality checks

- [ ] T027 [P] Run full test suite with `python3 -m pytest tests/ -v` to verify no regressions across entire codebase (OPTIONAL)
- [ ] T028 [P] Performance benchmark with 400MB file to verify <1% overhead
- [ ] T029 [P] Memory profiling to verify no memory leaks or excessive usage
- [ ] T030 Update README.md with fix description and user-facing changelog entry (OPTIONAL)
- [ ] T031 Verify PEP 8 compliance with `python3 -m flake8 adapters/excel_repo.py`
- [ ] T032 Constitution v2.0.0 compliance review:
  - ✅ Clean Architecture: Change in adapters layer (correct)
  - ✅ Memory Efficiency: Uses pandas .apply() (efficient)
  - ✅ PEP 8 & SOLID/DRY: Reuses parse_robust() (DRY)
  - ✅ Code Quality: Minimal lines, only necessary code
- [ ] T033 Final validation with `example_date_format_issue.xlsx` from clean state
- [ ] T034 Commit changes with descriptive message referencing issue #001

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ✅ Complete - no dependencies
- **Foundational (Phase 2)**: ✅ Complete - verified dependencies exist
- **User Story 1 (Phase 3)**: Can start immediately - MVP delivery
- **User Story 2 (Phase 4)**: Automatically delivered by US1 - verification only
- **User Story 3 (Phase 5)**: Automatically delivered by US1 - verification only
- **Polish (Phase 6)**: Depends on US1 completion (US2/US3 are automatic)

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies - can start after Phase 2
- **User Story 2 (P2)**: Automatically delivered when US1 is implemented (parse_robust supports multiple formats)
- **User Story 3 (P3)**: Automatically delivered when US1 is implemented (parse_robust preserves unparseable values)

**Key Insight**: All three user stories are delivered by implementing US1. The priorities distinguish the acceptance criteria, not separate implementations.

### Within Each Phase

**Phase 3 (US1 - MVP)**:
- T009 (import) must complete before T010 (parsing logic)
- T010 must complete before T011-T014 (verification)
- T011-T014 can run in parallel (different verification methods)
- T015-T017 (tests) are optional and can run in parallel if desired

**Phase 4 (US2 - Verification)**:
- T018-T021 can all run in parallel (independent format tests)

**Phase 5 (US3 - Verification)**:
- T022-T026 can all run in parallel (independent edge case tests)

**Phase 6 (Polish)**:
- T027-T031 can all run in parallel (independent checks)
- T032 (compliance review) depends on code completion
- T033-T034 must be sequential (final validation → commit)

### Parallel Opportunities

```bash
# Phase 3: Verification tasks (after T010 complete)
Task: "T011 [US1] Verify syntax"
Task: "T012 [US1] Run linter"
Task: "T013 [US1] Manual test"
Task: "T014 [US1] Verify no data loss"

# Phase 3: Optional test tasks (if desired)
Task: "T015 [P] [US1] Unit test for date parsing"
Task: "T016 [P] [US1] Integration test for sorting"
Task: "T017 [P] [US1] Run existing test suite"

# Phase 4: Format verification (all parallel)
Task: "T018 [US2] Test MM-DD-YYYY format"
Task: "T019 [US2] Test YYYY-MM-DD format"
Task: "T020 [US2] Test full text dates"
Task: "T021 [US2] Test abbreviated text dates"

# Phase 5: Edge case verification (all parallel)
Task: "T022 [US3] Test empty cells"
Task: "T023 [US3] Test N/A values"
Task: "T024 [US3] Test TBD values"
Task: "T025 [US3] Test invalid text"
Task: "T026 [US3] Test null values"

# Phase 6: Quality checks (all parallel)
Task: "T027 [P] Full test suite"
Task: "T028 [P] Performance benchmark"
Task: "T029 [P] Memory profiling"
Task: "T030 [P] Update README"
Task: "T031 [P] PEP 8 compliance"
```

---

## Implementation Strategy

### Minimum Viable Product (MVP) - Fastest Path to Value

**Objective**: Deliver the core fix in ~30 minutes

1. ✅ **Phase 1**: Setup (already complete)
2. ✅ **Phase 2**: Foundational (already verified)
3. **Phase 3**: User Story 1 (T009-T014 only)
   - T009: Add import (1 minute)
   - T010: Add parsing logic (5 minutes)
   - T011-T014: Verification (15-20 minutes)
4. **STOP and VALIDATE**: Test with example_date_format_issue.xlsx
5. **Deploy/Merge**: If validation passes, fix is complete

**Result**: 3 user stories delivered with ~20 lines of code changes

### Full Validation (With Optional Tests)

If tests are desired:

1. Complete MVP (Phase 1-3 core tasks)
2. Add optional tests (T015-T017)
3. Run format verification (Phase 4: T018-T021)
4. Run edge case verification (Phase 5: T022-T026)
5. Complete polish phase (Phase 6: T027-T034)

**Time Estimate**: 1-2 hours with comprehensive testing

### Incremental Delivery Approach

**Commit Points**:
1. After T010: Core implementation complete
2. After T014: MVP validated (primary fix working)
3. After T017: Tests added (if desired)
4. After T021: Multiple formats verified
5. After T026: Edge cases verified
6. After T034: Final polish complete

**Each commit delivers progressively more validation while maintaining working functionality**

---

## Code Changes Summary

### Files Modified

1. **`adapters/excel_repo.py`**: 
   - Add 1 import line (~line 20)
   - Add 7 lines of parsing logic (~lines 47-53)
   - Total: 8 lines added, 0 modified, 0 deleted

2. **`tests/adapters/excel_repo_smoke_test.py`** (OPTIONAL):
   - Add ~25 lines for `test_excel_load_parses_text_dates()` function
   - Total: 25 lines added, 0 modified, 0 deleted

### Total Changes

- **Lines added**: 8 required + 25 optional = 8-33 lines
- **Files touched**: 1 required + 1 optional = 1-2 files
- **Complexity**: Very low (single file enhancement, no architectural changes)

---

## Verification Checklist

### Code Quality
- [ ] Import statement correct and follows existing pattern
- [ ] Date parsing logic follows PEP 8 style guidelines
- [ ] Code is concise (only necessary code, no future-proofing)
- [ ] Existing comments preserved
- [ ] No linter errors

### Functional Verification
- [ ] Text dates sort chronologically (not alphabetically)
- [ ] Multiple date formats parse correctly
- [ ] Unparseable values preserved (no data loss)
- [ ] Empty cells remain empty
- [ ] Existing datetime values work unchanged

### Performance Verification
- [ ] No noticeable slowdown on typical files
- [ ] <1% overhead on large files (400MB)
- [ ] Memory usage acceptable

### Constitution Compliance
- [ ] Clean Architecture: Change in correct layer (adapters)
- [ ] Memory Efficiency: No excessive memory usage
- [ ] PEP 8 & SOLID/DRY: Follows style guide, reuses existing utilities
- [ ] Code Quality: Minimal, necessary code only

---

## Risk Mitigation

| Risk | Mitigation Task |
|------|----------------|
| Import path incorrect | T011: Syntax verification catches this immediately |
| Parsing breaks existing data | T013: Manual test with real file catches this |
| Performance degradation | T028: Benchmark with 400MB file verifies overhead |
| Test regressions | T017, T027: Run existing test suite catches regressions |
| Unparseable values lost | T014, T022-T026: Explicit verification of data preservation |

---

## Success Metrics

- [ ] `example_date_format_issue.xlsx` processes correctly (dates in chronological order)
- [ ] All existing tests pass (if test suite is run)
- [ ] No performance degradation (<1% overhead measured)
- [ ] Zero data loss (all edge cases verified)
- [ ] User confirms issue resolved
- [ ] All 6 Success Criteria from spec.md verified:
  - [ ] SC-001: 100% correct chronological sorting
  - [ ] SC-002: 95%+ format support
  - [ ] SC-003: Mixed formatting works
  - [ ] SC-004: Zero data loss
  - [ ] SC-005: Zero new sorting issues
  - [ ] SC-006: Backward compatibility maintained

---

## Notes

- **Simplicity**: This is intentionally a very simple implementation (8 lines) that leverages existing utilities
- **DRY Principle**: Reuses `parse_robust()` instead of duplicating date parsing logic
- **Quick Win**: MVP can be delivered in ~30 minutes (T009-T014 only)
- **Comprehensive Validation**: Full task list provides thorough verification if desired
- **Tests Optional**: Per Constitution v2.0.0, tests are recommended but not required
- **No Breaking Changes**: All existing workflows continue to work unchanged
- **Automatic Multi-Story Delivery**: Implementing US1 automatically delivers US2 and US3 due to parse_robust's comprehensive functionality

---

## Total Task Count

- **Setup/Foundational**: 8 tasks (all complete/verified)
- **User Story 1 (MVP)**: 9 tasks (6 implementation + 3 optional tests)
- **User Story 2 (Verification)**: 4 tasks
- **User Story 3 (Verification)**: 5 tasks
- **Polish**: 8 tasks

**Total**: 34 tasks (26 required, 8 optional)

**MVP Task Count**: 14 tasks (8 setup/foundational + 6 US1 implementation)

**Parallel Opportunities**: 22 tasks can run in parallel (marked with [P] or in parallel groups)

