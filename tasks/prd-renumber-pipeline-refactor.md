# PRD: RenumberService Pipeline Refactoring

## Introduction/Overview

The current `RenumberService` is a 190+ line monolithic method that violates SOLID principles and is difficult to maintain, test, and extend. This feature will refactor it into a clean, basic pipeline pattern while maintaining 100% backward compatibility. The key insight is to merge multiple file pairs into a single DataFrame and PDF outline early in the process, eliminating the complex conditional branching between merge and single-file logic.

**Goal**: Replace the monolithic `RenumberService.run()` method with a simple, linear pipeline of discrete steps that are easier to understand, test, and maintain.

## Goals

1. **Eliminate Code Complexity**: Replace 190+ line monolithic method with simple, single-responsibility pipeline steps
2. **Improve Testability**: Enable unit testing of individual pipeline steps in isolation
3. **Simplify Merge Logic**: Merge file pairs into single DataFrame/PDF early, eliminating dual code paths
4. **Maintain Compatibility**: Zero breaking changes to external API or behavior
5. **Clean Up Codebase**: Remove unused code and simplify architecture

## User Stories

1. **As a developer**, I want to understand what each step of the renumbering process does without reading 190 lines of procedural code
2. **As a developer**, I want to unit test individual transformation steps without running the entire pipeline
3. **As a maintainer**, I want to add new processing steps without modifying existing complex conditional logic
4. **As a user**, I want the application to work exactly the same as before, with no changes to functionality or behavior

## Functional Requirements

1. **Pipeline Architecture**: The system must implement a linear pipeline with hardcoded step order
2. **Step Skipping**: Pipeline steps must be conditionally executed based on `Options` object settings
3. **Early Merge**: Multiple file pairs must be merged into single DataFrame and PDF outline before any sorting/filtering
4. **Document ID Consistency**: Document IDs must be generated consistently for both single and merged workflows
5. **Error Handling**: Pipeline must fail fast on first error with clear error messages
6. **Backward Compatibility**: All existing functionality must work identically to current implementation
7. **Interface Preservation**: `RenumberService.run()` method signature and behavior must remain unchanged
8. **Clean Separation**: Each pipeline step must have single responsibility and clear input/output contracts

### Pipeline Steps (Hardcoded Order):
1. **LoadStep**: Load Excel/PDF files (single or multiple pairs)
2. **MergeStep**: Merge multiple pairs into single DataFrame/PDF (if merge enabled)
3. **ValidateStep**: Validate merged/single inputs
4. **CleanStep**: Clean data types
5. **FilterStep**: Apply optional filtering (if enabled)
6. **AddIdsStep**: Add document IDs consistently
7. **LinkStep**: Create document links
8. **SortStep**: Sort and renumber data
9. **TitleStep**: Generate new bookmark titles
10. **BookmarkStep**: Update PDF bookmarks
11. **ReorderStep**: Reorder PDF pages (if enabled)
12. **SaveStep**: Write Excel and PDF outputs

## Non-Goals (Out of Scope)

1. **UI Changes**: No modifications to the GUI or user interface
2. **File I/O Changes**: No changes to ExcelRepo or PdfRepo adapters
3. **New Dependencies**: No additional external libraries
4. **Performance Optimization**: Focus is on maintainability, not performance
5. **Feature Additions**: No new functionality beyond current capabilities
6. **Configuration System**: No complex pipeline configuration - keep it simple
7. **Async/Parallel Processing**: Keep it synchronous and simple

## Technical Considerations

1. **Existing Transform Functions**: Reuse existing pure functions from `core/transform/excel.py` and `core/transform/pdf.py`
2. **Pipeline Location**: Implement in `core/pipeline/` directory structure
3. **Interface Compliance**: All steps must work with existing `ExcelRepo`, `PdfRepo`, and `Logger` interfaces
4. **Document ID Strategy**: Unify document ID generation to work consistently for merged and single workflows
5. **Memory Management**: Process data in single pass through pipeline steps
6. **Error Context**: Each step should provide clear context about what failed

## Success Metrics

1. **Code Reduction**: Reduce `RenumberService.run()` from 190+ lines to <50 lines of pipeline orchestration
2. **Testability**: Each pipeline step can be unit tested independently
3. **Maintainability**: New developers can understand the process flow in <10 minutes
4. **Compatibility**: All existing tests pass without modification
5. **Simplicity**: Eliminate dual code paths for merge vs single-file processing

## Critical Issues Discovered

### Document ID Collision in Merge Workflows
**Issue**: When merging multiple Excel/PDF pairs, each file has its own Index# sequence (1,2,3...), creating duplicate indices that cause Document ID collisions and bookmark linking failures.

**Root Cause**: The original design called `add_document_ids()` after merging DataFrames, using a single source path and reset row positions, losing per-file uniqueness.

**Solution**: Modified MergeStep to add Document IDs BEFORE merging, preserving per-file uniqueness:
1. Call `add_document_ids()` on each DataFrame part individually with its original source path
2. Then concatenate DataFrames that already have unique Document IDs  
3. AddIdsStep becomes conditional (skip if Document_ID already exists)

This maintains backward compatibility while ensuring uniqueness across merged files.

## Open Questions

1. Should pipeline steps be implemented as classes or functions? ✅ **Resolved: Classes using BaseStep**
2. How should step-to-step data be passed (return values, context object, or shared state)? ✅ **Resolved: PipelineContext object**
3. Should there be a separate `PipelineContext` object to carry data between steps? ✅ **Resolved: Yes, implemented**

---

**Target Implementation**: Simple, linear pipeline that processes data through discrete steps, with early merge normalization to eliminate complex conditional branching.
