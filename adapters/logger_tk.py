#!/usr/bin/env python3
"""
Tkinter Logger adapter.

Bridges core Logger Protocol to a UI text/log function (e.g., Tk status area).
"""

from typing import Callable

from core.interfaces import Logger


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


class TkinterLogger(Logger):
    """Logger that writes to both console and UI for better debugging."""

    def __init__(self, gui) -> None:
        """Initialize with GUI for UI logging."""
        self.gui = gui

    def info(self, message: str) -> None:
        """Log an informational message to both console and UI."""
        print(f"INFO: {message}")  # Console output
        if hasattr(self.gui, 'log_status'):
            self.gui.log_status(message)  # UI output

    def error(self, message: str) -> None:
        """Log an error message to both console and UI."""
        print(f"ERROR: {message}")  # Console output
        if hasattr(self.gui, 'log_status'):
            self.gui.log_status(f"ERROR: {message}")  # UI output
