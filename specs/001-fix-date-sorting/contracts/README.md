# API Contracts

**Feature**: Fix Date Column Processing for Chronological Sorting  
**Date**: 2025-11-19

## No External Contracts

This feature does not require API contracts because:

1. **Internal Change Only**: The modification is to internal data processing logic in `adapters/excel_repo.py`

2. **No Interface Changes**: The `ExcelRepo.load()` method signature remains unchanged:
   ```python
   def load(self, path: str, sheet: Optional[str]) -> pd.DataFrame
   ```
   - Input parameters: same
   - Return type: same (pd.DataFrame)
   - Only internal behavior enhanced (date parsing)

3. **No New APIs**: No new methods, endpoints, or interfaces are created

4. **No External Integrations**: No communication with external systems or services

## Internal Contract (Informal)

While there are no formal API contracts, the internal behavior contract is:

### ExcelRepo.load() Behavior Contract

**Input**: Excel file path and optional sheet name

**Output**: pandas DataFrame with:
- All columns from Excel sheet
- Index# column converted to string dtype
- Date columns (name contains "date") converted to datetime64 dtype when possible
- Other columns preserved as loaded by pandas

**Guarantees**:
1. No data loss: Unparseable values preserved in original form
2. Backward compatible: Files with proper Excel dates work unchanged
3. Null handling: Empty cells and None values preserved as NaN
4. Performance: < 1% overhead for date parsing

**Side Effects**:
- Date columns change from object dtype → datetime64[ns] dtype (when parseable)
- Enables chronological sorting in downstream pipeline steps
- Enables proper date formatting in output files

## Data Flow Contract

```
Input:  Excel file → pd.read_excel() → DataFrame with object dtype dates
              ↓
        parse_robust() applied to date columns
              ↓
Output: DataFrame with datetime64[ns] dtype dates
              ↓
        Pipeline steps (sorting, saving, formatting)
```

## Testing Contract

No formal contract testing required. Verification through:
- Unit tests in `tests/adapters/excel_repo_smoke_test.py`
- Integration tests with `example_date_format_issue.xlsx`
- Manual verification of output file sorting

## Related Documentation

- **Implementation**: [quickstart.md](../quickstart.md)
- **Data Model**: [data-model.md](../data-model.md)
- **Research**: [research.md](../research.md)

