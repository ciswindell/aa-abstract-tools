#!/usr/bin/env python3
"""
Abstract Renumber Tool - Build Script
Created: 2025-11-19
Feature: 004-pyinstaller-setup

This script orchestrates the PyInstaller build process with validation,
error handling, and clear user feedback.
"""

import argparse
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class BuildResult:
    """Result of a PyInstaller build operation."""

    success: bool
    executable_path: Optional[str]
    file_size_bytes: Optional[int]
    build_time_seconds: float
    error_message: Optional[str]
    warnings: list[str]

    def __str__(self) -> str:
        """Human-readable build summary."""
        if self.success:
            size_mb = (
                self.file_size_bytes / (1024 * 1024) if self.file_size_bytes else 0
            )
            minutes = int(self.build_time_seconds // 60)
            seconds = int(self.build_time_seconds % 60)
            return (
                f"Build completed successfully!\n"
                f"Executable: {self.executable_path}\n"
                f"Size: {size_mb:.1f} MB\n"
                f"Build time: {minutes}m {seconds}s"
            )
        else:
            return f"Build failed: {self.error_message}"


class BuildOrchestrator:
    """Orchestrates PyInstaller build process with validation."""

    def __init__(
        self,
        spec_file: str,
        mode: str = "onefile",
        optimize: str = "basic",
        clean: bool = False,
        verbose: bool = False,
    ):
        """
        Initialize build orchestrator.

        Args:
            spec_file: Path to PyInstaller spec file
            mode: Build mode ('onefile' or 'onedir')
            optimize: Optimization level ('basic', 'medium', 'aggressive')
            clean: Whether to clean build artifacts before building
            verbose: Whether to show detailed output

        Raises:
            ValueError: If parameters are invalid
        """
        if mode not in ("onefile", "onedir"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'onefile' or 'onedir'")
        if optimize not in ("basic", "medium", "aggressive"):
            raise ValueError(
                f"Invalid optimize: {optimize}. Must be 'basic', 'medium', or 'aggressive'"
            )

        self.spec_file = Path(spec_file)
        self.mode = mode
        self.optimize = optimize
        self.clean = clean
        self.verbose = verbose
        self.repo_root = Path(__file__).parent.parent

    def validate_prerequisites(self) -> tuple[bool, list[str]]:
        """
        Validate build prerequisites.

        Returns:
            Tuple of (success, error_messages)
        """
        errors = []

        # Check Python version
        if sys.version_info < (3, 7):
            errors.append(f"Python 3.7+ required, found {sys.version.split()[0]}")

        # Check PyInstaller installed
        try:
            import PyInstaller

            pyinstaller_version = PyInstaller.__version__
        except ImportError:
            errors.append("PyInstaller not installed. Run: pip install pyinstaller")
            pyinstaller_version = None

        # Check PyInstaller version
        if pyinstaller_version and not pyinstaller_version.startswith("6."):
            errors.append(f"PyInstaller 6.x required, found {pyinstaller_version}")

        # Check spec file exists
        if not self.spec_file.exists():
            errors.append(f"Spec file not found: {self.spec_file}")

        # Check entry point exists
        main_py = self.repo_root / "main.py"
        if not main_py.exists():
            errors.append(f"Entry point not found: {main_py}")

        # Check disk space (require at least 500MB)
        try:
            stat = shutil.disk_usage(self.repo_root)
            free_mb = stat.free / (1024 * 1024)
            if free_mb < 500:
                errors.append(
                    f"Insufficient disk space. Need 500MB, have {free_mb:.0f}MB"
                )
        except Exception as e:
            errors.append(f"Cannot check disk space: {e}")

        # Platform warning
        if platform.system() != "Windows" and not errors:
            print(
                "[⚠] Warning: Building on non-Windows platform. Test on Windows required."
            )

        return (len(errors) == 0, errors)

    def clean_build_directories(self) -> None:
        """Remove previous build artifacts."""
        dist_dir = self.repo_root / "dist"
        build_dir = self.repo_root / "build" / "build"

        removed = []
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
            removed.append("dist/")
        if build_dir.exists():
            shutil.rmtree(build_dir)
            removed.append("build/build/")

        if removed:
            print(f"[✓] Cleaned build directories: {', '.join(removed)}")

    def build(self) -> BuildResult:
        """
        Execute the build process.

        Returns:
            BuildResult object with status and metadata
        """
        warnings = []
        start_time = time.time()

        # Validate prerequisites
        success, errors = self.validate_prerequisites()
        if not success:
            error_msg = self._format_error(
                "Validation",
                "Prerequisites not met",
                "\n".join(f"- {err}" for err in errors),
                "Install missing dependencies and verify setup",
            )
            return BuildResult(
                success=False,
                executable_path=None,
                file_size_bytes=None,
                build_time_seconds=time.time() - start_time,
                error_message=error_msg,
                warnings=warnings,
            )

        print("[✓] Prerequisites validated")

        # Clean if requested
        if self.clean:
            self.clean_build_directories()

        # Build PyInstaller command
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            str(self.spec_file),
        ]
        # Note: Mode flags and collect-all are configured in the spec file, not via CLI

        # Add optimization flags
        if self.optimize == "medium":
            # Medium optimization requires UPX
            if not self._check_upx_available():
                warnings.append("UPX not found. Medium optimization disabled.")
            else:
                # Modify spec file to enable UPX (handled in spec file)
                pass

        # Add verbose flag
        if not self.verbose:
            cmd.append("--log-level=WARN")

        # Run PyInstaller
        print("[→] Running PyInstaller...")
        print(f"    Mode: {self.mode}")
        print(f"    Optimization: {self.optimize}")
        if self.verbose:
            print(f"    Command: {' '.join(cmd)}")
        print()

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=not self.verbose,
                text=True,
                check=True,
            )

            if not self.verbose and result.stdout:
                # Show summary even in non-verbose mode
                lines = result.stdout.strip().split("\n")
                important_lines = [
                    l
                    for l in lines
                    if "successfully" in l.lower() or "warning" in l.lower()
                ]
                if important_lines:
                    print("\n".join(important_lines))

        except subprocess.CalledProcessError as e:
            error_msg = self._format_error(
                "Build",
                "PyInstaller execution failed",
                e.stderr if e.stderr else str(e),
                "Check error output above for specific issues",
            )
            return BuildResult(
                success=False,
                executable_path=None,
                file_size_bytes=None,
                build_time_seconds=time.time() - start_time,
                error_message=error_msg,
                warnings=warnings,
            )

        # Post-build validation
        exe_path, validation_warnings = self._validate_build_output()
        warnings.extend(validation_warnings)

        if not exe_path:
            error_msg = self._format_error(
                "Post-Build Validation",
                "Executable not found after build",
                "Expected executable in dist/ directory but none found",
                "Check PyInstaller output for errors during packaging",
            )
            return BuildResult(
                success=False,
                executable_path=None,
                file_size_bytes=None,
                build_time_seconds=time.time() - start_time,
                error_message=error_msg,
                warnings=warnings,
            )

        # Get file size
        file_size = exe_path.stat().st_size if exe_path.exists() else None

        build_time = time.time() - start_time

        return BuildResult(
            success=True,
            executable_path=str(exe_path),
            file_size_bytes=file_size,
            build_time_seconds=build_time,
            error_message=None,
            warnings=warnings,
        )

    def _validate_build_output(self) -> tuple[Optional[Path], list[str]]:
        """
        Validate that build output exists and is reasonable.

        Returns:
            Tuple of (executable_path, warnings)
        """
        warnings = []
        dist_dir = self.repo_root / "dist"

        if not dist_dir.exists():
            return None, warnings

        # Find executable
        if self.mode == "onefile":
            exe_path = dist_dir / "AbstractRenumberTool.exe"
            if not exe_path.exists():
                return None, warnings
        else:
            exe_dir = dist_dir / "AbstractRenumberTool"
            exe_path = exe_dir / "AbstractRenumberTool.exe"
            if not exe_path.exists():
                return None, warnings

            # Check for _internal directory in onedir mode
            internal_dir = exe_dir / "_internal"
            if not internal_dir.exists():
                warnings.append("Missing _internal directory in onedir build")

        # Check file size is reasonable (10MB - 200MB)
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            if size_mb < 10:
                warnings.append(f"Executable size unusually small: {size_mb:.1f}MB")
            elif size_mb > 200:
                warnings.append(f"Executable size unusually large: {size_mb:.1f}MB")

        return exe_path, warnings

    def _check_upx_available(self) -> bool:
        """Check if UPX is available in PATH."""
        try:
            subprocess.run(["upx", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _format_error(
        self, category: str, brief: str, details: str, solution: str
    ) -> str:
        """
        Format error message following contract format.

        Args:
            category: Error category (e.g., "Validation", "Build")
            brief: Brief description
            details: Detailed explanation
            solution: How to fix

        Returns:
            Formatted error message
        """
        return (
            f"\n[ERROR] {category}: {brief}\n\n"
            f"Details:\n{details}\n\n"
            f"Solution:\n{solution}\n"
        )

    def get_build_info(self) -> dict:
        """
        Get information about the build configuration.

        Returns:
            Dictionary with build configuration details
        """
        try:
            import PyInstaller

            pyinstaller_version = PyInstaller.__version__
        except ImportError:
            pyinstaller_version = "not installed"

        return {
            "spec_file": str(self.spec_file),
            "mode": self.mode,
            "optimize": self.optimize,
            "entry_point": "main.py",
            "output_dir": "dist/",
            "python_version": sys.version.split()[0],
            "pyinstaller_version": pyinstaller_version,
        }


def print_build_summary(result: BuildResult) -> None:
    """Print formatted build summary."""
    print()
    print("=" * 70)
    if result.success:
        print("[✓] Build completed successfully!")
        print("=" * 70)
        print()
        print("Build Summary:")
        print("-" * 70)
        print(f"Executable: {result.executable_path}")
        if result.file_size_bytes:
            size_mb = result.file_size_bytes / (1024 * 1024)
            print(f"Size: {size_mb:.1f} MB")
        minutes = int(result.build_time_seconds // 60)
        seconds = int(result.build_time_seconds % 60)
        print(f"Build time: {minutes}m {seconds}s")

        if result.warnings:
            print()
            print("Warnings:")
            for warning in result.warnings:
                print(f"  ⚠ {warning}")

        print()
        print("Next Steps:")
        print("-" * 70)
        print("1. Test on clean Windows machine (see docs/testing-executable.md)")
        print("2. Verify all features work correctly")
        print("3. Distribute to end users")
        print()
    else:
        print("[✗] Build failed")
        print("=" * 70)
        print(result.error_message)
        if result.warnings:
            print()
            print("Warnings:")
            for warning in result.warnings:
                print(f"  ⚠ {warning}")
        print()


def main() -> int:
    """Main entry point for build script."""
    parser = argparse.ArgumentParser(
        description="Build Abstract Renumber Tool as Windows executable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Basic build
  %(prog)s --mode onedir                      # Directory mode
  %(prog)s --optimize medium --clean          # Optimized clean build
  %(prog)s --verbose                          # Verbose output
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["onefile", "onedir"],
        default="onefile",
        help="Build mode (default: onefile)",
    )

    parser.add_argument(
        "--optimize",
        choices=["basic", "medium", "aggressive"],
        default="basic",
        help="Optimization level (default: basic)",
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove previous build artifacts before building",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed PyInstaller output"
    )

    parser.add_argument(
        "--spec",
        default="build/AbstractRenumberTool.spec",
        help="Path to spec file (default: build/AbstractRenumberTool.spec)",
    )

    args = parser.parse_args()

    print()
    print("=" * 70)
    print("Abstract Renumber Tool - Build Script")
    print("=" * 70)
    print()

    try:
        orchestrator = BuildOrchestrator(
            spec_file=args.spec,
            mode=args.mode,
            optimize=args.optimize,
            clean=args.clean,
            verbose=args.verbose,
        )

        # Show build info
        if args.verbose:
            info = orchestrator.get_build_info()
            print("Build Configuration:")
            print("-" * 70)
            for key, value in info.items():
                print(f"  {key}: {value}")
            print()

        # Execute build
        result = orchestrator.build()

        # Print summary
        print_build_summary(result)

        # Return appropriate exit code
        if result.success:
            return 0
        else:
            # Determine exit code based on error type
            if "Validation" in (result.error_message or ""):
                return 1
            elif "Post-Build" in (result.error_message or ""):
                return 3
            else:
                return 2

    except ValueError as e:
        print(f"[ERROR] Configuration: {e}")
        return 1

    except KeyboardInterrupt:
        print("\n[✗] Build cancelled by user")
        return 130

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
