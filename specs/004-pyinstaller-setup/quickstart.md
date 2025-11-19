# Quick Start: Building Windows Executable

**Feature**: 004-pyinstaller-setup  
**Date**: 2025-11-19  
**Audience**: Developers familiar with Python and PyInstaller

## TL;DR

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
python3 build/build.py

# Find output
ls -lh dist/AbstractRenumberTool.exe

# Test on Windows machine without Python
# (Copy exe to clean machine and run all features)
```

**Build time**: ~3-5 minutes  
**Output size**: ~80-90 MB (onefile mode)

---

## Prerequisites (One-Time Setup)

### 1. Install PyInstaller

```bash
pip install 'pyinstaller>=6.0.0,<7.0.0'
```

### 2. Optional: Install UPX (for compression)

**Windows**:
```bash
# Download from https://upx.github.io/
# Extract upx.exe to a directory in your PATH
```

**Linux** (for cross-compilation):
```bash
sudo apt-get install upx
```

---

## Build Commands

### Default Build (Onefile, Basic Optimization)

```bash
python3 build/build.py
```

**Output**: `dist/AbstractRenumberTool.exe` (single file)

---

### Onedir Build (Faster Startup)

```bash
python3 build/build.py --mode onedir
```

**Output**: `dist/AbstractRenumberTool/` (directory with executable and dependencies)

---

### Optimized Build (Medium Compression)

```bash
python3 build/build.py --optimize medium
```

**Requirements**: UPX must be installed  
**Result**: ~30% smaller file size

---

### Clean Build (Remove Previous Artifacts)

```bash
python3 build/build.py --clean
```

**Use when**: Previous build had errors or you changed dependencies

---

### Verbose Build (Debug Output)

```bash
python3 build/build.py --verbose
```

**Use when**: Troubleshooting build issues or import errors

---

## Testing

### Quick Smoke Test (Development Machine)

```bash
# Run the executable
./dist/AbstractRenumberTool.exe  # Windows
wine dist/AbstractRenumberTool.exe  # Linux with Wine

# Verify GUI launches and shows main window
```

### Full Test (Clean Windows Machine)

1. **Copy to test machine**:
   ```bash
   # Onefile mode
   scp dist/AbstractRenumberTool.exe user@windows-machine:~/
   
   # Onedir mode
   scp -r dist/AbstractRenumberTool/ user@windows-machine:~/
   ```

2. **Run on test machine**:
   - Double-click `AbstractRenumberTool.exe`
   - Select test Excel and PDF files
   - Run processing with default options
   - Verify output files created correctly

3. **Test all features**:
   - File selection and validation
   - Processing with default options
   - Filtering by column values
   - Multi-file merge
   - Document image checking
   - Error handling with invalid files

---

## Common Build Options

### Configuration Matrix

| Use Case | Command | Output | Size | Startup |
|----------|---------|--------|------|---------|
| **End-user distribution** | `python3 build/build.py` | Single .exe | ~85MB | 3-5s |
| **Faster startup** | `python3 build/build.py --mode onedir` | Directory | ~150MB | <1s |
| **Smaller size** | `python3 build/build.py --optimize medium` | Single .exe | ~60MB | 3-5s |
| **Development testing** | `python3 build/build.py --mode onedir --clean` | Directory | ~150MB | <1s |

---

## Troubleshooting Quick Fixes

### "PyInstaller not found"

```bash
pip install pyinstaller
```

### "Import error: [module]"

Edit `build/AbstractRenumberTool.spec` and add to `HIDDEN_IMPORTS`:
```python
HIDDEN_IMPORTS = [
    # ... existing imports ...
    'your_missing_module',
]
```

### "Executable is too large"

```bash
# Use medium optimization (requires UPX)
python3 build/build.py --optimize medium

# Or manually exclude unused modules in spec file
```

### "Antivirus flags executable"

- This is a common false positive with PyInstaller
- Solution: Code signing (requires certificate) or whitelist locally
- See `docs/troubleshooting.md` for details

### "DLL not found" on target machine

- Rare with PyInstaller 6.x (auto-collects dependencies)
- If it happens: Install Visual C++ Redistributable on target machine
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## File Locations

| Item | Location |
|------|----------|
| **Build script** | `build/build.py` |
| **Spec file** | `build/AbstractRenumberTool.spec` |
| **Output (onefile)** | `dist/AbstractRenumberTool.exe` |
| **Output (onedir)** | `dist/AbstractRenumberTool/` |
| **Build artifacts** | `build/build/` (temp, can delete) |
| **Detailed docs** | `docs/building-executable.md` |
| **Testing guide** | `docs/testing-executable.md` |
| **Troubleshooting** | `docs/troubleshooting.md` |

---

## Build Script Options Reference

```bash
python3 build/build.py [OPTIONS]

OPTIONS:
  --mode {onefile|onedir}     Build mode (default: onefile)
  --optimize {basic|medium|aggressive}  Optimization level (default: basic)
  --clean                      Remove previous build artifacts
  --verbose                    Show detailed PyInstaller output
  --spec PATH                  Path to spec file (default: build/AbstractRenumberTool.spec)
  --help                       Show help message

EXAMPLES:
  # Standard build
  python3 build/build.py
  
  # Onedir with clean
  python3 build/build.py --mode onedir --clean
  
  # Optimized onefile
  python3 build/build.py --optimize medium
  
  # Verbose build for debugging
  python3 build/build.py --verbose
```

---

## Customization Quick Reference

### Add Custom Icon

1. Create or obtain a `.ico` file (Windows icon format)
2. Edit `build/AbstractRenumberTool.spec`:
   ```python
   ICON_PATH = 'path/to/your/icon.ico'
   ```
3. Rebuild

### Include Additional Data Files

Edit `build/AbstractRenumberTool.spec`:
```python
a = Analysis(
    # ... existing config ...
    datas=[
        ('path/to/data/file.txt', 'destination/folder'),
    ],
)
```

### Change Executable Name

Edit `build/AbstractRenumberTool.spec`:
```python
APP_NAME = 'YourCustomName'
```

---

## Distribution Checklist

Before distributing to end users:

- [ ] Built with `--clean` flag
- [ ] Tested on clean Windows 10 machine
- [ ] Tested on clean Windows 11 machine
- [ ] All features verified working
- [ ] File size is reasonable (<100MB onefile or <150MB onedir)
- [ ] No console window appears
- [ ] Scanned with antivirus (optional but recommended)
- [ ] README included with usage instructions

---

## Next Steps

### For more details, see:

- **Complete build guide**: `docs/building-executable.md`
- **Testing procedures**: `docs/testing-executable.md`
- **Troubleshooting**: `docs/troubleshooting.md`
- **Technical plan**: `specs/004-pyinstaller-setup/plan.md`

### Need help?

- Check build output for specific error messages
- Review `docs/troubleshooting.md` for common issues
- Verify prerequisites: Python 3.7+, PyInstaller 6.x
- Run with `--verbose` flag to see detailed output

---

## Performance Expectations

| Metric | Target | Typical |
|--------|--------|---------|
| **Build time** | <10 min | 3-5 min |
| **Executable size (onefile)** | <100 MB | 80-90 MB |
| **Executable size (onedir)** | <150 MB | 120-140 MB |
| **Startup time (onefile)** | <5 sec | 3-5 sec |
| **Startup time (onedir)** | <2 sec | <1 sec |
| **Processing speed** | Same as Python | Same as Python |

---

## Summary

**Quick build**: `python3 build/build.py`  
**Quick test**: Copy to Windows machine and run  
**Distribute**: `dist/AbstractRenumberTool.exe` or `dist/AbstractRenumberTool/`

For detailed instructions, configuration options, and troubleshooting, see the complete documentation in the `docs/` directory.

