# Developer Quickstart: Reset Button

**Feature**: Reset Button  
**Date**: 2025-11-20  
**Audience**: Developers implementing or testing the Reset Button feature

## Prerequisites

- Python 3.7+ installed (`python3 --version`)
- Git repository cloned locally
- Feature branch `008-reset-button` checked out
- Virtual environment activated (recommended)

## Setup

### 1. Install Dependencies

```bash
cd /home/chris/Code/aa-abstract-renumber
pip install -r requirements.txt
```

**Key dependencies for this feature**:
- tkinter (Python stdlib—should be pre-installed)
- pytest (for testing)

### 2. Verify Current State

```bash
# Ensure you're on the feature branch
git branch --show-current
# Should output: 008-reset-button

# Run existing tests to ensure baseline passes
python3 -m pytest tests/app/ -v
```

## Implementation Checklist

### Phase 1: Add Reset Button UI Component

**File**: `app/tk_app.py`

**Location**: `AbstractRenumberGUI.setup_gui()` method (around line 94)

**Steps**:

1. Locate the Process button creation (currently at line 115-121)

2. Modify button layout to support horizontal grouping:

```python
# Create a button frame to hold both buttons
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=5, column=0, columnspan=2, pady=20)

# Process button
self.process_button = ttk.Button(
    button_frame,
    text="Process Files",
    command=self.controller.process_files,
    state="disabled",
)
self.process_button.grid(row=0, column=0, padx=(0, 10))

# Reset button (NEW)
self.reset_button = ttk.Button(
    button_frame,
    text="Reset",
    command=self._on_reset_clicked,
    state="normal",  # Always enabled per spec FR-008
)
self.reset_button.grid(row=0, column=1)
```

3. Add the Reset button instance variable to `__init__` documentation (line 56 area):

```python
self.reset_button: Optional[ttk.Button] = None
```

### Phase 2: Add Event Handler

**File**: `app/tk_app.py`

**Location**: Add new method to `AbstractRenumberGUI` class (after `_check_files_ready()` method, around line 541)

```python
def _on_reset_clicked(self) -> None:
    """Handle Reset button click event.
    
    Delegates to existing reset_gui() method which clears transient
    operation state (file selections, filter/merge configs) while
    preserving user preference settings.
    
    Future enhancement: Add defensive check if processing is active.
    """
    self.reset_gui()
```

### Phase 3: Add Unit Tests

**File**: `tests/app/test_reset_button.py` (NEW)

**Create new test file**:

```python
#!/usr/bin/env python3
"""
Tests for Reset Button functionality in AbstractRenumberGUI.
"""

import tkinter as tk
from unittest.mock import MagicMock

import pytest

from app.tk_app import AbstractRenumberGUI


@pytest.fixture
def gui():
    """Create GUI instance for testing."""
    root = tk.Tk()
    controller = MagicMock()
    gui_instance = AbstractRenumberGUI(root, controller)
    yield gui_instance
    root.destroy()


def test_reset_button_exists(gui):
    """Verify Reset button is created during GUI setup."""
    assert gui.reset_button is not None
    assert gui.reset_button.cget("text") == "Reset"


def test_reset_button_always_enabled(gui):
    """Verify Reset button is always enabled (spec FR-008)."""
    assert gui.reset_button.cget("state") == "normal"


def test_reset_clears_file_selections(gui):
    """Verify reset clears file path state."""
    gui.excel_file = "/path/to/test.xlsx"
    gui.pdf_file = "/path/to/test.pdf"
    
    gui.reset_gui()
    
    assert gui.excel_file is None
    assert gui.pdf_file is None


def test_reset_clears_filter_state(gui):
    """Verify reset clears filter configuration."""
    gui.filter_enabled.set(True)
    gui.filter_column = "test_column"
    gui.filter_values = ["value1", "value2"]
    
    gui.reset_gui()
    
    assert gui.filter_enabled.get() is False
    assert gui.filter_column is None
    assert gui.filter_values == []


def test_reset_clears_merge_state(gui):
    """Verify reset clears merge configuration."""
    gui.merge_enabled.set(True)
    gui.merge_pairs = [("/path/excel.xlsx", "/path/doc.pdf")]
    
    gui.reset_gui()
    
    assert gui.merge_enabled.get() is False
    assert gui.merge_pairs == []


def test_reset_preserves_backup_preference(gui):
    """Verify reset preserves user preference settings."""
    gui.backup_enabled.set(False)  # User changed default
    gui.sort_bookmarks_enabled.set(True)
    
    gui.reset_gui()
    
    # Preferences should be unchanged
    assert gui.backup_enabled.get() is False
    assert gui.sort_bookmarks_enabled.get() is True


def test_reset_disables_process_button(gui):
    """Verify reset disables Process button until new files selected."""
    gui.excel_file = "/path/to/test.xlsx"
    gui.pdf_file = "/path/to/test.pdf"
    gui._update_process_button_state()  # Enable it
    
    gui.reset_gui()
    
    assert gui.process_button.cget("state") == "disabled"


def test_reset_with_empty_state_safe(gui):
    """Verify reset with no files selected is safe no-op."""
    # Start with empty state
    assert gui.excel_file is None
    assert gui.pdf_file is None
    
    # Reset should not raise error
    gui.reset_gui()
    
    # State should remain empty
    assert gui.excel_file is None
    assert gui.pdf_file is None
```

### Phase 4: Manual Verification

**Run the application**:

```bash
python3 main.py
```

**Test scenarios**:

1. **Basic Reset**:
   - Select Excel and PDF files
   - Click Reset
   - Verify: Files cleared, labels show "No file selected"

2. **Reset After Processing**:
   - Select files and process successfully
   - Click Reset
   - Verify: Ready for new files, status shows reset message

3. **Preference Preservation**:
   - Disable backup checkbox
   - Select files
   - Click Reset
   - Verify: Backup checkbox still disabled (preference preserved)

4. **Filter State Reset**:
   - Enable filter
   - Click Reset
   - Verify: Filter checkbox disabled, no column/values selected

5. **Merge State Reset**:
   - Enable merge, add pairs
   - Click Reset
   - Verify: Merge disabled, pairs list cleared

6. **Button Always Enabled**:
   - Verify Reset button never becomes disabled in any state

## Running Tests

### Run All Tests

```bash
python3 -m pytest tests/ -v
```

### Run Only Reset Button Tests

```bash
python3 -m pytest tests/app/test_reset_button.py -v
```

### Run with Coverage

```bash
python3 -m pytest tests/app/test_reset_button.py --cov=app.tk_app --cov-report=term-missing
```

## Troubleshooting

### Issue: tkinter Not Available

**Error**: `ModuleNotFoundError: No module named '_tkinter'`

**Solution** (Ubuntu/Debian):
```bash
sudo apt-get install python3-tk
```

### Issue: Tests Fail Due to Display

**Error**: `_tkinter.TclError: no display name and no $DISPLAY environment variable`

**Solution**: Install virtual display for headless testing:
```bash
sudo apt-get install xvfb
xvfb-run python3 -m pytest tests/app/test_reset_button.py -v
```

### Issue: Existing Tests Break

**Symptom**: Tests in `tests/app/test_tk_app_document_found.py` fail after changes

**Solution**: Verify button frame change doesn't break grid layout. Check that all row/column indices are updated correctly.

## Code Review Checklist

Before submitting PR:

- [ ] Reset button appears next to Process button
- [ ] Button text is "Reset"
- [ ] Button is always enabled
- [ ] Clicking Reset calls `reset_gui()` method
- [ ] All unit tests pass
- [ ] Manual verification completed
- [ ] PEP 8 compliance verified (`flake8 app/tk_app.py`)
- [ ] Docstrings added for new method
- [ ] No linter errors introduced
- [ ] Version bumped in `_version.py` (MINOR increment for new feature)
- [ ] CHANGELOG.md updated with feature addition

## Next Steps

After implementation complete:

1. Run full test suite: `python3 -m pytest tests/ -v`
2. Update version: Edit `_version.py` (e.g., 1.0.0 → 1.1.0)
3. Update CHANGELOG.md: Add entry under `[Unreleased]` → Added section
4. Commit changes: `git commit -m "feat: add reset button for clearing app state"`
5. Create PR to merge `008-reset-button` → `dev` branch

## References

- Feature Spec: [spec.md](./spec.md)
- Implementation Plan: [plan.md](./plan.md)
- Research Notes: [research.md](./research.md)
- Data Model: [data-model.md](./data-model.md)
- Constitution: `.specify/memory/constitution.md`

