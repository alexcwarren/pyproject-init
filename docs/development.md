# Development

This guide covers the development environment, repository architecture, dependency model, package configuration, and template maintenance for `pyproject-init`.

For verification and CI, see [Testing](testing.md).

For the release process, see [Releasing](releasing.md).

## Toolchain

The generator repository uses:

- uv for Python installation, environment management, dependencies, locking, and command execution
- `uv_build` as the package build backend
- Click for the CLI
- Cookiecutter for project generation
- Ruff for linting and formatting
- MyPy for static type checking
- pytest for tests

The default generated project uses the same general uv-based Python workflow.

## Python policy

The generator supports:

```text
3.12
3.13
3.14
```

Normal repository development uses Python 3.14.

The repository records this in:

```text
.python-version
```

with:

```text
3.14
```

The package itself declares:

```toml
requires-python = ">=3.12"
```

Ruff and MyPy deliberately target the minimum supported version:

```toml
[tool.ruff]
target-version = "py312"

[tool.mypy]
python_version = "3.12"
```

This lets development use a current interpreter without accidentally introducing syntax that breaks Python 3.12.

## Initial setup

Install uv using its standalone installer.

Then, from the repository root:

```console
uv python install 3.14
uv python pin 3.14
uv sync
```

Verify:

```console
uv run python --version
```

Manual activation of `.venv` is not required.

## Windows and pyenv-win

This repository uses uv as its active Python-version manager.

`pyenv-win` may interfere because both tools recognize `.python-version`, and pyenv can intercept commands through its shim directory.

Check how uv resolves:

```powershell
where.exe uv
Get-Command uv -All
```

A standalone uv installation should resolve first, for example:

```text
C:\Users\<user>\.local\bin\uv.exe
```

If `pyenv-win` remains installed for older projects, its `bin` directory may remain useful for invoking `pyenv` deliberately.

Avoid allowing this directory to intercept project commands:

```text
C:\Users\<user>\.pyenv\pyenv-win\shims
```

Check both User and System PATH values if uv unexpectedly produces pyenv errors.

A global `python` command is not required. Prefer:

```console
uv run python ...
```

or:

```console
uv python ...
```

## Repository environment

Synchronize with:

```console
uv sync
```

The project environment is stored in:

```text
.venv/
```

`.venv` is disposable and is not committed.

If it becomes stale:

```powershell
Remove-Item -Recurse -Force .venv
uv sync
```

Unix-style equivalent:

```console
rm -rf .venv
uv sync
```

## Dependency model

Runtime dependencies are declared under:

```toml
[project]
dependencies = [
    ...
]
```

Development-only dependencies are declared under:

```toml
[dependency-groups]
dev = [
    ...
]
```

Current runtime dependencies include Click, Cookiecutter, and `jinja2-time`.

`jinja2-time` is a runtime dependency because the bundled template declares its Cookiecutter extension. An installed wheel therefore needs it during normal project generation.

This distinction matters: a development environment can accidentally hide missing runtime dependencies because `uv sync` installs the development dependency group too.

## Dependency management

Add a runtime dependency:

```console
uv add <package>
```

Add a development dependency:

```console
uv add --dev <package>
```

Remove a dependency:

```console
uv remove <package>
```

After intentional dependency changes:

```console
uv lock
uv sync
```

Verify that the lockfile is already current:

```console
uv lock --check
```

Synchronize without allowing lockfile changes:

```console
uv sync --locked
```

Do not hand-edit `uv.lock`.

Keep `pyproject.toml` and `uv.lock` together in version control.

## Package versioning

The generator version is stored directly in:

```toml
[project]
version = "..."
```

There is no separate `__about__.py` version source.

Do not change the package version simply because work is happening on a branch such as:

```text
release/v0.2.0
```

The release version is changed deliberately during release preparation.

## Building

Build the generator with:

```console
uv build
```

This produces a wheel and source distribution in:

```text
dist/
```

The configured backend is:

```toml
[build-system]
requires = ["uv_build>=0.12.17,<0.13"]
build-backend = "uv_build"
```

The default generated project uses `uv_build` as well.

For artifact verification, see [Testing](testing.md).

## Generator architecture

The CLI implementation lives in:

```text
src/pyproject_init/pyproject_init.py
```

At a high level:

```text
CLI arguments
    ↓
Click
    ↓
template selection and destination validation
    ↓
Cookiecutter
    ↓
bundled template
    ↓
generated Python project
```

Bundled templates live beneath:

```text
src/pyproject_init/templates/
```

The established template is:

```text
default
```

## Template values

The default template uses three especially important values:

| Value | Example | Purpose |
| --- | --- | --- |
| `project_name` | `my-cool-app` | Directory, distribution, repository, and console command |
| `project_slug` | `my_cool_app` | Importable Python package |
| `python_version` | `3.12` | Minimum Python version and development interpreter pin |

A hyphenated project should therefore result in a split such as:

```text
project_name: my-cool-app
project_slug: my_cool_app
```

Do not use the import slug as a substitute for the distribution/repository name.

## Default generated project

The template currently emits:

```text
.gitignore
.python-version
LICENSE
README.md
pyproject.toml
src/
tests/
```

The generated project uses:

- uv
- `uv_build`
- static `[project].version`
- a `src/` package layout
- pytest
- pytest-cov
- pytest-randomly
- Ruff
- MyPy

The selected Python version is written to `.python-version`.

## Generated dependency configuration

Generated development dependencies are declared under:

```toml
[dependency-groups]
dev = [
    "mypy",
    "pytest",
    "pytest-cov",
    "pytest-randomly",
    "ruff",
]
```

A generated project's own `uv.lock` is created when the user runs:

```console
uv sync
```

The template does not ship a pre-generated lockfile.

## Generated console entry point

The template defines:

```toml
[project.scripts]
{{ cookiecutter.project_name }} = "{{ cookiecutter.project_slug }}.main:main"
```

The generated `main.py` must therefore define `main()`.

Tests that only exercise `hello_world()` do not prove that the console entry point works. The generated-project smoke test validates it explicitly.

## Template maintenance

When changing the default template:

1. modify the template source rather than a generated test project;
2. update related paths and configuration together;
3. run routine generator verification;
4. generate a completely fresh project;
5. run the generated-project smoke test;
6. fix the template;
7. regenerate and retest.

The automated acceptance command is:

```console
uv run python scripts/smoke_generated_project.py
```

Do not manually repair generated output and treat that as proof that the template is correct.

## Generated repository defaults

The default template intentionally remains relatively small.

It currently includes common repository basics such as:

- `.gitignore`
- `.python-version`
- MIT `LICENSE`
- README
- package metadata
- tests

More opinionated open-source governance files such as `SECURITY.md`, contribution guides, issue templates, and pull-request templates may be added to `pyproject-init` itself or considered for future templates separately.

They are not automatically generated merely because they are useful in this repository.

## Formatting

Check formatting:

```console
uv run ruff format src tests scripts --check
```

Apply formatting:

```console
uv run ruff format src tests scripts
```

## Linting

Run:

```console
uv run ruff check src tests scripts
```

Ruff's configured rule set includes import sorting, so a separate isort invocation is unnecessary.

## Type checking

Run:

```console
uv run mypy src tests scripts
```

## Tests

Run:

```console
uv run pytest
```

For the complete routine verification sequence, use:

```console
uv run python scripts/verify.py
```

See [Testing](testing.md) for details.

## PowerShell equivalents

Some historical/manual procedures may still use PowerShell filesystem commands.

Useful equivalents:

```text
PowerShell                          Unix-style equivalent
----------                          ---------------------
Get-ChildItem                      ls
Remove-Item                        rm
Remove-Item -Recurse -Force        rm -rf
New-Item -ItemType Directory       mkdir
Select-String                      grep
Push-Location                      pushd
Pop-Location                       popd
Join-Path                          path construction
& <path>                           execute file at path
`                                   shell line continuation
```

Reusable project automation should generally remain cross-platform Python rather than PowerShell-specific.
