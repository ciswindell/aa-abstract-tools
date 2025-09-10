# Product Requirements Document: Streamlit GUI Architecture Refactoring

## Introduction/Overview

The current Streamlit GUI codebase suffers from massive code duplication, unused functions, and poor separation of concerns. The `single_file_processing.py` file has grown to 890 lines with significant architectural debt. Additionally, the multi-file merge workflow lacks the polished tabbed interface and session state management that was carefully developed for single file processing.

**Problem Statement:** The current GUI code has ~300+ lines of duplication across files, 5 unused functions (~200 lines of dead code), violates SOLID principles, and has inconsistent UX patterns between single file and merge workflows.

**Goal:** Create a maintainable, modular Streamlit GUI architecture that eliminates code duplication, follows SOLID principles, standardizes the tabbed interface across all workflows, and reduces total codebase size by 40-50%.

## Goals

1. **Eliminate Code Duplication:** Remove ~300+ lines of duplicated code across GUI files
2. **Remove Dead Code:** Delete 5 unused functions (~200 lines) from `single_file_processing.py`
3. **Standardize UX Patterns:** Implement consistent tabbed interface and session state management across all workflows
4. **Improve Maintainability:** Create reusable components following SOLID principles
5. **Reduce Codebase Size:** Achieve 40-50% reduction in total GUI code lines
6. **Maintain Compatibility:** Preserve 100% existing UI functionality and behavior
7. **Enhance Developer Experience:** Make code easier to understand and modify for junior developers

## User Stories

**As a developer maintaining the GUI code, I want:**
- Shared components so I don't have to duplicate CSS and UI logic across files
- Consistent tabbed interface patterns so all workflows feel familiar to users
- Unified session state management so I don't have to learn different patterns per page
- Small, focused functions so I can easily understand and modify specific features
- Clear separation of concerns so I know where to find specific functionality
- Reusable classes so I can easily add new pages or features

**As a user of the application, I want:**
- Consistent interface patterns so the merge workflow feels as polished as single file processing
- The same intuitive tabbed navigation across all workflows
- Reliable session state management so my selections persist as I navigate between tabs

**As a junior developer joining the project, I want:**
- Clean, well-organized code structure so I can quickly understand the codebase
- Consistent patterns across all GUI components so I can follow established conventions
- Clear component boundaries so I know where to make changes safely

## Functional Requirements

### Phase 1: Dead Code Removal
1. The system must remove the following unused functions from `single_file_processing.py`:
   - `show_filter_decision_point()` (lines 522-546)
   - `show_filter_configuration()` (lines 548-641)
   - `show_processing_options_decision()` (lines 643-687)
   - `show_final_processing_section()` (lines 689-730)
   - `show_download_ui()` (lines 783-800)

### Phase 2: Shared Components Architecture
2. The system must create a `pages/components/` directory with the following modules:
   - `styling.py` - Contains shared CSS injection functionality
   - `file_upload.py` - Contains file upload widgets and validation logic
   - `processing_options.py` - Contains processing options UI components
   - `downloads.py` - Contains download UI and ZIP creation logic
   - `state_management.py` - Contains session state utility functions
   - `tabbed_workflow.py` - Contains shared tabbed interface components

### Phase 3: Component Classes
3. The system must implement the following component classes:
   - `StyleManager` class in `styling.py` with `inject_custom_css()` method
   - `FileUploadManager` class in `file_upload.py` with upload and validation methods
   - `ProcessingOptionsManager` class in `processing_options.py` with options rendering methods
   - `DownloadManager` class in `downloads.py` with ZIP creation and download UI methods
   - `SessionStateManager` class in `state_management.py` with state management utilities
   - `TabbedWorkflowManager` class in `tabbed_workflow.py` with tab creation and navigation methods

### Phase 4: Base Page Class
4. The system must create a `BaseStreamlitPage` class in `pages/base_page.py` that:
   - Initializes common session state variables
   - Provides shared navigation functionality
   - Manages UI adapter initialization
   - Provides common utility methods

### Phase 5: Page Refactoring
5. The system must refactor `single_file_processing.py` and `multi_file_merge.py` to:
   - Inherit from `BaseStreamlitPage`
   - Use shared component classes instead of duplicated functions
   - Implement consistent tabbed interface using `TabbedWorkflowManager`
   - Use unified session state management patterns across both workflows
   - Reduce each page file to 200-300 lines maximum
   - Maintain identical UI behavior and functionality

### Phase 6: Multi-File Merge Workflow Enhancement
6. The system must enhance `multi_file_merge.py` to:
   - Implement the same 4-tab interface as single file processing: ["📁 Files", "🔍 Filtering", "⚙️ Options", "🚀 Process"]
   - Use the same session state management patterns developed for single file processing
   - Maintain the existing multi-file pair selection functionality within the Files tab
   - Apply consistent filtering and processing options across all selected file pairs
   - Provide the same polished user experience as single file processing

### Phase 7: Integration and Testing
7. The system must ensure all refactored components:
   - Maintain 100% backward compatibility with existing UI behavior
   - Preserve all existing functionality including file uploads, processing, and downloads
   - Work correctly with the existing `StreamlitUIAdapter` and processing pipeline
   - Handle all existing session state management correctly

### Phase 8: Streamlit Deprecation Updates
8. The system must address Streamlit deprecation warnings:
   - Replace all instances of `use_container_width` parameter with the new `width` parameter
   - Update `use_container_width=True` to `width='stretch'`
   - Update `use_container_width=False` to `width='content'`
   - Ensure compatibility with Streamlit versions beyond 2025-12-31

### Phase 9: Single File Download Naming Fix
9. The system must fix file naming in single file workflow downloads:
   - ZIP filename should remain: `original_name_processed.zip`
   - Files inside ZIP should use original names without suffix:
     - `original_name.xlsx` (not `original_name_processed.xlsx`)
     - `original_name.pdf` (not `original_name_processed.pdf`)
   - This provides cleaner file names for end users while maintaining clear ZIP identification

## Non-Goals (Out of Scope)

1. **Processing Logic Changes:** No modifications to core processing logic, pipeline, or business rules
2. **UI/UX Changes:** No changes to visual appearance, user workflows, or interface behavior
3. **New Dependencies:** No addition of external libraries or frameworks beyond existing stack
4. **Performance Optimization:** Focus is on code organization, not performance improvements
5. **Feature Additions:** No new functionality or capabilities beyond current features
6. **Backend Changes:** No modifications to `adapters/ui_streamlit.py` core interface methods
7. **Testing Framework:** No addition of automated testing (though manual testing required)

## Design Considerations

### Component Architecture
- **Pattern:** Use class-based components for stateful functionality, static methods for utilities
- **Inheritance:** Single inheritance from `BaseStreamlitPage` for all page classes
- **Composition:** Components should be composable and reusable across different pages
- **Naming:** Use descriptive class names ending in "Manager" for component classes

### File Organization
```
pages/
├── components/
│   ├── __init__.py
│   ├── styling.py
│   ├── file_upload.py
│   ├── processing_options.py
│   ├── downloads.py
│   ├── state_management.py
│   └── tabbed_workflow.py
├── base_page.py
├── mode_selection.py
├── single_file_processing.py
└── multi_file_merge.py
```

### Code Style
- Follow existing PEP 8 conventions
- Use type hints for all class methods
- Maintain existing docstring patterns
- Keep methods focused and under 50 lines each

## Technical Considerations

### Dependencies
- **No New Dependencies:** Use only existing Streamlit and standard Python libraries
- **Compatibility:** Maintain compatibility with current Python 3.x version requirements
- **Import Structure:** Use relative imports within components, absolute imports for external modules

### Session State Management
- Centralize session state key definitions to avoid conflicts
- Provide clear interfaces for state initialization and cleanup
- Maintain existing session state behavior for backward compatibility

### Error Handling
- Preserve existing error handling patterns
- Ensure component failures don't break entire page functionality
- Maintain existing user error message behavior

## Success Metrics

### Quantitative Metrics
1. **Code Reduction:** Achieve 40-50% reduction in total GUI code lines
2. **Duplication Elimination:** Remove 100% of identified duplicated code (~300+ lines)
3. **Dead Code Removal:** Delete 100% of unused functions (5 functions, ~200 lines)
4. **File Size Targets:** 
   - `single_file_processing.py`: Reduce from 890 to <300 lines
   - `multi_file_merge.py`: Reduce from 611 to <300 lines

### Qualitative Metrics
1. **Maintainability:** New developers can understand component structure within 30 minutes
2. **Reusability:** Adding a new page requires <50 lines of page-specific code
3. **Consistency:** All pages follow identical patterns for common functionality, including tabbed interfaces
4. **User Experience:** Multi-file merge workflow provides the same polished experience as single file processing
5. **Compatibility:** 100% of existing UI functionality works identically after refactoring

## Open Questions

1. **Component Initialization:** Should component classes be instantiated once per session or per use?
2. **State Persistence:** How should component-specific state be managed across page navigation?
3. **Tab State Management:** How should tab-specific state be preserved when switching between tabs in the merge workflow?
4. **Multi-File Session State:** How should session state handle multiple file pairs while maintaining the same patterns as single file processing?
5. **Error Boundaries:** Should components have individual error handling or rely on page-level handling?
6. **Testing Strategy:** What manual testing checklist should be used to verify functionality preservation?
7. **Migration Strategy:** Should refactoring be done incrementally or as a complete replacement?

## Implementation Priority

### Phase 1 (Immediate): Dead Code Cleanup
- Remove 5 unused functions from `single_file_processing.py`
- Verify no hidden dependencies on removed functions

### Phase 2 (High Priority): Shared Components
- Extract `inject_custom_css()` to `StyleManager`
- Create `FileUploadManager` for upload functionality
- Extract processing options to `ProcessingOptionsManager`

### Phase 3 (Medium Priority): Architecture
- Create `BaseStreamlitPage` class
- Create `TabbedWorkflowManager` for consistent tab interfaces
- Refactor existing pages to use base class and components
- Create `DownloadManager` for download functionality

### Phase 4 (High Priority): Multi-File Merge Enhancement
- Implement tabbed interface for multi-file merge workflow
- Apply consistent session state management patterns
- Integrate filtering and processing options into merge workflow
- Ensure UX parity with single file processing

### Phase 5 (High Priority): Streamlit Deprecation Updates
- Identify all uses of `use_container_width` parameter across the codebase
- Replace `use_container_width=True` with `width='stretch'`
- Replace `use_container_width=False` with `width='content'`
- Test all affected UI components to ensure visual consistency

### Phase 6 (Final): Integration
- Complete integration testing
- Performance verification
- Documentation updates
