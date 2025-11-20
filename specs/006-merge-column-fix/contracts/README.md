# API Contracts: Preserve All Columns When Merging Excel Files

**Feature**: Excel Column Preservation During Merge  
**Date**: 2025-11-20  
**Version**: 1.0.0

## Overview

This feature modifies existing internal APIs rather than creating new external APIs. The contracts defined here represent the enhanced behavior of existing methods.

## Modified Contracts

### 1. ExcelRepo.save()

**Enhanced Contract**: Now supports dynamic column addition for merge workflows

```python
def save(
    self,
    df: pd.DataFrame,
    template_path: str,
    target_sheet: str,
    out_path: str,
    add_missing_columns: bool = False,
) -> None:
    """
    Save DataFrame to Excel file using template, with optional column addition.
    
    Args:
        df: DataFrame to save (may contain columns not in template)
        template_path: Path to Excel template file
        target_sheet: Name of sheet to write data to
        out_path: Output file path
        add_missing_columns: If True, adds columns from df that don't exist in template
        
    Behavior:
        - When add_missing_columns=True:
          - All user data columns from df are preserved
          - System columns (starting with _ or Document_ID) are excluded
          - New columns are appended after template columns
          - Column matching is case-insensitive with whitespace normalization
        - When add_missing_columns=False:
          - Only writes columns that exist in template (current behavior)
    
    Raises:
        RuntimeError: If target sheet not found in template
        Exception: If save operation fails
    """
```

### 2. SaveStep Integration

**Enhanced Behavior**: Automatically enables column preservation for merge workflows

```python
# Pseudo-contract for SaveStep behavior
class SaveStep:
    def execute(self, context: PipelineContext) -> None:
        """
        Save step with automatic column preservation for merges.
        
        Behavior:
            - Detects merge workflow via context.is_merge_workflow()
            - Sets add_missing_columns=True for merge workflows
            - Sets add_missing_columns based on check_document_images option for single files
        """
        add_missing_columns = (
            context.options.get("check_document_images", False) 
            or context.is_merge_workflow()
        )
```

## Column Matching Rules

### Normalization Contract

```python
def normalize_column_name(name: str) -> str:
    """
    Normalize column name for matching.
    
    Args:
        name: Raw column name
        
    Returns:
        Normalized name (lowercase, trimmed, collapsed spaces)
        
    Example:
        " Status  " -> "status"
        "Date Created" -> "date created"
        "INDEX#" -> "index#"
    """
    return ' '.join(name.strip().lower().split())
```

### System Column Detection

```python
def is_system_column(name: str) -> bool:
    """
    Determine if a column is an internal system column.
    
    Args:
        name: Column name to check
        
    Returns:
        True if column should be excluded from user output
        
    System columns:
        - Any column starting with underscore (_include, _original_index)
        - Document_ID (used internally for tracking)
    """
    return name.startswith('_') or name == 'Document_ID'
```

## Error Handling

### Column Limit Exceeded

```python
class ColumnLimitExceeded(ValueError):
    """Raised when merged output would exceed Excel column limit."""
    
    def __init__(self, total_columns: int, limit: int = 16384):
        super().__init__(
            f"Merged file would have {total_columns} columns, "
            f"exceeding Excel limit of {limit}"
        )
```

### Type Conflict Resolution

When the same column contains different data types across files:

1. Numeric types (int, float) → float
2. Date/datetime types → datetime
3. Mixed types → object (string)
4. Null/empty → preserve target type

## Testing Contracts

### Test Scenarios

```python
# Test 1: Basic merge with extra columns
def test_merge_preserves_extra_columns():
    """
    Given: File1 has columns [A, B, C], File2 has columns [A, B, C, D]
    When: Files are merged
    Then: Output has columns [A, B, C, D] with all data preserved
    """

# Test 2: System column exclusion
def test_merge_excludes_system_columns():
    """
    Given: File has columns [A, B, _include, Document_ID]
    When: File is saved with add_missing_columns=True
    Then: Output has only columns [A, B]
    """

# Test 3: Case-insensitive matching
def test_column_matching_case_insensitive():
    """
    Given: File1 has "Status", File2 has "status"
    When: Files are merged
    Then: Output has single "Status" column with combined data
    """
```

## Version Compatibility

- **Backward Compatible**: Existing single-file workflows unchanged
- **Forward Compatible**: New column preservation only activates for merge workflows
- **Migration**: No data migration required

## Performance Guarantees

- Column detection: O(n) where n = number of columns
- Memory overhead: Negligible (column headers only)
- Processing time: <5% increase over current merge time
