# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Abstract Renumber Tool
Created: 2025-11-19
Feature: 004-pyinstaller-setup

This file defines how PyInstaller packages the Abstract Renumber Tool
into a standalone Windows executable.
"""

# =============================================================================
# CONFIGURATION SECTION - Users can modify these values
# =============================================================================

APP_NAME = 'AbstractRenumberTool'
ENTRY_POINT = 'main.py'
ICON_PATH = None  # Set to 'path/to/icon.ico' if you have a custom icon
CONSOLE = False  # True to show console window (useful for debugging)
UPX_ENABLED = False  # True to enable UPX compression (requires UPX in PATH)

# Hidden imports - modules that PyInstaller might miss via static analysis
# These are required for the application to run correctly
HIDDEN_IMPORTS = [
    # Tkinter GUI framework
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    # Pandas and dependencies
    'pandas',
    'pandas._libs',
    'pandas._libs.tslibs',
    # Excel file handling
    'openpyxl',
    'openpyxl.cell._writer',
    # PDF processing
    'pypdf',
    'pypdf._codecs',
    'pypdf._utils',
    # Natural sorting
    'natsort',
    # Date parsing
    'dateutil',
    'dateutil.parser',
]

# Modules to exclude - reduces executable size by removing unused packages
# Only exclude modules you're certain the application doesn't need
EXCLUDES = [
    # Pandas modules not needed for our use case
    'pandas.tests',
    'pandas.io.clipboard',
    # Data visualization (not used)
    'matplotlib',
    # Interactive Python (not needed in executable)
    'IPython',
    'jupyter',
    'notebook',
    # Testing frameworks (not needed in production)
    'pytest',
    # Build tools (not needed in executable)
    'setuptools',
]

# =============================================================================
# PYINSTALLER CONFIGURATION - Typically not modified by users
# =============================================================================

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

