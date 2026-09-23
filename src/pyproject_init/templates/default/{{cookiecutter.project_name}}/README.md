# `{{ cookiecutter.project_name }}`

{{ cookiecutter.project_short_description }}

## Getting started

### Prerequisites

Install [uv](https://docs.astral.sh/uv/) using its standalone installer.

This project requires Python {{ cookiecutter.python_version }} or newer and pins its normal development interpreter in `.python-version`.

uv can install the required Python version automatically when needed.

### Set up the project

After cloning the repository:

```shell
git clone https://github.com/{{ cookiecutter.user_name }}/{{ cookiecutter.project_name }}.git
cd {{ cookiecutter.project_name }}
uv sync
```

`uv sync` creates the project virtual environment and installs the project plus its development dependencies.

Manual virtual-environment activation is not required.

## Running the project

Run the generated console command with:

```shell
uv run {{ cookiecutter.project_name }}
```

You can also run the module directly:

```shell
uv run python -m {{ cookiecutter.project_slug }}.main
```

The starter application prints:

```text
Hello, World!
```

## Development

### Run tests

```shell
uv run pytest
```

### Run tests with coverage

```shell
uv run pytest --cov={{ cookiecutter.project_slug }} --cov-report=term-missing
```

### Lint

```shell
uv run ruff check src tests
```

### Check formatting

```shell
uv run ruff format src tests --check
```

### Format code

```shell
uv run ruff format src tests
```

### Type check

```shell
uv run mypy src tests
```

## Run the routine checks

Until a project-specific aggregate verification command is added, run:

```shell
uv run ruff check src tests
uv run ruff format src tests --check
uv run mypy src tests
uv run pytest
```

## Dependency management

Add a runtime dependency:

```shell
uv add <package>
```

Add a development dependency:

```shell
uv add --dev <package>
```

Remove a dependency:

```shell
uv remove <package>
```

Keep `pyproject.toml` and `uv.lock` together in version control.

Do not commit `.venv`.

## Build the package

Build the source distribution and wheel with:

```shell
uv build
```

Artifacts are written to:

```text
dist/
```
