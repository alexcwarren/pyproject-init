import enum
import logging
import shutil
from collections.abc import Sequence
from dataclasses import dataclass
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
DEFAULT_DIRS_TO_CLEAN: tuple[str, ...] = (
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
)

DEFAULT_FILES_TO_CLEAN: tuple[str, ...] = (
    ".coverage",
    "coverage.xml",
)


class Output:
    """Class for outputting click.echo and console logging messages."""

    def __init__(self, logging_level: int | None = None) -> None:
        self.__logging_level: int | None = logging_level

    def debug(self, msg: str) -> None:
        """Output msg at severity DEBUG."""
        if self.__logging_level is not None and self.__logging_level <= logging.DEBUG:
            click.echo(msg)
        logging.debug(msg)

    def info(self, msg: str) -> None:
        """Output msg at severity INFO."""
        if self.__logging_level is not None and self.__logging_level <= logging.INFO:
            click.echo(msg)
        logging.debug(msg)

    def warning(self, msg: str) -> None:
        """Output msg at severity WARNING."""
        if self.__logging_level is not None and self.__logging_level <= logging.WARNING:
            click.echo(msg)
        logging.warning(msg)

    def error(self, msg: str) -> None:
        """Output msg at severity ERROR."""
        if self.__logging_level is not None and self.__logging_level <= logging.ERROR:
            click.echo(msg)
        logging.error(msg)

    def set_logging_level(self, logging_level: int) -> None:
        """Set logging severity level for Output.

        Args:
            logging_level (int): logging severity level.

        Raises:
            ValueError:
                logging_level must be one of logging module's included severities.

        """
        if logging_level not in LOG_LEVELS.values():
            raise ValueError(f"Invalid logging_level: {logging_level}")
        self.__logging_level = logging_level

    def __repr__(self) -> str:
        return f"Output({self.__logging_level = })"


output: Output = Output()


@dataclass(frozen=True)
class CleanConfig:
    """Configuration for cleaning operations."""

    root_dir: Path
    dirs_to_clean: Sequence[Path]
    files_to_clean: Sequence[Path]
    assume_yes: bool = False


@dataclass(frozen=True)
class CleanPlan:
    """Computed plan for cleaning operations."""

    root_dir: Path
    dir_targets: Sequence[Path]
    file_targets: Sequence[Path]
    egg_info_dirs: Sequence[Path]
    pyc_files: Sequence[Path]


def rmtree_safe(path: Path | str, output_sink: Output = output) -> int:
    """Safely remove a directory.

    Args:
        path (Path | str): Path to directory.
        output_sink (Output): Output handler for messages.

    Returns:
        int: Number of directories removed.

    """
    dir_path: Path = path if isinstance(path, Path) else Path(path)
    dir_removed: int = 0
    if dir_path.is_dir():
        output_sink.debug(f"Removing directory: {dir_path}")
        try:
            shutil.rmtree(dir_path)
            dir_removed += 1
        except OSError as e:
            output_sink.error(f"Error removing directory {dir_path}: {e}")
    elif dir_path.exists():
        output_sink.warning(
            f'"{dir_path}" exists but is not a directory. Skipping rmtree.'
        )
    else:
        output_sink.debug(f'"{dir_path}" does not exist.')
    return dir_removed


def remove_file_safe(path: Path | str, output_sink: Output = output) -> int:
    """Safely remove file.

    Args:
        path (Path | str): Path to file.
        output_sink (Output): Output handler for messages.

    Returns:
        int: Number of directories removed.

    """
    dir_path: Path = path if isinstance(path, Path) else Path(path)
    file_removed: int = 0
    if dir_path.is_file():
        output_sink.debug(f"Removing file: {dir_path}")
        try:
            dir_path.unlink()
            file_removed += 1
        except OSError as e:
            output_sink.error(f"Error removing file {dir_path}: {e}")
    elif dir_path.exists():
        output_sink.warning(
            f'"{dir_path}" exists but is not a file. Skipping file removal.'
        )
    else:
        output_sink.debug(f'"{dir_path}" does not exist.')
    return file_removed


def build_default_config(root_dir: Path, assume_yes: bool = False) -> CleanConfig:
    """Build the default clean configuration."""
    return CleanConfig(
        root_dir=root_dir,
        dirs_to_clean=[root_dir.joinpath(d) for d in DEFAULT_DIRS_TO_CLEAN],
        files_to_clean=[root_dir.joinpath(f) for f in DEFAULT_FILES_TO_CLEAN],
        assume_yes=assume_yes,
    )


def plan_clean(config: CleanConfig) -> CleanPlan:
    """Compute a cleaning plan without mutating the filesystem."""
    root_dir = config.root_dir
    return CleanPlan(
        root_dir=root_dir,
        dir_targets=list(config.dirs_to_clean),
        file_targets=list(config.files_to_clean),
        egg_info_dirs=list(root_dir.rglob("*.egg-info")),
        pyc_files=list(root_dir.rglob("*.pyc")),
    )


def apply_clean(plan: CleanPlan, output_sink: Output = output) -> tuple[int, int]:
    """Execute a cleaning plan."""
    num_files = 0
    num_dirs = 0

    for directory in plan.dir_targets:
        num_dirs += rmtree_safe(directory, output_sink=output_sink)

    for file_path in plan.file_targets:
        num_files += remove_file_safe(file_path, output_sink=output_sink)

    for egg_info_dir in plan.egg_info_dirs:
        num_dirs += rmtree_safe(egg_info_dir, output_sink=output_sink)

    for pyc_file in plan.pyc_files:
        num_files += remove_file_safe(pyc_file, output_sink=output_sink)

    return num_files, num_dirs


@click.command()
@click.option(
    "--log-level",
    "-l",
    default=LogLevel.INFO,
    type=click.Choice(LogLevel, case_sensitive=False),
    help="Logging level.",
)
@click.option(
    "--yes",
    is_flag=True,
    help="Skip confirmation prompt.",
)
def main(log_level: LogLevel, yes: bool) -> None:
    """Run main function for `clean.py`.

    Args:
        log_level (LogLevel): _description_
        yes (bool): Skip confirmation prompt.

    Raises:
        NotADirectoryError: IF `PROJECT_DIR` is not a directory or doesn't exist.

    """
    if not PROJECT_DIR.is_dir():
        raise NotADirectoryError(f'"{PROJECT_DIR.absolute()}" is not a valid directory')
    config = build_default_config(PROJECT_DIR, assume_yes=yes)
    clean(log_level, config)


def clean(log_level: LogLevel, config: CleanConfig) -> None:
    """Run main function for clean.py.

    Args:
        log_level (LogLevel): Logging level.
        config (CleanConfig): Configuration for cleaning.

    """
    level: int = LOG_LEVELS[log_level]
    logger.setLevel(level)
    output.set_logging_level(level)

    output.info(f"Cleaning directory: {config.root_dir}")

    if not config.assume_yes:
        do_proceed: bool = input("Proceed? (y/N): ").lower().startswith("y")
        if not do_proceed:
            return

    plan = plan_clean(config)
    num_files, num_dirs = apply_clean(plan, output_sink=output)

    output.info(f"Cleaning complete: {num_files} files, {num_dirs} directories removed.")


if __name__ == "__main__":
    main()
