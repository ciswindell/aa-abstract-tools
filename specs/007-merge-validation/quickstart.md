# Implementation Quickstart: Prevent Single-File Processing with Merge Mode Enabled

**Feature**: Merge Mode Validation  
**Date**: 2025-11-20  
**Estimated Time**: 1-2 hours (implementation + testing)

## Prerequisites

- [x] Feature specification reviewed ([spec.md](spec.md))
- [x] Research completed ([research.md](research.md))
- [x] Data model understood ([data-model.md](data-model.md))
- [x] Working knowledge of tkinter and existing codebase
- [x] Branch `007-merge-validation` checked out

## Implementation Steps

### Step 1: Add Process Button State Update Method

**File**: `/home/chris/Code/aa-abstract-renumber/app/tk_app.py`  
**Location**: Add new method after `_on_file_change()`

#### New Method

```python
def _update_process_button_state(self) -> None:
    """Update Process button enabled state based on file selection and merge validity."""
    files_selected = self.excel_file is not None and self.pdf_file is not None
    
    # Check merge validity: merge disabled OR merge enabled with pairs selected
    merge_valid = not self.merge_enabled.get() or len(self.merge_pairs) > 0
    
    should_enable = files_selected and merge_valid
    
    if self.process_button:
        self.process_button.config(state="normal" if should_enable else "disabled")
```

### Step 2: Call Update Method from Relevant Locations

**File**: `/home/chris/Code/aa-abstract-renumber/app/tk_app.py`

#### Location 1: After file selection changes

Find `_on_file_change()` and add call at the end:
```python
def _on_file_change(self, *args):
    # ... existing logic ...
    self._update_process_button_state()  # ADD THIS
```

#### Location 2: In merge toggle callback

Modify `on_merge_toggle()` around line 302:
```python
def on_merge_toggle(*_args):
    if self.merge_enabled.get():
        # ... existing merge enable logic ...
    else:
        # ... existing merge disable logic ...
    
    self._update_process_button_state()  # ADD THIS at the end
```

#### Location 3: After pairs selected

Modify `_on_choose_merge_pairs()` around line 393:
```python
def _on_choose_merge_pairs(self) -> None:
    """Open pairs dialog via adapter and store results on the GUI."""
    try:
        pairs = self.controller.ui_adapter.prompt_merge_pairs()
    except Exception:
        pairs = None
    self.merge_pairs = list(pairs or [])
    if self.merge_pairs:
        preview = len(self.merge_pairs)
        self.merge_summary_label.config(
            text=f"Pairs selected: {preview}", foreground="green"
        )
    else:
        self.merge_summary_label.config(text="No pairs selected", foreground="gray")
    
    self._update_process_button_state()  # ADD THIS
```

### Step 3: Fix merge_pairs Return Value in Adapter

**File**: `/home/chris/Code/aa-abstract-renumber/adapters/ui_tkinter.py`  
**Method**: `get_options()`  
**Lines**: ~65-70

#### Current Code

```python
merge_pairs = (
    list(getattr(self.gui, "merge_pairs", []) or [])
    if getattr(self.gui, "get_merge_enabled", None)
    and self.gui.get_merge_enabled()
    else None
)
```

#### Modified Code

```python
# Get merge pairs only if merge is enabled AND pairs were actually selected
merge_enabled = (
    getattr(self.gui, "get_merge_enabled", None)
    and self.gui.get_merge_enabled()
)
if merge_enabled:
    pairs_list = list(getattr(self.gui, "merge_pairs", []) or [])
    merge_pairs = pairs_list if len(pairs_list) > 0 else None
else:
    merge_pairs = None
```

### Step 4: Add Backend Validation in Controller

**File**: `/home/chris/Code/aa-abstract-renumber/core/app_controller.py`  
**Method**: `process_files()`  
**Location**: After getting options, before processing (around line 71)

#### Add Validation

```python
# Get options from UI
options = self.ui.get_options()

# Validate merge configuration
if self.ui.get_merge_enabled() and (options.merge_pairs is None or len(options.merge_pairs) == 0):
    error_msg = (
        "Merge mode is enabled but no file pairs were selected.\n\n"
        "Please select at least one additional file pair using the 'Pairs...' button,\n"
        "or disable merge mode to process as a single file."
    )
    raise ValueError(error_msg)

# Continue with existing logic...
```

### Step 5: Create Tests

**New File**: `/home/chris/Code/aa-abstract-renumber/tests/app/test_merge_validation.py`

```python
#!/usr/bin/env python3
"""Tests for merge mode validation logic."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, MagicMock
from core.app_controller import AppController
from core.models import Options


class TestMergeValidation:
    """Test merge mode validation prevents invalid operations."""
    
    def test_merge_enabled_no_pairs_raises_error(self):
        """Test that processing fails when merge enabled but no pairs selected."""
        # Create mock UI that returns merge enabled but no pairs
        ui = Mock()
        ui.get_merge_enabled.return_value = True
        ui.get_options.return_value = Options(
            backup=False,
            sort_bookmarks=False,
            reorder_pages=False,
            sheet_name="Index",
            merge_pairs=None,  # No pairs selected
        )
        ui.get_file_paths.return_value = ("/path/excel.xlsx", "/path/file.pdf")
        
        controller = AppController(ui)
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="no file pairs were selected"):
            controller.process_files()
    
    def test_merge_enabled_with_pairs_succeeds(self):
        """Test that processing works when merge enabled with pairs."""
        # This would need more comprehensive mocking
        # Demonstrates the test pattern
        pass
    
    def test_merge_disabled_single_file_succeeds(self):
        """Test that single-file mode still works."""
        # Demonstrates regression test
        pass
```

## Testing Checklist

- [ ] Unit test: Process button disabled when merge enabled without pairs
- [ ] Unit test: Backend validation raises error for invalid merge state
- [ ] Integration test: End-to-end validation flow
- [ ] Regression test: Valid merges still work
- [ ] Regression test: Single-file mode still works
- [ ] Manual test: UI feedback is clear and helpful

## Common Issues & Solutions

### Issue 1: Process button doesn't update after pair selection
**Solution**: Ensure `_update_process_button_state()` is called in `_on_choose_merge_pairs()`

### Issue 2: Empty list still allows processing
**Solution**: Check for `len(merge_pairs) > 0`, not just truthiness

### Issue 3: Backup checkbox behavior confusing
**Solution**: Consider moving backup disable to after pairs selection (future enhancement)

## Rollback Plan

If issues arise:
1. Revert button state logic in `app/tk_app.py`
2. Revert adapter changes in `ui_tkinter.py`
3. Remove controller validation
4. Changes are isolated and can be reverted independently

## Next Steps

After implementation:
1. Run tests: `pytest tests/app/test_merge_validation.py -v`
2. Test manually: Enable merge, don't select pairs, try to process
3. Verify error message is clear and actionable
4. Test valid merge operations still work
5. Update version in `_version.py` (PATCH increment to 1.0.2)
6. Update CHANGELOG.md with the fix details
