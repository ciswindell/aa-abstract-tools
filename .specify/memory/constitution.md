<!--
  SYNC IMPACT REPORT
  Version: 0.0.0 → 1.0.0 (Initial Constitution)
  Date: 2025-11-19
  
  Changes:
  - Initial constitution ratification
  - Defined 5 core principles for Abstract Renumber Tool
  - Established quality standards and development workflow
  - Set governance rules
  
  Template Updates Required:
  ✅ plan-template.md - Updated constitution check section
  ✅ spec-template.md - No changes needed (already aligned)
  ✅ tasks-template.md - No changes needed (already aligned)
  
  Follow-up TODOs:
  - None (all placeholders filled)
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

## Development Workflow

### Code Organization

- Core business logic: `core/`
- External adapters: `adapters/`
- Application entry points: `app/`
- Tests mirror source structure: `tests/`
- Shared utilities: `utils/`

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

**Version**: 1.0.0 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-19
