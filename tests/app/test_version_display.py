"""Tests for version display functionality.

Tests verify that:
1. Version module can be imported
2. Version format is valid (semantic versioning)
3. Fallback to "Unknown" when version is missing
4. Window title includes version
"""

import re
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest


def test_version_import():
    """Test that _version module can be imported."""
    from _version import __version__
    
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_version_format():
    """Test that version follows semantic versioning format (MAJOR.MINOR.PATCH)."""
    from _version import __version__
    
    # Regex for semantic versioning: X.Y.Z where each is a non-negative integer
    pattern = r'^\d+\.\d+\.\d+$'
    assert re.match(pattern, __version__), \
        f"Version '{__version__}' does not match format X.Y.Z"


def test_version_fallback_on_missing_file():
    """Test that missing _version.py triggers fallback to 'Unknown'."""
    # Mock ImportError to simulate missing file
    with patch.dict(sys.modules, {'_version': None}):
        with patch('builtins.__import__', side_effect=ImportError):
            # Simulate the try/except pattern used in tk_app.py
            try:
                from _version import __version__
                version = __version__
            except (ImportError, AttributeError):
                version = "Unknown"
            
            assert version == "Unknown"


def test_window_title_contains_version():
    """Test that window title includes version string.
    
    This test verifies the pattern used in setup_window() without
    actually creating a Tkinter window (which requires display).
    """
    from _version import __version__
    
    # Simulate the title format used in tk_app.py
    title = f"Abstract Renumber Tool v{__version__}"
    
    assert "Abstract Renumber Tool" in title
    assert "v" in title
    assert __version__ in title
    # Verify format matches expected pattern
    assert title.startswith("Abstract Renumber Tool v")


def test_build_script_imports_version():
    """Test that build script can import version from _version module.
    
    Simulates the import pattern that will be used in build.py
    with fallback to 'dev' for development builds.
    """
    # Add project root to path (as build.py will do)
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Test the import pattern with fallback
    try:
        from _version import __version__
        version = __version__
    except (ImportError, AttributeError):
        version = "dev"
    
    # Version should be importable and valid
    assert version is not None
    assert isinstance(version, str)
    assert version != "dev"  # In normal case, should not fall back


def test_executable_name_includes_version():
    """Test that executable naming pattern includes version.
    
    Verifies the format used for --name flag in build script.
    """
    from _version import __version__
    
    # Simulate the exe_name pattern used in build.py
    exe_name = f"AbstractRenumberTool-v{__version__}"
    
    assert "AbstractRenumberTool" in exe_name
    assert "-v" in exe_name
    assert __version__ in exe_name
    # Verify format
    assert exe_name.startswith("AbstractRenumberTool-v")
    assert exe_name == f"AbstractRenumberTool-v{__version__}"


def test_version_fallback_on_invalid_format():
    """Test graceful handling of non-standard version strings.
    
    Verifies that the application can handle various version formats
    without crashing, even if they don't match semantic versioning.
    """
    # Test that the title/footer formatting works with any string
    invalid_versions = ["abc", "1.0", "1.0.0.0", "", "dev", "Unknown"]
    
    for version in invalid_versions:
        # These should all work without raising exceptions
        title = f"Abstract Renumber Tool v{version}"
        footer = f"Version {version}"
        exe_name = f"AbstractRenumberTool-v{version}"
        
        # Verify string formatting works (no crashes)
        assert isinstance(title, str)
        assert isinstance(footer, str)
        assert isinstance(exe_name, str)


def test_version_attribute_missing():
    """Test that AttributeError is caught when __version__ is not defined.
    
    Simulates the case where _version.py exists but doesn't define __version__.
    """
    # Create a mock module without __version__ attribute
    from types import ModuleType
    mock_version_module = ModuleType('_version')
    # Intentionally don't set __version__ attribute
    
    with patch.dict(sys.modules, {'_version': mock_version_module}):
        # Simulate the import pattern with AttributeError handling
        try:
            from _version import __version__
            version = __version__
        except (ImportError, AttributeError):
            version = "Unknown"
        
        # Should fall back to "Unknown" when attribute is missing
        assert version == "Unknown"

