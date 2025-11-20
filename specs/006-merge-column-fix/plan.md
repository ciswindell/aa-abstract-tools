# Implementation Plan: Preserve All Columns When Merging Excel Files

**Branch**: `006-merge-column-fix` | **Date**: 2025-11-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-merge-column-fix/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix the Excel merge functionality to preserve all columns from all source files, not just columns that exist in the primary template file. Currently, when merging files with different column structures, columns unique to secondary files are lost. The solution involves modifying the Excel save logic to dynamically add new columns to the output.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.7+ (per constitution requirements)  
**Primary Dependencies**: pandas, openpyxl (existing Excel processing libraries)  
**Storage**: File-based (Excel/PDF files)  
**Testing**: pytest (existing test framework)  
**Target Platform**: Desktop application (Linux/Windows/Mac)
**Project Type**: Single desktop application  
**Performance Goals**: Merge time increase <5% (per spec SC-003)  
**Constraints**: Must maintain backward compatibility with existing merge workflows  
**Scale/Scope**: Handle Excel files with up to 100 columns and 10,000 rows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Post-Design Re-check**: ✅ All principles still satisfied. The implementation:
- Uses existing ExcelRepo interface (no new protocols needed)
- All file I/O goes through repository pattern
- Integrates with existing pipeline SaveStep
- Preserves DocumentUnit relationships
- Follows PEP 8 and SOLID principles
- Includes comprehensive test plan
- Uses existing error handling
- Updates docstrings as needed

Verify compliance with `.specify/memory/constitution.md` principles:

- [x] **Protocol-Based Interfaces**: No new protocols needed - using existing ExcelRepo interface
- [x] **Repository Pattern**: All Excel operations go through ExcelRepo abstraction
- [x] **Pipeline Pattern**: Changes integrate with existing SaveStep in pipeline
- [x] **DocumentUnit Immutability**: Column preservation doesn't affect Excel ↔ PDF relationships
- [x] **Code Quality**: PEP 8 compliant, minimal changes following DRY principle
- [x] **Testing**: Pytest tests planned for column preservation scenarios
- [x] **Error Handling**: Existing error handling in ExcelRepo will be maintained
- [x] **Documentation**: Docstrings will be updated for modified methods

*If any principle is violated, document justification in Complexity Tracking section.*

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
adapters/
├── excel_repo.py              # Main modification: _write_dataframe_to_workbook method
└── __init__.py

core/
├── pipeline/
│   └── steps/
│       └── save_step.py       # Minor modification: add_missing_columns logic
└── interfaces.py              # No changes needed

tests/
├── adapters/
│   └── test_excel_repo_merge_columns.py  # New test file
└── integration/
    └── test_merge_column_preservation.py  # New integration test
```

**Structure Decision**: This feature modifies the existing single desktop application structure. Primary changes are in the adapters layer (ExcelRepo) with minor adjustments to the pipeline save step. No new directories or modules are required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all changes comply with constitution principles.
