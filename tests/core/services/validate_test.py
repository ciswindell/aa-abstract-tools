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


def test_validation_service_duplicate_required_raises():
    # Duplicate required header 'Index#' should trigger a validation error
    df = pd.DataFrame([[1, 2]], columns=["Index#", "Index#"])  # duplicate name
    svc = ValidationService(["Index#"])  # only required column is duplicated
    with pytest.raises(ValueError) as excinfo:
        svc.run(df=df)
    assert "Duplicate required columns" in str(excinfo.value)


def test_validation_service_pdf_conflicts_raises():
    svc = ValidationService(["Index#"])  # headers irrelevant for this test
    # Two bookmarks pointing to the same page should trigger a conflict
    bookmarks = [
        {"title": "1-Doc", "page": 2},
        {"title": "2-Other", "page": 2},
    ]
    with pytest.raises(ValueError) as excinfo:
        svc.run(bookmarks=bookmarks)
    assert "PDF bookmark conflicts detected" in str(excinfo.value)
