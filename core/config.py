#!/usr/bin/env python3
"""
Centralized configuration defaults for the application.

Notes for developers:
- DEFAULT_REQUIRED_COLUMNS: Consumed by ValidationService and UI to validate Excel headers.
- DEFAULT_SORT_COLUMNS: Used by core.transform.excel.sort_and_renumber when no sort is provided.
- DEFAULT_SHEET_NAME: Seed/default for the processing sheet (UI reads this; services accept via Options).
"""

# Excel headers that must be present (case-insensitive match)
DEFAULT_REQUIRED_COLUMNS = [
    "Index#",
    "Document Type",
    "Legal Description",
    "Grantee",
    "Grantor",
    "Document Date",
    "Received Date",
]

# Preferred Excel sort order when none is supplied by caller
DEFAULT_SORT_COLUMNS = [
    "Received Date",
    "Document Date",
    "Document Type",
    "Grantor",
    "Grantee",
    "Legal Description",
]

# Default Excel sheet name used by the UI to resolve the processing sheet
DEFAULT_SHEET_NAME = "Index"

# PDF backend selection will be added when multiple backends are supported.
