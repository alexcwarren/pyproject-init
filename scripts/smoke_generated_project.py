"""Smoke-test a freshly generated default project."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_NAME = "generated-smoke"
PROJECT_SLUG = "generated_smoke"

EXPECTED_FILES = (
    ".gitignore",
    ".python-version",
    "LICENSE",
    "README.md",
    "pyproject.toml",
    "src",
    "tests",
)

CHECK_DIRECTORIES: tuple[str, ...] = ("src", "tests")

GENERATED_CHECKS = (
    ("Synchronize generated project", ("uv", "sync", "--no-active")),
    ("Run generated CLI", ("uv", "run", "--no-active", PROJECT_NAME)),
    ("Run tests", ("uv", "run", "--no-active", "pytest")),
    ("Run Ruff lint", ("uv", "run", "--no-active", "ruff", "check", *CHECK_DIRECTORIES)),
    (
        "Run Ruff format check",
        ("uv", "run", "--no-active", "ruff", "format", *CHECK_DIRECTORIES, "--check"),
    ),
    ("Run MyPy", ("uv", "run", "--no-active", "mypy", *CHECK_DIRECTORIES)),
    ("Build generated project", ("uv", "build")),
)


def write(message: str = "") -> None:
    """Write a message to standard output."""
    sys.stdout.write(f"{message}\n")


def run(
    command: tuple[str, ...],
    *,
    cwd: Path,
) -> None:
    """Run a trusted command and stop on failure."""
    write("$ " + " ".join(command))

    subprocess.run(  # noqa: S603
        command,
        check=True,
        cwd=cwd,
    )


def run_expect_failure(
    command: tuple[str, ...],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    """Run a trusted command and require it to fail."""
    write("$ " + " ".join(command))

    result = subprocess.run(  # noqa: S603
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        raise RuntimeError("Command succeeded unexpectedly: " + " ".join(command))

    return result


def verify_expected_files(project_dir: Path) -> None:
    """Confirm the generated project contains expected top-level files."""
    missing = [name for name in EXPECTED_FILES if not (project_dir / name).exists()]

    if missing:
        missing_text = ", ".join(missing)
        raise RuntimeError(f"Generated project is missing: {missing_text}")


def verify_package_layout(project_dir: Path) -> None:
    """Confirm the generated src-layout package exists."""
    package_dir = project_dir / "src" / PROJECT_SLUG

    if not package_dir.is_dir():
        raise RuntimeError(f"Generated package directory not found: {package_dir}")

    main_file = package_dir / "main.py"

    if not main_file.is_file():
        raise RuntimeError(f"Generated main module not found: {main_file}")


def main() -> int:
    """Generate and verify a fresh default project."""
    repo_root = Path(__file__).resolve().parents[1]

    write("Running generated-project smoke test...")

    try:
        with tempfile.TemporaryDirectory(prefix="pyproject-init-generated-") as temp_dir:
            output_dir = Path(temp_dir)

            write()
            write("==> Generate project")

            run(
                (
                    "uv",
                    "run",
                    "pyproject-init",
                    "new",
                    PROJECT_NAME,
                    "--output-dir",
                    str(output_dir),
                    "--template",
                    "default",
                    "--no-input",
                ),
                cwd=repo_root,
            )

            write()
            write("==> Verify duplicate destination protection")

            duplicate_result = run_expect_failure(
                (
                    "uv",
                    "run",
                    "pyproject-init",
                    "new",
                    PROJECT_NAME,
                    "--output-dir",
                    str(output_dir),
                    "--template",
                    "default",
                    "--no-input",
                ),
                cwd=repo_root,
            )

            expected_message = "Project directory already exists"

            if expected_message not in duplicate_result.stderr:
                raise RuntimeError(
                    "Duplicate destination failed for an unexpected reason."
                )

            write("Duplicate destination was rejected as expected.")

            project_dir = output_dir / PROJECT_NAME

            write()
            write("==> Verify generated files")

            verify_expected_files(project_dir)
            verify_package_layout(project_dir)

            write("Generated file structure looks correct.")

            for name, command in GENERATED_CHECKS:
                write()
                write(f"==> {name}")
                run(command, cwd=project_dir)

            dist_dir = project_dir / "dist"

            if not dist_dir.is_dir():
                raise RuntimeError("Generated project did not produce dist/.")

            wheel_files = list(dist_dir.glob("*.whl"))
            sdist_files = list(dist_dir.glob("*.tar.gz"))

            if not wheel_files:
                raise RuntimeError("Generated project did not produce a wheel.")

            if not sdist_files:
                raise RuntimeError(
                    "Generated project did not produce a source distribution."
                )

            write()
            write("Generated project produced:")
            for artifact in sorted(wheel_files + sdist_files):
                write(f"  - {artifact.name}")

    except (subprocess.CalledProcessError, RuntimeError) as exc:
        sys.stderr.write(f"\nGenerated-project smoke test failed: {exc}\n")
        return 1

    write()
    write("Generated-project smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
