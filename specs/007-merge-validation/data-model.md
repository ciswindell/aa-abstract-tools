# Data Model: Prevent Single-File Processing with Merge Mode Enabled

**Feature**: Merge Mode Validation  
**Date**: 2025-11-20  
**Version**: 1.0.0

## Overview

This feature adds validation logic to prevent an invalid application state. The data model is minimal since this is primarily validation logic, but we need to understand the state transitions and validation rules.

## Core Entities

### 1. Merge State

**Purpose**: Represents the current merge mode configuration in the UI

**Attributes**:
- `merge_enabled`: boolean - Whether merge mode checkbox is checked
- `merge_pairs`: List[Tuple[str, str]] - Selected (Excel, PDF) file pairs
- `primary_files`: Tuple[str, str] - The primary (Excel, PDF) selection

**Validation Rules**:
- If `merge_enabled` is True, `merge_pairs` must contain at least one pair
- Merge pairs must not be empty list when merge mode is enabled
- Primary files can optionally be included in merge pairs (will be deduplicated)

**State Transitions**:
```
Initial State: merge_enabled=False, merge_pairs=[]
  ↓
User checks "Enable Merge"
  ↓
State: merge_enabled=True, merge_pairs=[] → INVALID (Process button disabled)
  ↓
User clicks "Pairs..." and selects files
  ↓
State: merge_enabled=True, merge_pairs=[(x1,p1), (x2,p2)] → VALID (Process enabled)
```

### 2. Process Button State

**Purpose**: Tracks whether the Process button should be enabled

**Attributes**:
- `files_selected`: boolean - Primary Excel and PDF files selected
- `merge_valid`: boolean - Merge requirements met (disabled OR pairs selected)
- `enabled`: boolean - Computed state of Process button

**Validation Rules**:
```python
merge_valid = (not merge_enabled) or (len(merge_pairs) > 0)
process_enabled = files_selected and merge_valid
```

**State Truth Table**:
| Files Selected | Merge Enabled | Pairs Selected | Process Enabled |
|----------------|---------------|----------------|-----------------|
| No             | No            | N/A            | No              |
| Yes            | No            | N/A            | Yes             |
| Yes            | Yes           | No (0 pairs)   | No (FIXED)      |
| Yes            | Yes           | Yes (1+ pairs) | Yes             |

## Validation Flow

### Pre-Processing Validation

```
User clicks Process
  ↓
Check 1: Files selected?
  No → Show "Select files" error
  Yes → Continue
  ↓
Check 2: Merge enabled?
  No → Process single file with backups
  Yes → Continue to Check 3
  ↓
Check 3: Merge pairs selected?
  No → Show "Select at least one pair" error → STOP
  Yes → Process merge workflow
```

### Error Messages

**Invalid State**: Merge enabled + No pairs
```
Error: Merge Mode Requires Additional Files

Merge mode is enabled but no file pairs were selected.

To proceed:
1. Click "Pairs..." to select files to merge, OR
2. Uncheck "Enable Merge" to process single file

Note: Backups are disabled during merge to protect original files.
```

## Business Rules

### Rule 1: Merge Requires Multiple Files
- Minimum: Primary file + 1 additional pair = 2 file pairs total
- Rationale: "Merge" by definition requires multiple sources

### Rule 2: Backup Protection
- Single-file mode: Backups available and recommended
- Merge mode: Backups disabled (originals untouched, output is new file)
- Invalid state (merge without pairs): Should NOT disable backups

### Rule 3: UI Consistency
- Process button state must reflect operation validity
- Users should not be able to initiate invalid operations
- Error messages should be actionable and specific

## Edge Cases

### Handled Scenarios

1. **Empty List vs None**: Treat empty merge_pairs list as no pairs selected
2. **Primary File in Merge List**: Silently deduplicate to avoid confusion
3. **Rapid Checkbox Toggling**: UI state updates correctly on each toggle

### Error Conditions

1. **Merge Enabled + Empty Pairs**: Prevent processing, show error
2. **Invalid File Paths in Pairs**: Existing validation will catch this later
3. **UI Bypassed**: Backend validation catches programmatic errors

## Implementation Notes

### Key Methods to Modify

1. **app/tk_app.py**:
   - `_update_process_button_state()` - Add merge validity check
   - `on_merge_toggle()` - Move backup disable to after pairs selected
   - `_on_choose_merge_pairs()` - Update Process button state after selection

2. **adapters/ui_tkinter.py**:
   - `get_options()` - Return None instead of [] for merge_pairs when empty

3. **core/app_controller.py**:
   - `process_files()` - Add validation before processing

### Testing Scenarios

1. Process button disabled when merge enabled without pairs
2. Error shown when attempting to process invalid merge state
3. Valid merge operations still work correctly
4. Single-file operations still work correctly
5. Backup state correct in all scenarios

## Version History

- v1.0.0 (2025-11-20): Initial data model for merge validation feature
