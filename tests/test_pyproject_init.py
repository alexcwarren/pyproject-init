from pathlib import Path

import pytest
from click.testing import CliRunner

from pyproject_init import pyproject_init
from pyproject_init.pyproject_init import cli


@pytest.fixture
def runner() -> CliRunner:
    """Fixture to provide a CliRunner instance."""
    return CliRunner()


def create_minimal_template(template_dir: Path) -> None:
    """Create a minimal cookiecutter template."""
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "cookiecutter.json").write_text(
        '{\n  "project_name": "Example Project",\n'
        "  \"project_slug\": \"{{ cookiecutter.project_name.lower().replace(' ', '-')"
        ' }}"\n'
        "}\n",
        encoding="utf-8",
    )
    project_dir = template_dir / "{{cookiecutter.project_slug}}"
    project_dir.mkdir()
    (project_dir / "README.md").write_text("Test README\n", encoding="utf-8")


def test_new_command_calls_cookiecutter(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that the 'new' command calls cookiecutter with expected args."""
    templates_dir = tmp_path / "templates"
    template_dir = templates_dir / "default"
    create_minimal_template(template_dir)
    monkeypatch.setattr(pyproject_init, "TEMPLATES_DIR", templates_dir)

    called: dict[str, object] = {}

    def fake_cookiecutter(
        *, template: str, output_dir: str, no_input: bool, **kwargs: object
    ) -> str:
        called["template"] = template
        called["output_dir"] = output_dir
        called["no_input"] = no_input
        called["extra_context"] = kwargs.get("extra_context")
        return str(Path(output_dir) / "example-project")

    monkeypatch.setattr(pyproject_init, "cookiecutter", fake_cookiecutter)

    output_dir = tmp_path / "out"
    result = runner.invoke(
        cli,
        ["new", "Example Project", "--output-dir", str(output_dir), "--no-input"],
    )

    assert result.exit_code == 0
    assert called["template"] == str(template_dir)
    assert called["output_dir"] == str(output_dir)
    assert called["no_input"] is True
    assert called["extra_context"] == {"project_name": "Example Project"}
    assert "Project created successfully" in result.output


def test_new_command_creates_project_from_template(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Integration-ish test using a minimal temporary template."""
    templates_dir = tmp_path / "templates"
    template_dir = templates_dir / "default"
    create_minimal_template(template_dir)
    monkeypatch.setattr(pyproject_init, "TEMPLATES_DIR", templates_dir)

    output_dir = tmp_path / "out"
    result = runner.invoke(
        cli,
        ["new", "Example Project", "--output-dir", str(output_dir), "--no-input"],
    )

    assert result.exit_code == 0
    generated_project = output_dir / "example-project"
    assert generated_project.is_dir()
    assert (generated_project / "README.md").is_file()
