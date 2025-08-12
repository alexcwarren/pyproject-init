import stat
from pathlib import Path

import pytest
from click.testing import CliRunner, Result

import scripts.clean as clean
from scripts.clean import LogLevel


@pytest.fixture(scope="function")
def runner() -> CliRunner:
    """Fixture to provide a CliRunner instance.

    Returns:
        CliRunner: instance of CliRunner class.

    """
    return CliRunner()


@pytest.fixture(scope="function")
def tmp_path(tmp_path: Path) -> Path:
    """Provide `pytest`'s tmp_path with directories and files to clean.

    Args:
        tmp_path (Path): `pytest`'s tmp_path Path fixture.

    Returns:
        Path: tmp_path containing newly created directories and files.

    """
    directories: list[str] = clean.DIRS_TO_CLEAN.copy()
    for d in directories:
        tmp_path.joinpath(d).mkdir(parents=True)
    files: list[str] = clean.FILES_TO_CLEAN.copy()
    for f in files:
        tmp_path.joinpath(f).touch()
    clean.PROJECT_DIR = tmp_path
    return tmp_path


MESSAGES: dict[LogLevel, list[str]] = {
    LogLevel.INFO: [
        "Cleaning directory: ",
        "Cleaning complete: ",
        f"{len(clean.FILES_TO_CLEAN)} files, ",
        f"{len(clean.DIRS_TO_CLEAN)} directories removed.",
    ],
    LogLevel.DEBUG: [
        "Removing directory: ",
        "Removing file: ",
    ],
}


# Skip lint formatting of pytest.mark.parametrize block:
# fmt: off
@pytest.mark.parametrize(
    "log_level, expected_list, unexpected_list",
    [
        (None,      MESSAGES[LogLevel.INFO], MESSAGES[LogLevel.DEBUG]),
        ("debug",   MESSAGES[LogLevel.DEBUG] + MESSAGES[LogLevel.INFO], []),
        ("info",    MESSAGES[LogLevel.INFO], MESSAGES[LogLevel.DEBUG]),
        ("warning", [], MESSAGES[LogLevel.DEBUG] + MESSAGES[LogLevel.INFO]),
        ("warn",    [], MESSAGES[LogLevel.DEBUG] + MESSAGES[LogLevel.INFO]),
        ("error",   [], MESSAGES[LogLevel.DEBUG] + MESSAGES[LogLevel.INFO]),
    ],
)
# fmt: on
def test_logging(
    runner: CliRunner,
    tmp_path: Path,
    log_level: str | None,
    expected_list: list[str],
    unexpected_list: list[str]
) -> None:
    """Test logging in `clean.py`.

    Args:
        runner (CliRunner): Provides functionality to invoke a `click` command.
        tmp_path (Path): Testing directory provided by `pytest`.
        log_level (str | None): Logging level to output at.
        expected_list (list[str]): ...
        unexpected_list (list[str]): ...

    """
    result: Result = (
        runner.invoke(clean.main)
        if log_level is None
        else runner.invoke(clean.main, ["--log-level", log_level])
    )
    for expected in expected_list:
        assert expected in result.output
    for unexpected in unexpected_list:
        assert unexpected not in result.output


def test_clean(runner: CliRunner, tmp_path: Path) -> None:
    """Test standard use of `clean.py`.

    Args:
        runner (CliRunner): Provides functionality to invoke a `click` command.
        tmp_path (Path): Testing directory provided by `pytest`.

    """
    # Verify tmp_path is not empty
    assert any(tmp_path.iterdir())

    # Invoke clean.py CLI
    runner.invoke(clean.main)

    # Verify tmp_path removed correct directories and files
    for item in tmp_path.iterdir():
        assert item not in clean.DIRS_TO_CLEAN
        assert item not in clean.FILES_TO_CLEAN


# fmt: off
@pytest.mark.parametrize(
    "directories, files",
    [
        (["fake_dir"], ["fake_file"]),
    ]
)
# fmt: on
def test_clean_does_not_exist(
    runner: CliRunner,
    tmp_path: Path,
    directories: list[str],
    files: list[str]
) -> None:
    """Test `clean.py` when directory/file doesn't exist.

    Args:
        runner (CliRunner): ...
        tmp_path (Path): ...
        directories (list[str]): ...
        files (list[str]): ...

    """
    assert any(tmp_path.iterdir())

    clean.DIRS_TO_CLEAN, original_dirs = directories.copy(), clean.DIRS_TO_CLEAN
    clean.FILES_TO_CLEAN, original_files = files.copy(), clean.FILES_TO_CLEAN

    result: Result = runner.invoke(clean.main, ["-l", "debug"])

    clean.DIRS_TO_CLEAN = original_dirs
    clean.FILES_TO_CLEAN = original_files

    assert len(directories) > 0
    for d in directories:
        assert f"{d}\" does not exist." in result.output
    assert len(files) > 0
    for f in files:
        assert f"{f}\" does not exist." in result.output


# fmt: off
@pytest.mark.parametrize(
    "directories, files",
    [
        (clean.FILES_TO_CLEAN[:1], clean.DIRS_TO_CLEAN[:1]),
    ]
)
# fmt: on
def test_clean_swap_directory_with_file(
    runner: CliRunner,
    tmp_path: Path,
    directories: list[str],
    files: list[str]
) -> None:
    """Test `clean.py` when directory swapped with file and vice versa.

    Args:
        runner (CliRunner): ...
        tmp_path (Path): ...
        directories (list[str]): ...
        files (list[str]): ...

    """
    assert any(tmp_path.iterdir())

    clean.DIRS_TO_CLEAN, original_dirs = directories.copy(), clean.DIRS_TO_CLEAN
    clean.FILES_TO_CLEAN, original_files = files.copy(), clean.FILES_TO_CLEAN

    result: Result = runner.invoke(clean.main, ["-l", "debug"])

    clean.DIRS_TO_CLEAN = original_dirs
    clean.FILES_TO_CLEAN = original_files

    assert len(directories) > 0
    for d in directories:
        assert f"{d}\" exists but is not a directory." in result.output
    assert len(files) > 0
    for f in files:
        assert f"{f}\" exists but is not a file." in result.output


def test_clean_errors(
    runner: CliRunner,
    tmp_path: Path,
) -> None:
    """Test `clean.py` with directories/files lacking permission to delete.

    Args:
        runner (CliRunner): ...
        tmp_path (Path): ...

    """
    for item in tmp_path.iterdir():
        item.chmod(stat.S_IREAD)
    tmp_path.chmod(stat.S_IREAD | stat.S_IEXEC)
    result: Result = runner.invoke(clean.main)
    assert "Error removing file " in result.output
    assert "Error removing directory " in result.output
