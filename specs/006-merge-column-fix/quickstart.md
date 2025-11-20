# Implementation Quickstart: Preserve All Columns When Merging Excel Files

**Feature**: Excel Column Preservation During Merge  
**Date**: 2025-11-20  
**Estimated Time**: 2-3 hours (implementation + testing)

## Prerequisites

- [x] Feature specification reviewed ([spec.md](spec.md))
- [x] Research completed ([research.md](research.md))
- [x] Data model understood ([data-model.md](data-model.md))
- [x] Working knowledge of pandas DataFrames and openpyxl
- [x] Branch `006-merge-column-fix` checked out

## Implementation Steps

### Step 1: Modify SaveStep to Enable Column Addition for Merges

**File**: `/home/chris/Code/aa-abstract-renumber/core/pipeline/steps/save_step.py`  
**Method**: `_save_excel_output()`  
**Line**: ~101

#### Current Code

```python
# Save Excel output with proper backup handling
add_missing_columns = context.options.get("check_document_images", False)
```

#### Modified Code

```python
# Save Excel output with proper backup handling
# Enable column preservation for merge workflows
add_missing_columns = (
    context.options.get("check_document_images", False) 
    or context.is_merge_workflow()
)
```

### Step 2: Update ExcelRepo to Handle All Columns

**File**: `/home/chris/Code/aa-abstract-renumber/adapters/excel_repo.py`  
**Method**: `_write_dataframe_to_workbook()`  
**Lines**: 94-117

#### Current Code

```python
# Handle new columns that should be added if missing (whitelist approach)
if add_missing_columns:
    # Define columns that are allowed to be added to Excel output
    ADDABLE_COLUMNS = {"Document_Found"}

    # Find whitelisted new columns that don't exist in template
    new_columns = [
        col
        for col in df.columns
        if col.strip().lower() not in header_to_col
        and col in ADDABLE_COLUMNS
    ]
```

#### Modified Code

```python
# Handle new columns that should be added if missing
if add_missing_columns:
    # Define system columns that should never be added to output
    SYSTEM_COLUMNS = {"_include", "_original_index", "Document_ID"}
    
    # Find all new columns that don't exist in template (excluding system columns)
    new_columns = [
        col
        for col in df.columns
        if col.strip().lower() not in header_to_col
        and col not in SYSTEM_COLUMNS
    ]
```

### Step 3: Add Column Name Normalization

**File**: `/home/chris/Code/aa-abstract-renumber/adapters/excel_repo.py`  
**Location**: Update the header map building logic around line 90

#### Current Code

```python
header_to_col = {
    h.lower(): idx + 1 for idx, h in enumerate(header_values) if h != ""
}
```

#### Modified Code

```python
# Normalize column names with whitespace handling
def normalize_name(name):
    return ' '.join(name.strip().lower().split())

header_to_col = {
    normalize_name(h): idx + 1 for idx, h in enumerate(header_values) if h != ""
}
```

Also update the column matching logic around line 133:

```python
col_idx = header_to_col.get(normalize_name(str(df_col)))
```

### Step 4: Create Unit Tests

**New File**: `/home/chris/Code/aa-abstract-renumber/tests/adapters/test_excel_repo_merge_columns.py`

```python
import pytest
import pandas as pd
from adapters.excel_repo import ExcelOpenpyxlRepo
import tempfile
from pathlib import Path

class TestExcelRepoMergeColumns:
    """Test column preservation during merge operations."""
    
    def test_preserve_extra_columns(self):
        """Test that new columns are added when add_missing_columns=True."""
        # Create a template with columns A, B, C
        template_df = pd.DataFrame({
            'A': [1, 2], 
            'B': [3, 4], 
            'C': [5, 6]
        })
        
        # Create data with additional column D
        data_df = pd.DataFrame({
            'A': [7, 8],
            'B': [9, 10], 
            'C': [11, 12],
            'D': [13, 14]
        })
        
        # Test implementation here
        # Assert column D appears in output
    
    def test_exclude_system_columns(self):
        """Test that system columns are not added to output."""
        # Test that _include, _original_index, Document_ID are excluded
        
    def test_case_insensitive_column_matching(self):
        """Test that column matching is case-insensitive."""
        # Test "Status" vs "status" produces single column
```

### Step 5: Create Integration Test

**New File**: `/home/chris/Code/aa-abstract-renumber/tests/integration/test_merge_column_preservation.py`

```python
import pytest
from core.services.renumber import RenumberService
from core.models import Options

class TestMergeColumnPreservation:
    """Integration tests for column preservation during merge."""
    
    def test_full_merge_workflow_preserves_columns(self):
        """Test complete merge workflow with different column structures."""
        # Set up test files with different columns
        # Run merge workflow
        # Verify all columns preserved in output
```

## Testing Checklist

- [ ] Unit test: Extra columns are preserved
- [ ] Unit test: System columns are excluded  
- [ ] Unit test: Case-insensitive matching works
- [ ] Unit test: Whitespace normalization works
- [ ] Integration test: Full merge workflow preserves columns
- [ ] Performance test: <5% impact on merge time
- [ ] Manual test: Merge real files with different columns

## Common Issues & Solutions

### Issue 1: Columns appear in wrong order
**Solution**: Ensure template columns are processed first, then new columns appended

### Issue 2: System columns appearing in output
**Solution**: Check SYSTEM_COLUMNS set includes all internal columns

### Issue 3: Duplicate columns with different cases
**Solution**: Verify normalize_name() is used consistently for all comparisons

## Rollback Plan

If issues arise:
1. Revert changes to `save_step.py` (remove `or context.is_merge_workflow()`)
2. Revert changes to `excel_repo.py` (restore ADDABLE_COLUMNS whitelist)
3. The changes are isolated and can be reverted independently

## Next Steps

After implementation:
1. Run all tests: `pytest tests/adapters/test_excel_repo_merge_columns.py -v`
2. Run integration tests: `pytest tests/integration/test_merge_column_preservation.py -v`
3. Test with real user data files
4. Update version in `_version.py` to reflect the bug fix
5. Update CHANGELOG.md with the fix details
