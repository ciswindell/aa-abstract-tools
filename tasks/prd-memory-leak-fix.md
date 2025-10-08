# PRD: Memory Leak Fix for Streamlit PDF Processing App

## Introduction/Overview

The Streamlit PDF processing application currently experiences critical memory leaks that cause the app to crash on the second processing run. The first run consumes 75% of available 4GB memory on Digital Ocean App Platform, and the second run crashes due to memory exhaustion. This PRD addresses simple, direct fixes to eliminate memory leaks without adding unnecessary complexity.

The core problem is three simple issues: (1) temporary files use `delete=False` and are never cleaned up, (2) large PDF objects and DataFrames remain in session state after processing, and (3) no garbage collection is triggered to free memory.

## Goals

1. **Eliminate Memory Crashes**: Ensure the app never crashes due to out-of-memory conditions during normal operation
2. **Enable Multiple Consecutive Runs**: Support unlimited consecutive processing runs without memory accumulation
3. **Maintain Processing Pipeline Integrity**: Fix memory leaks without altering or interfering with the core processing pipeline
4. **Preserve User Experience**: Keep all cleanup operations transparent to users with no performance degradation
5. **Support Concurrent Users**: Ensure cleanup operations are isolated per user session in production environment

## User Stories

1. **As a user**, I want to process multiple PDF files consecutively without the app crashing, so that I can complete my work efficiently without restarting the application.

2. **As a user**, I want the app to handle large PDF files (up to 400MB) reliably across multiple processing runs, so that I don't have to worry about file size limitations affecting app stability.

3. **As a user**, I want to switch between single-file and multi-file processing modes multiple times without experiencing performance degradation or crashes.

4. **As a user**, I want the existing "🔄 Process New Files" button to work seamlessly without any visible changes while automatically cleaning up memory behind the scenes.

5. **As a user**, I want to download my processed files and then start new processing without any additional steps or interactions required.

6. **As a system administrator**, I want the app to run stably in production with multiple concurrent users without memory-related failures.

7. **As a developer**, I want comprehensive logging of cleanup operations for debugging purposes without exposing technical details to end users.

## Functional Requirements

### Simple Memory Fixes
1. **Fix Temporary File Creation**: Change `tempfile.NamedTemporaryFile(delete=False)` to `delete=True` to enable automatic cleanup when files are no longer referenced.

2. **Clear Large Session State Objects**: Add deletion of large objects (PDF writers, DataFrames, cached data) from session state when the user clicks "🔄 Process New Files" button.

3. **Add Garbage Collection**: Trigger Python's `gc.collect()` after processing completes to ensure memory is actually freed.

4. **Clear Preview Cache**: Delete cached preview data (merged DataFrames) from session state in multi-file workflows when user resets.

### User Interface Preservation
5. **Silent Operation**: All cleanup operations must be completely transparent to users with no visible interface changes.

6. **Existing Button Behavior**: The existing "🔄 Process New Files" button must work exactly the same from the user's perspective while including cleanup behind the scenes.

### Error Handling
7. **Graceful Cleanup Failures**: Use try/except blocks around cleanup operations so cleanup failures don't break the app.

8. **Console Logging**: Log cleanup operations to console for debugging (no user-visible messages).

## Non-Goals (Out of Scope)

1. **Processing Pipeline Modifications**: This fix will NOT modify the core processing pipeline logic, steps, or data flow.

2. **Performance Optimization**: This is NOT a performance optimization project - no changes that could impact processing speed.

3. **File Size Limits**: Will NOT implement new file size restrictions or memory-aware upload limits.

4. **User Interface Changes**: Will NOT make ANY visible changes to the user interface.

5. **Complex Cleanup Systems**: Will NOT implement complex file tracking, lifecycle management, or multi-phase cleanup strategies.

6. **Download Detection**: Will NOT attempt to detect when users complete file downloads.

7. **Memory Usage Monitoring**: Will NOT add memory usage displays or monitoring systems.

8. **Processing Algorithm Changes**: Will NOT modify PDF processing, Excel handling, or document merging algorithms.

## Technical Considerations

### Architecture Constraints
- **Digital Ocean App Platform**: Must work within platform constraints and temporary file system limitations
- **Streamlit Framework**: Must work with Streamlit's session state and file handling mechanisms
- **Multi-User Environment**: Must handle concurrent user sessions safely

### Implementation Approach
- **Simple Direct Fixes**: Change `delete=False` to `delete=True` in temporary file creation
- **Session State Cleanup**: Add `del st.session_state[key]` for large objects in reset methods
- **Garbage Collection**: Add single `gc.collect()` call after processing completes
- **Error Handling**: Wrap cleanup operations in try/except blocks
- **Silent Operation**: All changes work behind the scenes with no user-visible modifications

### Dependencies
- **Standard Library Only**: Will use only `gc` module and existing components
- **No New Dependencies**: No additional packages required
- **Backward Compatibility**: Must not break existing functionality

## Success Metrics

### Primary Success Criteria
1. **Zero Memory Crashes**: App must handle 10+ consecutive processing runs without crashing
2. **Memory Stability**: Memory usage should not accumulate across runs
3. **User Experience Preservation**: Existing user workflow must remain completely unchanged
4. **Download Functionality**: File downloads must work exactly as before

### Secondary Success Criteria  
5. **Error Resilience**: App must continue functioning even if cleanup operations fail
6. **Console Logging**: Cleanup operations logged for debugging

## Testing Strategy

### Simple Testing Approach
1. **Before/After Memory Check**: Monitor memory usage for consecutive processing runs
2. **Download Functionality**: Verify downloads still work after changes  
3. **Reset Button**: Confirm reset works without changing user experience

### Test Scenarios
- Process same files 3-5 times, verify no memory accumulation
- Test with large files to verify cleanup under memory pressure
- Verify reset button clears session state properly

### Validation Criteria
- Memory usage should not grow significantly across runs
- All existing functionality continues to work
- No visible changes to user interface

## Implementation Plan

**Estimated Duration**: 1-2 hours

### Simple Implementation Steps
1. Change `delete=False` to `delete=True` in file upload methods
2. Add session state cleanup to reset methods  
3. Add `gc.collect()` after processing
4. Add try/except around cleanup operations
5. Test with consecutive runs

## Open Questions

1. **Error Recovery**: If cleanup fails, should we retry or just log the failure?

2. **Testing Integration**: Should we add memory testing to the existing test suite?
