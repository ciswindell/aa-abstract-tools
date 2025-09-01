# Task List: DocumentUnit Architecture Refactor

Based on the PRD: `prd-document-unit-architecture.md`

## Relevant Files

- `core/models.py` - Add DocumentUnit dataclass to existing models
- `core/pipeline/context.py` - Update PipelineContext to use DocumentUnits instead of separate lists
- `core/pipeline/steps/load_step.py` - Major refactor to implement Phase 1 (per-file linking and merging)
- `core/pipeline/steps/filter_df_step.py` - Filter DataFrame rows by column values (action_type_step naming)
- `core/pipeline/steps/sort_df_step.py` - Sort DataFrame rows and renumber Index# column (action_type_step naming)
- `core/pipeline/steps/rebuild_pdf_step.py` - PyPDF-optimized three-phase PDF reconstruction (action_type_step naming)
- `core/pipeline/pipeline.py` - Update pipeline registration to use new simplified steps
- `core/transform/document_unit.py` - New utility functions for DocumentUnit operations
- `tests/core/models_test.py` - Unit tests for DocumentUnit dataclass
- `tests/core/pipeline/steps/load_step_test.py` - Tests for Phase 1 implementation
- `tests/core/pipeline/steps/filter_df_step_test.py` - Tests for DataFrame filtering (action_type_step naming)
- `tests/core/pipeline/steps/sort_df_step_test.py` - Tests for DataFrame sorting (action_type_step naming)
- `tests/core/pipeline/steps/rebuild_pdf_step_test.py` - Tests for PDF rebuilding (action_type_step naming)
- `tests/core/pipeline/steps/validate_step_test.py` - Tests for comprehensive validation logic (30 tests)
- `tests/core/pipeline/steps/save_step_test.py` - Tests for backup logic and atomic saves (24 tests)
- `tests/core/transform/document_unit_test.py` - Tests for DocumentUnit utility functions
- `tests/core/pipeline/context_test.py` - Unit tests for PipelineContext class (14 tests)
- `tests/core/pipeline/pipeline_test.py` - Unit tests for Pipeline class (14 tests)
- `tests/integration_document_unit_workflow_test.py` - Comprehensive integration tests for full DocumentUnit workflow (11 tests)

### Notes

- The current pipeline has 12 steps that will be reduced to 4 steps with this refactor
- Steps to be eliminated: MergeStep, LinkStep, AddIdsStep, BookmarkStep, ReorderStep, ValidateStep, CleanStep, TitleStep
- Steps to be kept but simplified: LoadStep (major refactor), SaveStep (minor updates)
- New steps: FilterDfStep, SortDfStep, RebuildPdfStep (action_type_step naming)
- Use existing PyPDF functionality but with memory-efficient patterns
- Maintain backward compatibility with existing RenumberService API

## Tasks

- [x] 1.0 Create DocumentUnit Data Structure and Core Models
  - [x] 1.1 Add DocumentUnit dataclass to `core/models.py` with required fields
  - [x] 1.2 Create utility functions in `core/transform/document_unit.py` for DocumentUnit operations
  - [x] 1.3 Add DocumentUnit creation helper functions (from bookmark + Excel row)
  - [x] 1.4 Add DocumentUnit sorting and filtering helper functions
  - [x] 1.5 Create unit tests for DocumentUnit dataclass and utility functions

- [x] 2.0 Implement Phase 1: Per-File Linking and Merging (LoadStep)
  - [x] 2.1 Refactor LoadStep to process each Excel/PDF pair individually
  - [x] 2.2 Implement per-file Document ID generation and Excel row linking
  - [x] 2.3 Implement PDF page range detection and DocumentUnit creation
  - [x] 2.4 Implement sequential PDF merging with page offset tracking
  - [x] 2.5 Create intermediate merged PDF file and populate DocumentUnits list
  - [x] 2.6 Merge all Excel DataFrames into single DataFrame
  - [x] 2.7 Update LoadStep to handle both single-file and multi-file workflows
  - [x] 2.8 Add comprehensive error handling and logging for Phase 1
  - [x] 2.9 Create unit tests for refactored LoadStep

- [x] 3.0 Implement Phase 2: Filter, Sort, and Rebuild Pipeline Steps
  - [x] 3.1 **ARCHITECTURAL DECISION**: Use `_include` flag instead of removing DataFrame rows
    - **Problem**: Removing rows breaks DocumentUnit ↔ DataFrame alignment
    - **Solution**: Add `_include` boolean column to flag rows for processing
    - **Benefits**: Preserves DocumentUnit integrity, reversible filtering, order-agnostic design
  - [x] 3.1.1 Refactor FilterDfStep to use `_include` flag instead of removing rows
  - [x] 3.1.2 Refactor SortDfStep to work with `_include` flag and be order-agnostic
  - [x] 3.1.3 Test that Filter→Sort and Sort→Filter both work correctly
  - [x] 3.2 **ARCHITECTURAL DECISION**: Implement PyPDF-optimized three-phase PDF reconstruction
    - **Rationale**: Maximum robustness using PyPDF's native capabilities instead of bookmark preservation
    - **Benefits**: Never fails due to bookmark corruption, supports flexible filtering/reordering
  - [x] 3.2.1 Create RebuildPdfStep with three-phase reconstruction architecture
  - [x] 3.2.2 Phase A: Implement page filtering based on `_include` flag (conditional execution)
  - [x] 3.2.3 Phase B: Implement page reordering based on sorted DataFrame order (conditional execution)  
  - [x] 3.2.4 Phase C: Implement fresh bookmark generation using `PdfWriter.add_outline_item()`
  - [x] 3.2.5 Add immutable DocumentUnit architecture (ranges never change during processing)
  - [x] 3.2.6 Add temporary file cleanup logic and error handling
  - [x] 3.6 Update SaveStep to work with new DocumentUnit-based context
  - [x] 3.7 Add error handling and validation for Phase 2 steps

- [x] 4.0 Update PipelineContext and Pipeline Orchestration
  - [x] 4.1 Update PipelineContext to use `document_units: List[DocumentUnit]` instead of separate lists
  - [x] 4.2 Add backward compatibility properties for `bookmarks` and `pages` if needed
  - [x] 4.3 Remove obsolete merge-specific fields from PipelineContext
  - [x] 4.4 Update Pipeline class to register new simplified step sequence
  - [x] 4.5 Remove registrations for eliminated pipeline steps
  - [x] 4.6 Update pipeline execution logic to handle new step flow
  - [x] 4.7 Add intermediate PDF path management to PipelineContext

- [ ] 5.0 Testing, Cleanup, and Documentation
  - [x] 5.1 Create unit tests for FilterDfStep, SortDfStep, and RebuildPdfStep (35 tests - ALL PASSING)
  - [x] 5.1.1 Fix LoadStep unit tests (13 tests - ALL PASSING)
  - [x] 5.2 Create unit tests for updated PipelineContext and Pipeline (28 tests - ALL PASSING)
  - [x] 5.3 Create unit tests for ValidateStep (comprehensive validation logic) (30 tests - ALL PASSING)
  - [x] 5.4 Create unit tests for SaveStep (backup logic, atomic saves) (24 tests - ALL PASSING)
  - [x] 5.5 Fix existing unit tests to work with new architecture (ALL 152 TESTS PASSING)
    - [x] 5.5.1 Fix core/models_test.py (DocumentUnit tests) - PASSING
    - [x] 5.5.2 Fix core/transform/document_unit_test.py - PASSING
    - [x] 5.5.3 Fix core/services/validate_test.py - PASSING
    - [x] 5.5.4 Fix tests/adapters/excel_repo_smoke_test.py - PASSING (self-contained fixture)
    - [x] 5.5.5 Fix tests/adapters/pdf_repo_smoke_test.py - PASSING (removed missing fixture)
  - [x] 5.6 Create comprehensive integration test for full DocumentUnit workflow (9 tests - ALL PASSING)
  - [x] 5.9 Verify all tests pass with new architecture (run full test suite) - ALL 161 TESTS PASSING
  - [x] 5.10 Remove obsolete pipeline step files (MergeStep, LinkStep, etc.) - DONE
  - [x] 5.11 Update any remaining imports and references to removed steps - COMPLETED (fixed has_bookmark_formulas issue)
  - [x] 5.12 Clean up unused utility functions and dead code - COMPLETED
  - [x] 5.13 Update docstrings and comments to reflect new architecture - COMPLETED (updated all pipeline step docstrings to emphasize DocumentUnit architecture)
  - [x] 5.14 Add performance benchmarking test for multi-file processing - CANCELLED (not needed)
