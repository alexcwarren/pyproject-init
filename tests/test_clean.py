import platform
from pathlib import Path

import pytest
from click.testing import CliRunner, Result

import scripts.clean as clean
from scripts.clean import CleanConfig, LogLevel, build_default_config


@pytest.fixture(scope="function")
def runner() -> CliRunner:
    """Fixture to provide a `CliRunner` instance."""
    return CliRunner()


def populate_tmp_path(base_path: Path, directories: list[str], files: list[str]) -> None:
    """Populate a directory with test directories and files."""
    for d in directories:
        base_path.joinpath(d).mkdir(parents=True)
    for f in files:
        file_path = base_path.joinpath(f)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()


def build_config(
    root_dir: Path, directories: list[str], files: list[str]
) -> CleanConfig:
    """Build a clean config from relative paths."""
    return CleanConfig(
        root_dir=root_dir,
        dirs_to_clean=[root_dir.joinpath(d) for d in directories],
        files_to_clean=[root_dir.joinpath(f) for f in files],
        assume_yes=True,
    )


MESSAGES: dict[LogLevel, list[str]] = {
    LogLevel.INFO: [
        "Cleaning directory: ",
        (
            f"Cleaning complete: {len(clean.DEFAULT_FILES_TO_CLEAN)} files,"
            f" {len(clean.DEFAULT_DIRS_TO_CLEAN)} directories removed."
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
                    + [MESSAGES[LogLevel.DEBUG][0]] * len(clean.DEFAULT_DIRS_TO_CLEAN)
                    + [MESSAGES[LogLevel.DEBUG][1]] * len(clean.DEFAULT_FILES_TO_CLEAN)
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
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    log_level: str | None,
    expected_sequence: list[str],
    unexpected_sequence: list[str],
) -> None:
    """Test logging in `clean.py`."""
    populate_tmp_path(
        tmp_path,
        list(clean.DEFAULT_DIRS_TO_CLEAN),
        list(clean.DEFAULT_FILES_TO_CLEAN),
    )
    config = build_default_config(tmp_path, assume_yes=True)

    if log_level is None:
        clean.clean(LogLevel.INFO, config)
    else:
        clean.clean(LogLevel[log_level.upper()], config)

    output = capsys.readouterr().out
    output_sequence: list[str] = [msg for msg in output.split("\n") if msg]
    assert len(expected_sequence) == len(output_sequence)
    for expected, observed in zip(expected_sequence, output_sequence, strict=False):
        assert expected in observed

    for unexpected in unexpected_sequence:
        assert unexpected not in output


def test_clean(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test standard use of `clean.py`."""
    populate_tmp_path(
        tmp_path,
        list(clean.DEFAULT_DIRS_TO_CLEAN),
        list(clean.DEFAULT_FILES_TO_CLEAN),
    )

    empty_config = CleanConfig(
        root_dir=tmp_path,
        dirs_to_clean=[],
        files_to_clean=[],
        assume_yes=True,
    )
    clean.clean(LogLevel.INFO, empty_config)
    assert "Cleaning complete: 0 files, 0 directories removed." in (
        capsys.readouterr().out
    )

    config = build_default_config(tmp_path, assume_yes=True)
    clean.clean(LogLevel.INFO, config)

    # Verify tmp_path removed correct directories and files
    for d in clean.DEFAULT_DIRS_TO_CLEAN:
        assert not tmp_path.joinpath(d).exists()
    for f in clean.DEFAULT_FILES_TO_CLEAN:
        assert not tmp_path.joinpath(f).exists()

    # Verify successive run doesn't break anything
    clean.clean(LogLevel.INFO, config)


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
    ],
)
def test_clean_bad_args(runner: CliRunner, bad_args: tuple[str]) -> None:
    """Test running `clean.py` with bad CLI arguments."""
    result: Result = runner.invoke(clean.main, [*bad_args, "--yes"])
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
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    directories: list[str],
    files: list[str],
) -> None:
    """Test `clean.py` when directory/file doesn't exist."""
    config = build_config(tmp_path, directories, files)
    clean.clean(LogLevel.DEBUG, config)

    output = capsys.readouterr().out
    for d in directories:
        assert f"{d}\" does not exist." in output
    for f in files:
        assert f"{f}\" does not exist." in output


# fmt: off
@pytest.mark.parametrize(
    "directories, files",
    [
        (list(clean.DEFAULT_FILES_TO_CLEAN[:1]), list(clean.DEFAULT_DIRS_TO_CLEAN[:1])),
    ]
)
# fmt: on
def test_clean_swap_directory_with_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    directories: list[str],
    files: list[str],
) -> None:
    """Test `clean.py` when directory swapped with file and vice versa."""
    for d in directories:
        tmp_path.joinpath(d).touch()
    for f in files:
        tmp_path.joinpath(f).mkdir(parents=True)

    config = build_config(tmp_path, directories, files)
    clean.clean(LogLevel.DEBUG, config)

    output = capsys.readouterr().out
    for d in directories:
        assert f"{d}\" exists but is not a directory." in output
    for f in files:
        assert f"{f}\" exists but is not a file." in output


def test_clean_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify OSErrors are handled properly when running `clean.py`."""
    populate_tmp_path(
        tmp_path,
        list(clean.DEFAULT_DIRS_TO_CLEAN),
        list(clean.DEFAULT_FILES_TO_CLEAN),
    )

    new_dir: Path = tmp_path.joinpath("new_dir")
    new_dir.mkdir()
    new_file: Path = new_dir.joinpath("new_file")
    new_file.touch()

    config = CleanConfig(
        root_dir=tmp_path,
        dirs_to_clean=[tmp_path.joinpath(d) for d in clean.DEFAULT_DIRS_TO_CLEAN]
        + [new_dir],
        files_to_clean=[tmp_path.joinpath(f) for f in clean.DEFAULT_FILES_TO_CLEAN]
        + [new_file],
        assume_yes=True,
    )

    if platform.system().lower().startswith("win"):
        with new_file.open("r"):
            clean.clean(LogLevel.DEBUG, config)
    else:
        original_rmtree = clean.shutil.rmtree
        original_unlink = Path.unlink

        def guarded_rmtree(target: Path) -> None:
            if target == new_dir:
                raise OSError("simulated rmtree error")
            original_rmtree(target)

        def guarded_unlink(target: Path) -> None:
            if target == new_file:
                raise OSError("simulated unlink error")
            original_unlink(target)

        monkeypatch.setattr(clean.shutil, "rmtree", guarded_rmtree)
        monkeypatch.setattr(Path, "unlink", guarded_unlink)
        clean.clean(LogLevel.DEBUG, config)

    output = capsys.readouterr().out
    expected_output: list[str] = [
        "Cleaning directory: ",
        "Error removing directory",
        "Error removing file",
        (
            f"Cleaning complete: {len(config.files_to_clean) - 1} files,"
            f" {len(config.dirs_to_clean) - 1} directories removed."
        ),
    ]

    matches: list[bool] = [False] * len(expected_output)
    i: int = 0
    for line in output.split("\n"):
        if expected_output[i] in line:
            matches[i] = True
            i += 1
        if i >= len(expected_output):
            break

    # If all elements of expected_output where found in output (in order), i
    # should equal length of expected_output
    assert matches.count(True) == len(expected_output)
