#!/usr/bin/env python3
"""
Tkinter Logger adapter.

Bridges core Logger Protocol to a UI text/log function (e.g., Tk status area).
"""

from typing import Callable

from core.interfaces import Logger
from core.message_types import MSG_ERROR, MSG_INFO, MSG_WARNING


class TkLogger(Logger):
    """Logger that forwards messages to a provided write function."""

    def __init__(self, write: Callable[[str], None]) -> None:
        """Initialize with a callable that accepts a single string message."""

        self._write = write

    def info(self, message: str) -> None:
        """Log an informational message to the UI."""

        self._write(message)

    def error(self, message: str) -> None:
        """Log an error message to the UI."""

        self._write(message)
    
    def warning(self, message: str) -> None:
        """Log a warning message to the UI."""

        self._write(message)


class TkinterLogger(Logger):
    """Logger that writes to both console and UI with color-coded message types.
    
    Uses MSG_INFO for informational messages (black text), MSG_ERROR for
    error messages (red bold text), and MSG_WARNING for warning messages
    (orange text) to provide visual distinction in the UI.
    """

    def __init__(self, gui) -> None:
        """Initialize with GUI for UI logging."""
        self.gui = gui

    def info(self, message: str) -> None:
        """Log an informational message to both console and UI.
        
        Displays in black text (MSG_INFO) in the status area.
        """
        print(f"INFO: {message}")  # Console output
        if hasattr(self.gui, 'log_status'):
            self.gui.log_status(message, MSG_INFO)  # UI output with info styling

    def error(self, message: str) -> None:
        """Log an error message to both console and UI.
        
        Displays in red bold text (MSG_ERROR) in the status area for high visibility.
        """
        print(f"ERROR: {message}")  # Console output
        if hasattr(self.gui, 'log_status'):
            self.gui.log_status(f"ERROR: {message}", MSG_ERROR)  # UI output with error styling
    
    def warning(self, message: str) -> None:
        """Log a warning message to both console and UI.
        
        Displays in orange text (MSG_WARNING) in the status area.
        """
        print(f"WARNING: {message}")  # Console output
        if hasattr(self.gui, 'log_status'):
            self.gui.log_status(f"WARNING: {message}", MSG_WARNING)  # UI output with warning styling
