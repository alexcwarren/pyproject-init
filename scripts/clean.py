import enum
import inspect
import logging
import shutil
import sys
from pathlib import Path

import click

PROJECT_DIR = Path(__file__).parent.parent

logger = logging.getLogger("clean_script")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class LogLevel(enum.Enum):
    """Class to define logging levels."""

    DEBUG = enum.auto()
    INFO = enum.auto()
    WARNING = enum.auto()
    WARN = enum.auto()
    ERROR = enum.auto()


LOG_LEVELS: dict[LogLevel, int] = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.WARNING: logging.WARNING,
    LogLevel.WARN: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
}

# Define common directories and files to clean up
DIRS_TO_CLEAN = [
    "__pycache__",
    r"src/pyproject_init/__pycache__",
    r"tests/__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    ".hatch",
    "htmlcov",
]

FILES_TO_CLEAN = [
    ".coverage",
    "coverage.xml",
]


def rmtree_safe(path: Path | str) -> int:
    """Safely remove a directory.

    Args:
        path (Path | str): Path to directory.

    Returns:
        int: Number of directories removed.

    """
    dir_path: Path = path if isinstance(path, Path) else Path(path)
    dir_removed: int = 0
    if dir_path.exists() and dir_path.is_dir():
        logger.debug(f"Removing directory: {dir_path}")
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            logger.error(f"Error removing directory {dir_path}: {e}", sys.stderr)
        dir_removed += 1
    elif dir_path.exists():
        logger.warning(f"`{dir_path}` exists but is not a directory. Skipping rmtree.")
    return dir_removed


def remove_file_safe(path: Path | str) -> int:
    """Safely remove file.

    Args:
        path (Path | str): Path to file.

    Returns:
        int: Number of directories removed.

    """
    dir_path: Path = path if isinstance(path, Path) else Path(path)
    file_removed: int = 0
    if dir_path.exists() and dir_path.is_file():
        logger.debug(f"Removing file: {dir_path}")
        try:
            dir_path.unlink()
        except OSError as e:
            logger.error(f"Error removing file {dir_path}: {e}", sys.stderr)
        file_removed += 1
    elif dir_path.exists():
        logger.warning(f"`{dir_path}` exists but is not a file. Skipping file removal.")
    return file_removed


@click.command()
@click.option(
    "--log-level",
    "-l",
    default=LogLevel.INFO,
    type=click.Choice(LogLevel, case_sensitive=False),
    help="Logging level.",
)
def main(log_level: LogLevel) -> None:
    """Run main function for clean.py.

    Args:
        log_level (LogLevel): Logging level.

    """
    root_path: Path = PROJECT_DIR
    level: int = LOG_LEVELS[log_level]
    logger.setLevel(level)

    logger.info(f"Cleaning directory: {root_path}")

    pytest_is_invoking: bool = any(
        "pytest" in frame.function for frame in inspect.stack()
    )
    if not pytest_is_invoking and not is_forced:
        do_proceed: bool = input("Proceed? (y/N): ").lower().startswith("y")
        if not do_proceed:
            return

    num_files: int = 0
    num_dirs: int = 0

    # Remove specific directories
    for d in DIRS_TO_CLEAN:
        num_dirs += rmtree_safe(root_path.joinpath(d))

    # Remove specific files
    for f in FILES_TO_CLEAN:
        num_files += remove_file_safe(root_path.joinpath(f))

    # Clean up *.egg-info directories (often created by build processes)
    for egg_info_dir in root_path.rglob("*.egg-info"):
        num_dirs += rmtree_safe(egg_info_dir)

    # Clean up .pyc files across the project
    for pyc_file in root_path.rglob("*.pyc"):
        num_files += remove_file_safe(str(pyc_file))

    logger.info(f"Cleaning complete: {num_files} files, {num_dirs} directories removed.")


if __name__ == "__main__":
    if not PROJECT_DIR.is_dir():
        raise NotADirectoryError(f'"{PROJECT_DIR.absolute()}" is not a valid directory')
    main()
