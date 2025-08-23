#!/usr/bin/env python3
"""
File helpers for backups and atomic writes.
"""

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Callable


def generate_backup_filename(original_path: str) -> str:
    """Return a timestamped backup filename in the same directory."""

    p = Path(original_path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(p.with_name(f"{p.stem}_backup_{ts}{p.suffix}"))


def create_backup(path: str) -> str:
    """Copy file to a timestamped backup path and return the backup path."""

    backup_path = generate_backup_filename(path)
    shutil.copy2(path, backup_path)
    return backup_path


def create_backups(excel_path: str, pdf_path: str) -> tuple[str, str]:
    """Create backups for Excel and PDF files, returning their backup paths."""

    return create_backup(excel_path), create_backup(pdf_path)


def atomic_write_with_template(
    template_path: str,
    out_path: str,
    write_into_path: Callable[[str], None],
) -> None:
    """Write using a template into a temp file, then atomically replace out_path.

    Steps:
      1) Create a temp file in out_path's directory.
      2) Copy template into the temp file.
      3) Call write_into_path(temp_file_path) to write updates.
      4) os.replace(temp_file_path, out_path) to atomically swap.
      5) Cleanup temp file on error.
    """

    dest_dir = os.path.dirname(out_path) or "."
    temp_file: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=".tmp_excel_",
            suffix=Path(out_path).suffix,
            dir=dest_dir,
            delete=False,
        ) as tf:
            temp_file = tf.name

        shutil.copy2(template_path, temp_file)
        write_into_path(temp_file)
        os.replace(temp_file, out_path)
        temp_file = None
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
