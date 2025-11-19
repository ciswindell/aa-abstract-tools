# Tasks: Reduce Excessive Info Logging

**Input**: Design documents from `/specs/003-reduce-info-logging/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md  
**Branch**: `003-reduce-info-logging`

**Approach**: Simple deletion - remove 70+ verbose log calls, keep 10 essential messages with step counters.

**Tests**: Manual testing only (no automated tests requested in spec).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All file paths are from repository root: `/home/chris/Code/aa-abstract-renumber/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup needed - using existing project structure

_No tasks - skip to Phase 2_

---

## Phase 2: Foundational (Step Counter Infrastructure)

**Purpose**: Add step counter to pipeline context - BLOCKS all user story implementation

**⚠️ CRITICAL**: This phase must complete before any logging cleanup can begin

- [X] T001 Add `step_number: int = 0` and `total_steps: int = 0` attributes to `PipelineContext` class in `core/pipeline/context.py`
- [X] T002 Update `Pipeline.execute()` method to count non-skipped steps and inject `total_steps` into context before execution loop
- [X] T003 Update `Pipeline.execute()` method to increment `step_number` for each non-skipped step during execution

**Checkpoint**: ✅ Foundation ready - step counter infrastructure in place, user story work can begin

---

## Phase 3: User Stories 1 & 3 - Clean Logging + Progress Indicators (Priority: P1)

**Goal**: Reduce UI messages from 80+ to 8-10 per operation while showing clear progress with step counters

**Why Combined**: These stories must be implemented together because we're deleting verbose messages AND replacing them with step-counted progress messages. Cannot do one without the other.

**Independent Test**: Run full pipeline with real files, count messages in UI status area, verify 8-10 messages with "Step X of Y" format

### Implementation: Update 7 Pipeline Steps

**Pattern for each step**:
1. Find all `self.logger.info()` calls
2. Delete all except one at the start
3. Update the one you keep to use step counter with user-friendly phase name
4. Verify ERROR/WARNING/SUCCESS calls unchanged

---

- [X] T004 [P] [US1] [US3] Delete verbose logging from ValidateStep in `core/pipeline/steps/validate_step.py` - removed 12 info() calls about file validation, sheet names, PDF structure, cross-references
- [X] T005 [US1] [US3] Add single user-friendly message at start of ValidateStep.execute(): `self.logger.info(f"Step {context.step_number} of {context.total_steps}: Validating files...")`

---

- [X] T006 [P] [US1] [US3] Delete verbose logging from LoadStep in `core/pipeline/steps/load_step.py` - removed 11 info() calls about file loading, DocumentUnit creation, PDF pages/bookmarks, intermediate files
- [X] T007 [US1] [US3] Add single user-friendly message at start of LoadStep.execute(): `self.logger.info(f"Step {context.step_number} of {context.total_steps}: Loading data...")`

---

- [X] T008 [P] [US1] [US3] Delete verbose logging from FilterDfStep in `core/pipeline/steps/filter_df_step.py` - removed 7 info() calls about filtering logic
- [X] T009 [US1] [US3] Add single user-friendly message at start of FilterDfStep.execute(): `self.logger.info(f"Step {context.step_number} of {context.total_steps}: Filtering data...")`

---

- [X] T010 [P] [US1] [US3] Delete verbose logging from SortDfStep in `core/pipeline/steps/sort_df_step.py` - removed 9 info() calls about sorting operations, row counts
- [X] T011 [US1] [US3] Add single user-friendly message at start of SortDfStep.execute(): `self.logger.info(f"Step {context.step_number} of {context.total_steps}: Sorting data...")`

---

- [X] T012 [P] [US1] [US3] Delete verbose logging from RebuildPdfStep in `core/pipeline/steps/rebuild_pdf_step.py` - removed 10 info() calls about Phase A/B/C, filtering, reordering, PDF reconstruction
- [X] T013 [US1] [US3] Add single user-friendly message at start of RebuildPdfStep.execute(): `self.logger.info(f"Step {context.step_number} of {context.total_steps}: Rebuilding PDF...")`

---

- [X] T014 [P] [US1] [US3] Delete verbose logging from SaveStep in `core/pipeline/steps/save_step.py` - removed 11 info() calls about backups, row counts, Excel/PDF saving details
- [X] T015 [US1] [US3] Add single user-friendly message at start of SaveStep.execute(): `self.logger.info(f"Step {context.step_number} of {context.total_steps}: Saving outputs...")`

---

- [X] T016 [P] [US1] [US3] Delete verbose logging from FormatExcelStep in `core/pipeline/steps/format_excel_step.py` - removed 2 info() calls about formatting operations
- [X] T017 [US1] [US3] Add single user-friendly message at start of FormatExcelStep.execute(): `self.logger.info(f"Step {context.step_number} of {context.total_steps}: Formatting Excel...")`

---

### Implementation: Update App Controller

- [X] T018 [US3] Removed unnecessary "Starting processing...", "Files selected...", and "Processing documents..." messages from AppController
- [X] T019 [US3] Changed "Processing complete!" to "Done!" SUCCESS message in `core/app_controller.py`

### Cleanup: Pipeline Executor and Additional Verbose Messages

- [X] Remove "Starting pipeline with X steps" message from Pipeline executor
- [X] Remove "Executing step X/Y: StepName" messages from Pipeline executor
- [X] Remove "Completed step StepName" messages from Pipeline executor  
- [X] Remove "Skipping step X/Y: StepName (conditions not met)" message from Pipeline executor
- [X] Remove "Pipeline completed successfully (X steps executed)" message from Pipeline executor
- [X] Remove 7 additional verbose messages from FormatExcelStep helper methods ("Found date column...", "Applied date formatting...", "Applied auto-filter...", "Saved formatted Excel file...")

**Checkpoint**: All verbose logging deleted (83+ messages removed), step-counted progress messages added (7 clean messages). User Stories 1 and 3 complete.

---

## Phase 4: User Story 2 - Verify Critical Messages Preserved (Priority: P1)

**Goal**: Confirm ERROR/WARNING/SUCCESS messages unchanged during cleanup

**Independent Test**: Trigger error conditions, warnings, and success scenarios. Verify all critical messages still appear with original formatting and clarity.

- [ ] T020 [US2] Manually verify ERROR messages unchanged - search codebase for `logger.error()` calls, confirm none were accidentally deleted during cleanup
- [ ] T021 [US2] Manually verify WARNING messages unchanged - search codebase for `logger.warning()` calls, confirm none were accidentally deleted
- [ ] T022 [US2] Manually verify SUCCESS messages unchanged - search codebase for `logger.success()` calls, confirm none were accidentally deleted

**Checkpoint**: All critical messages verified preserved. User Story 2 complete.

---

## Phase 5: Manual Testing & Validation

**Purpose**: End-to-end validation of all three user stories

- [ ] T023 Run application with real files (Excel + PDF pair)
- [ ] T024 Count messages in UI status area - verify 8-10 total messages (not 80+)
- [ ] T025 Verify all messages show "Step X of Y" format for phase transitions
- [ ] T026 Verify "Starting processing..." appears at operation start
- [ ] T027 Verify "Processing complete: X documents, Y pages" appears at operation end
- [ ] T028 Verify no verbose technical details visible (no "Phase A/B/C", no class names, no item counts)
- [ ] T029 Verify ERROR/WARNING/SUCCESS messages still appear correctly if triggered
- [ ] T030 Verify message timestamps and auto-scroll still work correctly

**Success Criteria** (from spec.md):
- ✅ 5-10 messages per operation (SC-001)
- ✅ Messages show "Step X of Y" format (US3)
- ✅ User-friendly phase names, no class names (US1)
- ✅ ERROR/WARNING/SUCCESS preserved (SC-003, US2)
- ✅ No verbose technical details (US1)
- ✅ Net code reduction: ~60-70 lines deleted

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: SKIPPED - using existing project
- **Foundational (Phase 2)**: No dependencies - can start immediately - BLOCKS all user stories
- **User Stories 1 & 3 (Phase 3)**: Depends on Foundational (Phase 2) completion
  - Within Phase 3: All [P] tasks (T004, T006, T008, T010, T012, T014, T016) can run in parallel
  - Each pipeline step has 2 sequential tasks: delete verbose logging, then add new message
- **User Story 2 (Phase 4)**: Depends on Phase 3 completion (verification after cleanup)
- **Testing (Phase 5)**: Depends on all implementation phases (2, 3, 4) completion

### User Story Dependencies

- **User Story 1 (Clean Feedback)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (Show Progress)**: Depends on Foundational (Phase 2) - Implemented WITH US1 (cannot separate)
- **User Story 2 (Preserve Critical)**: Depends on US1/US3 completion - This is verification only

### Within Each Phase

**Phase 2 (Foundational)**:
- T001 → T002 → T003 (sequential - building step counter infrastructure)

**Phase 3 (Implementation)**:
- Parallel groups: All [P] tasks for different pipeline steps can run simultaneously
  - T004, T006, T008, T010, T012, T014, T016 (delete verbose logging - different files)
- Within each pipeline step: Delete first, then add new message
  - T004 → T005 (ValidateStep)
  - T006 → T007 (LoadStep)
  - T008 → T009 (FilterDfStep)
  - T010 → T011 (SortDfStep)
  - T012 → T013 (RebuildPdfStep)
  - T014 → T015 (SaveStep)
  - T016 → T017 (FormatExcelStep)
- App controller: T018 → T019 (can run in parallel with pipeline step updates)

**Phase 4 (Verification)**:
- T020, T021, T022 can run in parallel (different searches)

**Phase 5 (Testing)**:
- T023 → T024 → T025 → T026 → T027 → T028 → T029 → T030 (sequential manual test steps)

### Parallel Opportunities

```bash
# Phase 2: Sequential only (3 tasks building infrastructure)

# Phase 3: Launch all "delete" tasks together (7 pipeline steps):
Task T004: Delete verbose logging from ValidateStep
Task T006: Delete verbose logging from LoadStep  
Task T008: Delete verbose logging from FilterDfStep
Task T010: Delete verbose logging from SortDfStep
Task T012: Delete verbose logging from RebuildPdfStep
Task T014: Delete verbose logging from SaveStep
Task T016: Delete verbose logging from FormatExcelStep
# Plus T018 in parallel: Update app controller

# Then add new messages (sequential per step, but steps independent)

# Phase 4: Launch all verification tasks together:
Task T020: Verify ERROR messages unchanged
Task T021: Verify WARNING messages unchanged
Task T022: Verify SUCCESS messages unchanged
```

---

## Parallel Example: Phase 3 Pipeline Steps

**Parallel batch 1** (delete verbose logging from all 7 steps):
```bash
Task T004: "Delete verbose logging from ValidateStep in core/pipeline/steps/validate_step.py"
Task T006: "Delete verbose logging from LoadStep in core/pipeline/steps/load_step.py"
Task T008: "Delete verbose logging from FilterDfStep in core/pipeline/steps/filter_df_step.py"
Task T010: "Delete verbose logging from SortDfStep in core/pipeline/steps/sort_df_step.py"
Task T012: "Delete verbose logging from RebuildPdfStep in core/pipeline/steps/rebuild_pdf_step.py"
Task T014: "Delete verbose logging from SaveStep in core/pipeline/steps/save_step.py"
Task T016: "Delete verbose logging from FormatExcelStep in core/pipeline/steps/format_excel_step.py"
```

**Sequential batch** (add new messages to each step):
```bash
Task T005: ValidateStep
Task T007: LoadStep
Task T009: FilterDfStep
Task T011: SortDfStep
Task T013: RebuildPdfStep
Task T015: SaveStep
Task T017: FormatExcelStep
```

---

## Implementation Strategy

### Simple Sequential Approach (Recommended for Solo Developer)

1. **Phase 2**: Add step counter infrastructure (T001 → T002 → T003)
2. **Phase 3**: Update pipeline steps one at a time
   - ValidateStep: T004 → T005
   - LoadStep: T006 → T007
   - FilterDfStep: T008 → T009
   - SortDfStep: T010 → T011
   - RebuildPdfStep: T012 → T013
   - SaveStep: T014 → T015
   - FormatExcelStep: T016 → T017
   - AppController: T018 → T019
3. **Phase 4**: Verify critical messages (T020 → T021 → T022)
4. **Phase 5**: Manual testing (T023 → T030)

**Estimated Time**: ~1 hour total
- Phase 2: 10 min
- Phase 3: 35 min (7 steps × 5 min each)
- Phase 4: 5 min
- Phase 5: 10 min

### MVP Approach (Minimal Viable Change)

Could implement just ValidateStep, LoadStep, and SaveStep first to prove the concept:
1. Phase 2: Add step counter
2. Implement T004-T005, T006-T007, T014-T015 only
3. Test with 3 messages instead of 12+ for those steps
4. Verify concept works before completing remaining steps

---

## Notes

### Message Volume Reduction

**Before**: 80-85 messages per operation
- ValidateStep: 12 messages
- LoadStep: 11 messages
- FilterDfStep: 5 messages
- SortDfStep: 8 messages
- RebuildPdfStep: 20 messages
- SaveStep: 15 messages
- FormatExcelStep: 10 messages

**After**: 8-10 messages per operation
- "Starting processing...": 1
- 7 phase transitions: "Step X of Y: ...": 6-7 (some may skip)
- "Processing complete: ...": 1
- ERROR/WARNING/SUCCESS: As needed

**Reduction**: 85-90% fewer messages

### Code Reduction

- **Lines deleted**: ~70-80 lines (verbose log calls)
- **Lines added**: ~10 lines (step counter + new messages)
- **Net reduction**: ~60-70 lines of code ✓

### What Gets Deleted

Verbose messages like:
- "Executing step 1/7: ValidateStep"
- "Phase A: Filtering DocumentUnits..."
- "Created 67 DocumentUnits from..."
- "Loaded PDF with 126 pages, 67 bookmarks"
- "Applied date formatting to 4 columns, 4000 cells"

### What Gets Kept/Added

User-friendly messages like:
- "Starting processing..."
- "Step 1 of 7: Validating files..."
- "Step 3 of 7: Sorting data..."
- "Processing complete: 67 documents, 126 pages"

### User-Friendly Phase Names

| Step Class | Phase Name |
|------------|-----------|
| ValidateStep | "Validating files..." |
| LoadStep | "Loading data..." |
| FilterDfStep | "Filtering data..." |
| SortDfStep | "Sorting data..." |
| RebuildPdfStep | "Rebuilding PDF..." |
| SaveStep | "Saving outputs..." |
| FormatExcelStep | "Formatting Excel..." |

### Critical Messages (Unchanged)

- ERROR messages: Red bold, user-friendly
- WARNING messages: Orange
- SUCCESS messages: Green bold

### Testing Approach

Manual testing only (no automated tests per spec):
1. Run with real files
2. Count messages (target: 8-10)
3. Verify step counter format
4. Verify no verbose details
5. Verify critical messages preserved

---

## Summary

**Total Tasks**: 30 tasks across 5 phases

**Task Breakdown**:
- Phase 1 (Setup): 0 tasks (skip - existing project)
- Phase 2 (Foundational): 3 tasks (step counter infrastructure)
- Phase 3 (US1 + US3): 16 tasks (cleanup 7 pipeline steps + app controller)
- Phase 4 (US2): 3 tasks (verify critical messages)
- Phase 5 (Testing): 8 tasks (manual validation)

**Parallel Opportunities**: 
- Phase 3: Up to 7 tasks in parallel (delete from different pipeline steps)
- Phase 4: 3 tasks in parallel (verification)

**User Stories**:
- US1 (Clean Feedback) + US3 (Show Progress): Tasks T004-T019 (Phase 3)
- US2 (Preserve Critical): Tasks T020-T022 (Phase 4)

**Implementation Time**: ~1 hour (solo developer, sequential)

**Expected Outcome**: 
- 85-90% message reduction (80+ → 8-10)
- 60-70 lines of code deleted (net)
- Clear progress indicators with "Step X of Y" format
- All critical messages preserved
- Simpler, cleaner codebase

