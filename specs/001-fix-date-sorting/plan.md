# Implementation Plan: Fix Date Column Processing for Chronological Sorting

**Branch**: `001-fix-date-sorting` | **Date**: 2025-11-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-fix-date-sorting/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix the date column sorting issue where Excel cells formatted as text are sorted alphabetically instead of chronologically. The solution involves applying date parsing using the existing `parse_robust()` utility from `utils/dates.py` during data loading in `adapters/excel_repo.py`, converting text-formatted dates to pandas Timestamp objects before sorting occurs.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: pandas (already present), openpyxl (already present), python-dateutil (already present)  
**Storage**: N/A (file-based processing only)  
**Testing**: pytest (optional - existing test suite may be updated)  
**Target Platform**: Linux desktop (Ubuntu 22.04+), secondary support for Windows/macOS  
**Project Type**: Single project (desktop application)  
**Performance Goals**: Process 400MB files efficiently, maintain existing performance (no degradation)  
**Constraints**: Zero data loss during parsing, backward compatibility with existing workflows  
**Scale/Scope**: Single file change in `adapters/excel_repo.py`, leverages existing `utils/dates.py` module

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with Abstract Renumber Tool Constitution (v2.0.0):

- [x] **Clean Architecture**: Change is in `adapters/excel_repo.py` (correct layer for data loading), uses existing `utils/dates.py` utility
- [x] **Pipeline Processing**: N/A - not creating new pipeline steps, enhancing existing data loading
- [x] **Memory Efficiency**: Using pandas `.apply()` on columns is memory efficient, no additional large object creation
- [x] **Immutable Data**: N/A - not touching DocumentUnit classes or relationships
- [x] **PEP 8 & SOLID/DRY**: Uses existing `parse_robust()` function (DRY), single responsibility change (data type normalization at load boundary)
- [x] **Local Desktop Interface**: N/A - no UI changes, internal data processing only

**Constitution Compliance**: ✅ PASSED (Initial Check)

**Post-Design Re-Check**: ✅ PASSED
- All design artifacts maintain compliance
- Implementation approach confirmed to follow all applicable principles
- No new violations introduced during design phase

## Project Structure

### Documentation (this feature)

```text
specs/001-fix-date-sorting/
├── plan.md              # This file (/speckit.plan command output) ✅
├── spec.md              # Feature specification (already created) ✅
├── research.md          # Phase 0 output (research findings) ✅
├── data-model.md        # Phase 1 output (data transformations) ✅
├── quickstart.md        # Phase 1 output (implementation guide) ✅
├── contracts/           # Phase 1 output ✅
│   └── README.md        # Explanation of N/A contracts
└── checklists/          # Quality validation checklists ✅
    └── requirements.md  # Spec quality checklist (already created)
```

### Source Code (repository root)

```text
adapters/
├── excel_repo.py        # PRIMARY CHANGE: Add date column parsing in load() method
└── ...

utils/
├── dates.py             # EXISTING: parse_robust() function (no changes needed)
└── ...

tests/
├── adapters/
│   ├── excel_repo_smoke_test.py     # MAY UPDATE: Verify date parsing behavior
│   └── test_excel_repo_document_found.py
└── ...
```

**Structure Decision**: Single project structure maintained. This is a targeted fix to an existing adapter component with no new modules or architectural changes required. The modification point (`adapters/excel_repo.py`) is the correct location per Clean Architecture principles for data type normalization at the boundary layer.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - table not needed. All constitution principles are satisfied.

## Phase 0: Research & Design Decisions

See [research.md](research.md) for detailed findings.

### Key Decisions

1. **Where to apply date parsing**: In `ExcelRepo.load()` method after `pd.read_excel()` but before returning DataFrame
   - **Rationale**: Data type normalization belongs at the data boundary (Clean Architecture)
   - **Alternative rejected**: Parsing in pipeline steps would violate single responsibility and require changes in multiple locations

2. **Which parsing function to use**: Existing `utils/dates.parse_robust()`
   - **Rationale**: Already handles multiple formats, preserves original values on failure, follows DRY principles
   - **Alternative rejected**: Creating new parsing logic would violate DRY and introduce maintenance burden

3. **Which columns to parse**: Detect columns containing "date" (case-insensitive) in column name
   - **Rationale**: Follows existing codebase pattern (see `FormatExcelStep._find_date_columns()`)
   - **Alternative rejected**: Hardcoding specific column names would be fragile and miss future date columns

4. **How to apply parsing**: Use pandas `.apply()` on each date column
   - **Rationale**: Memory efficient, handles null values naturally, preserves DataFrame structure
   - **Alternative rejected**: Loop through rows would be slower and less idiomatic

## Phase 1: Design Artifacts

### Data Transformations

See [data-model.md](data-model.md) for detailed data flow analysis.

**Summary**: Date columns transform from `object` dtype (text strings) → `datetime64[ns]` dtype (pandas Timestamp) during load, enabling proper chronological sorting downstream.

### Implementation Guide

See [quickstart.md](quickstart.md) for step-by-step implementation instructions.

### API Contracts

N/A - This feature involves internal data processing only. No external APIs or interfaces are modified. The `ExcelRepo.load()` method signature remains unchanged; only internal behavior is enhanced. See [contracts/README.md](contracts/README.md).

## Phase 2: Task Breakdown

Task breakdown will be generated by `/speckit.tasks` command. See [tasks.md](tasks.md) (not yet created).

## Dependencies & Integration Points

### Upstream Dependencies
- `pandas.read_excel()`: Initial DataFrame loading
- `utils/dates.parse_robust()`: Date parsing logic
- Column detection pattern from `FormatExcelStep._find_date_columns()`

### Downstream Consumers
- `core/pipeline/steps/sort_df_step.py`: Benefits from datetime columns for chronological sorting
- `adapters/excel_repo.save()`: Openpyxl automatically handles datetime → Excel date conversion
- `core/pipeline/steps/format_excel_step.py`: Date formatting works correctly with datetime values

### Side Effects
- **Positive**: Sorting becomes chronologically correct for text-formatted dates
- **Positive**: Excel formatting (M/D/YYYY) now applies correctly to parsed dates
- **Neutral**: Unparseable values remain as-is (backward compatible)
- **None**: No breaking changes - existing datetime values pass through unchanged

## Testing Strategy

*Note: Tests are optional per Constitution v2.0.0, but recommended for this change*

### Recommended Test Updates

1. **Unit test** for date parsing in `tests/adapters/excel_repo_smoke_test.py`:
   - Create test Excel file with text-formatted dates
   - Verify `.load()` returns datetime64 dtype for date columns
   - Verify unparseable values are preserved

2. **Integration test** for sorting behavior:
   - Process file with text dates ("1/5/2024", "12/25/2023", "3/15/2024")
   - Verify output sorts chronologically (12/25/2023, 1/5/2024, 3/15/2024)
   - Use existing `example_date_format_issue.xlsx` as test fixture

3. **Regression test** for backward compatibility:
   - Process file with properly formatted Excel dates
   - Verify behavior unchanged from before the fix

### Manual Testing

User can verify fix by:
1. Processing `example_date_format_issue.xlsx` (provided in repo root)
2. Checking output file sorts Received Date chronologically
3. Comparing with previous incorrect alphabetical sorting

## Rollout Plan

1. **Development**: Implement change in `adapters/excel_repo.py`
2. **Validation**: Run existing test suite (`python3 -m pytest`)
3. **Manual verification**: Process `example_date_format_issue.xlsx`
4. **Deployment**: Merge to main branch (local desktop tool, no deployment infrastructure)
5. **User communication**: Update README.md with fix description

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Performance degradation on large files | Low | Medium | Use `.apply()` which is optimized; benchmark with 400MB file |
| Unexpected date parsing breaking data | Low | High | `parse_robust()` preserves original on failure; thorough testing with edge cases |
| Ambiguous dates parsed incorrectly (01/02/2024) | Medium | Low | Document limitation; `parse_robust()` uses pandas default (M/D/Y for U.S. locale) |
| Memory usage increase | Very Low | Low | `.apply()` operates column-wise; no significant memory overhead expected |

## Success Metrics

- [ ] `example_date_format_issue.xlsx` processes with correct chronological sort order
- [ ] Existing test suite passes without modifications (backward compatibility)
- [ ] No performance degradation (process 400MB file in similar time)
- [ ] Zero data loss (unparseable values preserved in output)
- [ ] User reports issue is resolved (confirmation from reporter)

## Open Questions

None - all technical decisions resolved during Phase 0 research based on existing codebase analysis.

## Planning Status

**Phase 0 (Research)**: ✅ COMPLETE
- research.md created with all technical decisions documented

**Phase 1 (Design)**: ✅ COMPLETE
- data-model.md created with data transformation analysis
- quickstart.md created with implementation instructions
- contracts/ directory created (N/A explained in README)
- Agent context updated for Cursor IDE

**Phase 2 (Tasks)**: ⏳ PENDING
- Task breakdown to be generated by `/speckit.tasks` command
- See [tasks.md](tasks.md) when ready

**Ready for Implementation**: ✅ YES
- All design artifacts complete
- Constitution compliance verified
- Implementation path clear
