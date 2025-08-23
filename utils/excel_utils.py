#!/usr/bin/env python3
"""
Excel-related utilities shared across modules.
"""

from typing import Optional


def index_to_col_letter(position: int) -> str:
    """Convert 0-based column index to Excel column letter (A, B, ..., AA, AB, ...).

    Returns empty string for negative positions.
    """

    if position < 0:
        return ""

    result = ""
    col = position
    while col >= 0:
        result = chr(col % 26 + ord("A")) + result
        col = col // 26 - 1
    return result
