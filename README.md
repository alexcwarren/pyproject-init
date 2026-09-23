# pyproject-init

Create a ready-to-develop Python project from the command line.

`pyproject-init` uses Click and Cookiecutter to generate a modern `src/`-layout Python project with:

- [uv](https://docs.astral.sh/uv/) for Python, environments, dependencies, and commands
- `uv_build` for packaging
- pytest and pytest-cov
- Ruff
- MyPy
- a `.python-version`
- a practical `.gitignore`
- an MIT `LICENSE`
- a starter CLI application and test

## Requirements

`pyproject-init` supports CPython 3.12, 3.13, and 3.14.

The repository normally develops on Python 3.14.

Install uv using the official standalone installer before working from a source checkout.

## Development checkout

Clone the repository and synchronize its environment:

```console
git clone https://github.com/alexcwarren/pyproject-init.git
cd pyproject-init
uv sync
```

Verify the CLI:

```console
uv run pyproject-init --help
```

Manual virtual-environment activation is not required.

## Quick start

Create a project interactively:

```console
uv run pyproject-init new
```

Or provide a project name:

```console
uv run pyproject-init new my-cool-app
```

Choose an output directory:

```console
uv run pyproject-init new my-cool-app --output-dir /absolute/path/to/projects
```

PowerShell example:

```powershell
uv run pyproject-init new my-cool-app `
    --output-dir "C:\Users\YourUser\Documents\Projects"
```

Use the default template without prompts:

```console
uv run pyproject-init new my-cool-app --template default --no-input
```

Review generated metadata before publishing a project created with `--no-input`.

## Generated projects

A default generated project looks roughly like this:

```text
my-cool-app/
├── .gitignore
├── .python-version
├── LICENSE
├── README.md
├── pyproject.toml
├── src/
│   └── my_cool_app/
│       ├── __init__.py
│       └── main.py
└── tests/
    └── test_main.py
```

The template distinguishes between:

```text
project_name: my-cool-app
project_slug: my_cool_app
```

`project_name` is used for the distribution, repository, directory, and console command.

`project_slug` is used for the importable Python package.

The default template currently lets you choose Python 3.12, 3.13, or 3.14. The selected version is written to `.python-version` and becomes the project's minimum Python version.

## Working in a generated project

Enter the generated project and synchronize it:

```console
cd my-cool-app
uv sync
```

Run its starter command:

```console
uv run my-cool-app
```

Expected output:

```text
Hello, World!
```

Run tests:

```console
uv run pytest
```

Run linting:

```console
uv run ruff check src tests
```

Check formatting:

```console
uv run ruff format src tests --check
```

Format the code:

```console
uv run ruff format src tests
```

Run type checking:

```console
uv run mypy src tests
```

Build the package:

```console
uv build
```

The generated project's own README contains its working commands and dependency-management instructions.

## CLI usage

```text
pyproject-init new [OPTIONS] [PROJECT_NAME]
```

When running from this repository's development checkout, prefix the command with `uv run`.

| Option | Purpose |
| --- | --- |
| `-o, --output-dir DIRECTORY` | Parent directory in which to create the project |
| `-t, --template TEXT` | Bundled template to use; `default` is the established template |
| `--no-input` | Skip prompts and use defaults plus any supplied project name |
| `--help` | Display command help |

Get detailed help with:

```console
uv run pyproject-init --help
uv run pyproject-init new --help
```

## Development

Routine repository verification is automated:

```console
uv run python scripts/verify.py
```

Additional smoke tests validate generated projects and built release artifacts:

```console
uv run python scripts/smoke_generated_project.py
uv run python scripts/smoke_package.py
```

See [README_DEV.md](README_DEV.md) for the developer quick-reference.

Detailed documentation:

- [Development guide](docs/development.md)
- [Testing guide](docs/testing.md)
- [Release guide](docs/releasing.md)

## Continuous integration

GitHub Actions validates:

- routine quality checks
- Python 3.12 compatibility
- Python 3.13 compatibility
- Python 3.14 compatibility
- a freshly generated project
- the built `pyproject-init` wheel and bundled template

The workflow exposes a final aggregate `CI` status check for branch protection.

## Current limitations

- The bundled `default` template is the primary supported generation path.
- Custom-template support is not yet a fully established workflow.
- Existing destination directories are rejected rather than overwritten.
- Generated projects intentionally provide a small, conventional starting point rather than a complete open-source governance setup.

## License

`pyproject-init` is licensed under the MIT License.
