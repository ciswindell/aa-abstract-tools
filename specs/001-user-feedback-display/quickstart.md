# Quickstart: User Feedback Display

**Feature**: 001-user-feedback-display  
**Audience**: Developers working on Abstract Renumber Tool  
**Purpose**: Guide for using the enhanced status feedback system

## Overview

The enhanced status feedback system provides colored, typed messages to users during document processing operations. This guide shows how to use the system effectively in your code.

## Basic Usage

### Display Information Messages

Use for regular progress updates and status changes:

```python
# In any class that has access to UIController
self.ui.log_status("Loading files...")
self.ui.log_status("Processing document 5 of 42...")
self.ui.log_status("Saving results...")
```

### Display Error Messages

Use for failures that stop processing or require user action:

```python
# Simple error
self.ui.log_status("Cannot find the Excel file. Please select a valid file and try again.", MSG_ERROR)

# Error with context
self.ui.log_status(f"Invalid date format in row {row_num}. Expected YYYY-MM-DD.", MSG_ERROR)
```

### Display Success Messages

Use for successful operation completion:

```python
self.ui.log_status("Processing complete!", MSG_SUCCESS)
self.ui.log_status(f"Successfully processed {count} documents.", MSG_SUCCESS)
```

### Display Warning Messages

Use for non-fatal issues that users should be aware of:

```python
self.ui.log_status("Document image not found for page 5. Continuing without image check.", MSG_WARNING)
self.ui.log_status("Backup disabled - original files will be modified directly.", MSG_WARNING)
```

---

## Message Type Constants

Import from the core message types module:

```python
from core.message_types import MSG_INFO, MSG_ERROR, MSG_SUCCESS, MSG_WARNING
```

**Constants**:
- `MSG_INFO` - Black text (default) - Progress updates
- `MSG_ERROR` - Red bold text - Errors requiring user action  
- `MSG_SUCCESS` - Green bold text - Successful completion
- `MSG_WARNING` - Orange text - Non-fatal issues

---

## Best Practices

### 1. Write User-Friendly Messages

❌ **Don't write**:
```python
self.ui.log_status("IOError: [Errno 2] No such file or directory: 'data.xlsx'", MSG_ERROR)
```

✅ **Do write**:
```python
self.ui.log_status("Cannot find 'data.xlsx'. Please check the file path and try again.", MSG_ERROR)
```

### 2. Provide Context and Actions

❌ **Don't write**:
```python
self.ui.log_status("Error", MSG_ERROR)
```

✅ **Do write**:
```python
self.ui.log_status("Cannot process the Excel file. Please ensure the file is not corrupted and try again.", MSG_ERROR)
```

### 3. Show Progress for Long Operations

❌ **Don't write**:
```python
self.ui.log_status("Processing...")
# ... long operation with no updates ...
```

✅ **Do write**:
```python
self.ui.log_status(f"Processing document 1 of {total}...")
# ... process document 1 ...
self.ui.log_status(f"Processing document 2 of {total}...")
# ... process document 2 ...
```

### 4. Use Present Continuous for In-Progress

```python
# Good - shows ongoing action
self.ui.log_status("Loading files...")
self.ui.log_status("Validating data...")
self.ui.log_status("Saving results...")
```

### 5. Confirm Completion

```python
# Always provide clear completion message
self.ui.log_status("Processing complete!", MSG_SUCCESS)
```

---

## Operation Separation

When starting a new operation after a previous one, add a separator for clarity:

```python
# In AbstractRenumberGUI or similar
def start_new_operation(self):
    """Insert visual separator for new operation."""
    separator = "\n" + "="*50 + "\n"
    self.status_text.insert(tk.END, separator, "separator")
    self.ui.log_status("Starting new operation...", MSG_INFO)
```

Call this at the start of `process_files()` or similar entry points.

---

## Error Handling Pattern

### Converting Exceptions to User Messages

```python
def process_files(self):
    try:
        self.ui.log_status("Starting processing...", MSG_INFO)
        
        # ... processing logic ...
        
        self.ui.log_status("Processing complete!", MSG_SUCCESS)
        
    except FileNotFoundError as e:
        self.ui.log_status(
            f"Cannot find the file: {e.filename}. Please check the file path.",
            MSG_ERROR
        )
    except PermissionError:
        self.ui.log_status(
            "Cannot access the file. Please close it if it's open and try again.",
            MSG_ERROR
        )
    except Exception as e:
        # Fallback for unexpected errors
        self.ui.log_status(
            f"An unexpected error occurred: {str(e)}. Please check your files and try again.",
            MSG_ERROR
        )
```

### Using Error Simplification Helper

```python
from adapters.ui_tkinter import simplify_error

try:
    # ... processing logic ...
except Exception as e:
    user_message = simplify_error(e)
    self.ui.log_status(user_message, MSG_ERROR)
```

---

## Common Patterns

### Progress Counter

```python
def process_documents(self, documents):
    total = len(documents)
    for i, doc in enumerate(documents, start=1):
        self.ui.log_status(f"Processing document {i} of {total}...", MSG_INFO)
        # ... process document ...
    
    self.ui.log_status(f"Successfully processed {total} documents.", MSG_SUCCESS)
```

### Multi-Step Operation

```python
def multi_step_operation(self):
    # Step 1
    self.ui.log_status("Step 1: Loading data...", MSG_INFO)
    data = self.load_data()
    
    # Step 2
    self.ui.log_status("Step 2: Validating data...", MSG_INFO)
    self.validate_data(data)
    
    # Step 3
    self.ui.log_status("Step 3: Processing data...", MSG_INFO)
    result = self.process_data(data)
    
    # Done
    self.ui.log_status("All steps complete!", MSG_SUCCESS)
```

### Conditional Warnings

```python
def check_document_images(self, pages):
    missing_count = 0
    for page in pages:
        if not has_image(page):
            missing_count += 1
    
    if missing_count > 0:
        self.ui.log_status(
            f"Warning: {missing_count} pages are missing document images.",
            MSG_WARNING
        )
```

---

## Testing Your Messages

### Manual Testing Checklist

1. **Trigger each message type**: Ensure INFO, ERROR, SUCCESS, WARNING all display with correct colors
2. **Check auto-scroll**: Verify latest message is always visible
3. **Test long operations**: Confirm updates appear throughout long-running processes
4. **Test multiple operations**: Verify messages from different operations are distinguishable
5. **Test error scenarios**: Trigger various errors to check message clarity

### Unit Testing Message Logic

```python
def test_error_message_simplification():
    """Test that technical errors are converted to user-friendly messages."""
    from adapters.ui_tkinter import simplify_error
    
    # FileNotFoundError
    error = FileNotFoundError("data.xlsx")
    message = simplify_error(error)
    assert "Cannot find the file" in message
    assert "technical" not in message.lower()
    
    # PermissionError
    error = PermissionError("Access denied")
    message = simplify_error(error)
    assert "Cannot access" in message
    assert "permissions" in message.lower()
```

---

## Architecture Notes

### Where Messages Flow

```
Pipeline Step or Service
  ↓ (calls)
UIController.log_status(message, type)
  ↓ (implemented by)
TkinterUIAdapter.log_status(message, type)
  ↓ (calls)
AbstractRenumberGUI.log_status(message, type)
  ↓ (inserts to)
status_text (tk.Text widget with tags)
```

### Protocol Compliance

The `UIController` protocol defines:
```python
def log_status(self, message: str) -> None:
    """Log a status message to the UI."""
```

Enhancement adds optional parameter (backward compatible):
```python
def log_status(self, message: str, msg_type: str = MSG_INFO) -> None:
    """Log a status message to the UI with specified type."""
```

---

## Troubleshooting

### Messages Not Appearing

**Problem**: Status messages don't show up in the GUI

**Solution**: Ensure you're calling `self.root.update()` after insert to force UI refresh:
```python
self.status_text.insert(tk.END, f"{message}\n", msg_type)
self.status_text.see(tk.END)
self.root.update()  # Force immediate display
```

### Colors Not Showing

**Problem**: All messages appear in default black text

**Solution**: Verify tags are configured in `setup_gui()`:
```python
self.status_text.tag_config(MSG_ERROR, foreground="#d32f2f", font=("Arial", 9, "bold"))
self.status_text.tag_config(MSG_SUCCESS, foreground="#388e3c", font=("Arial", 9, "bold"))
self.status_text.tag_config(MSG_WARNING, foreground="#f57c00")
```

### Auto-Scroll Not Working

**Problem**: Latest messages scroll off screen

**Solution**: Call `see(tk.END)` after each insert:
```python
self.status_text.insert(tk.END, message, tag)
self.status_text.see(tk.END)  # Scroll to bottom
```

---

## Migration Guide

### Updating Existing Code

**Before** (still works):
```python
self.ui.log_status("Loading files...")
```

**After** (enhanced):
```python
self.ui.log_status("Loading files...", MSG_INFO)
self.ui.log_status("Cannot find file!", MSG_ERROR)
self.ui.log_status("Complete!", MSG_SUCCESS)
```

**Migration Strategy**: 
1. All existing `log_status()` calls work without changes (default to MSG_INFO)
2. Add message types gradually, starting with errors (highest user impact)
3. Then add success messages
4. Finally add warnings and explicit info types

---

## Examples from Codebase

### Pipeline Steps

```python
class LoadStep(PipelineStep):
    def execute(self, ctx: PipelineContext) -> PipelineContext:
        self.logger.info("Loading Excel and PDF files...")  # Adapter converts to log_status
        
        # ... loading logic ...
        
        self.logger.info(f"Loaded {len(ctx.df)} records from Excel")
        return ctx
```

### Controller

```python
class AppController:
    def process_files(self):
        try:
            self.ui.log_status("Starting processing...", MSG_INFO)
            
            # Run pipeline
            result = self.pipeline.run(context)
            
            self.ui.show_success("Processing complete!")  # Shows message box + status
            
        except Exception as e:
            error_msg = simplify_error(e)
            self.ui.show_error("Processing Error", error_msg)  # Shows error box + status
```

---

## Reference

- **Spec**: [spec.md](./spec.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Contracts**: [contracts/README.md](./contracts/README.md)

For implementation tasks, see: [tasks.md](./tasks.md) (generated by `/speckit.tasks`)

