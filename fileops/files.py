#!/usr/bin/env python3
"""
File helpers for backups and atomic writes.
"""

import contextlib
import os
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

# Removed unused backup functions:
# - generate_backup_filename()
# - create_backup()
# - create_backups()
# These were replaced by atomic_save_with_backup() which handles backups internally.


def atomic_save_with_backup(
    original_path: str, write_func: Callable[[str], None], create_backup: bool = True
) -> str | None:
    """Atomically save to original file with optional backup.

    For single-file workflows with backup enabled:
    1. Create temp backup of original
    2. Write new content to original path
    3. Rename temp backup to timestamped backup

    For single-file workflows without backup:
    1. Write new content directly to original path

    Args:
        original_path: Path to the original file
        write_func: Function that writes content to the given path
        create_backup: Whether to create a backup of the original

    Returns:
        Backup path if backup was created, None otherwise
    """
    original = Path(original_path)

    if not create_backup:
        # Simple case: just write to original path
        write_func(str(original))
        return None

    # Backup case: temp backup → write original → rename backup
    temp_backup = None
    try:
        # Step 1: Create temp backup
        with tempfile.NamedTemporaryFile(
            prefix=f".tmp_backup_{original.stem}_",
            suffix=original.suffix,
            dir=original.parent,
            delete=False,
        ) as tf:
            temp_backup = Path(tf.name)

        shutil.copy2(original, temp_backup)

        # Step 2: Write new content to original path
        write_func(str(original))

        # Step 3: Rename temp backup to timestamped backup
        # Inline backup filename generation (replaced removed function)
        from datetime import datetime

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_backup_path = str(
            original.with_name(f"{original.stem}_backup_{ts}{original.suffix}")
        )
        temp_backup.rename(final_backup_path)
        temp_backup = None  # Successfully renamed

        return final_backup_path

    except Exception:
        # Cleanup temp backup on failure
        if temp_backup and temp_backup.exists():
            with contextlib.suppress(Exception):
                temp_backup.unlink()
        raise


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
            with contextlib.suppress(Exception):
                os.remove(temp_file)
