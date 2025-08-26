# Task List: SOLID/DRY Refactoring for Abstract Renumber Tool

## Relevant Files

- `src/interfaces/workflow_processor.py` - Base interface for all workflow processing strategies
- `src/interfaces/file_handler.py` - Interface for file operations (load, save, backup)
- `src/interfaces/status_notifier.py` - Interface for status update callbacks
- `src/services/file_service.py` - Service for handling file operations and backups
- `src/services/config_service.py` - Simple configuration management service
- `src/workflows/abstract_renumber_workflow.py` - Current renumbering workflow implementation
- `src/workflows/workflow_factory.py` - Factory for creating workflow instances
- `main.py` - Modified main application file (refactored GUI and controller)
- `excel_processor.py` - Refactored to follow single responsibility principle
- `pdf_processor.py` - Refactored to follow single responsibility principle
- `column_mapper.py` - Refactored for better separation of concerns

### Notes

- Keep new files simple and focused on single responsibilities
- Avoid over-abstracting existing functionality
- Maintain backward compatibility throughout the refactoring process
- Use basic inheritance and composition patterns, not complex enterprise patterns

## Tasks

- [ ] 1.0 Create Foundation Architecture
  - [ ] 1.1 Create `src/` directory structure with interfaces, services, and workflows folders
  - [ ] 1.2 Define `WorkflowProcessor` interface with essential methods only
  - [ ] 1.3 Create `FileHandler` interface for basic file operations (load, save, backup)
  - [ ] 1.4 Create `StatusNotifier` interface for simple callback-based status updates
  - [ ] 1.5 Create basic `ConfigService` class to hold configuration settings

- [ ] 2.0 Extract and Refactor Core Components
  - [ ] 2.1 Extract file handling logic from `AbstractRenumberTool` into `FileService`
  - [ ] 2.2 Refactor `ExcelProcessor` to focus only on Excel operations, remove GUI dependencies
  - [ ] 2.3 Refactor `PDFProcessor` to focus only on PDF operations, remove external dependencies
  - [ ] 2.4 Extract backup logic into reusable methods in `FileService`
  - [ ] 2.5 Remove duplicate error handling code and centralize in service classes

- [ ] 3.0 Implement Workflow Strategy Pattern
  - [ ] 3.1 Create `AbstractRenumberWorkflow` class implementing `WorkflowProcessor` interface
  - [ ] 3.2 Move current processing logic from `AbstractRenumberTool` into the workflow class
  - [ ] 3.3 Create simple `WorkflowFactory` to instantiate workflow types
  - [ ] 3.4 Update workflow to use injected services instead of direct file operations
  - [ ] 3.5 Implement basic validation chain within the workflow

- [ ] 4.0 Integrate New Architecture with Existing GUI
  - [ ] 4.1 Refactor `AbstractRenumberGUI` to remove business logic, keep only UI concerns
  - [ ] 4.2 Update `AbstractRenumberTool` controller to use workflow and services
  - [ ] 4.3 Implement simple dependency injection in the main controller
  - [ ] 4.4 Update status callback system to use new `StatusNotifier` interface
  - [ ] 4.5 Ensure all existing GUI functionality works with new architecture

- [ ] 5.0 Validate and Test Backward Compatibility
  - [ ] 5.1 Test all existing functionality works exactly as before
  - [ ] 5.2 Verify file selection, processing, and backup features are unchanged
  - [ ] 5.3 Test error handling and status updates work as expected
  - [ ] 5.4 Run performance validation to ensure no significant degradation
  - [ ] 5.5 Clean up any unused code and add basic documentation comments 