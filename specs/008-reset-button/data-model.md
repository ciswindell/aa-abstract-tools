# Data Model: Reset Button

**Feature**: Reset Button  
**Date**: 2025-11-20  
**Purpose**: Document GUI state entities and their relationships for reset functionality

## Overview

The Reset Button feature operates on in-memory GUI state only. No persistent storage or data serialization is involved. This document defines the state model managed by the `AbstractRenumberGUI` class.

## State Categories

### 1. Transient Operation State (Reset Target)

State that should be cleared when starting a new processing operation.

#### File Selection State

```python
class FileSelectionState:
    """File paths selected by user for processing"""
    excel_file: Optional[str] = None  # Path to Excel file
    pdf_file: Optional[str] = None    # Path to PDF file
```

**Lifecycle**: Set via Browse buttons, cleared on Reset, never persisted

**UI Bindings**:
- `excel_file` → `excel_label` displays basename or "No file selected"
- `pdf_file` → `pdf_label` displays basename or "No file selected"
- Both files required → `process_button` enabled state

**Reset Behavior**: Set both to `None`, update labels to "No file selected" (gray)

---

#### Filter State

```python
class FilterState:
    """Configuration for filtering Excel rows by column values"""
    filter_enabled: tk.BooleanVar      # Checkbox state
    filter_column: Optional[str]       # Selected column name
    filter_values: list[str]           # Selected values to include
    _filter_prompt_requested: bool     # Internal flag for prompt timing
```

**Lifecycle**: Configured via Enable Filter checkbox and prompt dialog, cleared on Reset

**UI Bindings**:
- `filter_enabled` → Checkbox widget
- Summary label shows: "Filter: {column} ∈ [{values}]" when active

**Reset Behavior**: 
- `filter_enabled.set(False)`
- `filter_column = None`
- `filter_values = []`
- `_filter_prompt_requested = False`
- Clear summary label text

---

#### Merge State

```python
class MergeState:
    """Configuration for merging multiple file pairs"""
    merge_enabled: tk.BooleanVar        # Checkbox state
    merge_pairs: list[tuple[str, str]]  # List of (excel_path, pdf_path) pairs
```

**Lifecycle**: Configured via Enable Merge checkbox and Pairs dialog, cleared on Reset

**UI Bindings**:
- `merge_enabled` → Checkbox widget
- Summary label shows: "Pairs selected: {count}" when active
- Disables backup checkbox when enabled (originals untouched)

**Reset Behavior**:
- `merge_enabled.set(False)`
- `merge_pairs = []`
- Clear summary label text
- Re-enable backup checkbox (triggers preference restoration)

---

#### Status Display State

```python
class StatusDisplayState:
    """Message history displayed in status text area"""
    status_text: tk.Text  # Widget containing timestamped messages
```

**Lifecycle**: Accumulates messages during operation, partially cleared on Reset

**Reset Behavior**:
- Keep last 3 lines (completion messages as context breadcrumb)
- Add reset confirmation message: "GUI reset - ready for new files!"

---

#### Process Button State

```python
class ProcessButtonState:
    """Enable/disable state of main action button"""
    process_button: ttk.Button
```

**Lifecycle**: Enabled when valid files selected and merge valid, disabled otherwise

**Reset Behavior**: Set to disabled state (waits for new file selection)

**Validation Rules** (unchanged by Reset feature):
```python
should_enable = (
    excel_file is not None 
    and pdf_file is not None 
    and (not merge_enabled or len(merge_pairs) > 0)
)
```

---

### 2. User Preference State (Preserved Across Resets)

Settings that reflect user's workflow preferences, not operation-specific choices.

#### Processing Options

```python
class ProcessingPreferences:
    """User preferences for how processing operates"""
    backup_enabled: tk.BooleanVar               # Create timestamped backups
    sort_bookmarks_enabled: tk.BooleanVar       # Sort PDF bookmarks
    reorder_pages_enabled: tk.BooleanVar        # Reorder pages to match bookmarks
    # Note: check_document_images_enabled is reset to default True (spec FR-005)
```

**Lifecycle**: Set by user at session start, preserved across multiple Reset operations

**Reset Behavior**: **No changes** (preserve user preferences)

**Exception**: `check_document_images_enabled` is reset to default `True` (spec requirement)

---

### 3. Immutable UI Components (Never Modified)

Components that exist for the lifetime of the window.

#### Widget References

```python
class ImmutableComponents:
    """Tkinter widgets that persist throughout application lifetime"""
    root: tk.Tk                    # Main window
    excel_label: ttk.Label         # File selection labels
    pdf_label: ttk.Label
    process_button: ttk.Button     # Action buttons
    reset_button: ttk.Button       # NEW: Reset button
    status_text: tk.Text           # Status display area
    backup_checkbox: ttk.Checkbutton
    # ... other checkboxes and labels
```

**Lifecycle**: Created once in `setup_gui()`, destroyed when window closes

**Reset Behavior**: Update content/state via `.config()`, never recreate

---

## State Transitions

### Initial State (Application Startup)

```
Files: None, None
Filter: Disabled, no column, no values
Merge: Disabled, no pairs
Status: "Ready. Please select Excel and PDF files."
Process Button: Disabled
Preferences: backup=True, sort=False, reorder=False, check_images=True
```

### Files Selected State

```
Files: "/path/to/file.xlsx", "/path/to/file.pdf"
Filter: [user may enable and configure]
Merge: [user may enable and configure]
Status: "Ready to process!"
Process Button: Enabled (if merge valid)
Preferences: [unchanged]
```

### After Processing State

```
Files: [unchanged from previous]
Filter: [configured state preserved]
Merge: [configured state preserved]
Status: [history of processing messages]
Process Button: Enabled
Preferences: [unchanged]
```

### After Reset State (Target)

**Returns to Initial State** with preference preservation:

```
Files: None, None                     ← RESET
Filter: Disabled, no column, no values ← RESET
Merge: Disabled, no pairs             ← RESET
Status: [last 3 lines] + reset message ← PARTIAL RESET
Process Button: Disabled               ← RESET
Preferences: [preserved from before]   ← PRESERVED
check_document_images: True            ← RESET TO DEFAULT
```

---

## Implementation Mapping

### Existing Methods (Reused)

**`AbstractRenumberGUI.reset_gui()` (lines 622-675 in `tk_app.py`)**:

Already implements correct reset logic:
- Clears file selections
- Resets filter/merge state
- Preserves preferences (except check_document_images)
- Manages status text correctly
- Disables process button

**New Requirement**: Add button that calls this method

---

### New Components

**Reset Button**:

```python
# In setup_gui() method
self.reset_button = ttk.Button(
    main_frame,
    text="Reset",
    command=self._on_reset_clicked,
    state="normal",  # Always enabled per spec FR-008
)
self.reset_button.grid(row=5, column=1, padx=(10, 0), pady=20)
```

**Event Handler**:

```python
def _on_reset_clicked(self) -> None:
    """Handle Reset button click - delegates to existing reset_gui()."""
    # Defensive check: warn if processing active (future enhancement)
    # if self.controller.is_processing():
    #     self.log_status("Cannot reset during processing", MSG_WARNING)
    #     return
    
    self.reset_gui()  # Call existing reset logic
```

---

## State Validation Rules

### Process Button Enable Logic

**Current Implementation** (`_update_process_button_state()` at line 522):

```python
files_selected = excel_file is not None and pdf_file is not None
merge_valid = not merge_enabled or len(merge_pairs) > 0
should_enable = files_selected and merge_valid
```

**Unchanged by Reset Feature**: Button state automatically updates when files cleared

---

### Filter/Merge Mutual Independence

No restrictions—user can enable both filter and merge simultaneously.

**Behavior**:
- Filter applies to merged dataset (after loading all pairs)
- Reset clears both configurations independently

---

## Edge Cases

### Reset with Empty State

**Scenario**: User clicks Reset without selecting any files

**Behavior**: Safe no-op, logs reset message, state remains empty

**Implementation**: `reset_gui()` handles None values gracefully

---

### Reset During Processing

**Scenario**: User clicks Reset while `process_files()` is running

**Mitigation**: Add defensive check in `_on_reset_clicked()` (research Q2)

**Current Risk**: Low (processing locks GUI thread, button unresponsive)

**Future Enhancement**: Track `self.processing` flag in controller

---

### Rapid Repeated Resets

**Scenario**: User clicks Reset multiple times rapidly

**Behavior**: Each click safely re-executes reset logic, logs message each time

**Performance**: Negligible (in-memory assignment operations only)

---

## Testing Strategy

### State Verification Tests

```python
def test_reset_clears_file_selections():
    gui.excel_file = "/path/to/test.xlsx"
    gui.pdf_file = "/path/to/test.pdf"
    
    gui.reset_gui()
    
    assert gui.excel_file is None
    assert gui.pdf_file is None
    assert gui.excel_label.cget("text") == "No file selected"
```

### Preference Preservation Tests

```python
def test_reset_preserves_backup_preference():
    gui.backup_enabled.set(False)  # User disabled backup
    
    gui.reset_gui()
    
    assert gui.backup_enabled.get() is False  # Still disabled
```

### State Transition Tests

```python
def test_reset_disables_process_button():
    gui.excel_file = "/path/to/test.xlsx"
    gui.pdf_file = "/path/to/test.pdf"
    gui._update_process_button_state()  # Enable button
    
    gui.reset_gui()
    
    assert gui.process_button.cget("state") == "disabled"
```

---

## Summary

**Total State Variables**: ~15 (10 transient, 4 preferences, 1 UI component reference)

**Reset Scope**: Clears transient operation state, preserves user preferences

**No Database/Persistence**: Entirely in-memory GUI state management

**Existing Implementation**: 90% complete—only needs button UI component added

