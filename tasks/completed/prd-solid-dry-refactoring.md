# Product Requirements Document: SOLID/DRY Refactoring for Abstract Renumber Tool

## Introduction/Overview

The Abstract Renumber Tool currently works well for its primary use case of renumbering PDF bookmarks based on sorted Excel data. However, the codebase has accumulated technical debt that violates SOLID principles and contains code duplication (DRY violations). This refactoring will prepare the system for upcoming workflows including Excel filtering, combining multiple spreadsheets, and additional processing rules while maintaining all existing functionality.

**Key Principle: Keep It Simple**. This refactoring prioritizes clean, readable code over complex patterns. We will avoid over-engineering and focus on practical improvements that make the code easier to understand and extend.

## Goals

1. **Improve Code Maintainability**: Refactor to follow SOLID principles for easier maintenance and debugging
2. **Eliminate Code Duplication**: Apply DRY principle to reduce duplicate code patterns
3. **Enable Easy Extension**: Create a modular architecture that allows adding new workflows without modifying existing code
4. **Preserve Existing Functionality**: Maintain 100% backward compatibility with current features
5. **Prepare for Future Workflows**: Create abstractions that support filtering, combining spreadsheets, and custom processing rules
6. **Maintain Simplicity**: Avoid code bloat - no excessive validation, logging, or overly complex patterns

## User Stories

1. **As a developer**, I want to add a new Excel filtering workflow without modifying existing processing logic, so that I can extend functionality safely
2. **As a developer**, I want to combine multiple Excel files before renumbering without duplicating file handling code, so that I can reuse existing components
3. **As a developer**, I want to add custom processing rules that integrate seamlessly with the existing pipeline, so that the system remains cohesive
4. **As an end user**, I want all existing functionality to work exactly as before, so that my workflow is not disrupted
5. **As a maintainer**, I want clear separation of concerns between GUI, business logic, and file operations, so that bugs are easier to isolate and fix

## Functional Requirements

### Core Architecture Requirements
1. **Workflow Abstraction**: Create a `WorkflowProcessor` interface that defines the standard processing pipeline
2. **Strategy Pattern Implementation**: Implement different processing strategies (current renumbering, filtering, combining) as separate classes
3. **Dependency Injection**: Use dependency injection to decouple components and enable easy testing
4. **Single Responsibility**: Each class should have one clear responsibility (GUI, file handling, data processing, etc.)
5. **Factory Pattern**: Create factories for instantiating different workflow types

### Specific Refactoring Requirements
6. **Separate GUI from Business Logic**: Extract all business logic from `AbstractRenumberGUI` into dedicated service classes
7. **Create File Handler Abstraction**: Abstract file operations (backup, save, load) into reusable components
8. **Implement Validation Chain**: Create a validation pipeline that can be extended with new rules
9. **Extract Configuration Management**: Move configuration logic into a dedicated configuration service
10. **Create Event System**: Implement observer pattern for status updates and progress tracking

### Extensibility Requirements
11. **Plugin Architecture**: Design system to support adding new workflow plugins without code changes
12. **Configurable Processing Pipeline**: Allow workflows to define their own processing steps
13. **Flexible Data Transformation**: Support different data transformation rules for different document types
14. **Modular Validation**: Enable adding new validation rules without modifying existing validators

## Non-Goals (Out of Scope)

1. **UI/UX Changes**: No changes to the existing user interface or user experience
2. **New Features**: No new end-user features in this refactoring (filtering/combining come later)
3. **Performance Optimization**: Focus is on code quality, not performance improvements
4. **Database Integration**: No database or persistence layer changes
5. **Configuration File Format**: No changes to how configuration is stored or loaded
6. **Excessive Logging**: No comprehensive logging system - keep current simple status updates
7. **Complex Validation**: No over-engineered validation frameworks - use simple, direct validation
8. **Enterprise Patterns**: Avoid heavy enterprise patterns that add complexity without clear benefit

## Design Considerations

### Architectural Patterns to Implement
- **Strategy Pattern**: For different processing workflows (simple implementation)
- **Factory Pattern**: For creating workflow instances (basic factory, not abstract factory)
- **Observer Pattern**: For status updates (simple event callbacks, not complex pub/sub)
- **Template Method Pattern**: For common processing steps (straightforward inheritance)

**Note**: Use these patterns only where they clearly simplify the code. Avoid pattern overuse.

### Key Abstractions
- `WorkflowProcessor`: Base interface for all processing workflows (simple ABC)
- `FileHandler`: Abstract file operations (basic file ops, not complex file system abstraction)
- `DataValidator`: Simple validation functions (not a framework)
- `StatusNotifier`: Basic event callbacks for UI updates
- `ConfigurationService`: Simple configuration holder (not dependency injection container)

### Simplicity Guidelines
- **Prefer composition over complex inheritance hierarchies**
- **Use simple functions instead of classes where appropriate**
- **Keep interfaces minimal - only essential methods**
- **Avoid deep nesting of abstractions**
- **Use direct, readable code over clever implementations**

## Technical Considerations

### Dependencies
- Maintain existing dependencies (pandas, PyPDF2, openpyxl, tkinter)
- **No new dependencies** unless absolutely necessary
- Avoid heavy frameworks or complex libraries

### Code Organization
- Create simple `src/` directory structure with logical modules
- Keep interfaces minimal and focused
- Use type hints consistently but don't over-complicate
- Write clear docstrings for public methods only

### Testing Considerations
- Design classes to be easily testable through simple dependency injection
- Keep testing strategy simple - focus on core business logic
- Avoid complex mocking frameworks

## Success Metrics

### Code Quality Metrics
1. **Cyclomatic Complexity**: Reduce average method complexity from current ~8 to <5
2. **Class Responsibilities**: Each class should have single, clear responsibility
3. **Code Duplication**: Eliminate duplicate code blocks >10 lines
4. **Coupling**: Reduce tight coupling between modules
5. **Code Readability**: Junior developer can understand any module in <10 minutes

### Extensibility Metrics
6. **New Workflow Addition**: Should be possible to add new workflow in <50 lines of code
7. **Validation Rules**: Should be able to add new validation without modifying existing validators
8. **File Format Support**: Architecture should support adding new file formats easily

### Functional Metrics
9. **Backward Compatibility**: 100% of existing functionality preserved
10. **Error Handling**: Clear, simple error messages (no complex error handling framework)
11. **Performance**: No significant performance degradation (within 10% of current)

## Open Questions

1. **Workflow Configuration**: Should workflows be configurable through simple dictionaries or code-only?
2. **Error Recovery**: What minimal level of error recovery should be built in?
3. **Type System**: Should we use simple ABC classes or basic inheritance?
4. **Testing Strategy**: Should we add basic unit tests or focus purely on refactoring?

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Create simple base classes and interfaces
- Extract basic configuration management
- **Avoid**: Complex dependency injection, extensive logging setup

### Phase 2: Core Refactoring (Week 2-3)
- Refactor existing classes to follow SOLID principles simply
- Implement basic strategy pattern for current workflow
- Create straightforward file handling abstraction
- **Avoid**: Over-abstracting existing functionality

### Phase 3: Integration & Testing (Week 4)
- Integrate new simple architecture with existing GUI
- Basic testing of backward compatibility
- Minimal documentation updates
- **Avoid**: Complex integration patterns, extensive test suites

### Phase 4: Validation & Cleanup (Week 5)
- Code review focusing on simplicity
- Performance validation
- Simple examples and minimal documentation
- **Avoid**: Over-documenting, complex examples 