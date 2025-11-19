# API Contracts: Reduce Excessive Info Logging

**Feature**: 003-reduce-info-logging  
**Date**: 2025-11-19  
**Approach**: No API changes - just delete logging calls

## Summary

**No protocol updates needed** - this feature just deletes logging calls.

The Logger protocol stays unchanged:
```python
class Logger(Protocol):
    def info(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...
```

The PipelineContext gets two new attributes (not a protocol change):
```python
context.step_number: int = 0
context.total_steps: int = 0
```

---

## What Changes

### PipelineContext (Data Class)

**Add two attributes** for step counter:

```python
@dataclass
class PipelineContext:
    # ... existing attributes ...
    step_number: int = 0      # Injected by pipeline executor
    total_steps: int = 0      # Injected by pipeline executor
```

**Why**: Steps need to know current position for "Step X of Y" format

**Backward Compatible**: Yes - new attributes with defaults, existing code unaffected

---

### Pipeline Executor (Function)

**Update** to inject step counter:

```python
def execute_pipeline(steps: list[PipelineStep], context: PipelineContext) -> None:
    """Execute pipeline steps with progress tracking."""
    # Count non-skipped steps
    non_skipped = [s for s in steps if not s.should_skip(context)]
    context.total_steps = len(non_skipped)
    
    # Execute with step counter
    context.step_number = 0
    for step in steps:
        if step.should_skip(context):
            continue
        context.step_number += 1
        step.execute(context)
```

**Change**: Adds step counting logic, no signature change

**Backward Compatible**: Yes - context is mutable, steps can ignore new attributes

---

### Pipeline Steps (Classes)

**Change**: Delete 10-20 log calls, keep 1 at start

**Before**:
```python
def execute(self, context: PipelineContext) -> None:
    self.logger.info("Executing step 1/7: ValidateStep")
    self.logger.info("Validating input files before loading")
    # ... 10+ more log calls ...
    
    # ... business logic ...
```

**After**:
```python
def execute(self, context: PipelineContext) -> None:
    self.logger.info(f"Step {context.step_number} of {context.total_steps}: Validating files...")
    
    # ... business logic (unchanged) ...
```

**Signature**: No change  
**Backward Compatible**: Yes - only internal logging changed

---

## What Doesn't Change

### Logger Protocol

**Stays the same** - no new methods or parameters:
```python
class Logger(Protocol):
    def info(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...
```

No ui_visible parameter, no debug() method, no complexity.

---

### UIController Protocol

**Stays the same** - no changes needed:
```python
class UIController(Protocol):
    def log_status(self, message: str, msg_type: str = MSG_INFO) -> None: ...
    def start_new_operation(self) -> None: ...
    # ... other methods ...
```

---

### TkinterLogger Implementation

**Stays the same** - no filtering logic needed:
```python
class TkinterLogger(Logger):
    def info(self, message: str) -> None:
        print(f"INFO: {message}")
        if hasattr(self.gui, 'log_status'):
            self.gui.log_status(message, MSG_INFO)
    
    def error(self, message: str) -> None:
        print(f"ERROR: {message}")
        if hasattr(self.gui, 'log_status'):
            self.gui.log_status(f"ERROR: {message}", MSG_ERROR)
```

No ui_visible parameter, no auto-detection, no complexity.

---

## Testing Contract

### Manual Testing

**Test**: Run full pipeline with real files

**Verify**:
- UI shows 8-10 messages (not 80+)
- All messages show "Step X of Y" format
- Phase names are user-friendly
- ERROR/WARNING/SUCCESS unchanged

**Time**: 5 minutes

---

### Integration Testing (Optional)

```python
def test_reduced_logging():
    """Verify UI shows ~10 messages instead of 80+."""
    ui_mock = Mock()
    # Setup and run pipeline
    process_files()
    # Count messages
    message_count = ui_mock.log_status.call_count
    # Verify reduction
    assert message_count <= 15, f"Too many messages: {message_count}"
```

**Purpose**: Catch accidental re-addition of verbose logging

---

## Migration Strategy

**No migration needed** - just delete code.

**Steps**:
1. Add `step_number` and `total_steps` to PipelineContext
2. Update pipeline executor to inject step counter
3. Delete verbose log calls from each pipeline step
4. Keep one log call per step with step counter
5. Test manually

**Backward Compatibility**: 100% - no breaking changes

---

## API Version

**Current**: 1.0.0  
**After Feature**: 1.0.0 (no version bump needed - internal changes only)

**Breaking Changes**: None  
**Deprecations**: None  
**New APIs**: None (just new attributes on existing data class)

---

## Summary

This feature has **zero API impact**:
- No new protocols
- No new methods
- No new parameters
- No new abstractions

Just:
- Add two attributes to existing data class
- Delete logging calls
- Rewrite a few keepers

**Result**: Simpler code, fewer lines, no complexity.
