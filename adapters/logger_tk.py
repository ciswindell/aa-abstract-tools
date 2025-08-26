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
