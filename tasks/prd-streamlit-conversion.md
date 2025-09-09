# Product Requirements Document: Streamlit Web Interface Conversion

## Introduction/Overview

Convert the existing Tkinter-based Abstract Renumber Tool to a modern web-based interface using Streamlit. This conversion will provide web accessibility and improved user experience while maintaining all existing functionality for Excel and PDF document processing. The tool automates sorting Excel data and renumbering corresponding PDF bookmarks, maintaining synchronized numbering when documents need reordering.

**Problem Solved:** Current desktop application limits accessibility and deployment options. Users need web access and a more intuitive interface for document processing workflows.

**Goal:** Create a web-accessible version of the Abstract Renumber Tool with improved UX, easier deployment via Streamlit Cloud, and enhanced workflow for multi-file merge operations.

## Goals

1. **Web Accessibility**: Enable users to access the tool through any web browser
2. **Improved User Experience**: Provide modern, intuitive interface with better visual feedback
3. **Simplified Deployment**: Deploy easily via Streamlit Cloud without complex setup
4. **Enhanced Multi-File Workflow**: Improve the merge functionality with better file management
5. **Maintain Core Functionality**: Preserve all existing document processing capabilities
6. **Streamlined File Handling**: Provide processed files with clear naming, no backup creation needed

## User Stories

**As a document processor, I want to:**
- Access the tool from any computer with a web browser so I can work remotely
- Upload Excel and PDF files via drag-and-drop so the process feels modern and intuitive
- See real-time progress updates so I know the processing status
- Choose between single-file and multi-file merge workflows so I can handle different scenarios efficiently
- Download processed files with clear naming (e.g., `original_file_name_processed.xlsx`) so I can distinguish them from originals
- Get immediate feedback on validation errors so I can fix issues quickly

**As an administrator, I want to:**
- Deploy the application to Streamlit Cloud so users can access it without installation
- Maintain the existing processing logic so results remain consistent
- Keep existing backup code available for future use even though web version won't use it

## Functional Requirements

### Core Architecture Requirements
1. **Preserve Existing Backend**: Maintain all existing core processing logic, pipeline architecture, and interfaces
2. **Create Streamlit UI Adapter**: Implement `StreamlitUIAdapter` class that satisfies the existing `UIController` interface
3. **Maintain Processing Pipeline**: Keep the existing `RenumberService`, `Pipeline`, and all processing steps unchanged
4. **Preserve Backup Code**: Keep existing backup functionality in codebase but disable for Streamlit version

### Multi-Page Application Structure
5. **Navigation System**: Implement sidebar navigation between application pages
6. **Mode Selection Page**: Create landing page where users choose "Single File Processing" or "Merge Multiple Files"
7. **Single File Processing Page**: Dedicated page for standard single Excel/PDF processing workflow
8. **Multi-File Merge Page**: Specialized page for handling multiple file pairs with enhanced UX

### File Handling Requirements
9. **File Upload Interface**: Implement drag-and-drop file uploaders for Excel (.xlsx, .xls) and PDF files with 400MB limit
10. **File Validation**: Provide immediate feedback on file type, size (max 400MB per file), and format validation
11. **Temporary File Management**: Handle uploaded files by saving to temporary locations for processing
12. **Processed File Downloads**: Provide download buttons for processed files with `_processed` suffix (e.g., `original_file_name_processed.xlsx`, `original_file_name_processed.pdf`)
13. **No Backup Creation**: Disable backup functionality for web version since users retain originals locally

### User Interface Requirements
14. **Processing Options Sidebar**: Move all processing options (sort bookmarks, reorder pages, etc.) to sidebar, excluding backup option
15. **Real-Time Status Updates**: Display processing progress with status messages and progress bars
17. **Error Display**: Show validation errors and processing errors in user-friendly format
18. **Success Feedback**: Provide clear success messages with download links

### Single File Processing Workflow
19. **Guided Upload Process**: Step-by-step file upload with validation feedback including file size limits
20. **Sheet Selection**: Dropdown interface for Excel sheet selection when default not found
21. **Filter Configuration**: Interactive column and value selection for data filtering
22. **Options Configuration**: Sidebar checkboxes and controls for processing options (excluding backup)
23. **Process Execution**: Single button to start processing with real-time feedback

### Multi-File Merge Workflow
24. **File Pair Management**: Interface to add/remove Excel-PDF file pairs
25. **Batch Upload Support**: Allow multiple file uploads simultaneously
26. **Pair Validation**: Validate each file pair before processing
27. **Sheet Selection Per File**: Handle sheet selection for each Excel file in merge
28. **Merge Preview**: Show summary of files to be merged before processing

### Processing Features
29. **Filter Prompting**: Interactive filtering interface using merged data for value selection
30. **Progress Tracking**: Step-by-step progress indication during pipeline execution
31. **Error Recovery**: Clear error messages with suggestions for resolution
32. **Session State Management**: Maintain user selections and progress across page interactions

## Non-Goals (Out of Scope)

1. **Backup File Creation**: No backup files created in web version (users have originals locally)
2. **Local File System Integration**: No direct file system access beyond temporary processing
3. **User Authentication**: No login or user management system
4. **File Storage**: No permanent file storage or user file history
5. **Advanced Data Visualization**: No charts, graphs, or data preview features
6. **Mobile Optimization**: Focus on desktop/tablet experience, basic mobile compatibility only
7. **Real-Time Collaboration**: No multi-user or collaborative features
8. **API Integration**: No external service integrations
9. **Custom Themes**: Use default Streamlit styling
10. **Architecture Changes**: No modifications to existing core processing logic or pipeline structure

## Design Considerations

### Page Layout Structure
- **Sidebar Navigation**: Always-visible navigation between pages with current page highlighting
- **Main Content Area**: Full-width content area for file uploads and processing interface
- **Options Sidebar**: Collapsible sidebar on right for processing options and settings
- **Status Area**: Fixed bottom area or expandable section for processing logs and status

### File Upload Interface
- **Drag-and-Drop Zones**: Large, clearly labeled upload areas for Excel and PDF files
- **File Information Display**: Show uploaded file names, sizes, and validation status
- **Upload Progress**: Visual feedback during file upload process
- **Error States**: Clear visual indication of file validation errors

### Multi-File Merge Interface
- **File Pair Cards**: Visual cards showing each Excel-PDF pair with remove option
- **Add Pair Button**: Prominent button to add new file pairs
- **Batch Actions**: Options to clear all pairs or validate all pairs
- **Processing Summary**: Overview of total files and estimated processing time

### File Download Interface
- **Clear Naming Convention**: Processed files named with `_processed` suffix (e.g., `document_processed.xlsx`)
- **Download Buttons**: Prominent download buttons for each processed file
- **File Size Display**: Show processed file sizes before download
- **Batch Download**: Option to download all processed files as ZIP when multiple files

## Technical Considerations

### Streamlit-Specific Implementation
- **Session State**: Use `st.session_state` for maintaining user selections and processing status
- **File Handling**: Implement temporary file management for uploaded files using `tempfile` module
- **Progress Updates**: Use `st.progress()`, `st.status()`, and `st.empty()` containers for real-time updates
- **Error Handling**: Leverage `st.error()`, `st.warning()`, and `st.success()` for user feedback

### Architecture Integration
- **Minimal Backend Changes**: Only create new `StreamlitUIAdapter` and modify main entry point
- **Interface Compliance**: Ensure `StreamlitUIAdapter` fully implements existing `UIController` protocol
- **Dependency Injection**: Maintain existing dependency injection pattern in `AppController`
- **Backup Code Preservation**: Keep existing backup functionality but set `backup=False` in Options for Streamlit

### Deployment Considerations
- **Streamlit Cloud Compatibility**: Ensure all dependencies are compatible with Streamlit Cloud
- **File Size Limits**: Configure 400MB per file limit via `.streamlit/config.toml` (required for deployment)
- **Memory Management**: Optimize for Streamlit Cloud's memory constraints (files stored in RAM during processing)
- **Requirements**: Add `streamlit` to requirements.txt, maintain existing dependencies
- **Configuration**: Create `.streamlit/config.toml` with 400MB upload limit (mandatory for deployment)

## Success Metrics

### User Experience Metrics
1. **Accessibility Improvement**: Users can access tool from any device with web browser
2. **Deployment Simplification**: Reduce deployment complexity from local installation to simple URL access
4. **Error Recovery**: Improve error message clarity and user ability to resolve issues

### Technical Metrics
1. **Feature Parity**: 100% of existing Tkinter functionality available in Streamlit version (excluding backups)
2. **Processing Consistency**: Identical output files compared to Tkinter version
4. **Reliability**: Successful deployment and operation on Streamlit Cloud


## Open Questions

1. **Memory Optimization**: How should we handle memory usage when processing multiple large files (400MB each) simultaneously?
2. **Session Timeout**: How should we handle long processing times and potential session timeouts?
3. **Concurrent Users**: Are there any considerations for multiple users processing files simultaneously?
4. **Error Logging**: Should we implement any server-side error logging for debugging purposes?
6. **User Training**: Will users need training materials for the new web interface?
7. **File Naming Convention**: Confirm `original_file_name_processed.xlsx` format meets user expectations for all file types?
