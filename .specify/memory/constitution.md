<!--
Sync Impact Report (Version: 2.0.0)
===========================================
Version Change: 1.0.0 → 2.0.0 (MAJOR)
Bump Rationale: Removed NON-NEGOTIABLE principle (Test-First Development) and fundamentally 
changed interface architecture from multi-interface to Tkinter-only local deployment

Modified Principles:
  - III. Test-First Development → REMOVED (No longer required)
  - IV. Memory Efficiency → Updated to remove Streamlit-specific references
  - VII. Multiple Interface Options → VI. Local Desktop Interface (Tkinter-only)

Removed Sections:
  - Streamlit web interface references throughout
  - Cloud deployment (DigitalOcean) references
  - Web interface file size limits and ZIP creation mentions

Added Guidance:
  - Testing now optional/recommended rather than mandatory
  - Focus on local desktop deployment only
  - Simplified interface architecture

Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Constitution Check updated to reflect 6 principles
  ✅ .specify/templates/spec-template.md - Architecture Requirements updated
  ✅ .specify/templates/tasks-template.md - Test-first tasks made optional, removed web-specific tasks

Follow-up TODOs: None
===========================================
-->

# Abstract Renumber Tool Constitution

## Core Principles

### I. Clean Architecture (NON-NEGOTIABLE)
**Core business logic MUST remain independent of external frameworks and interfaces.**

- All business logic resides in `core/` directory
- External concerns (UI, file I/O, frameworks) belong in `adapters/`
- Dependencies flow inward: adapters depend on core, never the reverse
- All external interfaces defined via Protocol classes in `core/interfaces.py`
- Dependency injection enforced through protocol-based interfaces

**Rationale**: Enables independent testing, framework swapping, and long-term maintainability by preventing coupling between business rules and external systems.

### II. Pipeline Processing Pattern
**Complex workflows MUST be decomposed into discrete, testable pipeline steps.**

- Each processing step is a separate class implementing `PipelineStep` protocol
- Steps have clear inputs/outputs for independent testing
- Pipeline context (`core/pipeline/context.py`) carries state between steps
- Steps can be conditionally executed based on configuration
- All steps located in `core/pipeline/steps/` with descriptive names

**Rationale**: Ensures workflow clarity, enables step-level testing, and simplifies debugging by isolating transformation logic into single-responsibility components.

### III. Memory Efficiency
**The application MUST handle large files (up to 400MB) without memory leaks or crashes.**

- Explicitly clear large objects (DataFrames, PDFs) after processing
- Use `gc.collect()` to force garbage collection after heavy operations
- For Linux systems, use `malloc_trim(0)` to return memory to OS
- Monitor memory with `psutil` during critical operations
- Document memory spikes and their causes in code comments

**Rationale**: Large PDF/Excel files can cause out-of-memory crashes if memory is not actively managed. Proper cleanup ensures stable operation with large datasets.

### IV. Immutable Data Relationships
**DocumentUnit instances MUST maintain immutable Excel row ↔ PDF page range relationships.**

- DocumentUnit objects created once during load step
- No modification of existing DocumentUnit instances after creation
- Transformations create new DocumentUnit instances rather than mutating
- All DocumentUnit operations are pure functions without side effects

**Rationale**: Prevents data corruption during sorting and reordering operations. Immutability guarantees that original document relationships cannot be accidentally broken.

### V. PEP 8 & Code Quality
**All Python code MUST follow PEP 8 style guidelines and SOLID/DRY principles.**

- Use `python3` explicitly (Linux environment)
- Imports MUST be at top level only
- Minimize line count: write only necessary code, no future-proofing
- Apply SOLID principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- Apply DRY: No code duplication, extract common logic into reusable functions
- Preserve existing comments when refactoring

**Rationale**: Consistent code style improves readability and maintainability. SOLID/DRY principles reduce technical debt and increase code flexibility.

### VI. Local Desktop Interface
**The application is a local-only desktop tool using Tkinter for the user interface.**

- Business logic in `core/` is UI-agnostic
- Tkinter UI adapter in `adapters/ui_tkinter.py`
- Entry point: `main.py`
- Configuration handled via `core/config.py` and environment variables
- No web interfaces or remote deployment

**Rationale**: Focus on local desktop usage provides direct file system access, eliminates upload/download overhead, and simplifies deployment for single-user scenarios.

## Development Workflow

### Code Review Requirements
- No commented-out code (delete instead, git preserves history)
- Linter errors MUST be fixed before commit
- Complex logic changes SHOULD include tests (recommended but not mandatory)

### Testing Approach
- Tests are RECOMMENDED but not required for all changes
- Existing test suite (pytest) SHOULD be maintained and run before releases
- Test organization mirrors source structure (`tests/core/`, `tests/adapters/`)
- Use `python3 -m pytest` to run tests when available

### Documentation Standards
- Update README.md when adding features or changing user-facing behavior
- Document complex algorithms inline with clear comments
- Keep MEMORY_ANALYSIS.md updated with memory optimization findings
- Remove outdated deployment documentation (DEPLOYMENT.md) if web deployment no longer relevant

### Complexity Justification
- New abstractions MUST solve real, current problems (not hypothetical future needs)
- Repository pattern justified: separates file I/O from business logic
- Pipeline pattern justified: multi-step workflow requires clear separation
- Tkinter adapter justified: clean separation between UI and business logic

## Performance & Scalability Standards

### File Size Limits
- Desktop interface: System-dependent (no artificial limits)
- Practical limit: ~400MB files recommended for reasonable performance
- Batch processing: Not currently supported (out of scope)

### Processing Performance
- Excel sorting: Linear time complexity O(n log n) for n rows
- PDF bookmark updates: Linear time complexity O(p) for p pages
- Memory usage: Should stay reasonable for typical file sizes (<2GB for 400MB files)
- Temporary memory spikes acceptable during processing operations

### Platform Support
- Primary: Linux (Ubuntu 22.04+)
- Secondary: Windows, macOS
- Python version: 3.7+ (3.11 recommended)
- Tkinter required: `sudo apt-get install python3-tk` on Linux

## Security & Data Integrity

### File Handling
- Create timestamped backups before modifying files
- Never overwrite original files without backup
- Validate Excel columns before processing (ValidateStep)
- Rollback to backup on processing failure

### Input Validation
- Required Excel columns: Index#, Document Type, Legal Description, Grantee, Grantor, Document Date, Received Date
- Column names are case-insensitive
- Date columns must be valid date types (not text)
- PDF must contain bookmarks

### Error Handling
- Detailed error messages with context
- Errors logged to stderr
- Pipeline stops on validation failures
- User-friendly error display in Tkinter UI

## Governance

### Constitution Authority
This constitution supersedes all other development practices and conventions. When conflicts arise, constitution principles take precedence.

### Amendment Process
1. Propose amendment with rationale and impact analysis
2. Update constitution version following semantic versioning:
   - **MAJOR**: Backward-incompatible principle removals or redefinitions
   - **MINOR**: New principles added or materially expanded guidance
   - **PATCH**: Clarifications, wording fixes, non-semantic refinements
3. Update dependent templates (plan, spec, tasks)
4. Document changes in Sync Impact Report
5. Update `LAST_AMENDED_DATE` to today

### Compliance Review
- All pull requests SHOULD verify compliance with constitution principles
- Constitution violations MUST be justified in Complexity Tracking section of plan.md
- Simpler alternatives MUST be documented when introducing new patterns
- Memory optimizations SHOULD be documented in code and MEMORY_ANALYSIS.md

### Version History
Refer to git history for detailed constitution change log.

**Version**: 2.0.0 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-19
