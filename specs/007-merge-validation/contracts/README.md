# API Contracts: Prevent Single-File Processing with Merge Mode Enabled

**Feature**: Merge Mode Validation  
**Date**: 2025-11-20  
**Version**: 1.0.0

## Overview

This feature modifies existing internal APIs to add validation logic. No new external APIs are created.

## Modified Contracts

### 1. UIController.get_options()

**Enhanced Contract**: Returns None for merge_pairs when empty to distinguish from intentional single-file mode

```python
def get_options(self) -> Options:
    """
    Get processing options from UI with merge validation.
    
    Returns:
        Options with merge_pairs set to None (not empty list) when:
        - Merge mode is disabled, OR
        - Merge mode is enabled but no pairs selected
        
    Behavior Change:
        Before: merge_pairs = [] when enabled but empty
        After:  merge_pairs = None when enabled but empty (prevents confusion)
    """
```

### 2. AppController.process_files()

**Enhanced Contract**: Validates merge state before processing

```python
def process_files(self) -> None:
    """
    Main processing function with merge validation.
    
    Validation Rules:
        - If merge_enabled and (merge_pairs is None or len(merge_pairs) == 0):
          Raise ValueError with clear message
        - Otherwise proceed normally
        
    Raises:
        ValueError: If merge enabled but no pairs selected
    """
```

### 3. AbstractRenumberGUI._update_process_button_state()

**New Contract**: Manages Process button enablement with merge validation

```python
def _update_process_button_state(self) -> None:
    """
    Update Process button enabled state based on file selection and merge validity.
    
    Enable Conditions:
        - Primary files selected AND
        - (Merge disabled OR Merge pairs selected)
        
    Disable Conditions:
        - No primary files selected OR
        - Merge enabled but no pairs selected
    """
```

## Validation Rules

### Merge Validity Check

```python
def is_merge_valid(merge_enabled: bool, merge_pairs: Optional[List]) -> bool:
    """
    Determine if merge configuration is valid.
    
    Args:
        merge_enabled: Whether merge checkbox is checked
        merge_pairs: List of selected pairs (may be None or empty)
        
    Returns:
        True if merge configuration is valid for processing
        
    Rules:
        - If merge_enabled is False: Always valid (single-file mode)
        - If merge_enabled is True: Valid only if merge_pairs has 1+ items
    """
    if not merge_enabled:
        return True  # Single-file mode always valid
    return merge_pairs is not None and len(merge_pairs) > 0
```

## Error Messages

### Merge Pairs Required Error

**Trigger**: Attempt to process with merge enabled but no pairs

**Message**:
```
Merge Mode Requires Additional Files

Merge mode is enabled but no file pairs were selected.

To proceed, choose one:
1. Click "Pairs..." to select at least one file pair to merge
2. Uncheck "Enable Merge" to process as a single file

Note: Backups are disabled during merge operations because 
originals remain untouched (output creates new _merged files).
```

**Display**: Error dialog with title "Invalid Merge Configuration"

## Testing Contracts

### Test Scenarios

```python
# Test 1: Process button disabled when merge enabled without pairs
def test_process_button_disabled_merge_no_pairs():
    """
    Given: Merge enabled, no pairs selected
    When: Checking process button state
    Then: Button is disabled
    """

# Test 2: Validation error on process attempt
def test_validation_error_merge_no_pairs():
    """
    Given: Merge enabled, no pairs selected
    When: process_files() is called
    Then: ValueError raised with clear message
    """

# Test 3: Valid merge still works
def test_valid_merge_processes_correctly():
    """
    Given: Merge enabled, 1+ pairs selected
    When: process_files() is called
    Then: Processing proceeds normally
    """

# Test 4: Single-file mode unaffected
def test_single_file_mode_unchanged():
    """
    Given: Merge disabled
    When: process_files() is called with single file
    Then: Processing proceeds with backups available
    """
```

## State Management

### UI State Transitions

```
State 1: Merge Disabled
  - backup_checkbox: enabled
  - merge_button: disabled
  - process_button: enabled (if files selected)

State 2: Merge Enabled, No Pairs
  - backup_checkbox: disabled (with explanation)
  - merge_button: enabled
  - process_button: DISABLED (FIXED - was enabled)
  - merge_summary: "Select one or more pairs"

State 3: Merge Enabled, Pairs Selected
  - backup_checkbox: disabled (with explanation)
  - merge_button: enabled
  - process_button: enabled
  - merge_summary: "Pairs selected: N"
```

## Performance Guarantees

- Validation check: O(1) - simple length check
- No performance impact on merge operations
- Instant UI feedback (<1ms for button state update)

## Backward Compatibility

- ✅ Existing valid merge operations unchanged
- ✅ Single-file operations unchanged
- ✅ Only invalid state (the bug) is prevented
- ✅ No API signature changes (internal behavior fix only)
