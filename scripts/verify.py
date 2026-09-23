"""Run the routine local verification checks for pyproject-init."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    """A verification command and a human-readable label."""

    name: str
    command: tuple[str, ...]


CHECK_DIRECTORIES: tuple[str, ...] = ("src", "tests", "scripts")

CHECKS = (
    Check("Lockfile", ("uv", "lock", "--check")),
    Check("Ruff lint", ("uv", "run", "ruff", "check", *CHECK_DIRECTORIES)),
    Check(
        "Ruff format",
        ("uv", "run", "ruff", "format", *CHECK_DIRECTORIES, "--check"),
    ),
    Check("MyPy", ("uv", "run", "mypy", *CHECK_DIRECTORIES)),
    Check("Tests", ("uv", "run", "pytest")),
    Check("CLI help", ("uv", "run", "pyproject-init", "--help")),
    Check(
        "CLI new help",
        ("uv", "run", "pyproject-init", "new", "--help"),
    ),
)


def write(message: str = "") -> None:
    """Write a message to standard output."""
    sys.stdout.write(f"{message}\n")


def run_check(check: Check) -> None:
    """Run one verification command and stop on failure."""
    write()
    write(f"==> {check.name}")
    write("$ " + " ".join(check.command))

    subprocess.run(  # noqa: S603
        check.command,
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )


def main() -> int:
    """Run all routine verification checks."""
    write("Running pyproject-init verification...")

    try:
        for check in CHECKS:
            run_check(check)
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"\nVerification failed with exit code {exc.returncode}.\n")
        return exc.returncode

    write()
    write("All verification checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
