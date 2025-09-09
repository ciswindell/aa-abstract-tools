## Relevant Files

- `streamlit_main.py` - Main Streamlit application entry point with multi-page navigation
- `adapters/streamlit_ui.py` - Streamlit implementation of UIController interface
- `pages/mode_selection.py` - Landing page for choosing single file or merge workflow
- `pages/single_file_processing.py` - Single file processing workflow page
- `pages/multi_file_merge.py` - Multi-file merge workflow page
- `utils/streamlit_helpers.py` - Streamlit-specific utility functions for file handling and UI components
- `.streamlit/config.toml` - Streamlit configuration for 400MB file upload limit
- `requirements.txt` - Updated to include streamlit dependency

### Notes

- The existing core architecture (interfaces, pipeline, services) will remain unchanged
- Only UI layer components need to be created/modified
- Backup functionality will be disabled by setting `backup=False` in Options
- File naming will use `original_file_name_processed.xlsx` format

## Tasks

- [ ] 1.0 Setup Streamlit Infrastructure and Configuration
  - [ ] 1.1 Add `streamlit` to requirements.txt
  - [ ] 1.2 Create `.streamlit/config.toml` with 400MB upload limit configuration
  - [ ] 1.3 Create main Streamlit entry point `streamlit_main.py`
  - [ ] 1.4 Set up basic Streamlit page configuration and navigation structure
- [ ] 2.0 Create Streamlit UI Adapter Implementation
  - [ ] 2.1 Create `adapters/streamlit_ui.py` implementing UIController interface
  - [ ] 2.2 Implement `get_file_paths()` method using session state for uploaded files
  - [ ] 2.3 Implement `get_options()` method collecting settings from Streamlit widgets
  - [ ] 2.4 Implement `log_status()` method for displaying status messages
  - [ ] 2.5 Implement `show_error()` and `show_success()` methods using Streamlit alerts
  - [ ] 2.6 Implement `prompt_sheet_selection()` method using selectbox widget
  - [ ] 2.7 Implement `prompt_filter_selection()` method using column/multiselect widgets
  - [ ] 2.8 Implement `prompt_merge_pairs()` method for file pair management
  - [ ] 2.9 Implement `reset_gui()` method to clear session state
- [ ] 3.0 Build Multi-Page Application Structure
  - [ ] 3.1 Create `pages/mode_selection.py` for choosing single file vs merge workflow
  - [ ] 3.2 Create `pages/single_file_processing.py` for standard processing workflow
  - [ ] 3.3 Create `pages/multi_file_merge.py` for multi-file merge workflow
  - [ ] 3.4 Implement sidebar navigation between pages with current page highlighting
  - [ ] 3.5 Create shared processing options sidebar component
- [ ] 4.0 Implement File Upload and Processing Workflows
  - [ ] 4.1 Create file upload components with drag-and-drop support and 400MB validation
  - [ ] 4.2 Implement temporary file management for uploaded files using tempfile module
  - [ ] 4.3 Create file validation logic for file types, sizes, and format checking
  - [ ] 4.4 Implement single file processing workflow with real-time progress updates
  - [ ] 4.5 Implement multi-file merge workflow with file pair management interface
  - [ ] 4.6 Create processed file download system with `_processed` suffix naming
  - [ ] 4.7 Integrate existing AppController with StreamlitUIAdapter for processing
  - [ ] 4.8 Implement session state management for maintaining user selections
- [ ] 5.0 Deploy and Test Streamlit Application
  - [ ] 5.1 Test file upload functionality with various file sizes up to 400MB
  - [ ] 5.2 Test single file processing workflow end-to-end
  - [ ] 5.3 Test multi-file merge workflow with multiple file pairs
  - [ ] 5.4 Verify processed file downloads with correct naming convention
  - [ ] 5.5 Test error handling and validation feedback
  - [ ] 5.6 Deploy to Streamlit Cloud and verify configuration works
  - [ ] 5.7 Perform user acceptance testing comparing output with Tkinter version
