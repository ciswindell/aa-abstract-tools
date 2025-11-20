# Data Model: Preserve All Columns When Merging Excel Files

**Feature**: Excel Column Preservation During Merge  
**Date**: 2025-11-20  
**Version**: 1.0.0

## Overview

This document describes the data structures and relationships involved in preserving all columns when merging Excel files. The core challenge is dynamically handling varying column structures across multiple source files.

## Core Entities

### 1. Excel Column

**Purpose**: Represents a data field that may exist in one or more source files

**Attributes**:
- `name`: string - The column header text
- `normalized_name`: string - Lowercase, whitespace-trimmed version for matching
- `source_file`: string - Path to the file this column originated from
- `data_type`: type - The pandas dtype of the column
- `is_system_column`: boolean - Whether this is an internal column

**Validation Rules**:
- Column names must be non-empty after whitespace trimming
- System columns are identified by prefix ("_") or specific names ("Document_ID")
- Normalized names are used for equality comparison

**Example**:
```python
{
    "name": "Status",
    "normalized_name": "status",
    "source_file": "/path/to/file2.xlsx",
    "data_type": "object",
    "is_system_column": False
}
```

### 2. Column Mapping

**Purpose**: Tracks which columns from source files map to which columns in the merged output

**Attributes**:
- `source_columns`: List[Excel Column] - All unique columns from all source files
- `output_columns`: List[string] - Ordered list of column names in merged output
- `column_index_map`: Dict[string, int] - Maps normalized column names to output positions

**Relationships**:
- One Column Mapping per merge operation
- Contains multiple Excel Columns (1:many)

**Validation Rules**:
- No duplicate normalized column names in output
- Template columns appear first in output order
- System columns excluded from output

**State Transitions**:
1. Initialize with template columns
2. Add columns from each additional file
3. Finalize with complete column set

### 3. Template Structure

**Purpose**: The column structure from the primary Excel file that serves as the base for formatting

**Attributes**:
- `template_path`: string - Path to the template Excel file
- `template_columns`: List[string] - Ordered list of columns in template
- `column_formats`: Dict[string, Format] - Excel formatting per column

**Validation Rules**:
- Template must have at least one column
- Template columns maintain their original order
- Formatting is preserved for template columns only

## Data Flow

### Merge Process Flow

```
1. Load Template Structure
   └─> Extract column headers and formatting

2. Process Each Source File
   ├─> Load DataFrame
   ├─> Identify new columns not in template
   └─> Add to Column Mapping

3. Build Merged DataFrame
   ├─> Create output with all columns
   ├─> Fill data from each source
   └─> Empty cells for missing columns

4. Save with Dynamic Columns
   ├─> Apply template formatting
   ├─> Add new column headers
   └─> Write all data
```

### Column Detection Algorithm

```python
def detect_new_columns(df: DataFrame, existing: Set[str]) -> List[str]:
    """
    Identify columns in df that don't exist in the existing set.
    
    Args:
        df: Source DataFrame
        existing: Set of normalized column names already in output
    
    Returns:
        List of new column names to add
    """
    new_columns = []
    for col in df.columns:
        normalized = col.strip().lower()
        if normalized not in existing and not is_system_column(col):
            new_columns.append(col)
    return new_columns
```

## Constraints

### Business Rules

1. **Column Uniqueness**: Each column name (normalized) appears only once in output
2. **Data Preservation**: All non-system data must be preserved
3. **Order Preservation**: Template column order is maintained
4. **Format Preservation**: Template formatting applies only to template columns

### Technical Constraints

1. **Memory**: All DataFrames must fit in memory simultaneously during merge
2. **Column Limit**: Excel has a maximum of 16,384 columns (XFD)
3. **Performance**: Column processing must not exceed 5% of total merge time

## Edge Cases

### Handled Scenarios

1. **Empty Columns**: Preserved to maintain structure
2. **Whitespace Variations**: Normalized for matching
3. **Case Differences**: Treated as same column (case-insensitive)
4. **Type Conflicts**: Auto-detected best common type
5. **System Columns**: Automatically excluded from output

### Error Conditions

1. **Column Limit Exceeded**: Fail with clear error message
2. **Invalid Column Names**: Skip columns with empty normalized names
3. **Memory Exhaustion**: Fail gracefully with cleanup

## Implementation Notes

### Key Methods to Modify

1. **SaveStep.execute()**: Add merge workflow detection
2. **ExcelRepo._write_dataframe_to_workbook()**: Remove whitelist restriction
3. **Column name normalization**: Add whitespace handling

### Testing Scenarios

1. Basic two-file merge with extra columns
2. Multi-file merge with varied columns
3. Columns with whitespace/case variations
4. System column exclusion
5. Performance benchmarks

## Version History

- v1.0.0 (2025-11-20): Initial data model for column preservation feature
