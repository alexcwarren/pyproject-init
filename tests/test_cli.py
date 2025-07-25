import pytest
from click.testing import CliRunner
from pyproject_init.cli import cli
from pathlib import Path
import shutil

# Fixture to provide a CliRunner instance
@pytest.fixture
def runner():
    return CliRunner()

# Test the 'new' command
def test_new_command_creates_project(runner, tmp_path: Path):
    """
    Tests that the 'pyproject-init new' command successfully creates a project
    in a temporary directory.
    """
    project_name = "test-new-project"
    output_dir = tmp_path # Use pytest's tmp_path fixture for a temporary directory

    # Create a dummy cookiecutter.json for the internal template for this test
    # In a real scenario, we'd mock cookiecutter, but for integration, this works.
    # We need to ensure the template exists for the test to run
    template_path = Path("src/pyproject_init/templates/default")
    template_path.mkdir(parents=True, exist_ok=True)
    (template_path / "cookiecutter.json").write_text("""
    {
        "project_name": "test-project",
        "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-') }}",
        "author_name": "Test Author",
        "author_email": "test@example.com"
    }
    """)
    # Also create the {{cookiecutter.project_slug}} directory inside the dummy template
    (template_path / "{{cookiecutter.project_slug}}").mkdir(exist_ok=True)
    (template_path / "{{cookiecutter.project_slug}}" / "dummy.txt").write_text("This is a dummy file.")


    # Run the CLI command
    result = runner.invoke(
        cli,
        ["new", project_name, "--output-dir", str(output_dir), "--no-input"]
    )

    # Assertions
    assert result.exit_code == 0
    assert f"Project created successfully at: {output_dir / project_name}" in result.output

    # Verify the project directory exists
    generated_project_path = output_dir / project_name
    assert generated_project_path.is_dir()

    # Verify a file from the template exists within the generated project
    assert (generated_project_path / "dummy.txt").is_file()

    # Clean up the dummy template files created for the test
    # shutil.rmtree(template_path)
