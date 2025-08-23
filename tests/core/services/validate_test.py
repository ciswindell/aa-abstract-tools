#!/usr/bin/env python3
"""
Unit tests for ValidationService.
"""

import pandas as pd
import pytest

from core.services.validate import ValidationService


def test_validation_service_ok():
    df = pd.DataFrame(
        {
            "Index#": [1],
            "Document Type": ["Doc"],
            "Legal Description": ["X"],
            "Grantee": ["A"],
            "Grantor": ["B"],
            "Document Date": ["2024-01-01"],
            "Received Date": ["2024-01-02"],
        }
    )
    svc = ValidationService(
        [
            "Index#",
            "Document Type",
            "Legal Description",
            "Grantee",
            "Grantor",
            "Document Date",
            "Received Date",
        ]
    )
    report = svc.run(df=df, bookmarks=[])
    assert report.get("excel", {}).get("ok")
    assert report.get("pdf", {}).get("ok")


def test_validation_service_missing_required_raises():
    df = pd.DataFrame({"Index#": [1]})
    svc = ValidationService(["Index#", "Document Type"])
    with pytest.raises(ValueError):
        svc.run(df=df)
