# pyproject-init

Create a Python project from the command line with a ready-to-use development setup.

`pyproject-init` uses Click and Cookiecutter to generate projects with a `src/` package layout, Hatch/Hatchling configuration, Ruff, MyPy, pytest, pytest-randomly, and GitHub Actions configuration. The bundled default template includes starter code and a basic test.

## Current migration state

Development toward v0.2.0 is in progress. The generator repository now uses **uv** for its development environment, dependencies, and commands, with a committed `uv.lock`. Its packaging backend is still **Hatchling**, and its version still comes from `src/pyproject_init/__about__.py`.

The generated default project still uses **Hatch** for development tasks and **Hatchling** for packaging. Moving the template and build backend to uv-based alternatives, modernizing Python requirements, and updating CI are separate migration steps; they are not complete at this checkpoint.

## Installation

The generator currently requires Python 3.10 or newer. Its Ruff and MyPy settings still target Python 3.10.

### Work from a source checkout

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these commands from the repository root:

```console
uv sync
uv run pyproject-init --help
```

Use `uv run pyproject-init ...` from this checkout for the examples below. You do not need to activate the environment manually.

### Install without the development workflow

To install the checked-out source into your chosen Python environment:

```console
python -m pip install .
```

That installation exposes `pyproject-init` directly. If a release is published on PyPI, it can instead be installed with `python -m pip install pyproject-init`; a GitHub release alone does not imply PyPI availability.

## Quick start

From the generator repository, create a project interactively:

```console
uv run pyproject-init new
```

Or supply a name and an absolute parent output directory:

```powershell
uv run pyproject-init new my-cool-app --output-dir "C:\Users\YourUser\Documents\NewProjects"
```

Follow the prompts for metadata and Python version. For development and testing of the generator, create projects outside its checkout.

The generated default project still needs Hatch. Install Hatch separately if necessary:

```console
python -m pip install hatch
```

Enter the generated project's directory and run its checks:

```powershell
cd "C:\Users\YourUser\Documents\NewProjects\my-cool-app"
hatch run all
```

Read the generated README for its starter application command and next steps. Run `uv run ...` in the generator checkout and `hatch run ...` in the generated project at this stage of the migration.

## Usage

For an installed CLI:

```text
pyproject-init new [OPTIONS] [PROJECT_NAME]
```

For the development checkout, prefix that command with `uv run`.

| Option | Purpose |
| --- | --- |
| `-o, --output-dir DIRECTORY` | Parent directory in which to create the project. Supply an absolute path. |
| `-t, --template TEXT` | Select a bundled template; `default` is the supported starting point. |
| `--no-input` | Skip prompts and use template defaults together with the supplied project name. |
| `--help` | Display command help. |

### Choose an output directory

Windows, from the generator checkout:

```powershell
uv run pyproject-init new my-cool-app --output-dir "C:\Users\YourUser\Documents\NewProjects"
```

macOS/Linux, from the generator checkout:

```console
uv run pyproject-init new my-cool-app --output-dir /absolute/path/to/projects
```

The project is created beneath that directory, for example `NewProjects/my-cool-app`.

### Use defaults without prompts

```console
uv run pyproject-init new my-cool-app --template default --no-input
```

Review generated author information, descriptions, and other metadata before publishing.

### Get help

```console
uv run pyproject-init --help
uv run pyproject-init new --help
```

## Project names

The folder and distribution name can contain hyphens; the Python package name must be a valid identifier:

```text
my-cool-app/
├── README.md
├── pyproject.toml
├── src/
│   └── my_cool_app/
│       ├── __about__.py
│       ├── __init__.py
│       └── main.py
└── tests/
    └── test_main.py
```

The template calls these values `project_name` (`my-cool-app`) and `project_slug` (`my_cool_app`). Keep the package name importable if you change it during the prompts.

## Current limitations

- Explicit `--output-dir` values need to be absolute paths; relative-path support remains follow-up work.
- Use a new destination. The CLI protects against creating a project at an existing destination.
- The bundled `default` template is the established workflow. Broader custom-template support and additional validation remain follow-up work.
- The generator's uv environment does not migrate generated projects. Their Hatch commands remain applicable until the template migration is implemented and tested.

## Contributing

See [README_DEV.md](README_DEV.md) for setup, checks, template maintenance, fresh-project acceptance tests, and the milestone/issue/branch/PR release workflow. v0.2.0 work integrates through the protected `release/v0.2.0` branch before its final PR into `main`.
