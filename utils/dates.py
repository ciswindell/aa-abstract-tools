#!/usr/bin/env python3
"""
Date parsing and formatting utilities.
"""

from datetime import datetime
from typing import Any

import pandas as pd
from dateutil.parser import parse as dateutil_parse


def parse_robust(value: Any) -> Any:
    """Parse a date value into pandas.Timestamp when possible, else return original.

    Preserves original value on failure to avoid data loss.
    """

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return value

    if isinstance(value, (datetime, pd.Timestamp)):
        return value

    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return value

    # Pandas parse
    try:
        parsed = pd.to_datetime(text, errors="raise")
        if pd.notna(parsed):
            return parsed
    except Exception:
        pass

    # Common formats
    common = [
        "%m/%d/%Y",
        "%m/%d/%y",
        "%m-%d-%Y",
        "%m-%d-%y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in common:
        try:
            return pd.Timestamp(datetime.strptime(text, fmt))
        except Exception:
            continue

    # dateutil fallback
    try:
        return pd.Timestamp(dateutil_parse(text))
    except Exception:
        return value


def format_mdy(dt: Any) -> str:
    """Format a datetime-like as M/D/YYYY without leading zeros; 'N/A' if not parseable."""

    if dt is None:
        return "N/A"

    # If string, try to parse via parse_robust
    if isinstance(dt, str):
        dt = parse_robust(dt)

    # Normalize to Timestamp
    if isinstance(dt, (datetime, pd.Timestamp)):
        try:
            # Use platform-friendly approach
            formatted = pd.Timestamp(dt).strftime("%m/%d/%Y")
            parts = formatted.split("/")
            return f"{int(parts[0])}/{int(parts[1])}/{parts[2]}"
        except Exception:
            return "N/A"

    return "N/A"
