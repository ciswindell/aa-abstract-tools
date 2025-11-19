# Research: PyInstaller Windows Executable Setup

**Feature**: 004-pyinstaller-setup  
**Date**: 2025-11-19  
**Status**: Complete

## Overview

Research findings for packaging the Abstract Renumber Tool as a Windows executable using PyInstaller, covering configuration options, dependency handling, optimization strategies, and common pitfalls.

## Key Decisions

### Decision 1: PyInstaller Version and Mode

**Decision**: Use PyInstaller 6.x with both onefile and onedir build modes

**Rationale**:
- PyInstaller 6.x is the current stable release with best Windows 10/11 support
- Onefile mode: Single .exe for easy distribution (default for end users)
- Onedir mode: Directory with dependencies for faster startup (dev/testing)
- Both modes supported by same spec file via command-line flag

**Alternatives Considered**:
- **cx_Freeze**: Less popular, requires more manual configuration, fewer maintained hooks for common packages
- **Nuitka**: Better performance but requires C++ compiler on build machine, longer build times, more complex troubleshooting
- **py2exe**: Windows-only, less actively maintained, limited Python 3.11+ support
- **PyInstaller 5.x**: Older version, missing some Windows 11 compatibility fixes

**Implementation Notes**:
- Specify `pyinstaller>=6.0.0,<7.0.0` in requirements
- Use spec file for configuration (more maintainable than CLI args)
- Provide both build commands in documentation

---

### Decision 2: Handling Tkinter and GUI Dependencies

**Decision**: Use windowed mode (no console) with explicit tkinter plugin and DLL collection

**Rationale**:
- `--windowed` flag prevents console window from appearing (better UX for GUI apps)
- PyInstaller's tk-inter plugin automatically collects necessary Tcl/Tk files
- Modern PyInstaller versions handle tkinter reasonably well, but spec file should explicitly include tk-inter plugin
- Must test on clean Windows to verify all Tk DLLs are bundled

**Alternatives Considered**:
- **Console mode**: Shows ugly console window alongside GUI, poor user experience
- **Manual DLL specification**: Error-prone, version-dependent, unnecessary with plugin
- **Hide console with subprocess**: Hacky workaround, not needed with --windowed

**Implementation Notes**:
```python
# In spec file
hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.filedialog']
# Build command includes --windowed flag or set in spec
```

---

### Decision 3: Handling Scientific Python Dependencies

**Decision**: Use explicit hidden imports for pandas, openpyxl, pypdf with excludes for unused modules

**Rationale**:
- pandas brings heavy dependencies (numpy, etc.) but is essential for Excel processing
- openpyxl and pypdf have dynamic imports that PyInstaller may miss
- Excluding unused pandas modules (tests, io backends) reduces size significantly
- Must include dateutil and natsort explicitly

**Alternatives Considered**:
- **Bundle entire pandas**: Simple but adds 50-80MB of unnecessary code
- **Manual imports**: Error-prone, misses transitive dependencies
- **Hook files**: Overkill for this project, harder to maintain

**Implementation Notes**:
```python
hiddenimports=[
    'pandas', 'pandas._libs', 'pandas._libs.tslibs',
    'openpyxl', 'openpyxl.cell._writer',
    'pypdf', 'pypdf._codecs', 'pypdf._utils',
    'natsort', 'dateutil', 'dateutil.parser'
]

excludes=[
    'pandas.tests', 'pandas.io.clipboard',
    'matplotlib', 'IPython', 'jupyter'
]
```

---

### Decision 4: Build Validation and Error Handling

**Decision**: Create Python build script with prerequisite checks and clear error messages

**Rationale**:
- Checks for PyInstaller installation before attempting build
- Validates main.py exists and is executable
- Provides actionable error messages for missing dependencies
- Single entry point for both onefile and onedir builds

**Alternatives Considered**:
- **Batch/PowerShell script**: Less portable, harder to maintain, no Python error handling
- **Makefile**: Unfamiliar to many Windows developers, requires make installation
- **Direct pyinstaller command**: No validation, cryptic errors on failure

**Implementation Notes**:
- Use subprocess module to run pyinstaller with captured output
- Check sys.platform to warn if not building on Windows (cross-compile limitations)
- Return clear exit codes (0=success, 1=validation failure, 2=build failure)

---

### Decision 5: Optimization Strategy

**Decision**: Three-tier optimization: basic (default), medium (UPX), aggressive (excludes)

**Rationale**:
- Basic: Just hidden imports and excludes, balances size vs compatibility (default)
- Medium: Add UPX compression (requires UPX in PATH), ~30% size reduction
- Aggressive: Exclude more modules, risks runtime import errors, for experts only

**Alternatives Considered**:
- **Always use maximum optimization**: Risks breaking executable, hard to debug
- **No optimization**: Results in 150MB+ executables, slow distribution
- **Lazy imports in code**: Requires application changes, violates constitution

**Implementation Notes**:
```python
# Basic (default in spec)
upx=False
excludes=[...common unused modules...]

# Medium (command-line flag)
upx=True

# Aggressive (separate spec file or manual edit)
excludes=[...extensive list...]
```

---

### Decision 6: Icon and Version Information

**Decision**: Support optional icon via spec file, document Windows version resource usage

**Rationale**:
- Custom icon improves professional appearance
- Icon file must be .ico format (not PNG/SVG)
- Version information embedded in .exe helps users identify builds
- Both are optional (sensible defaults if omitted)

**Alternatives Considered**:
- **Require icon**: Unnecessary barrier, not all users have icon files
- **Generate icon from PNG**: Adds dependency (pillow), overkill for optional feature
- **Skip version info**: Makes troubleshooting harder, but can be added later

**Implementation Notes**:
```python
# In spec file
exe = EXE(
    # ...
    icon='path/to/icon.ico',  # Optional, remove line if no icon
    version='version_info.txt',  # Optional, for advanced users
)
```

---

### Decision 7: Testing and Validation Strategy

**Decision**: Manual testing checklist with virtual machine or clean Windows machine requirement

**Rationale**:
- Automated testing of PyInstaller builds is complex and fragile
- Real-world validation requires testing on machine without Python
- Checklist ensures all features are tested, not just basic launch
- VM or separate machine is necessary to verify true standalone behavior

**Alternatives Considered**:
- **Docker Windows containers**: Limited GUI support, licensing complexity
- **Automated test suite**: Brittle, doesn't catch DLL issues, maintenance burden
- **Trust build without testing**: Unacceptable, will miss critical issues

**Implementation Notes**:
- Provide detailed testing checklist in docs/testing-executable.md
- Include both smoke tests (launches) and full feature tests
- Document VM setup options (VirtualBox, Hyper-V, VMware)
- Recommend testing on both Windows 10 and Windows 11

---

## Best Practices Summary

1. **Always use spec file**: More maintainable than command-line arguments
2. **Test on clean machine**: Only way to verify standalone behavior
3. **Start simple**: Basic build first, optimize later if needed
4. **Document everything**: Build process, dependencies, troubleshooting steps
5. **Version control spec file**: Track changes to build configuration
6. **Provide both modes**: Onefile for distribution, onedir for development
7. **Clear error messages**: Help users diagnose build failures quickly
8. **Exclude tests/docs**: Reduce size by excluding development-only modules

## Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| PyInstaller | 6.x | Application bundler |
| Python | 3.7+ | Runtime (bundled in executable) |
| UPX | 3.96+ (optional) | Executable compression |
| pandas | 2.0.0+ | Excel processing (bundled) |
| openpyxl | 3.0.0+ | Excel file I/O (bundled) |
| pypdf | 4.2.0 | PDF processing (bundled) |
| tkinter | (stdlib) | GUI framework (bundled) |
| natsort | 8.0.0+ | Natural sorting (bundled) |
| python-dateutil | 2.8.0+ | Date parsing (bundled) |

## Open Questions & Risks

### Questions Resolved
- ✅ Which PyInstaller version? → 6.x (current stable)
- ✅ Onefile vs onedir? → Support both, onefile as default
- ✅ How to handle Tkinter? → Use tk-inter plugin with windowed mode
- ✅ Size optimization? → Three-tier strategy (basic/medium/aggressive)
- ✅ Testing approach? → Manual checklist on clean Windows machine

### Remaining Risks

**Risk 1: Antivirus False Positives**
- **Likelihood**: High (common with PyInstaller executables)
- **Impact**: Medium (users may be blocked from running)
- **Mitigation**: Document code signing process, provide VirusTotal scan links, add to common AV whitelists

**Risk 2: Missing DLLs on Target Machine**
- **Likelihood**: Low (PyInstaller collects most automatically)
- **Impact**: High (executable won't run)
- **Mitigation**: Test on multiple Windows versions/configurations, document MSVC runtime requirements

**Risk 3: Large Executable Size**
- **Likelihood**: High (pandas adds significant size)
- **Impact**: Low (acceptable for desktop application)
- **Mitigation**: Provide optimization guidance, consider onedir for faster updates

**Risk 4: Slow Startup Time**
- **Likelihood**: Medium (onefile mode unpacks to temp)
- **Impact**: Low (5-10 seconds acceptable for desktop tool)
- **Mitigation**: Recommend onedir for frequent use, optimize imports

## References

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller Hooks](https://github.com/pyinstaller/pyinstaller-hooks-contrib)
- [Tkinter + PyInstaller Guide](https://pyinstaller.org/en/stable/when-things-go-wrong.html#specific-features)
- [Windows Code Signing](https://learn.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)
- [UPX Compression](https://upx.github.io/)

