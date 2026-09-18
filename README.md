# pyproject-init

Create a Python project from the command line with a ready-to-use development setup.

`pyproject-init` uses Click and Cookiecutter to generate projects with a `src/` package layout, Hatch/Hatchling configuration, Ruff, MyPy, pytest, pytest-randomly, and GitHub Actions configuration. The bundled default template includes starter code and a basic test so you can run the project's checks immediately.

## Installation

Requires Python 3.10 or newer. The project's CI covers Python 3.10, 3.11, and 3.12.

Once the package is published on PyPI:

```console
python -m pip install pyproject-init
```

For a source checkout, install from the repository root:

```console
python -m pip install .
```

Install Hatch to run the generated project's development commands:

```console
python -m pip install hatch
```

## Quick start

Create a project interactively in the current directory:

```console
pyproject-init new
```

Or supply a project name:

```console
pyproject-init new my-cool-app
```

Follow the prompts for project metadata and the Python version. After generation, enter the directory reported by the command:

```console
cd my-cool-app
hatch run all
```

This runs the generated project's linting, type checking, and tests. Read its generated README for the application command and next steps.

## Usage

```text
pyproject-init new [OPTIONS] [PROJECT_NAME]
```

| Option | Purpose |
| --- | --- |
| `-o, --output-dir DIRECTORY` | Parent directory in which to create the project. Use an absolute path when supplying this option. |
| `-t, --template TEXT` | Select a bundled template; `default` is the supported starting point. |
| `--no-input` | Skip prompts and use template defaults, together with the supplied project name. |
| `--help` | Display command help. |

### Choose an output directory

Windows:

```powershell
pyproject-init new my-cool-app --output-dir "C:\Users\YourUser\Documents\NewProjects"
```

macOS/Linux:

```console
pyproject-init new my-cool-app --output-dir /absolute/path/to/projects
```

The project is created beneath the output directory, for example `NewProjects/my-cool-app`.

### Use defaults without prompts

```console
pyproject-init new my-cool-app --template default --no-input
```

Review the generated author information, description, and other metadata before publishing your project.

### Get help

```console
pyproject-init --help
pyproject-init new --help
```

## Project names

The project folder and distribution name can contain hyphens, while Python package names must be valid identifiers. For example:

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

- Explicit `--output-dir` values currently need to be absolute paths; relative-path support is planned.
- Use a new destination. The CLI includes protection against creating a project at an existing destination.
- The bundled `default` template is the established workflow. Broader custom-template support and additional template validation remain follow-up work.

## Contributing

For setup, architecture, template maintenance, checks, troubleshooting, and release preparation, see [README_DEV.md](README_DEV.md).
