from pathlib import Path

import pytest
from click.testing import CliRunner, Result

import scripts.clean as clean
from scripts.clean import LogLevel


@pytest.fixture(scope="function")
def runner() -> CliRunner:
    """Fixture to provide a `CliRunner` instance.

    Returns:
        CliRunner: instance of `CliRunner` class.

    """
    return CliRunner()


@pytest.fixture(scope="function")
def tmp_path(tmp_path: Path) -> Path:
    """Provide `pytest`'s `tmp_path` fixture with directories and files to clean.

    Args:
        tmp_path (Path): `pytest`'s `tmp_path` fixture.

    Returns:
        Path: `tmp_path` containing newly created directories and files.

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
        (
            f"Cleaning complete: {len(clean.FILES_TO_CLEAN)} files,"
            f" {len(clean.DIRS_TO_CLEAN)} directories removed."
        ),
    ],
    LogLevel.DEBUG: [
        "Removing directory: ",
        "Removing file: ",
    ],
}


# Skip lint formatting of pytest.mark.parametrize block:
# fmt: off
@pytest.mark.parametrize(
    "log_level, expected_sequence, unexpected_sequence",
    [
        (None,      MESSAGES[LogLevel.INFO], MESSAGES[LogLevel.DEBUG]),
        ("debug",
                    [MESSAGES[LogLevel.INFO][0]]
                    + [MESSAGES[LogLevel.DEBUG][0]] * len(clean.DIRS_TO_CLEAN)
                    + [MESSAGES[LogLevel.DEBUG][1]] * len(clean.FILES_TO_CLEAN)
                    + [MESSAGES[LogLevel.INFO][1]],
                    []
        ),
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
    expected_sequence: list[str],
    unexpected_sequence: list[str]
) -> None:
    """Test logging in `clean.py`.

    Args:
        runner (CliRunner): Provides functionality to invoke a `click` command.
        tmp_path (Path): Testing directory provided by `pytest`.
        log_level (str | None): Logging level to output at.
        expected_sequence (list[str]): Sequence of expected logging messages.
        unexpected_sequence (list[str]): Sequence of unexpected logging messages.

    """
    # Verify tmp_path is not empty
    assert verify_tmp_path(tmp_path)

    result: Result = (
        runner.invoke(clean.main)
        if log_level is None
        else runner.invoke(clean.main, ["--log-level", log_level])
    )
    assert result.exit_code == 0

    output_sequence: list = [msg for msg in result.output.split("\n") if msg]
    assert len(expected_sequence) == len(output_sequence)
    for e, o in zip(expected_sequence, output_sequence, strict=False):
        assert e in o

    for unexpected in unexpected_sequence:
        assert unexpected not in result.output


@pytest.mark.parametrize(
    "args",
    [
        ("--log-level", "info"),
        ("--log-level", "INFO"),
        ("--log-level", "debug"),
        ("--log-level", "DEBUG"),
        ("--log-level", "warning"),
        ("--log-level", "WARNING"),
        ("--log-level", "warn"),
        ("--log-level", "WARN"),
        ("--log-level", "error"),
        ("--log-level", "ERROR"),
        ("-l", "info"),
        ("-l", "INFO"),
        ("-l", "debug"),
        ("-l", "DEBUG"),
        ("-l", "warning"),
        ("-l", "WARNING"),
        ("-l", "warn"),
        ("-l", "WARN"),
        ("-l", "error"),
        ("-l", "ERROR"),
    ]
)
def test_clean(runner: CliRunner, tmp_path: Path, args: tuple[str]) -> None:
    """Test standard use of `clean.py`.

    Args:
        runner (CliRunner): Provides functionality to invoke a `click` command.
        tmp_path (Path): Testing directory provided by `pytest`.
        args (tuple[str]): Tuple of valid argument strings.

    """
    # Verify tmp_path is not empty
    assert verify_tmp_path(tmp_path)

    # Invoke clean.py CLI when clean.DIRS_TO_CLEAN and clean.FILES_TO_CLEAN are empty
    clean.DIRS_TO_CLEAN, original_dirs = [], clean.DIRS_TO_CLEAN
    clean.FILES_TO_CLEAN, original_files = [], clean.FILES_TO_CLEAN

    result: Result = runner.invoke(clean.main, args)
    assert result.exit_code == 0

    clean.DIRS_TO_CLEAN = original_dirs
    clean.FILES_TO_CLEAN = original_files

    # Invoke clean.py CLI under normal conditions
    result = runner.invoke(clean.main)
    assert result.exit_code == 0

    # Verify tmp_path removed correct directories and files
    for d in clean.DIRS_TO_CLEAN:
        assert not tmp_path.joinpath(d).exists()
    for f in clean.FILES_TO_CLEAN:
        assert not tmp_path.joinpath(f).exists()

    # Verfiy successive run doesn't break anything
    result = runner.invoke(clean.main)
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "bad_args",
    [
        ("--log-level", ""),
        ("-l", ""),
        ("--log-level", "inf0"),
        ("--log-level", "d3bug"),
        ("--log-level", "3RR0R"),
        ("log"),
        ("bad"),
    ]
)
def test_clean_bad_args(runner: CliRunner, tmp_path: Path, bad_args: tuple[str]) -> None:
    """Test running `clean.py` with bad CLI arguments.

    Args:
        runner (CliRunner): Provides functionality to invoke a `click` command.
        tmp_path (Path): Testing directory provided by `pytest`.
        bad_args (tuple[str]): Tuple of invalid arguments.

    """
    # Verify tmp_path is not empty
    assert verify_tmp_path(tmp_path)

    result: Result = runner.invoke(clean.main, bad_args)
    assert result.exit_code != 0


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
        runner (CliRunner): Provides functionality to invoke a `click` command.
        tmp_path (Path): Testing directory provided by `pytest`.
        directories (list[str]): List of non-existant directory/ies.
        files (list[str]): List of non-existant file/s.

    """
    # Verify tmp_path is not empty
    assert verify_tmp_path(tmp_path)

    clean.DIRS_TO_CLEAN, original_dirs = directories, clean.DIRS_TO_CLEAN
    clean.FILES_TO_CLEAN, original_files = files, clean.FILES_TO_CLEAN

    result: Result = runner.invoke(clean.main, ["-l", "debug"])
    assert result.exit_code == 0

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
        runner (CliRunner): Provides functionality to invoke a `click` command.
        tmp_path (Path): Testing directory provided by `pytest`.
        directories (list[str]): List of "directory/ies" that are actually file/s.
        files (list[str]): List of "file/s" that are actually directory/ies.

    """
    # Verify tmp_path is not empty
    assert verify_tmp_path(tmp_path)

    clean.DIRS_TO_CLEAN, original_dirs = directories, clean.DIRS_TO_CLEAN
    clean.FILES_TO_CLEAN, original_files = files, clean.FILES_TO_CLEAN

    result: Result = runner.invoke(clean.main, ["-l", "debug"])
    assert result.exit_code == 0

    clean.DIRS_TO_CLEAN = original_dirs
    clean.FILES_TO_CLEAN = original_files

    assert len(directories) > 0
    for d in directories:
        assert f"{d}\" exists but is not a directory." in result.output
    assert len(files) > 0
    for f in files:
        assert f"{f}\" exists but is not a file." in result.output


def test_clean_errors(runner: CliRunner, tmp_path: Path) -> None:
    """Verify OSErrors are handled properly when running `clean.py`.

    Args:
        runner (CliRunner): Provides functionality to invoke a `click` command.
        tmp_path (Path): Testing directory provided by `pytest`.

    """
    # Verify tmp_path is not empty
    assert verify_tmp_path(tmp_path)

    # Create new file in a directory from DIRS_TO_CLEAN
    new_file: Path = tmp_path.joinpath(clean.DIRS_TO_CLEAN[0]).joinpath("test_file")
    new_file.touch()

    # Add new_file to FILES_TO_CLEAN so running clean.py will trigger an error both while
    # attempting to delete the directory containing new_file and when attempting to
    # delete new_file itself
    original_files: list[str] = clean.FILES_TO_CLEAN
    clean.FILES_TO_CLEAN.append(f"{new_file.parent.name}/{new_file.name}")

    # Run clean.py while new_file is open
    with Path.open(new_file) as _:
        result: Result = runner.invoke(clean.main, ["-l", "debug"])
    assert result.exit_code == 0

    clean.FILES_TO_CLEAN = original_files

    expected_output: list[str] = [
        "Cleaning directory: ",
        "Error removing directory",
        "Error removing file",
        (
            f"Cleaning complete: {len(clean.FILES_TO_CLEAN) - 1} files,"
            f" {len(clean.DIRS_TO_CLEAN) - 1} directories removed."
        ),
    ]

    i: int = 0
    for line in result.output.split("\n"):
        i += 1 if expected_output[i] in line else 0
        if i >= len(expected_output):
            break
    # If all elements of expected_output where found in result.output (in order), i
    # should equal length of expected_output
    assert i == len(expected_output)


def verify_tmp_path(path: Path) -> bool:
    """Verify `pytest`'s `tmp_path` contains correct directories and files.

    Args:
        path (Path): `pytest`'s `tmp_path` fixture.

    Returns:
        bool: Returns `True` if `tmp_path` contains all correct directories and files.
              Returns `False` otherwise.

    """
    # Concatenate DIRS_TO_CLEAN and FILES_TO_CLEAN into one list of items:
    #     clean.DIRS_TO_CLEAN + clean.FILES_TO_CLEAN
    # Create sequence from this concatenated list where each element is True if each item
    # exists at least in one location in `path`:
    #     any(path.rglob(item)) for item in clean.DIRS_TO_CLEAN + clean.FILES_TO_CLEAN
    # return True if any of this sequence's elements is True, otherwise False:
    return any(
        any(path.rglob(item)) for item in clean.DIRS_TO_CLEAN + clean.FILES_TO_CLEAN
    )
