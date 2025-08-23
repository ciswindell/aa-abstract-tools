#!/usr/bin/env python3
"""Shared pytest fixtures for tests."""

import pytest


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
