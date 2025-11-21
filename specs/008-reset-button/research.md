# Research: Reset Button

**Feature**: Reset Button  
**Date**: 2025-11-20  
**Purpose**: Document technical decisions, patterns, and alternatives for implementing GUI reset functionality

## Research Questions

### Q1: How should the Reset button be positioned relative to the Process button?

**Decision**: Place Reset button horizontally to the right of Process button using tkinter grid layout with shared row

**Rationale**:
- Follows common UI pattern of action buttons in horizontal alignment
- Existing code uses grid layout at row 5 for Process button
- Can use same row with column offset (column=2) for visual grouping
- Maintains visual hierarchy: Process (primary) on left, Reset (secondary) on right

**Alternatives considered**:
- Vertical stacking below Process: Rejected—wastes vertical space in already tall window
- Separate "File" menu: Rejected—adds unnecessary complexity for single action
- Keyboard shortcut only: Rejected—discoverability issue for non-technical users

**Implementation approach**: Modify `_create_backup_options()` section to place buttons in same row with appropriate padding

---

### Q2: Should Reset button have any disabled/enabled state logic?

**Decision**: Keep Reset button always enabled, but add defensive check to prevent reset during active processing

**Rationale**:
- Spec requirement FR-008 states button must be enabled at all times
- Edge case identified: User should not reset mid-processing
- Solution: Add `self.processing = False` flag tracked by controller
- Reset handler checks flag and logs warning if processing active
- Simpler than managing button state through processing lifecycle

**Alternatives considered**:
- Disable during processing: Rejected—adds complexity to track processing state across all code paths
- Modal confirmation dialog: Rejected—slows down common use case (reset after successful completion)
- No protection: Rejected—could cause undefined state if reset during file I/O

**Implementation approach**: Add boolean flag to `AppController`, set True at start of `process_files()`, False at end/error

---

### Q3: What GUI state should be preserved vs. reset?

**Decision**: Reset transient operation state, preserve user preference settings

**Reset (transient state)**:
- File selections (excel_file, pdf_file paths)
- File labels showing selected filenames
- Filter state (enabled, column, values, prompt flag)
- Merge state (enabled, pairs list)
- Status text area (keep last 3 lines as breadcrumb)
- Process button enabled state

**Preserve (user preferences)**:
- Backup enabled checkbox
- Sort bookmarks checkbox  
- Reorder pages checkbox
- Check document images checkbox (reset to default True, not preserved)
- Window size/position

**Rationale**:
- Existing `reset_gui()` method already implements this pattern correctly
- Users set preferences once per session, but change files/operations frequently
- Document images defaults to True per spec requirement (FR-005)
- Matches user mental model: "Reset my work, keep my settings"

**Alternatives considered**:
- Reset everything: Rejected—forces users to reconfigure preferences each time
- Reset nothing: Rejected—doesn't solve the cleanup problem
- Add "Reset All" vs "Reset Files": Rejected—over-engineering for simple use case

**Implementation approach**: Reuse existing `reset_gui()` method, add button that calls it

---

### Q4: How should status area be handled during reset?

**Decision**: Clear status area but keep last 3 lines as contextual breadcrumb trail

**Rationale**:
- Spec requirement FR-006: Clear except for most recent completion messages
- Provides continuity—user can see what they just completed before resetting
- Prevents jarring "everything disappeared" feeling
- Existing implementation already does this correctly (lines 657-672 in tk_app.py)
- Adds reset confirmation message at end

**Alternatives considered**:
- Complete clear: Rejected—loses helpful context of what just happened
- Keep all history: Rejected—defeats purpose of reset (preparing for new operation)
- Separator only: Rejected—doesn't provide enough context

**Implementation approach**: Leverage existing behavior in `reset_gui()`, no changes needed

---

### Q5: What testing strategy is appropriate for GUI reset functionality?

**Decision**: Create unit tests in `tests/app/test_reset_button.py` that mock GUI components and verify state transitions

**Rationale**:
- Existing test pattern in `tests/app/test_tk_app_document_found.py` shows how to test GUI components
- Can instantiate `AbstractRenumberGUI` with mocked root and controller
- Verify state before/after reset by checking attribute values
- No need for integration tests—pure UI state management

**Test coverage**:
1. Reset clears file selections
2. Reset clears filter state
3. Reset clears merge pairs
4. Reset preserves preference checkboxes
5. Reset disables Process button
6. Reset button is always enabled
7. Reset logs confirmation message
8. Reset with empty state (no-op, safe)

**Alternatives considered**:
- Manual testing only: Rejected—no regression protection
- GUI integration tests with screenshot comparison: Rejected—overkill for state verification
- Smoke tests: Rejected—insufficient coverage for state management correctness

**Implementation approach**: Follow existing test patterns using pytest fixtures and assertions on GUI object attributes

---

## Best Practices Applied

### Tkinter Button Patterns

**Grid Layout for Button Grouping**:
```python
# Process button
self.process_button = ttk.Button(
    main_frame,
    text="Process Files",
    command=self.controller.process_files,
    state="disabled",
)
self.process_button.grid(row=5, column=0, pady=20)

# Reset button (new)
self.reset_button = ttk.Button(
    main_frame,
    text="Reset",
    command=self._on_reset_clicked,
    state="normal",  # Always enabled
)
self.reset_button.grid(row=5, column=1, padx=(10, 0), pady=20)
```

**Reference**: tkinter grid geometry manager documentation, ttk.Button styling

---

### State Management Patterns

**Existing Pattern (Preserved)**:
- GUI class (`AbstractRenumberGUI`) owns all UI state as instance attributes
- Controller (`AbstractRenumberTool`) delegates to GUI methods
- Adapter (`TkinterUIAdapter`) provides protocol abstraction for controller

**Reset Implementation**:
- Add button in `setup_gui()` method
- Create `_on_reset_clicked()` handler that calls existing `reset_gui()`
- No new state variables needed—reuses existing reset logic

**Reference**: Existing `reset_gui()` implementation at lines 622-675 in `app/tk_app.py`

---

### Error Handling Patterns

**Defensive Programming**:
- Check for None/null state before resetting (already handled in existing code)
- Use `hasattr()` checks for optional attributes (filter_summary_label, merge_summary_label)
- Log reset action for debugging/audit trail

**No Expected Errors**:
- Reset is pure memory operation—no I/O, no validation
- Cannot fail under normal circumstances
- Processing-in-progress check is preventative, not reactive

---

## Technology Decisions

### UI Framework: tkinter (stdlib)

**Why**: Already in use, no additional dependencies needed

**Alternatives**: Not applicable—GUI framework is established project decision

---

### Layout Manager: Grid

**Why**: Existing GUI uses grid for precise control of component positioning

**Alternatives**: Pack manager—rejected because changing layout system would require rewriting entire GUI

---

### Button Style: ttk.Button

**Why**: Consistent with existing Process button styling (native platform appearance)

**Alternatives**: tk.Button—rejected because ttk provides better theming and accessibility

---

## Open Questions

**None**. All implementation details resolved through analysis of existing codebase and spec requirements.

---

## Implementation Checklist

Phase 1 (Design):
- [ ] Document GUI state model in `data-model.md`
- [ ] Create developer quickstart in `quickstart.md`
- [ ] No contracts needed (no APIs)

Phase 2 (Implementation):
- [ ] Add Reset button to `AbstractRenumberGUI.setup_gui()`
- [ ] Create `_on_reset_clicked()` handler method
- [ ] Add processing flag to `AppController` (defensive check)
- [ ] Write unit tests in `tests/app/test_reset_button.py`
- [ ] Manual verification with GUI application
- [ ] Update version in `_version.py` (MINOR bump: new feature)
- [ ] Update CHANGELOG.md with feature addition

