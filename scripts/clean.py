import enum
import logging
import click
import shutil
import sys
from pathlib import Path

logger = logging.getLogger("clean_script")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class LogLevel(enum.Enum):
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
    LogLevel.ERROR: logging.ERROR
}

# Define common directories and files to clean up
DIRS_TO_CLEAN = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    ".hatch",  # Hatch's own environment cache, if you want to clean it
]

FILES_TO_CLEAN = [
    ".coverage",
    "coverage.xml",
]


def rmtree_safe(path: str) -> int:
    """Safely remove a directory.

    Args:
        path (str): Path to directory.

    Returns:
        int: Number of directories removed.
    """
    path: Path = Path(path)
    if path.exists() and path.is_dir():
        logger.debug(f"Removing directory: {path}")
        try:
            shutil.rmtree(path)
        except OSError as e:
            logger.error(f"Error removing directory {path}: {e}", file=sys.stderr)
    elif path.exists():
        logger.warning(f"`{path}` exists but is not a directory. Skipping rmtree.")
    return 1


def remove_file_safe(path: str) -> int:
    """Safely remove file.

    Args:
        path (str): Path to file.

    Returns:
        int: Number of directories removed.

    """
    path: Path = Path(path)
    if path.exists() and path.is_file():
        logger.debug(f"Removing file: {path}")
        try:
            path.unlink()
        except OSError as e:
            logger.error(f"Error removing file {path}: {e}", file=sys.stderr)
    elif path.exists():
        logger.warning(f"`{path}` exists but is not a file. Skipping file removal.")
    return 1

@click.command()
@click.option('--root-dir', default=None)
@click.option(
    '--log-level',
    default=LogLevel.INFO,
    type=click.Choice(LogLevel, case_sensitive=False),
    help="Logging level."
)
def main(root_dir: str, log_level: LogLevel) -> None:
    """Run main function for clean.py.

    Args:
        root_dir (str): Path to root directory.

    """
    root_path: Path = Path.cwd()
    if root_dir is not None:
        root_path = Path(root_dir)

    level: int = LOG_LEVELS[log_level]
    logger.setLevel(level)

    logger.info("Starting clean process...")

    num_files: int = 0
    num_dirs: int = 0

    # Remove specific directories
    for d in DIRS_TO_CLEAN:
        num_dirs += rmtree_safe(f"{root_dir}/{d}")

    # Remove specific files
    for f in FILES_TO_CLEAN:
        num_files += remove_file_safe(f"{root_dir}/{f}")

    # Clean up *.egg-info directories (often created by build processes)
    for egg_info_dir in root_path.rglob("*.egg-info"):
        num_dirs += rmtree_safe(egg_info_dir)

    # Clean up .pyc files across the project
    for pyc_file in root_path.rglob("*.pyc"):
        num_files += remove_file_safe(str(pyc_file))

    logger.info(f"Cleaning complete: {num_files} files, {num_dirs} directories removed.")


if __name__ == "__main__":
    main()
