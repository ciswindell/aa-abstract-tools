# Feature Specification: Reduce Excessive Info Logging

**Feature Branch**: `003-reduce-info-logging`  
**Created**: 2025-11-19  
**Status**: Draft  
**Input**: User description: "most of the info messages are junk and need to be removed from the codebase"

## Clarifications

### Session 2025-11-19

- Q: How should developers/advanced users access detailed logging when troubleshooting issues? → A: No UI toggle; developers view verbose logs in console/terminal or log files only. UI stays clean for all users.
- Q: How should the system display progress during long-running operations? → A: Phase-based with count - Show "Step 3 of 7: Sorting..." style messages. Clear, contextual, non-technical.
- Q: Should console/terminal and log files receive ALL log messages (including those filtered from the UI), or should they also be cleaned up? → A: Output ALL messages to console/files - Complete logging preserved. UI filters what users see, but developers get full technical details in logs.
- Q: What qualifies as a "major phase" that should be shown in the UI versus an internal sub-step that should be hidden? → A: Pipeline steps/stages - Top-level steps in the processing pipeline (e.g., ValidateStep, LoadStep, SortStep, SaveStep). Clear architectural boundaries.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Clean Status Feedback (Priority: P1)

As a **non-technical user** processing files through the application, I want to see **only essential status updates** in the feedback area, so that I can **quickly understand what's happening without being overwhelmed by technical details**.

**Why this priority**: This is the core value proposition - users are currently experiencing information overload with 80+ log messages per operation. Reducing clutter directly improves usability and user confidence. This addresses the primary complaint that "most of the info messages are junk."

**Independent Test**: Can be fully tested by running a file processing operation and verifying that the status area shows only 5-10 high-level messages instead of 80+ verbose technical messages, while still conveying all necessary information about progress and completion.

**Acceptance Scenarios**:

1. **Given** a file processing operation is started, **When** the user views the status area, **Then** they see only high-level milestone messages like "Starting processing...", "Validating files...", "Processing files...", "Processing complete" (approximately 5-10 messages total)

2. **Given** files are being processed, **When** the operation progresses through multiple internal steps, **Then** the user does NOT see verbose technical messages about internal phases, data structure operations, or low-level validation details

3. **Given** an error occurs during processing, **When** the error is displayed, **Then** the error message is still shown with full context and user-friendly explanation (error messages are NOT reduced)

4. **Given** a successful operation completes, **When** the user views the final status, **Then** they see a clear success message with key outcome metrics (e.g., "Processing complete: 67 documents processed, 126 pages")

---

### User Story 2 - Preserve Critical Information (Priority: P1)

As a **user troubleshooting issues**, I want **all errors, warnings, and operation outcomes** to remain visible in the status area, so that I can **understand what went wrong or what succeeded without losing important information**.

**Why this priority**: While reducing verbose INFO messages, we must preserve all critical information that helps users understand errors, warnings, and results. This ensures the cleanup doesn't harm the user's ability to troubleshoot or verify outcomes.

**Independent Test**: Can be tested by triggering error conditions, warnings, and successful operations, then verifying that all ERROR, WARNING, and SUCCESS messages still appear in the status area with their original clarity and detail.

**Acceptance Scenarios**:

1. **Given** an error occurs (e.g., file not found, permission denied), **When** the error is logged, **Then** the error message appears in red with full user-friendly explanation (unchanged from current behavior)

2. **Given** a warning condition occurs (e.g., missing data, skipped items), **When** the warning is logged, **Then** the warning message appears in orange with clear context (unchanged from current behavior)

3. **Given** an operation completes successfully, **When** the success status is shown, **Then** the success message appears in green with outcome summary (unchanged from current behavior)

4. **Given** the user needs to understand operation results, **When** they view the status area after completion, **Then** they see key metrics like number of items processed, time taken, or items created/updated

---

### User Story 3 - Understand Operation Progress (Priority: P2)

As a **user running a long operation**, I want to see **high-level progress indicators** for major phases, so that I can **know the operation is progressing and estimate completion time without seeing every internal step**.

**Why this priority**: Long-running operations need progress feedback to prevent user anxiety and confusion. However, this feedback should be at a meaningful granularity (phases/stages) rather than individual technical steps.

**Independent Test**: Can be tested by running a multi-phase operation and verifying that the status area shows phase transitions (e.g., "Validating files...", "Loading data...", "Sorting...", "Saving outputs...") at 5-10 second intervals or major milestones, without showing every sub-step.

**Acceptance Scenarios**:

1. **Given** a multi-phase operation is running, **When** the operation transitions between major phases, **Then** the user sees phase transition messages in the format "Step X of Y: [Phase Name]..." (e.g., "Step 1 of 7: Validating files...", "Step 3 of 7: Processing data...", "Step 7 of 7: Saving results...")

2. **Given** the operation is within a single phase, **When** internal sub-steps are executing, **Then** the user does NOT see verbose messages about each sub-step (e.g., individual validation checks, data structure operations, internal counters)

3. **Given** an operation starts, **When** the user views the initial status, **Then** they see an operation separator line (if multiple operations) followed by "Starting processing..." or similar high-level message

4. **Given** the operation is running, **When** the user monitors progress, **Then** they see messages appearing at a reasonable cadence (every 5-10 seconds for long operations, not multiple per second)

---

### Edge Cases

- **What happens when logging configuration is unclear?** System should default to conservative approach (keep more messages rather than accidentally hiding critical info)
- **What happens if verbose logging is needed for debugging?** Developers and advanced users should use console/terminal output or log files for verbose debugging. The UI will not provide a verbose mode toggle, keeping the interface clean and focused on end-users.
- **What happens to existing log levels (DEBUG, INFO, etc.)?** INFO level should be reserved for user-facing milestone messages; internal technical details should use DEBUG level (which isn't shown in UI)
- **How are progress indicators shown for long operations?** System uses phase-based progress with step count format (e.g., "Step 3 of 7: Sorting...") which provides clear context about current phase and overall progress without technical percentage calculations.
- **What qualifies as a "major phase" versus internal sub-step?** Major phases are top-level pipeline steps/stages (e.g., ValidateStep, LoadStep, SortStep, SaveStep) that represent distinct architectural boundaries in the processing workflow. Internal operations within these steps (e.g., "Phase A: Filtering", "Phase B: Reordering", individual validation checks) are considered sub-steps and should be filtered from the UI.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST reduce INFO-level messages in the UI status area to only high-level milestones and phase transitions (approximately 5-10 messages per operation instead of 80+)

- **FR-002**: System MUST preserve ALL error messages (ERROR level) in the UI status area with their current user-friendly formatting and red bold styling

- **FR-003**: System MUST preserve ALL warning messages (WARNING level) in the UI status area with their current orange styling

- **FR-004**: System MUST preserve ALL success messages (SUCCESS level) in the UI status area with their current green bold styling

- **FR-005**: System MUST show operation start messages (e.g., "Starting processing...") for each new operation with visual separator

- **FR-006**: System MUST show operation completion messages (e.g., "Processing complete") with summary metrics (e.g., items processed, time taken)

- **FR-007**: System MUST show major phase transition messages for top-level pipeline steps/stages using the format "Step X of Y: [Phase Name]..." (e.g., "Step 1 of 7: Validating files...", "Step 3 of 7: Sorting...", "Step 7 of 7: Saving outputs..."). Major phases are defined as pipeline steps with clear architectural boundaries (e.g., ValidateStep, LoadStep, SortStep, SaveStep), not internal sub-operations within those steps

- **FR-008**: System MUST NOT show verbose technical messages about internal implementation details (e.g., "Phase A: Filtering DocumentUnits", "INFO: Created 67 DocumentUnits from...", "INFO: About to sort 91 rows from...")

- **FR-009**: System MUST NOT show progress messages for individual items being processed (e.g., "Processing item 1 of 100", "Loading row 5", "Validating bookmark 23")

- **FR-010**: System MUST maintain message history management (500 message limit with auto-trim) to prevent UI performance degradation

- **FR-011**: System MUST maintain timestamp formatting (HH:MM:SS) for all messages shown in the UI

- **FR-012**: System MUST maintain auto-scroll behavior to always show the latest message

- **FR-013**: System MUST output ALL log messages (INFO, DEBUG, ERROR, WARNING, SUCCESS) to console/terminal and log files without filtering. Only the UI status area applies the message reduction; console/file logs preserve complete technical details for developer debugging and auditing

### Key Entities

- **Log Message**: Represents a status update shown to the user, with attributes:
  - **Type**: INFO, ERROR, WARNING, SUCCESS, DEBUG
  - **Content**: User-facing text describing the status or outcome
  - **Timestamp**: When the message was created
  - **UI Visibility**: Whether the message should appear in UI status area (high-level milestones, errors, warnings, success) or be filtered to console/file logs only (verbose technical details, DEBUG messages)

- **Operation Phase**: Represents a major stage in the processing workflow, defined as a top-level pipeline step with clear architectural boundary, with attributes:
  - **Name**: User-friendly phase name (e.g., "Validating Files", "Loading Data", "Sorting", "Saving Outputs")
  - **Step Number**: Current phase position in sequence (e.g., step 3 of 7)
  - **Start/End Status**: Messages shown when phase begins and completes
  - **Duration**: Time taken for the phase (optional for summary)
  - **Scope**: Pipeline-level step (e.g., ValidateStep, LoadStep, SortStep), not internal sub-operations

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Status area shows 5-10 messages per operation instead of 80+ messages (85-90% reduction in message volume)

- **SC-002**: Users can understand operation progress and completion status by reading only the messages in the status area (validated through user testing or feedback)

- **SC-003**: All errors and warnings remain visible in the status area with clear, actionable information (100% preservation of ERROR and WARNING messages)

- **SC-004**: Operation completion time remains unchanged (performance is not negatively impacted by logging changes)

- **SC-005**: Users report improved clarity and reduced information overload (qualitative feedback or survey showing positive response)

- **SC-006**: Status messages appear at a reasonable cadence (no more than 1-2 messages per second during peak operation phases)

- **SC-007**: Zero loss of critical information - all necessary context for understanding success, failure, or warnings is preserved in the reduced message set

- **SC-008**: Console/terminal and log files contain 100% of all log messages (no filtering applied), preserving complete technical details for developer debugging and system auditing
