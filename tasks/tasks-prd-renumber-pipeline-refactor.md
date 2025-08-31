# Task List: RenumberService Pipeline Refactoring

## Relevant Files

- `core/pipeline/pipeline.py` - Main pipeline orchestrator class that executes steps in sequence
- `core/pipeline/steps/__init__.py` - Pipeline steps module initialization
- `core/pipeline/steps/load_step.py` - Step for loading Excel/PDF files (single or multiple pairs)
- `core/pipeline/steps/merge_step.py` - Step for merging multiple file pairs into single DataFrame/PDF
- `core/pipeline/steps/validate_step.py` - Step for validating inputs using existing ValidationService
- `core/pipeline/steps/clean_step.py` - Step for cleaning data types using existing transform functions
- `core/pipeline/steps/filter_step.py` - Step for applying optional filtering
- `core/pipeline/steps/add_ids_step.py` - Step for adding document IDs consistently
- `core/pipeline/steps/link_step.py` - Step for creating document links
- `core/pipeline/steps/sort_step.py` - Step for sorting and renumbering data
- `core/pipeline/steps/title_step.py` - Step for generating new bookmark titles
- `core/pipeline/steps/bookmark_step.py` - Step for updating PDF bookmarks
- `core/pipeline/steps/reorder_step.py` - Step for reordering PDF pages (optional)
- `core/pipeline/steps/save_step.py` - Step for writing Excel and PDF outputs
- `core/pipeline/context.py` - Pipeline context object for passing data between steps
- `core/services/renumber.py` - Modified to use pipeline instead of monolithic run() method
- `tests/core/pipeline/test_pipeline.py` - Unit tests for pipeline orchestrator
- `tests/core/pipeline/steps/test_load_step.py` - Unit tests for load step
- `tests/core/pipeline/steps/test_merge_step.py` - Unit tests for merge step
- `tests/core/pipeline/steps/test_validate_step.py` - Unit tests for validate step
- `tests/core/pipeline/steps/test_clean_step.py` - Unit tests for clean step
- `tests/core/pipeline/steps/test_filter_step.py` - Unit tests for filter step
- `tests/core/pipeline/steps/test_add_ids_step.py` - Unit tests for add IDs step
- `tests/core/pipeline/steps/test_link_step.py` - Unit tests for link step
- `tests/core/pipeline/steps/test_sort_step.py` - Unit tests for sort step
- `tests/core/pipeline/steps/test_title_step.py` - Unit tests for title step
- `tests/core/pipeline/steps/test_bookmark_step.py` - Unit tests for bookmark step
- `tests/core/pipeline/steps/test_reorder_step.py` - Unit tests for reorder step
- `tests/core/pipeline/steps/test_save_step.py` - Unit tests for save step

### Notes

- Unit tests should be placed in corresponding test directories mirroring the source structure
- Use `python3 -m pytest tests/core/pipeline/` to run pipeline-specific tests
- Existing integration tests should continue to pass without modification

## Tasks

- [x] 1.0 Create Pipeline Infrastructure
  - [x] 1.1 Create `core/pipeline/context.py` with PipelineContext dataclass to hold data between steps
  - [x] 1.2 Create `core/pipeline/pipeline.py` with Pipeline class that executes steps in sequence
  - [x] 1.3 Create `core/pipeline/steps/__init__.py` with base Step protocol/interface
  - [x] 1.4 Add pipeline step registration and execution logic with fail-fast error handling

- [x] 2.0 Implement Core Pipeline Steps
  - [x] 2.1 Implement `LoadStep` - load Excel/PDF files based on merge vs single file options
  - [x] 2.2 Implement `MergeStep` - merge multiple file pairs into single DataFrame/PDF early in process
  - [x] 2.2.1 **CRITICAL FIX**: Add Document IDs before merging to prevent ID collisions in merge workflows
  - [x] 2.3 Implement `ValidateStep` - wrap existing ValidationService in pipeline step
  - [x] 2.4 Implement `CleanStep` - wrap existing clean_types function in pipeline step
  - [x] 2.5 Implement `FilterStep` - wrap existing filter_df function with conditional execution
  - [x] 2.6 Implement `AddIdsStep` - wrap existing add_document_ids function consistently for merged/single (conditional execution)
  - [x] 2.7 Implement `LinkStep` - wrap existing create_document_links function in pipeline step
  - [x] 2.8 Implement `SortStep` - wrap existing sort_and_renumber function in pipeline step
  - [x] 2.9 Implement `TitleStep` - wrap existing make_titles function in pipeline step
  - [x] 2.10 Implement `BookmarkStep` - update PDF bookmarks using existing logic
  - [x] 2.11 Implement `ReorderStep` - reorder PDF pages with conditional execution based on options
  - [x] 2.12 Implement `SaveStep` - save Excel and PDF outputs using existing repo methods

- [ ] 3.0 Refactor RenumberService to Use Pipeline
  - [x] 3.1 Replace monolithic `run()` method with pipeline instantiation and execution
  - [x] 3.2 Maintain exact same method signature and return type for backward compatibility
  - [x] 3.3 Preserve all existing error handling and logging behavior
  - [ ] 3.4 Remove complex conditional branching logic (now handled by early merge)

- [ ] 4.0 Update Early Merge Logic
  - [ ] 4.1 Modify document ID generation to work consistently for merged workflows
  - [ ] 4.2 Update merge logic to create single DataFrame and PDF outline at start of pipeline
  - [ ] 4.3 Remove duplicate merge/single conditional paths throughout codebase
  - [ ] 4.4 Ensure merged output file naming remains consistent with current behavior

- [ ] 5.0 Testing and Cleanup
  - [ ] 5.1 Create unit tests for each pipeline step with mock dependencies
  - [ ] 5.2 Create integration test for full pipeline execution
  - [ ] 5.3 Verify all existing tests continue to pass without modification
  - [ ] 5.4 Remove unused helper functions from original RenumberService
  - [ ] 5.5 Clean up imports and remove dead code
  - [ ] 5.6 Update any relevant documentation or comments
