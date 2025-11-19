# Data Model: PyInstaller Windows Executable Setup

**Feature**: 004-pyinstaller-setup  
**Date**: 2025-11-19  
**Status**: Complete

## Overview

This document defines the key entities involved in the PyInstaller build system for the Abstract Renumber Tool. These are configuration and tooling entities, not runtime application data.

## Core Entities

### BuildConfiguration

Represents the PyInstaller spec file configuration that defines how the executable is built.

**Attributes**:
- `entry_point` (string): Path to main.py, the application entry point
- `app_name` (string): Output executable name (e.g., "AbstractRenumberTool")
- `icon_path` (string, optional): Path to .ico file for executable icon
- `windowed` (boolean): Whether to hide console window (true for GUI apps)
- `onefile` (boolean): Whether to create single executable or directory bundle
- `hidden_imports` (list of strings): Modules that PyInstaller may miss via static analysis
- `excludes` (list of strings): Modules to explicitly exclude from bundle
- `upx_enabled` (boolean): Whether to compress executable with UPX
- `debug` (boolean): Whether to include debug information in build

**Relationships**:
- Consumed by → PyInstallerSpec (produces .spec file)
- Consumed by → BuildScript (configures build process)

**Validation Rules**:
- `entry_point` must exist and be a valid Python file
- `app_name` must be valid Windows filename (no special chars)
- `icon_path` if provided must exist and be .ico format
- `hidden_imports` must be valid Python module names
- If `upx_enabled`, UPX must be available in system PATH

**State Transitions**:
```
[Created] → [Validated] → [Written to Spec File] → [Used in Build]
```

---

### PyInstallerSpec

Represents the generated .spec file that PyInstaller uses to build the executable.

**Attributes**:
- `file_path` (string): Absolute path to the .spec file (e.g., "build/AbstractRenumberTool.spec")
- `analysis_config` (dict): Configuration for Analysis phase (paths, imports, excludes)
- `pyz_config` (dict): Configuration for PYZ archive (compression, cipher)
- `exe_config` (dict): Configuration for EXE generation (name, console, icon)
- `template_version` (string): Version of spec template used

**Relationships**:
- Created from → BuildConfiguration
- Consumed by → PyInstallerProcess
- Persisted as → File on disk

**Validation Rules**:
- Must be valid Python syntax (spec files are Python scripts)
- All referenced paths in analysis_config must exist
- exe_config must specify valid Windows executable properties

**File Structure**:
```python
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[...],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[...],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    # ... additional config based on onefile/onedir
    name='AbstractRenumberTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
```

---

### BuildScript

Represents the Python build script that orchestrates the build process with validation and error handling.

**Attributes**:
- `script_path` (string): Path to build.py
- `build_mode` (enum): 'onefile' or 'onedir'
- `optimization_level` (enum): 'basic', 'medium', 'aggressive'
- `verbose` (boolean): Whether to show detailed build output
- `clean_before_build` (boolean): Whether to remove previous build artifacts

**Relationships**:
- Uses → BuildConfiguration (reads config)
- Executes → PyInstallerProcess (runs pyinstaller command)
- Produces → BuildArtifacts (creates dist/ and build/ directories)

**Validation Rules**:
- PyInstaller must be installed (`pip show pyinstaller` succeeds)
- spec file must exist before build
- Sufficient disk space for build (at least 500MB free)
- Python version compatible with PyInstaller (3.7+)

**Operations**:
1. `validate_prerequisites()`: Check Python version, PyInstaller installation, disk space
2. `clean_build_directories()`: Remove dist/ and build/ if clean_before_build=True
3. `run_pyinstaller()`: Execute pyinstaller with spec file
4. `validate_output()`: Check that expected executable exists in dist/
5. `report_results()`: Display build summary (size, location, next steps)

**State Transitions**:
```
[Initialized] → [Prerequisites Validated] → [Building] → [Completed/Failed]
```

---

### BuildArtifacts

Represents the output of a successful PyInstaller build.

**Attributes**:
- `executable_path` (string): Path to the built .exe file
- `build_mode` (enum): 'onefile' or 'onedir' (determines structure)
- `file_size_bytes` (integer): Size of executable or bundle
- `build_timestamp` (datetime): When build completed
- `python_version` (string): Version of Python used for build
- `pyinstaller_version` (string): Version of PyInstaller used

**Relationships**:
- Produced by → BuildScript
- Contains → ExecutableBundle (in onedir mode) or SingleExecutable (in onefile mode)

**Structure (onefile mode)**:
```
dist/
└── AbstractRenumberTool.exe    # Single standalone executable
```

**Structure (onedir mode)**:
```
dist/
└── AbstractRenumberTool/
    ├── AbstractRenumberTool.exe  # Main executable
    ├── _internal/                # Dependencies
    │   ├── python3XX.dll
    │   ├── pandas/
    │   ├── openpyxl/
    │   └── ...
    └── base_library.zip          # Standard library
```

**Validation Rules**:
- Executable must be a valid PE (Portable Executable) file
- File size must be reasonable (10MB - 150MB range)
- In onedir mode, _internal directory must exist and contain dependencies

---

### BuildValidation

Represents the testing checklist and validation process for verifying the built executable.

**Attributes**:
- `test_environment` (string): Description of test machine (OS version, clean/dev)
- `tests_passed` (list of strings): Names of successful test cases
- `tests_failed` (list of strings): Names of failed test cases
- `issues_found` (list of strings): Problems discovered during testing

**Test Cases**:
1. `executable_launches`: Does the .exe start without errors?
2. `gui_displays`: Does the Tkinter window appear correctly?
3. `file_selection_works`: Can user browse and select Excel/PDF files?
4. `processing_succeeds`: Does file processing complete successfully?
5. `filter_feature_works`: Does data filtering operate correctly?
6. `merge_feature_works`: Does multi-file merge function properly?
7. `output_files_created`: Are processed files generated correctly?
8. `clean_shutdown`: Does application close without errors?

**Relationships**:
- Validates → BuildArtifacts
- Documents → TestResults

**Validation Rules**:
- Must test on Windows machine without Python installed
- All core features must be tested, not just launch
- Test both success cases and error handling
- Document any antivirus warnings or performance issues

---

### BuildDocumentation

Represents the documentation bundle for the build system.

**Attributes**:
- `build_guide_path` (string): Path to building-executable.md
- `testing_guide_path` (string): Path to testing-executable.md
- `troubleshooting_guide_path` (string): Path to troubleshooting.md
- `quickstart_path` (string): Path to quickstart.md

**Sections**:

**Build Guide** (building-executable.md):
- Prerequisites (Python, PyInstaller, UPX optional)
- Step-by-step build instructions
- Configuration options (onefile vs onedir, optimization levels)
- Common build errors and solutions

**Testing Guide** (testing-executable.md):
- Test environment setup (VM or clean machine)
- Complete testing checklist
- Expected behavior for each feature
- How to report issues

**Troubleshooting Guide** (troubleshooting.md):
- Import errors (missing hidden imports)
- DLL not found errors (missing dependencies)
- Antivirus false positives (code signing, whitelisting)
- Performance issues (slow startup, large size)
- GUI rendering problems (Tkinter/Tk issues)

**Quickstart** (quickstart.md):
- 5-minute quick start for experienced users
- Single command to build
- Single command to test
- Where to find output

**Relationships**:
- References → BuildConfiguration (explains spec file)
- References → BuildScript (explains build.py usage)
- References → BuildValidation (explains testing process)

---

## Entity Relationships Diagram

```
BuildConfiguration
    ↓ (generates)
PyInstallerSpec
    ↓ (consumed by)
BuildScript
    ↓ (executes)
PyInstallerProcess (external)
    ↓ (produces)
BuildArtifacts
    ↓ (validated by)
BuildValidation
    ↓ (documented in)
BuildDocumentation
```

## File System Mapping

| Entity | File/Directory |
|--------|----------------|
| BuildConfiguration | Embedded in BuildScript (build.py) |
| PyInstallerSpec | build/AbstractRenumberTool.spec |
| BuildScript | build/build.py |
| BuildArtifacts | dist/AbstractRenumberTool.exe or dist/AbstractRenumberTool/ |
| BuildValidation | docs/testing-executable.md (checklist) |
| BuildDocumentation | docs/*.md files |

## Notes

- All entities are configuration/tooling, not runtime application data
- No changes to existing application data models (DocumentUnit, Options, etc.)
- Build process is read-only for source code—only creates output in build/ and dist/
- Spec file is version-controlled, build artifacts (dist/) are not

