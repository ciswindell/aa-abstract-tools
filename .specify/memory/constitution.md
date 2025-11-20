<!--
  SYNC IMPACT REPORT
  Version: 1.1.0 → 1.1.1 (Version Increment Requirement Clarified)
  Date: 2025-11-20
  
  Changes:
  - Clarified that code changes MUST trigger version increments
  - Made version update mandatory for all code changes (features, fixes, breaking changes)
  - Emphasized version updates are part of the standard development workflow
  
  Previous Changes (v1.1.0):
  - Added new "Version Management" quality standard section
  - Defined single source of truth pattern for versioning
  - Established semantic versioning rules (MAJOR.MINOR.PATCH)
  - Documented version display requirements
  - Added version update workflow to Feature Development section
  
  Template Updates Required:
  ✅ plan-template.md - Constitution check already flexible enough
  ✅ spec-template.md - No changes needed
  ✅ tasks-template.md - No changes needed
  
  Follow-up TODOs:
  - None (all standards implemented in feature 005-version-display-system)
-->

# Abstract Renumber Tool Constitution

## Core Principles

### I. Clean Architecture with Protocol-Based Interfaces

All components MUST use Protocol-based interfaces (`core/interfaces.py`) for dependency injection. Business logic in `core/` MUST NOT import from `adapters/` or `app/`. Adapters implement protocols but never define them.

**Rationale**: Enables testability, allows adapter replacement without touching business logic, and enforces unidirectional dependency flow.

### II. Repository Pattern for External I/O

All file operations (Excel, PDF) MUST go through repository abstractions (`ExcelRepo`, `PdfRepo`). Direct file I/O libraries MUST NOT be imported outside the `adapters/` directory.

**Rationale**: Isolates external dependencies, enables mocking in tests, and provides consistent error handling for file operations.

### III. Pipeline Processing Pattern

Complex workflows MUST use the pipeline pattern (`core/pipeline/`) with discrete, single-responsibility steps. Each step MUST be independently testable and operate on an immutable context object.

**Rationale**: Enforces modularity, enables conditional execution, simplifies debugging, and allows step reordering without cascading changes.

### IV. DocumentUnit Immutability

The DocumentUnit abstraction MUST maintain immutable Excel row ↔ PDF page range relationships throughout processing. Any transformation MUST preserve this binding to prevent data corruption.

**Rationale**: Critical business constraint—losing the Excel-PDF relationship would corrupt document ordering and bookmark synchronization.

### V. PEP 8 Compliance & Code Quality

All code MUST follow PEP 8. MUST apply SOLID and DRY principles. MUST NOT add speculative "future-proofing" code. MUST write minimal, sufficient implementations. MUST preserve existing comments.

**Rationale**: Maintains readability, reduces cognitive load, prevents premature abstraction, and keeps codebase maintainable by enforcing consistent style.

## Quality Standards

### Testing Requirements

- All new features MUST have pytest tests in appropriate directories (`tests/core/`, `tests/adapters/`, `tests/integration/`)
- Pipeline steps MUST have isolated unit tests
- Integration tests MUST verify DocumentUnit workflow end-to-end
- Tests MUST NOT depend on external files (use fixtures or mocks)

### Error Handling

- All user-facing errors MUST be logged through the `Logger` protocol
- File operation failures MUST provide actionable error messages
- Pipeline failures MUST rollback to backup state when backups are enabled
- MUST validate Excel column requirements before processing

### Documentation

- All public functions and classes MUST have docstrings
- Complex algorithms (sorting, renumbering) MUST include inline comments
- Repository root MUST maintain up-to-date README.md
- Breaking changes MUST be documented in commit messages

### Version Management

- Application version MUST be stored in a single source of truth file (`_version.py` at project root)
- Version MUST follow semantic versioning format: `MAJOR.MINOR.PATCH` (e.g., "1.0.0")
- Version MUST be displayed in multiple locations for user visibility:
  - GUI window title: "Abstract Renumber Tool v{VERSION}"
  - GUI footer: "Version {VERSION}" (bottom-right, gray text)
  - Build artifacts: Executable named "AbstractRenumberTool-v{VERSION}.exe"
- All version displays MUST import from `_version.py` (no hardcoded version strings)
- **Code changes MUST trigger version increments** in `_version.py` according to semantic versioning rules:
  - **MAJOR**: Breaking changes affecting user workflows (UI redesigns, removed features, incompatible changes)
  - **MINOR**: New features that are backward compatible (new options, enhancements, additional functionality)
  - **PATCH**: Bug fixes and minor improvements (error corrections, performance tweaks, documentation updates)
- Version increment MUST occur before building distribution artifacts
- Version updates MUST be committed with descriptive message: `chore: bump version to X.Y.Z`
- Build scripts MUST automatically read version from `_version.py` for artifact naming
- Application MUST handle missing or invalid version gracefully with fallback to "Unknown"

**Rationale**: Single source of truth prevents version inconsistencies across displays. Semantic versioning communicates change impact to users. Mandatory version increments for code changes ensure users can identify which release they're running and track changes over time. Automatic propagation eliminates manual update errors. Graceful fallback ensures application stability even with version file issues.

## Development Workflow

### Code Organization

- Core business logic: `core/`
- External adapters: `adapters/`
- Application entry points: `app/`
- Tests mirror source structure: `tests/`
- Shared utilities: `utils/`
- Version information: `_version.py` (project root)

### Dependency Management

- Python 3.7+ required (specify `python3` in all commands)
- Dependencies tracked in `requirements.txt` with versions
- No implicit dependencies—all imports MUST be explicit

### Feature Development

1. Define protocols in `core/interfaces.py` if new contracts needed
2. Implement business logic in `core/services/` or `core/pipeline/steps/`
3. Create adapters in `adapters/` for external integrations
4. Add UI components in `app/` or `adapters/ui_*.py`
5. Write tests covering happy path and edge cases
6. Update version in `_version.py` if releasing:
   - PATCH for bug fixes (X.Y.Z → X.Y.Z+1)
   - MINOR for new features (X.Y.Z → X.Y+1.0)
   - MAJOR for breaking changes (X.Y.Z → X+1.0.0)

## Governance

### Amendment Process

This constitution supersedes all other development practices. Amendments require:
1. Documented justification in git commit message
2. Version bump per semantic versioning (see below)
3. Update to all dependent templates (`plan-template.md`, `spec-template.md`, `tasks-template.md`)
4. Sync Impact Report prepended to this file (as HTML comment)

### Versioning Policy

- **MAJOR** (X.0.0): Remove/redefine a core principle or add mandatory architectural constraint
- **MINOR** (x.Y.0): Add new principle, expand quality standard, introduce new workflow requirement
- **PATCH** (x.y.Z): Clarifications, typo fixes, wording improvements without semantic change

### Compliance Review

- All pull requests MUST verify compliance with core principles
- Code reviews MUST check for PEP 8 violations, dependency direction, and protocol usage
- Complexity MUST be justified if deviating from principles (document in plan.md)

**Version**: 1.1.1 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-20
