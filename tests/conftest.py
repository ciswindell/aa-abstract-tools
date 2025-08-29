#!/usr/bin/env python3
"""Shared pytest fixtures for tests."""

import pytest
import os


class _TestLogger:
    def __init__(self) -> None:
        self.messages = []

    def info(self, message: str) -> None:
        self.messages.append(f"INFO:{message}")

    def error(self, message: str) -> None:
        self.messages.append(f"ERROR:{message}")


@pytest.fixture
def fake_logger():
    return _TestLogger()


@pytest.fixture(params=["pypdf", "pypdf2"])
def pdf_engine_env(monkeypatch, request):
    """Parametrize tests to run with both PDF engines where applicable."""
    monkeypatch.setenv("PDF_ENGINE", request.param)
    yield request.param
    # Restore to default behavior
    if "PDF_ENGINE" in os.environ:
        monkeypatch.delenv("PDF_ENGINE", raising=False)
