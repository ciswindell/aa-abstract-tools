# Feature Specification: Remove Streamlit Interface

**Feature Branch**: `002-remove-streamlit`  
**Created**: 2025-11-19  
**Status**: Draft  
**Input**: User description: "I want to cleanup the dev branch. For example I am no longer developing the streamlit interface and want to completely remove all streamlit stoff because it just won't work correctly."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simplified Codebase (Priority: P1)

As a developer maintaining the Abstract Renumber application, I need the Streamlit interface code completely removed from the dev branch so that the codebase only contains the actively maintained Tkinter interface, reducing confusion and maintenance overhead.

**Why this priority**: This is the core objective - removing all Streamlit-related code eliminates a non-functional interface that creates confusion and increases maintenance burden. This is the primary cleanup goal.

**Independent Test**: Can be fully tested by verifying that no Streamlit imports, files, or dependencies exist in the codebase after the removal, and that the Tkinter application continues to function correctly.

**Acceptance Scenarios**:

1. **Given** the dev branch contains Streamlit interface code, **When** the cleanup is complete, **Then** no Streamlit-related imports exist in any Python files
2. **Given** the dev branch contains Streamlit dependencies, **When** the cleanup is complete, **Then** no Streamlit packages are listed in requirements files
3. **Given** the dev branch contains Streamlit UI files, **When** the cleanup is complete, **Then** no Streamlit-specific files (e.g., `*_streamlit.py`, `streamlit_*.py`) exist in the repository
4. **Given** the existing Tkinter interface, **When** Streamlit code is removed, **Then** the Tkinter application continues to function without any errors or broken imports

---

### User Story 2 - Reduced Dependencies (Priority: P2)

As a developer or user installing the application, I need Streamlit and its dependencies removed from the dependency list so that installation is faster and requires fewer packages.

**Why this priority**: Removing unused dependencies improves installation experience and reduces potential conflicts, but the application can still function with Streamlit dependencies present (they're just unused).

**Independent Test**: Can be fully tested by installing the application in a fresh virtual environment and verifying that Streamlit is not installed.

**Acceptance Scenarios**:

1. **Given** requirements.txt contains Streamlit, **When** the cleanup is complete, **Then** Streamlit is not listed in requirements.txt or any other dependency file
2. **Given** a fresh virtual environment, **When** dependencies are installed, **Then** Streamlit and its sub-dependencies are not installed
3. **Given** the application is installed, **When** checking installed packages, **Then** the package count is reduced by the number of Streamlit-related packages

---

### User Story 3 - Cleaned Documentation (Priority: P3)

As a developer or user reading project documentation, I need any references to Streamlit removed from README files and documentation so that I'm not confused about which interface to use.

**Why this priority**: Documentation cleanup prevents confusion, but outdated documentation doesn't prevent the application from working. This is polish that can be done after core code removal.

**Independent Test**: Can be fully tested by searching all documentation files for Streamlit references and verifying they're either removed or updated to reflect Tkinter-only support.

**Acceptance Scenarios**:

1. **Given** README.md mentions Streamlit interface, **When** the cleanup is complete, **Then** README.md only documents the Tkinter interface
2. **Given** documentation files reference Streamlit installation, **When** the cleanup is complete, **Then** installation instructions omit Streamlit
3. **Given** code comments mention Streamlit, **When** the cleanup is complete, **Then** Streamlit-related comments are removed or updated

---

### Edge Cases

- What happens when imports from removed Streamlit modules are referenced elsewhere in the codebase (should cause import errors that guide complete removal)?
- How does the system handle configuration files that may reference both Streamlit and Tkinter interfaces (remove Streamlit sections)?
- What if there are shared utility functions that were used by both interfaces (keep them if Tkinter uses them, remove if Streamlit-only)?
- What happens to any Streamlit-specific environment variables or configuration settings (remove them)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST identify all Streamlit-related Python files in the repository (files with 'streamlit' in the name or path)
- **FR-002**: System MUST remove all Streamlit-related imports from all Python files
- **FR-003**: System MUST remove Streamlit package from all dependency files (requirements.txt, setup.py, pyproject.toml, etc.)
- **FR-004**: System MUST remove all Streamlit-related files and directories from the repository
- **FR-005**: System MUST preserve all Tkinter interface functionality after Streamlit removal
- **FR-006**: System MUST remove or update any documentation references to Streamlit
- **FR-007**: System MUST verify that no broken imports remain after removal (code must still run)
- **FR-008**: System MUST remove any Streamlit-specific configuration sections from config files

### Architecture Requirements (per Constitution v2.0.0)

- **AR-001**: Removal MUST NOT affect business logic in `core/` directory (Clean Architecture principle)
- **AR-002**: Removal MUST NOT introduce new dependencies or increase memory usage (Memory Efficiency principle)
- **AR-003**: Remaining code MUST continue to follow PEP 8 style guidelines (Code Quality principle)
- **AR-004**: Tkinter UI in `adapters/ui_tkinter.py` MUST remain fully functional (Local Desktop Interface principle)
- **AR-005**: Tests (if present) MUST pass after removal, or Streamlit-related tests must be removed

### Key Entities *(include if feature involves data)*

- **Streamlit File**: Python file containing Streamlit-specific code (identified by imports, filename patterns, or Streamlit API usage)
- **Streamlit Import Statement**: Import statement referencing streamlit or streamlit-related packages
- **Streamlit Dependency**: Package entry in requirements files for streamlit or related packages
- **Streamlit Configuration**: Configuration sections or files specific to Streamlit interface

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero Streamlit imports remain in any Python file in the repository (100% removal)
- **SC-002**: Zero Streamlit-related files remain in the repository (verified by filename search)
- **SC-003**: Streamlit package and all its dependencies are removed from requirements files (0 Streamlit entries)
- **SC-004**: Existing Tkinter application functionality works without errors after removal (100% functional)
- **SC-005**: Repository size is reduced by removing unused code (measurable by git diff stats)
- **SC-006**: Fresh installation in clean environment does not install Streamlit (verified by pip list)
- **SC-007**: All documentation (README.md, docstrings, comments) contains zero references to Streamlit or updated to note Tkinter-only support

## Assumptions

- Streamlit interface code is completely separate from Tkinter interface code (no shared files with mixed interfaces)
- No production users are currently using the Streamlit interface
- The Streamlit interface was never fully functional, so removal won't impact working features
- All critical functionality exists in the Tkinter interface
- Test suite (if present) covers Tkinter functionality adequately
- The Streamlit code is identifiable by standard naming patterns and imports

## Out of Scope

- Refactoring or improving the existing Tkinter interface (only preserving current functionality)
- Adding new UI features or capabilities
- Migrating any Streamlit-specific features to Tkinter (those features are being abandoned)
- Performance optimization of remaining code
- Creating new documentation (only updating existing documentation)
- Adding new tests (only ensuring existing tests pass or removing Streamlit-related tests)
