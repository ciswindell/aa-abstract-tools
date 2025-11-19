# Build System Contracts

**Feature**: 004-pyinstaller-setup  
**Date**: 2025-11-19  
**Purpose**: Define interfaces and contracts for PyInstaller build system

## Overview

This document specifies the contracts (interfaces) for the build system components. These contracts define how developers interact with the build tooling and what outputs to expect.

## Build Script Interface

### Command-Line Interface

**Script**: `build/build.py`

**Signature**:
```bash
python3 build/build.py [OPTIONS]
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--mode` | string | `onefile` | Build mode: 'onefile' or 'onedir' |
| `--optimize` | string | `basic` | Optimization level: 'basic', 'medium', 'aggressive' |
| `--clean` | flag | false | Remove previous build artifacts before building |
| `--verbose` | flag | false | Show detailed PyInstaller output |
| `--spec` | string | `build/AbstractRenumberTool.spec` | Path to spec file to use |
| `--help` | flag | - | Display help message and exit |

**Examples**:
```bash
# Basic build (default)
python3 build/build.py

# Onedir mode with medium optimization
python3 build/build.py --mode onedir --optimize medium

# Clean build with verbose output
python3 build/build.py --clean --verbose

# Use custom spec file
python3 build/build.py --spec custom.spec
```

**Return Codes**:
- `0`: Build succeeded
- `1`: Validation failed (prerequisites not met)
- `2`: Build failed (PyInstaller error)
- `3`: Post-build validation failed (executable not found/invalid)

**Output**:
```
Abstract Renumber Tool - Build Script
=====================================

[✓] Checking prerequisites...
    - Python version: 3.11.5
    - PyInstaller: 6.3.0
    - Disk space: 2.5 GB available
    
[✓] Validating configuration...
    - Entry point: main.py (exists)
    - Spec file: build/AbstractRenumberTool.spec (valid)
    
[✓] Cleaning build directories...
    - Removed: dist/
    - Removed: build/build/
    
[→] Running PyInstaller...
    Mode: onefile
    Optimization: basic
    
    ... [PyInstaller output] ...
    
[✓] Build completed successfully!

Build Summary:
--------------
Executable: dist/AbstractRenumberTool.exe
Size: 87.3 MB
Build time: 3m 42s
Mode: onefile

Next Steps:
-----------
1. Test on clean Windows machine (see docs/testing-executable.md)
2. Verify all features work correctly
3. Distribute to end users

```

---

### Python API (Programmatic Interface)

For integration with CI/CD or custom build workflows.

**Module**: `build.build`

**Class**: `BuildOrchestrator`

```python
class BuildOrchestrator:
    """Orchestrates PyInstaller build process with validation."""
    
    def __init__(
        self,
        spec_file: str,
        mode: str = "onefile",
        optimize: str = "basic",
        clean: bool = False,
        verbose: bool = False
    ):
        """
        Initialize build orchestrator.
        
        Args:
            spec_file: Path to PyInstaller spec file
            mode: Build mode ('onefile' or 'onedir')
            optimize: Optimization level ('basic', 'medium', 'aggressive')
            clean: Whether to clean build artifacts before building
            verbose: Whether to show detailed output
        
        Raises:
            ValueError: If parameters are invalid
        """
        pass
    
    def validate_prerequisites(self) -> tuple[bool, list[str]]:
        """
        Validate build prerequisites.
        
        Returns:
            Tuple of (success, error_messages)
            success: True if all prerequisites met
            error_messages: List of error descriptions if validation failed
        
        Checks:
            - Python version >= 3.7
            - PyInstaller installed
            - Spec file exists and is valid
            - Entry point (main.py) exists
            - Sufficient disk space (>500MB)
        """
        pass
    
    def build(self) -> BuildResult:
        """
        Execute the build process.
        
        Returns:
            BuildResult object with status and metadata
        
        Raises:
            PrerequisiteError: If prerequisites not met
            BuildError: If PyInstaller build fails
        
        Process:
            1. Validate prerequisites
            2. Clean build directories if requested
            3. Execute PyInstaller with spec file
            4. Validate output executable exists
            5. Generate build summary
        """
        pass
    
    def get_build_info(self) -> dict:
        """
        Get information about the build configuration.
        
        Returns:
            Dictionary with build configuration details:
            {
                'spec_file': str,
                'mode': str,
                'optimize': str,
                'entry_point': str,
                'output_dir': str,
                'python_version': str,
                'pyinstaller_version': str
            }
        """
        pass
```

**Class**: `BuildResult`

```python
@dataclass
class BuildResult:
    """Result of a PyInstaller build operation."""
    
    success: bool
    executable_path: str | None
    file_size_bytes: int | None
    build_time_seconds: float
    error_message: str | None
    warnings: list[str]
    
    def __str__(self) -> str:
        """Human-readable build summary."""
        pass
```

**Example Usage**:
```python
from build.build import BuildOrchestrator

orchestrator = BuildOrchestrator(
    spec_file="build/AbstractRenumberTool.spec",
    mode="onefile",
    optimize="basic",
    clean=True,
    verbose=False
)

# Validate before building
success, errors = orchestrator.validate_prerequisites()
if not success:
    print(f"Prerequisites failed: {errors}")
    exit(1)

# Build
result = orchestrator.build()
if result.success:
    print(f"Build succeeded: {result.executable_path}")
    print(f"Size: {result.file_size_bytes / (1024*1024):.1f} MB")
else:
    print(f"Build failed: {result.error_message}")
    exit(2)
```

---

## Spec File Contract

### File Format

**File**: `build/AbstractRenumberTool.spec`

**Format**: Python script executed by PyInstaller

**Required Sections**:

1. **Analysis**: Defines input files and import discovery
2. **PYZ**: Defines Python archive creation
3. **EXE**: Defines executable generation

**Template Structure**:

```python
# -*- mode: python ; coding: utf-8 -*-

# Configuration section (can be modified by users)
APP_NAME = 'AbstractRenumberTool'
ENTRY_POINT = 'main.py'
ICON_PATH = None  # Set to 'path/to/icon.ico' if available
CONSOLE = False  # True to show console window
UPX_ENABLED = False  # True to enable compression

# Hidden imports (modules PyInstaller might miss)
HIDDEN_IMPORTS = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'pandas',
    'pandas._libs',
    'pandas._libs.tslibs',
    'openpyxl',
    'openpyxl.cell._writer',
    'pypdf',
    'pypdf._codecs',
    'pypdf._utils',
    'natsort',
    'dateutil',
    'dateutil.parser',
]

# Modules to exclude (reduce size)
EXCLUDES = [
    'pandas.tests',
    'pandas.io.clipboard',
    'matplotlib',
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'setuptools',
]

# PyInstaller configuration (typically not modified)
block_cipher = None

a = Analysis(
    [ENTRY_POINT],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=HIDDEN_IMPORTS,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE configuration changes based on onefile vs onedir
# This spec supports both (PyInstaller command determines mode)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=UPX_ENABLED,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=CONSOLE,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,
)
```

**Modification Contract**:
- Users MAY modify values in "Configuration section"
- Users SHOULD NOT modify PyInstaller configuration section
- Adding items to `HIDDEN_IMPORTS` is safe and often necessary
- Adding items to `EXCLUDES` may break functionality (test thoroughly)
- Changing `CONSOLE` to `True` shows terminal window (useful for debugging)

---

## Validation Contract

### Prerequisites Validation

**Function**: `validate_prerequisites()`

**Checks**:

| Check | Pass Condition | Error Message |
|-------|----------------|---------------|
| Python version | `sys.version_info >= (3, 7)` | "Python 3.7+ required, found {version}" |
| PyInstaller installed | `importlib.import_module('PyInstaller')` succeeds | "PyInstaller not installed. Run: pip install pyinstaller" |
| PyInstaller version | `>= 6.0.0` | "PyInstaller 6.x required, found {version}" |
| Entry point exists | `os.path.exists('main.py')` | "Entry point main.py not found" |
| Spec file exists | `os.path.exists(spec_file)` | "Spec file not found: {spec_file}" |
| Disk space | `>= 500 MB free` | "Insufficient disk space. Need 500MB, have {available}MB" |
| Platform check | Warning on non-Windows | "Warning: Building on {platform}. Test on Windows required" |

**Returns**: `(success: bool, errors: list[str])`

---

### Post-Build Validation

**Function**: `validate_build_output()`

**Checks**:

| Check | Pass Condition | Error Message |
|-------|----------------|---------------|
| Executable exists | File exists at expected path | "Executable not found: {expected_path}" |
| File is executable | File has .exe extension | "Output is not an executable file" |
| File size reasonable | 10 MB < size < 200 MB | "Warning: Executable size unusual: {size}MB" |
| Directory structure (onedir) | `_internal/` subdirectory exists | "Missing _internal directory in onedir build" |

**Returns**: `(success: bool, warnings: list[str])`

---

## Testing Contract

### Test Checklist

**File**: `docs/testing-executable.md`

**Required Test Cases**:

1. **Smoke Test**: Executable launches without error
2. **GUI Test**: Main window appears with all controls
3. **File Selection Test**: Can browse and select Excel/PDF files
4. **Processing Test**: Successfully processes valid input files
5. **Filter Test**: Data filtering feature works correctly
6. **Merge Test**: Multi-file merge feature works correctly
7. **Output Test**: Processed files created with correct content
8. **Error Handling Test**: Invalid inputs show appropriate errors
9. **Shutdown Test**: Application closes cleanly

**Test Environment Requirements**:
- Windows 10 or Windows 11
- No Python installation
- No development tools installed
- Fresh user account or VM
- At least 100MB free disk space

**Pass Criteria**:
- All 9 test cases pass
- No crashes or unhandled exceptions
- Output files match expected format
- Performance within acceptable ranges (<5s startup, <30s processing)

---

## Documentation Contract

### Required Documentation Files

| File | Purpose | Required Sections |
|------|---------|------------------|
| `docs/building-executable.md` | Complete build guide | Prerequisites, Build Steps, Configuration, Troubleshooting |
| `docs/testing-executable.md` | Testing checklist | Test Environment, Test Cases, Pass Criteria, Issue Reporting |
| `docs/troubleshooting.md` | Common issues guide | Build Errors, Runtime Errors, Performance Issues, Antivirus Issues |
| `specs/004-pyinstaller-setup/quickstart.md` | Quick reference | TL;DR Build Command, Test Command, Distribution Notes |

### Documentation Standards

- All commands must be copy-pasteable
- All file paths must be relative to repository root
- All error messages must include solution steps
- All examples must be tested and verified
- Screenshots for GUI issues (if applicable)

---

## Distribution Contract

### Deliverables

**Onefile Mode** (default):
```
AbstractRenumberTool.exe    # Single standalone executable
```

**Onedir Mode**:
```
AbstractRenumberTool/
├── AbstractRenumberTool.exe
├── _internal/
│   └── [all dependencies]
└── base_library.zip
```

### User Requirements

**Minimum System Requirements**:
- Windows 10 (1809) or later
- 4 GB RAM
- 100 MB free disk space
- No administrative privileges required

**No Software Requirements**:
- No Python installation needed
- No Visual C++ redistributables needed (bundled)
- No additional libraries needed

### Distribution Checklist

- [ ] Executable tested on clean Windows 10
- [ ] Executable tested on clean Windows 11
- [ ] All features verified working
- [ ] File size under 100MB (onefile) or 150MB (onedir)
- [ ] No console window appears (windowed mode)
- [ ] Custom icon visible (if applicable)
- [ ] Version information embedded (if applicable)
- [ ] Scanned for viruses (VirusTotal or equivalent)
- [ ] README included with usage instructions
- [ ] License file included

---

## Error Handling Contract

### Error Categories

**Validation Errors** (Exit code 1):
- Missing prerequisites
- Invalid configuration
- Insufficient resources

**Build Errors** (Exit code 2):
- PyInstaller failures
- Import errors
- Dependency resolution failures

**Post-Build Errors** (Exit code 3):
- Missing output files
- Invalid executable
- Corruption detected

### Error Message Format

```
[ERROR] {Category}: {Brief Description}

Details:
{Detailed explanation of what went wrong}

Solution:
{Step-by-step fix instructions}

Example:
{Command or code example if applicable}
```

**Example**:
```
[ERROR] Validation: PyInstaller not installed

Details:
PyInstaller package is required to build executables but was not found
in the current Python environment.

Solution:
Install PyInstaller using pip:
    pip install pyinstaller

Then re-run the build script.
```

---

## Summary

This contracts document defines:
- ✅ Command-line interface for build script
- ✅ Python API for programmatic access
- ✅ Spec file structure and modification rules
- ✅ Validation requirements (pre and post build)
- ✅ Testing checklist and pass criteria
- ✅ Documentation requirements
- ✅ Distribution deliverables and requirements
- ✅ Error handling standards

All components implementing these contracts must adhere to the defined interfaces to ensure consistency and maintainability.

