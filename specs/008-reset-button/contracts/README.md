# Contracts: Reset Button

**Feature**: Reset Button  
**Date**: 2025-11-20

## Status: No API Contracts Required

This feature does not introduce any new API contracts, protocols, or external interfaces.

**Rationale**:
- Pure GUI feature—operates on in-memory UI state only
- No data exchange between components
- No network communication
- No file format specifications
- Reuses existing `UIController` protocol methods (no changes needed)

## Existing Interfaces (Unchanged)

The Reset Button leverages existing protocol methods defined in `core/interfaces.py`:

### UIController Protocol

```python
def reset_gui(self) -> None:
    """Reset GUI to initial state after successful processing."""
```

**Usage**: Reset button calls this existing method through the adapter pattern.

**No modifications needed**: Method signature and behavior remain unchanged.

## Implementation Contract

**Internal Only** (not a public API):

### AbstractRenumberGUI._on_reset_clicked() → void

**Purpose**: Handle Reset button click event

**Preconditions**: None (button always enabled)

**Behavior**: Delegates to `reset_gui()` method

**Side Effects**: 
- Clears file selections
- Resets filter/merge state
- Clears status area (except last 3 lines)
- Disables Process button
- Logs "GUI reset - ready for new files!" message

**Error Handling**: No errors expected (pure memory operation)

## Testing Contract

See `tests/app/test_reset_button.py` for behavioral specifications.

**Key assertions**:
- Reset clears transient state
- Reset preserves preferences
- Reset button always enabled
- Reset is idempotent (safe to call multiple times)

