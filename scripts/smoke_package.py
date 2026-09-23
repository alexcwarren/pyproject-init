"""Smoke-test the built pyproject-init wheel in a clean environment."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_NAME = "wheel-smoke"


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


def find_single_artifact(dist_dir: Path, pattern: str) -> Path:
    """Return exactly one matching build artifact."""
    matches = list(dist_dir.glob(pattern))

    if not matches:
        raise RuntimeError(f"No artifact matching {pattern!r} found in {dist_dir}.")

    if len(matches) > 1:
        names = ", ".join(path.name for path in matches)
        raise RuntimeError(f"Expected one artifact matching {pattern!r}, found: {names}")

    return matches[0]


def main() -> int:
    """Build, install, and smoke-test the packaged CLI."""
    repo_root = Path(__file__).resolve().parents[1]
    dist_dir = repo_root / "dist"

    write("Running package smoke test...")

    try:
        if dist_dir.exists():
            shutil.rmtree(dist_dir)

        write()
        write("==> Build package")

        run(("uv", "build"), cwd=repo_root)

        wheel = find_single_artifact(dist_dir, "*.whl")
        sdist = find_single_artifact(dist_dir, "*.tar.gz")

        write()
        write("Built artifacts:")
        write(f"  - {wheel.name}")
        write(f"  - {sdist.name}")

        with tempfile.TemporaryDirectory(prefix="pyproject-init-package-") as temp_dir:
            test_root = Path(temp_dir)
            venv_dir = test_root / ".venv"

            write()
            write("==> Create clean virtual environment")

            run(
                (
                    "uv",
                    "venv",
                    str(venv_dir),
                    "--python",
                    "3.14",
                ),
                cwd=test_root,
            )

            python_exe = venv_dir / "Scripts" / "python.exe"
            cli_exe = venv_dir / "Scripts" / "pyproject-init.exe"

            if sys.platform != "win32":
                python_exe = venv_dir / "bin" / "python"
                cli_exe = venv_dir / "bin" / "pyproject-init"

            write()
            write("==> Install built wheel")

            run(
                (
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    str(python_exe),
                    str(wheel),
                ),
                cwd=test_root,
            )

            write()
            write("==> Verify installed CLI")

            run(
                (str(cli_exe), "--help"),
                cwd=test_root,
            )

            write()
            write("==> Generate project from packaged template")

            run(
                (
                    str(cli_exe),
                    "new",
                    PROJECT_NAME,
                    "--output-dir",
                    str(test_root),
                    "--template",
                    "default",
                    "--no-input",
                ),
                cwd=test_root,
            )

            generated_project = test_root / PROJECT_NAME

            if not generated_project.is_dir():
                raise RuntimeError(f"Generated project not found: {generated_project}")

            expected_files = (
                ".gitignore",
                ".python-version",
                "LICENSE",
                "README.md",
                "pyproject.toml",
                "src",
                "tests",
            )

            missing = [
                name
                for name in expected_files
                if not (generated_project / name).exists()
            ]

            if missing:
                raise RuntimeError(
                    "Packaged template generated an incomplete project: "
                    + ", ".join(missing)
                )

            write()
            write("Packaged template generated the expected project structure.")

    except (subprocess.CalledProcessError, RuntimeError) as exc:
        sys.stderr.write(f"\nPackage smoke test failed: {exc}\n")
        return 1

    write()
    write("Package smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
