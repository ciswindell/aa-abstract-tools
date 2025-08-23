#!/usr/bin/env python3
"""
Abstract Renumber Tool entrypoint.

Thin launcher that delegates to the Tk application controller in app.tk_app.
"""

from app.tk_app import AbstractRenumberTool


def main() -> None:
    app = AbstractRenumberTool()
    app.run()


if __name__ == "__main__":
    main()
