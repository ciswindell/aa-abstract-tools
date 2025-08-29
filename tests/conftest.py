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


@pytest.fixture
def pdf_engine_env(monkeypatch):
    """Backwards compat: force pypdf backend; to be removed soon."""
    monkeypatch.setenv("PDF_BACKEND", "pypdf")
    yield "pypdf"
    if "PDF_BACKEND" in os.environ:
        monkeypatch.delenv("PDF_BACKEND", raising=False)
