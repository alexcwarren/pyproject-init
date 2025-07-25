import click
from cookiecutter.main import cookiecutter
import os
from pathlib import Path
import shutil

# Get the path to the internal templates directory
# This assumes your templates will live in src/pyproject_init/templates/
TEMPLATES_DIR = Path(__file__).parent / "templates"

@click.group()
def cli():
    """A CLI tool to automate Python project creation."""
    pass

@cli.command()
@click.argument('project_name', required=False)
@click.option(
    '--output-dir',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    default=Path.cwd(),
    help="Directory where the new project will be created.",
)
@click.option(
    '--template',
    default='default', # We'll start with a 'default' template
    help="The name of the internal template to use (e.g., 'default').",
)
@click.option(
    '--no-input',
    is_flag=True,
    help="Do not prompt for parameters and only use cookiecutter.json file defaults.",
)
def new(project_name: str | None, output_dir: Path, template: str, no_input: bool) -> None:
    """
    Create a new Python project from a template.
    If PROJECT_NAME is not provided, you will be prompted.
    """
    template_path = TEMPLATES_DIR / template

    if not template_path.is_dir():
        click.echo(f"Error: Template '{template}' not found at {template_path}", err=True)
        return

    click.echo(f"Creating new project using template '{template}'...")
    click.echo(f"Output directory: {output_dir}")

    try:
        # Cookiecutter expects a string path for template and output_dir
        cookiecutter_args = {
            "template": str(template_path),
            "output_dir": str(output_dir),
            "no_input": no_input,
        }

        if project_name:
            # If project_name is provided as an argument, pass it to cookiecutter
            # This will override the default from cookiecutter.json
            cookiecutter_args["extra_context"] = {"project_name": project_name}

        # Run cookiecutter
        generated_path = cookiecutter(**cookiecutter_args)

        click.echo(f"\nProject created successfully at: {generated_path}")
        click.echo("Navigate into your new project and follow its README for next steps.")
    except Exception as e:
        click.echo(f"An error occurred during project creation: {e}", err=True)
        click.echo("Please ensure you have valid template variables or try running without --no-input.")
        # You might want to remove the partially created directory if an error occurs
        # Be cautious with this, as it could delete unexpected files if output_dir is wrong
        # if generated_path and Path(generated_path).exists():
        #     click.echo(f"Attempting to clean up partially created project at {generated_path}")
        #     shutil.rmtree(generated_path)
        #     click.echo("Cleanup complete.")
