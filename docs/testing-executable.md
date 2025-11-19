# Testing Checklist: Abstract Renumber Tool Executable

**Created**: 2025-11-19  
**Feature**: 004-pyinstaller-setup  
**Purpose**: Validate the Windows executable works correctly on clean machines without Python

## Test Environment Requirements

### Minimum System Requirements

- **Operating System**: Windows 10 (version 1809 or later) or Windows 11
- **RAM**: 4 GB minimum
- **Disk Space**: 100 MB free for application
- **Permissions**: No administrative privileges required
- **Screen Resolution**: 1024x768 minimum

### Critical Requirements

**❌ Python MUST NOT be installed** - This test validates standalone operation

- No Python installation
- No development tools (Visual Studio, PyCharm, etc.)
- No Python packages or pip
- Fresh user account or clean VM recommended

### Test Machine Setup Options

#### Option 1: Virtual Machine (Recommended)

**VirtualBox** (Free):
```
1. Download VirtualBox from virtualbox.org
2. Download Windows 10/11 evaluation ISO from Microsoft
3. Create new VM:
   - 4 GB RAM
   - 50 GB virtual disk
   - Enable shared folders for file transfer
4. Install Windows (no Python)
5. Copy AbstractRenumberTool.exe to VM
```

**Hyper-V** (Windows Pro/Enterprise):
```
1. Enable Hyper-V in Windows Features
2. Create new VM in Hyper-V Manager
3. Install Windows 10/11 from ISO
4. Use Enhanced Session for file transfer
5. Copy AbstractRenumberTool.exe to VM
```

**VMware Workstation/Player**:
```
1. Download VMware from vmware.com
2. Create new VM with Windows 10/11
3. Install VMware Tools for file sharing
4. Copy AbstractRenumberTool.exe to VM
```

#### Option 2: Physical Machine

Use a separate physical Windows machine:
- Clean Windows installation
- No Python or development tools
- Not your development machine
- Can access test files (Excel/PDF)

#### Option 3: Windows Sandbox (Windows Pro)

```
1. Enable Windows Sandbox in Windows Features
2. Launch Windows Sandbox
3. Copy test files into sandbox
4. Test executable (disposable environment)
5. Note: Data is lost when closed
```

---

## Test Data Preparation

### Required Test Files

Prepare these files BEFORE testing:

1. **Valid Excel File** (`test-valid.xlsx`):
   - Contains all required columns: Index#, Document Type, Legal Description, Grantee, Grantor, Document Date, Received Date
   - At least 10 rows of test data
   - Some rows with varying dates for sort testing

2. **Valid PDF File** (`test-valid.pdf`):
   - Contains bookmarks matching Excel rows
   - At least 10 bookmarks
   - Each bookmark corresponds to an Excel entry

3. **Invalid Excel File** (`test-invalid.xlsx`):
   - Missing required columns (for error testing)

4. **Non-Excel File** (`test-fake.xlsx`):
   - Renamed text file (for validation testing)

5. **Empty File** (`test-empty.xlsx`):
   - Valid Excel but empty/no data

### Copy Files to Test Machine

```bash
# On development machine, create test package:
mkdir test-package
cp dist/AbstractRenumberTool.exe test-package/
cp test-data/*.xlsx test-package/
cp test-data/*.pdf test-package/
zip -r abstract-test.zip test-package/

# Transfer to test machine via:
# - Shared folder (VM)
# - USB drive
# - Network share
# - Email/cloud storage
```

---

## Test Cases

### Test 1: Smoke Test - Executable Launches

**Objective**: Verify the executable starts without errors

**Steps**:
1. Navigate to folder containing `AbstractRenumberTool.exe`
2. Double-click `AbstractRenumberTool.exe`
3. Wait for application to start (allow 5-10 seconds)

**Expected Behavior**:
- ✅ Application launches without error dialogs
- ✅ No console window appears (GUI-only)
- ✅ No "Python not found" or DLL errors
- ✅ Application shows in taskbar
- ✅ Startup time under 10 seconds

**Pass Criteria**:
- Application window appears
- No error messages
- No crashes

**Common Issues**:
- **Antivirus blocks**: Temporarily disable or add exception
- **Windows SmartScreen**: Click "More info" → "Run anyway"
- **DLL errors**: Extremely rare with PyInstaller 6.x; report if occurs

---

### Test 2: GUI Test - Main Window Display

**Objective**: Verify all GUI controls render correctly

**Steps**:
1. Launch AbstractRenumberTool.exe
2. Observe the main window layout
3. Check all visible controls

**Expected Behavior**:
- ✅ Window title: "Abstract Renumber Tool"
- ✅ Window size: ~900x900 pixels, resizable
- ✅ Window centered on screen
- ✅ All labels visible and readable
- ✅ All buttons visible and not overlapping
- ✅ Status text area visible at bottom
- ✅ Checkboxes for options visible
- ✅ No missing fonts or rendering errors

**Visual Checklist**:
```
[ ] Title label: "Abstract Renumber Tool"
[ ] "Select Files:" section header
[ ] "Excel File:" label with Browse button
[ ] "PDF File:" label with Browse button
[ ] "Processing Options" section with checkboxes:
    [ ] "Create backup files before processing"
    [ ] "Sort PDF Bookmarks"
    [ ] "Reorder Pages to Match Bookmarks"
    [ ] "Enable Filter"
    [ ] "Enable Merge"
    [ ] "Check for Document Images"
[ ] "Process Files" button (initially disabled)
[ ] "Status" area with scrollbar
[ ] Initial status message: "Ready. Please select Excel and PDF files."
```

**Pass Criteria**:
- All UI elements visible
- No rendering glitches
- Text is legible
- Layout is clean and organized

---

### Test 3: File Selection Test

**Objective**: Verify file browsing and selection works correctly

**Steps**:
1. Launch application
2. Click "Browse..." next to "Excel File:"
3. Navigate to test files
4. Select `test-valid.xlsx`
5. Click "Browse..." next to "PDF File:"
6. Select `test-valid.pdf`

**Expected Behavior**:
- ✅ File browser dialog opens (Windows native dialog)
- ✅ Can navigate directories
- ✅ Can filter by file type (.xlsx, .pdf)
- ✅ Selected filename appears next to Browse button
- ✅ Filename changes from gray "No file selected" to black with filename
- ✅ "Process Files" button becomes enabled after both files selected
- ✅ Status area shows "Ready to process!"

**Pass Criteria**:
- File browser opens correctly
- Selected files display in UI
- Process button enables when both files selected

**Error Handling**:
- Try selecting wrong file type (should filter properly)
- Try canceling selection (should not crash)

---

### Test 4: Processing Test - Valid Files

**Objective**: Verify the application successfully processes valid input files

**Steps**:
1. Select valid Excel file (`test-valid.xlsx`)
2. Select valid PDF file (`test-valid.pdf`)
3. Keep default options (backup enabled, document check enabled)
4. Click "Process Files" button
5. Wait for processing to complete
6. Check status messages

**Expected Behavior**:
- ✅ Status area shows progress messages
- ✅ Processing completes without errors
- ✅ Success message appears: "Processing completed successfully!"
- ✅ Output files created in same directory as input files
- ✅ Backup files created (timestamped .bak files)
- ✅ Original files preserved if backup enabled

**Output Files to Check**:
```
test-valid.xlsx            # Original (unchanged if backup enabled)
test-valid_YYYYMMDD_HHMMSS.xlsx.bak  # Backup
test-valid.pdf             # Original (unchanged if backup enabled)
test-valid_YYYYMMDD_HHMMSS.pdf.bak   # Backup
```

**Pass Criteria**:
- Processing completes without crash
- Success message displayed
- Output files created correctly
- Backup files present (if enabled)
- Processing time reasonable (< 30 seconds for small files)

**Validation Steps**:
1. Open processed Excel file in Excel/LibreOffice
2. Verify Index# column renumbered (1, 2, 3, ...)
3. Verify rows are sorted correctly
4. Verify Document_Found column added (if enabled)
5. Open processed PDF in Adobe Reader
6. Check bookmarks updated with new Index# values

---

### Test 5: Filter Test - Data Filtering

**Objective**: Verify data filtering feature works correctly

**Steps**:
1. Select valid Excel and PDF files
2. Check "Enable Filter" checkbox
3. Click "Process Files"
4. Application should prompt for filter column and values
5. Select a column (e.g., "Document Type")
6. Select values to keep (e.g., "Release", "Decision")
7. Complete processing

**Expected Behavior**:
- ✅ Filter dialog appears after clicking Process
- ✅ Column dropdown shows Excel columns
- ✅ Can select column
- ✅ Can select multiple values to filter
- ✅ Processing continues with filtered data
- ✅ Output contains only selected rows
- ✅ PDF contains only matching pages

**Pass Criteria**:
- Filter dialog appears and is usable
- Filtering works correctly
- Only selected data in output
- Application doesn't crash

**Note**: If filtering UI doesn't appear, this is expected behavior if the filter prompt hasn't been implemented yet. Mark as "Feature not available" and continue.

---

### Test 6: Merge Test - Multi-File Merge

**Objective**: Verify multi-file merge feature works correctly

**Steps**:
1. Check "Enable Merge" checkbox
2. Click "Pairs..." button
3. Add multiple Excel/PDF pairs
4. Click Process
5. Verify merged output

**Expected Behavior**:
- ✅ Pairs dialog opens
- ✅ Can add multiple file pairs
- ✅ Can remove pairs
- ✅ Processing merges all pairs
- ✅ Single consolidated Excel and PDF created
- ✅ All data from all files present in output

**Pass Criteria**:
- Merge UI functional
- Multiple files merge correctly
- Consolidated output created
- No data loss

**Note**: If merge functionality isn't fully implemented, mark as "Feature in development" and continue.

---

### Test 7: Output Test - Processed Files Content

**Objective**: Verify processed files have correct content and formatting

**Steps**:
1. Process valid test files
2. Open processed Excel file
3. Open processed PDF file
4. Verify content integrity

**Excel Validation**:
- ✅ Index# column renumbered starting from 1
- ✅ Rows sorted by: Legal Description → Grantee → Grantor → Document Type → Document Date → Received Date
- ✅ All original data preserved (no data loss)
- ✅ Original Excel formatting/colors preserved
- ✅ Document_Found column added (if enabled)
- ✅ No blank rows introduced
- ✅ No formula errors

**PDF Validation**:
- ✅ Bookmarks updated to match new Index# values
- ✅ Bookmark format: `Index#-DocumentType-ReceivedDate`
- ✅ Example: `1-Release-2/20/1961`
- ✅ All pages present (no missing content)
- ✅ PDF readable and not corrupted
- ✅ If "Reorder Pages" enabled, pages match bookmark order

**Pass Criteria**:
- Output files are valid and openable
- Data is correctly transformed
- No corruption or data loss
- Formatting preserved

---

### Test 8: Error Handling Test - Invalid Inputs

**Objective**: Verify application handles errors gracefully

**Steps & Expected Behavior**:

**Test 8a: Missing Required Columns**
1. Select `test-invalid.xlsx` (missing required columns)
2. Select valid PDF
3. Click Process
4. **Expected**: Error message explaining missing columns
5. **Expected**: Application doesn't crash
6. **Expected**: Can select different files and retry

**Test 8b: Corrupted/Invalid File**
1. Select `test-fake.xlsx` (not a real Excel file)
2. Select valid PDF
3. Click Process
4. **Expected**: Error message about invalid Excel file
5. **Expected**: Graceful error handling

**Test 8c: Mismatched Files**
1. Select Excel with 10 rows
2. Select PDF with 5 bookmarks (mismatch)
3. Click Process
4. **Expected**: Warning or error about mismatch
5. **Expected**: Processing continues or fails gracefully

**Test 8d: Empty File**
1. Select `test-empty.xlsx` (no data rows)
2. Select valid PDF
3. Click Process
4. **Expected**: Error about empty file
5. **Expected**: Clear error message

**Pass Criteria**:
- Application displays clear error messages
- No crashes or freezes
- Can recover and try again
- Error messages are helpful (not technical stack traces)

---

### Test 9: Shutdown Test - Clean Application Exit

**Objective**: Verify application closes cleanly without errors

**Steps**:
1. Launch application
2. Perform some operations (select files, process, etc.)
3. Close application using X button
4. Relaunch application
5. Verify fresh state

**Expected Behavior**:
- ✅ Application closes immediately (no hang)
- ✅ No error dialogs on close
- ✅ No background processes remain (check Task Manager)
- ✅ Relaunch works correctly
- ✅ Previous state not remembered (fresh start)
- ✅ No temporary files left behind (check temp folder)

**Pass Criteria**:
- Clean shutdown
- No lingering processes
- Can relaunch successfully

---

## Pass Criteria Summary

### Overall Test Results

**All tests must pass for release approval:**

| Test | Status | Notes |
|------|--------|-------|
| 1. Smoke Test | ☐ Pass / ☐ Fail | Executable launches |
| 2. GUI Test | ☐ Pass / ☐ Fail | All controls visible |
| 3. File Selection | ☐ Pass / ☐ Fail | Browse dialogs work |
| 4. Processing | ☐ Pass / ☐ Fail | Valid files process |
| 5. Filter | ☐ Pass / ☐ Fail / ☐ N/A | Filtering works |
| 6. Merge | ☐ Pass / ☐ Fail / ☐ N/A | Multi-file merge |
| 7. Output | ☐ Pass / ☐ Fail | Correct content |
| 8. Error Handling | ☐ Pass / ☐ Fail | Graceful errors |
| 9. Shutdown | ☐ Pass / ☐ Fail | Clean exit |

### Performance Targets

- ✅ Startup time: < 10 seconds
- ✅ Processing time: < 30 seconds (for 100 rows)
- ✅ No crashes during normal operation
- ✅ No memory leaks (can run multiple times)
- ✅ Responsive UI (no freezing)

### Compatibility Targets

- ✅ Works on Windows 10 (1809+)
- ✅ Works on Windows 11
- ✅ No Python installation required
- ✅ No additional dependencies needed
- ✅ Works on both 64-bit systems

---

## Issue Reporting Template

When tests fail, document issues using this template:

```markdown
### Issue Report

**Test Case**: [Test number and name]
**Severity**: [Critical / High / Medium / Low]
**Environment**:
- OS: Windows 10/11 [version]
- Executable: AbstractRenumberTool.exe [size, date]
- Test Data: [file names used]

**Steps to Reproduce**:
1. [First step]
2. [Second step]
3. [etc.]

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happened]

**Error Messages**:
```
[Copy any error messages here]
```

**Screenshots**:
[Attach screenshots if applicable]

**Workaround**:
[If found, describe temporary workaround]

**Additional Notes**:
[Any other relevant information]
```

---

## Testing Checklist

Use this checklist to track testing progress:

### Pre-Test Setup
- [ ] Test machine prepared (no Python)
- [ ] Test files created and validated
- [ ] Executable copied to test machine
- [ ] Antivirus configured (if needed)

### Core Tests
- [ ] Test 1: Smoke Test completed
- [ ] Test 2: GUI Test completed
- [ ] Test 3: File Selection completed
- [ ] Test 4: Processing completed
- [ ] Test 5: Filter completed
- [ ] Test 6: Merge completed
- [ ] Test 7: Output validation completed
- [ ] Test 8: Error handling completed
- [ ] Test 9: Shutdown completed

### Validation
- [ ] All tests passed
- [ ] Performance targets met
- [ ] No critical/high severity issues
- [ ] Issues documented (if any)
- [ ] Ready for release: YES / NO

### Sign-Off

**Tested By**: ___________________  
**Date**: ___________________  
**Test Environment**: ___________________  
**Executable Version**: ___________________  
**Result**: PASS / FAIL  
**Notes**: ___________________

---

## Troubleshooting Common Issues

### Issue: Antivirus Blocks Executable

**Symptom**: Antivirus deletes or quarantines the .exe file

**Solution**:
1. Add AbstractRenumberTool.exe to antivirus exclusions
2. Or temporarily disable antivirus for testing
3. This is a common false positive with PyInstaller executables
4. For production: Consider code signing certificate

### Issue: "Windows Protected Your PC" (SmartScreen)

**Symptom**: Blue SmartScreen warning when launching

**Solution**:
1. Click "More info"
2. Click "Run anyway"
3. This appears because executable isn't digitally signed
4. For production: Code signing eliminates this warning

### Issue: Slow Startup (> 10 seconds)

**Symptom**: Application takes long time to launch

**Possible Causes**:
1. Antivirus scanning (check antivirus logs)
2. Onefile mode unpacking to temp (consider onedir mode)
3. Large file size (consider optimization)
4. Slow disk (especially spinning hard drives)

**Not a failure** if under 15 seconds, but note in report

### Issue: Missing VCRUNTIME140.dll

**Symptom**: Error about missing Visual C++ runtime DLL

**Solution**:
1. Download VC++ Redistributable from Microsoft
2. URL: https://aka.ms/vs/17/release/vc_redist.x64.exe
3. Install on test machine
4. Relaunch application

**Note**: PyInstaller 6.x usually bundles this, so report if it occurs

### Issue: GUI Rendering Problems

**Symptom**: Garbled text, missing controls, wrong colors

**Possible Causes**:
1. Display scaling settings (check Windows display settings)
2. Very old Windows version (update Windows)
3. Remote desktop artifacts (test locally)

**Solution**: Try on different monitor or adjust scaling to 100%

---

## Advanced Testing (Optional)

### Stress Testing

Test with large files to verify performance:

1. Excel with 1000+ rows
2. PDF with 1000+ bookmarks
3. Process multiple times in succession
4. Verify no memory leaks (check Task Manager)

### Edge Case Testing

- Very long file paths (> 200 characters)
- Special characters in filenames (é, ñ, 中, etc.)
- Read-only input files
- Network drive locations
- Files locked by another program

### Multiple Sessions

- Run multiple instances simultaneously
- Process different files in parallel
- Verify no conflicts or crashes

---

## Next Steps After Testing

### If All Tests Pass

1. Document test results
2. Archive test data and logs
3. Prepare for release/distribution
4. Update release notes
5. Plan deployment

### If Tests Fail

1. Document all failures using issue template
2. Prioritize critical/high issues
3. Report to development team
4. Retest after fixes
5. Do NOT release until all critical issues resolved

### Release Readiness

**Minimum Requirements for Release**:
- ✅ All 9 core tests pass
- ✅ No critical or high severity issues
- ✅ Performance targets met
- ✅ Tested on both Windows 10 and 11
- ✅ Documentation complete

---

## Contact & Support

For issues or questions during testing:

1. Check `docs/troubleshooting.md` for common issues
2. Review `docs/building-executable.md` for build information
3. Check project issue tracker
4. Contact development team

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-19  
**Related Documents**:
- `docs/building-executable.md` - How to build the executable
- `docs/troubleshooting.md` - Common issues and solutions
- `build/README.md` - Build system documentation

