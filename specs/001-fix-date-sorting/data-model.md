# Data Model: Date Column Transformation

**Feature**: Fix Date Column Processing for Chronological Sorting  
**Date**: 2025-11-19

## Overview

This document describes the data transformation that occurs when date columns are parsed during Excel file loading. The transformation converts text-formatted date values to proper datetime objects, enabling correct chronological sorting.

## Entity: Date Column

**Definition**: Any DataFrame column with a name containing "date" (case-insensitive match)

**Examples**:
- "Document Date"
- "Received Date"
- "Date"
- "date_modified"
- "DATE_CREATED"

**Detection Rule**:
```python
is_date_column = "date" in column_name.lower()
```

## Data Type Transformation

### Before Transformation (Current State)

**Source**: Excel file with text-formatted date cells

```python
# DataFrame after pd.read_excel()
columns: ["Index#", "Document Date", "Received Date", "Grantee"]
dtypes: {
    "Index#": object,           # Already converted to string
    "Document Date": object,     # ❌ Text string (should be datetime)
    "Received Date": object,     # ❌ Text string (should be datetime)
    "Grantee": object            # Text (correct)
}

# Sample values
"Document Date": ["1/5/2024", "12/25/2023", "3/15/2024"]
"Received Date": ["1/10/2024", "12/30/2023", "3/20/2024"]
```

**Problem**: When sorted, these text values use lexicographic ordering:
- "1/10/2024" < "1/5/2024" < "12/25/2023" < "12/30/2023" < "3/15/2024" (WRONG!)

### After Transformation (Target State)

**Result**: DataFrame with parsed datetime columns

```python
# DataFrame after parse_robust() applied
dtypes: {
    "Index#": object,                    # Unchanged (correct)
    "Document Date": datetime64[ns],     # ✅ Converted to datetime
    "Received Date": datetime64[ns],     # ✅ Converted to datetime
    "Grantee": object                    # Unchanged (correct)
}

# Sample values (pandas Timestamp objects)
"Document Date": [
    Timestamp('2024-01-05 00:00:00'),    # 1/5/2024
    Timestamp('2023-12-25 00:00:00'),    # 12/25/2023
    Timestamp('2024-03-15 00:00:00')     # 3/15/2024
]

"Received Date": [
    Timestamp('2024-01-10 00:00:00'),
    Timestamp('2023-12-30 00:00:00'),
    Timestamp('2024-03-20 00:00:00')
]
```

**Benefit**: When sorted, datetime values use chronological ordering:
- 2023-12-25 < 2023-12-30 < 2024-01-05 < 2024-01-10 < 2024-03-15 (CORRECT!)

## Transformation Logic

### Cell-Level Transformation

```python
def parse_robust(value: Any) -> Any:
    """Transform a single cell value from text → datetime if possible."""
    
    # Case 1: Already datetime → return unchanged
    if isinstance(value, (datetime, pd.Timestamp)):
        return value
    
    # Case 2: Null/empty → preserve as-is
    if value is None or pd.isna(value):
        return value
    
    # Case 3: Text → attempt parsing
    text = str(value).strip()
    
    # Try pandas parser (fast, handles most formats)
    try:
        return pd.to_datetime(text)
    except:
        pass
    
    # Try common format patterns
    for fmt in ["%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", ...]:
        try:
            return pd.Timestamp(datetime.strptime(text, fmt))
        except:
            continue
    
    # Try dateutil parser (flexible fallback)
    try:
        return pd.Timestamp(dateutil_parse(text))
    except:
        pass
    
    # Case 4: Unparseable → preserve original value
    return value
```

### Column-Level Application

```python
# Apply to each date column in DataFrame
for col in df.columns:
    if "date" in col.lower():
        df[col] = df[col].apply(parse_robust)
```

## State Transitions

### State Diagram

```
┌─────────────────┐
│   Excel Cell    │
│  (Text Format)  │
└────────┬────────┘
         │
         │ pd.read_excel()
         ▼
┌─────────────────┐
│  DataFrame Cell │
│  dtype: object  │
│  value: "1/5/24"│
└────────┬────────┘
         │
         │ parse_robust()
         ▼
    ┌────────────────────┐
    │  Is text parseable │
    │     as date?       │
    └────┬──────────┬────┘
         │ Yes      │ No
         ▼          ▼
┌────────────┐  ┌─────────────┐
│ Timestamp  │  │  Original   │
│ object     │  │  value      │
│ (datetime64│  │  preserved  │
│  [ns])     │  │  (object)   │
└────────────┘  └─────────────┘
```

### Supported Format Examples

| Input (Text) | Parsed As | Notes |
|-------------|-----------|-------|
| "1/5/2024" | 2024-01-05 | U.S. format (M/D/Y) |
| "01/05/2024" | 2024-01-05 | Leading zeros optional |
| "1-5-2024" | 2024-01-05 | Hyphen separator |
| "2024-01-05" | 2024-01-05 | ISO format |
| "January 5, 2024" | 2024-01-05 | Full text |
| "Jan 5, 2024" | 2024-01-05 | Abbreviated month |
| "" (empty) | NaN | Preserved as null |
| "N/A" | "N/A" | Preserved as text |
| "TBD" | "TBD" | Preserved as text |

## Validation Rules

### Input Validation
- **No validation on input**: Accept any value, attempt parsing, preserve on failure
- **Rationale**: User data integrity is paramount; no data should be rejected or lost

### Output Guarantees
1. **Type Safety**: Date columns contain either `datetime64[ns]` or `object` dtype values
2. **Data Preservation**: Unparseable values remain unchanged (no loss)
3. **Null Handling**: Empty cells remain empty (NaN preserved)
4. **Backward Compatibility**: Already-datetime values pass through unchanged

### Business Rules
- **Sorting**: Date columns MUST sort chronologically (primary requirement)
- **Display**: Date columns SHOULD display in M/D/YYYY format (handled by FormatExcelStep)
- **Range**: No date range restrictions (accept dates from 1800s to 2100s+)

## Relationships

### DataFrame Schema Evolution

```
INPUT SCHEMA (from Excel)
┌──────────────────────────────────────────┐
│ DataFrame                                │
├──────────────┬───────────────────────────┤
│ Column       │ dtype                     │
├──────────────┼───────────────────────────┤
│ Index#       │ object (string)           │
│ Document Type│ object (string)           │
│ Legal Desc   │ object (string)           │
│ Grantee      │ object (string)           │
│ Grantor      │ object (string)           │
│ Document Date│ object (text string) ❌   │
│ Received Date│ object (text string) ❌   │
└──────────────┴───────────────────────────┘

OUTPUT SCHEMA (after transformation)
┌──────────────────────────────────────────┐
│ DataFrame                                │
├──────────────┬───────────────────────────┤
│ Column       │ dtype                     │
├──────────────┼───────────────────────────┤
│ Index#       │ object (string)           │
│ Document Type│ object (string)           │
│ Legal Desc   │ object (string)           │
│ Grantee      │ object (string)           │
│ Grantor      │ object (string)           │
│ Document Date│ datetime64[ns] ✅         │
│ Received Date│ datetime64[ns] ✅         │
└──────────────┴───────────────────────────┘
```

### Pipeline Data Flow

```
┌──────────────┐
│ Excel File   │
│ (User Upload)│
└──────┬───────┘
       │
       │ ExcelRepo.load() ← TRANSFORMATION POINT
       ▼
┌──────────────────┐
│ DataFrame        │
│ (datetime cols)  │
└──────┬───────────┘
       │
       │ Pipeline Steps
       ▼
┌──────────────────┐
│ LoadStep         │ Creates DocumentUnits
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ ValidateStep     │ Checks required columns
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ FilterDfStep     │ Optional filtering
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ SortDfStep       │ ✅ Chronological sort works correctly
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ SaveStep         │ Writes DataFrame to Excel
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ FormatExcelStep  │ ✅ Date formatting applies correctly
└──────────────────┘
```

## Edge Cases & Error Handling

### Edge Case Matrix

| Scenario | Input | Output | Behavior |
|----------|-------|--------|----------|
| Empty cell | `NaN` | `NaN` | Preserved |
| Null string | `""` | `NaN` | Converted to null |
| Text literal | `"N/A"` | `"N/A"` | Preserved |
| Invalid format | `"Not a date"` | `"Not a date"` | Preserved |
| Ambiguous date | `"01/02/2024"` | `2024-01-02` | Parsed as M/D/Y (pandas default) |
| Mixed types | Column with dates + text | Mixed: datetime + text | Both types coexist |
| Already datetime | `Timestamp('2024-01-05')` | `Timestamp('2024-01-05')` | Pass-through |
| Excel serial | `44927` (text) | `44927` (preserved) | Not a date string format |
| Future date | `"12/31/2099"` | `2099-12-31` | Accepted |
| Historical date | `"1/1/1800"` | `1800-01-01` | Accepted |

### Error Handling Strategy

**No Exceptions Raised**: The `parse_robust()` function never raises exceptions
- All parsing failures return the original value
- DataFrame structure remains intact
- Processing continues normally

**Rationale**: Data integrity over strict validation - preserve user data at all costs

## Performance Characteristics

### Time Complexity
- **Per-cell parsing**: O(1) amortized (with format caching)
- **Per-column transformation**: O(n) where n = number of rows
- **Total overhead**: O(n × d) where d = number of date columns (typically 2)

### Space Complexity
- **Before**: ~80 bytes per text cell (Python object overhead)
- **After**: 8 bytes per datetime cell
- **Memory savings**: ~90% reduction for date columns

### Benchmark Estimates
- 10K rows, 2 date columns: ~20ms
- 50K rows, 2 date columns: ~100ms  
- 100K rows, 2 date columns: ~200ms

## Testing Considerations

### Test Data Requirements

```python
# Test DataFrame with various date formats
test_data = {
    "Index#": ["1", "2", "3", "4", "5"],
    "Document Date": [
        "1/5/2024",          # Standard M/D/Y
        "12/25/2023",        # Test alphabetical vs chronological
        "2024-03-15",        # ISO format
        "",                  # Empty cell
        "N/A"                # Unparseable text
    ],
    "Received Date": [
        "January 10, 2024",  # Full text
        "Dec 30, 2023",      # Abbreviated
        None,                # Null value
        "01-05-2024",        # Hyphen separator
        "Invalid"            # Should be preserved
    ]
}
```

### Validation Assertions

```python
# After transformation
assert df["Document Date"].dtype == "datetime64[ns]"
assert pd.isna(df["Document Date"].iloc[3])  # Empty → NaN
assert df["Document Date"].iloc[4] == "N/A"  # Preserved

# Sorting works correctly
sorted_df = df.sort_values("Document Date")
assert sorted_df["Document Date"].iloc[0] == pd.Timestamp("2023-12-25")
assert sorted_df["Document Date"].iloc[1] == pd.Timestamp("2024-01-05")
```

## Summary

The date column transformation is a **single-point data type normalization** that:
1. Converts text-formatted dates → datetime objects at the data boundary
2. Preserves data integrity for unparseable values
3. Enables correct chronological sorting throughout the pipeline
4. Fixes date formatting display issues as a side benefit
5. Reduces memory usage by ~90% for date columns
6. Maintains backward compatibility with existing workflows

**Critical Success Factors**:
- ✅ No data loss (unparseable values preserved)
- ✅ Automatic detection (no configuration needed)
- ✅ Performance acceptable (<1% overhead)
- ✅ Clean architecture (transformation at boundary layer)

