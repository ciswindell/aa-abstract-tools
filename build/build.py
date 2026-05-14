#!/usr/bin/env python3
"""Thin wrapper that runs PyInstaller against the project spec file.

For local builds. CI invokes this same script after injecting the version
from the release tag into `_version.py`. The actual packaging configuration
(hidden imports, excludes, exe name) lives in `build/AbstractRenumberTool.spec`.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_FILE = REPO_ROOT / "build" / "AbstractRenumberTool.spec"


def main() -> int:
    if not SPEC_FILE.exists():
        print(f"[ERROR] Spec file not found: {SPEC_FILE}", file=sys.stderr)
        return 1

    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", str(SPEC_FILE)]
    print(f"[>] {' '.join(cmd)}")

    try:
        subprocess.run(cmd, cwd=REPO_ROOT, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] PyInstaller exited with code {exc.returncode}", file=sys.stderr)
        return exc.returncode
    except FileNotFoundError:
        print(
            "[ERROR] PyInstaller not installed. Run: pip install pyinstaller",
            file=sys.stderr,
        )
        return 1

    print("[OK] Build complete. Executable in dist/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
