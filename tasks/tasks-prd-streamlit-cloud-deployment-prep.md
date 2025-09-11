# Task List: Streamlit Cloud Deployment Preparation

## Relevant Files

- `pages/components/file_upload.py` - Contains file upload handling and temporary file creation that needs cleanup implementation
- `pages/components/state_management.py` - Session state management that may need cleanup integration
- `requirements.txt` - Package dependencies that need version constraint updates for Streamlit Cloud compatibility
- `fileops/files.py` - File operations utilities that may need cloud environment compatibility checks
- `.streamlit/config.toml` - Streamlit configuration for deployment settings
- `streamlit_main.py` - Main entry point that needs verification for cloud deployment
- `adapters/ui_streamlit.py` - Streamlit UI adapter that handles temporary file paths

### Notes

- Focus on temporary file cleanup to prevent storage issues in Streamlit Cloud's ephemeral environment
- Ensure dependency versions are compatible with Streamlit Cloud's package management
- Test changes locally before deployment to verify backward compatibility

## Tasks

- [ ] 1.0 Implement Temporary File Cleanup System
  - [ ] 1.1 Add cleanup method to FileUploadManager class in `pages/components/file_upload.py`
  - [ ] 1.2 Implement automatic cleanup in `save_to_temp()` method using context managers or atexit
  - [ ] 1.3 Add cleanup integration to session state management in `pages/components/state_management.py`
  - [ ] 1.4 Update `reset_workflow_state()` method to clean up temporary files
  - [ ] 1.5 Add error handling for cleanup operations to prevent cleanup failures from breaking the app

- [ ] 2.0 Update Requirements.txt for Streamlit Cloud Compatibility
  - [ ] 2.1 Change `streamlit==1.49.0` to `streamlit>=1.49.0` for better compatibility
  - [ ] 2.2 Review and update `protobuf<=3.20.3` constraint to avoid conflicts with newer dependencies
  - [ ] 2.3 Verify all package versions are compatible with Streamlit Cloud environment
  - [ ] 2.4 Test requirements.txt locally to ensure no dependency conflicts

- [ ] 3.0 Enhance File Upload Management for Cloud Environment
  - [ ] 3.1 Review temporary file creation in `save_to_temp()` method for cloud compatibility
  - [ ] 3.2 Add file size validation before creating temporary files
  - [ ] 3.3 Implement proper error handling for temporary file operations
  - [ ] 3.4 Update `adapters/ui_streamlit.py` to handle temporary file paths more robustly
  - [ ] 3.5 Add logging for temporary file operations to aid debugging in cloud environment

- [ ] 4.0 Verify and Update Deployment Configuration
  - [ ] 4.1 Review `.streamlit/config.toml` settings for cloud deployment compatibility
  - [ ] 4.2 Verify `streamlit_main.py` as proper entry point for Streamlit Cloud
  - [ ] 4.3 Check for any hardcoded paths or local dependencies in configuration
  - [ ] 4.4 Ensure no environment variables are required that aren't available in cloud
  - [ ] 4.5 Validate that all imports and module paths work in cloud environment

- [ ] 5.0 Test Cloud Environment Compatibility
  - [ ] 5.1 Test file upload functionality with various file sizes locally
  - [ ] 5.2 Verify temporary file cleanup works correctly during processing
  - [ ] 5.3 Test error scenarios to ensure proper cleanup on failures
  - [ ] 5.4 Run full workflow test with Excel and PDF files to validate end-to-end functionality
  - [ ] 5.5 Verify memory usage doesn't accumulate during multiple file processing sessions
