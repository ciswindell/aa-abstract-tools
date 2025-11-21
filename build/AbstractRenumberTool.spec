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

# Import version - SPECPATH is provided by PyInstaller
import sys
from pathlib import Path
# SPECPATH points to directory containing the spec file (build/)
# Parent is the repo root
_repo_root = str(Path(SPECPATH).parent)
sys.path.insert(0, _repo_root)
try:
    from _version import __version__
except (ImportError, AttributeError):
    __version__ = "dev"

APP_NAME = f'AbstractRenumberTool-v{__version__}'
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
    'tkinter.messagebox',
    # Numpy (pandas dependency)
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    # Pandas and all its internal modules
    'pandas',
    'pandas._libs',
    'pandas._libs.tslibs',
    'pandas._libs.tslibs.base',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.offsets',
    'pandas._libs.tslibs.parsing',
    'pandas._libs.tslibs.period',
    'pandas._libs.tslibs.strptime',
    'pandas._libs.tslibs.timestamps',
    'pandas._libs.tslibs.timezones',
    'pandas._libs.tslibs.tzconversion',
    'pandas._libs.tslibs.vectorized',
    'pandas._libs.hashtable',
    'pandas._libs.lib',
    'pandas._libs.missing',
    'pandas._libs.properties',
    'pandas.core',
    'pandas.core.groupby',
    'pandas.io',
    'pandas.io.formats',
    'pandas.io.formats.excel',
    'pandas.io.excel',
    'pandas.io.excel._base',
    'pandas.io.excel._openpyxl',
    # Excel file handling
    'openpyxl',
    'openpyxl.cell',
    'openpyxl.cell._writer',
    'openpyxl.styles',
    'openpyxl.styles.stylesheet',
    'openpyxl.worksheet',
    'openpyxl.worksheet._reader',
    'openpyxl.workbook',
    'openpyxl.utils',
    # PDF processing
    'pypdf',
    'pypdf._codecs',
    'pypdf._utils',
    'pypdf._reader',
    'pypdf._writer',
    # Natural sorting
    'natsort',
    # Date parsing
    'dateutil',
    'dateutil.parser',
    'dateutil.tz',
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

import os
# Note: sys and Path already imported above for version handling

# Get the repository root (parent of build directory)
# SPECPATH is provided by PyInstaller and points to the directory containing the spec file
REPO_ROOT = Path(SPECPATH).parent
ENTRY_POINT_PATH = str(REPO_ROOT / ENTRY_POINT)

block_cipher = None

a = Analysis(
    [ENTRY_POINT_PATH],
    pathex=[str(REPO_ROOT)],
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

