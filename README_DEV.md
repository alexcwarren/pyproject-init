# pyproject-init developer guide

This file is the quick re-entry point for repository development.

For deeper reference, use:

- [Development](docs/development.md)
- [Testing](docs/testing.md)
- [Releasing](docs/releasing.md)

## Current architecture

`pyproject-init` is a Click CLI that uses Cookiecutter to render bundled project templates.

The generator and its default generated project both use:

- uv
- `uv_build`
- static `[project].version`
- Ruff
- MyPy
- pytest

The generator supports CPython 3.12–3.14 and normally develops on Python 3.14.

## Repository map

```text
.python-version
pyproject.toml
uv.lock

src/pyproject_init/
    pyproject_init.py
    templates/
        default/
            cookiecutter.json
            {{cookiecutter.project_name}}/
                .gitignore
                .python-version
                LICENSE
                README.md
                pyproject.toml
                src/
                tests/

scripts/
    clean.py
    verify.py
    smoke_generated_project.py
    smoke_package.py

tests/
    test_clean.py
    test_pyproject_init.py

docs/
    development.md
    testing.md
    releasing.md

.github/workflows/
    ci.yml
```

## Start here after a break

Before changing branches:

```console
git status
git branch -vv
git log --oneline --decorate -10
```

Synchronize the repository:

```console
uv sync
```

Confirm the interpreter:

```console
uv run python --version
```

Verify the CLI:

```console
uv run pyproject-init --help
uv run pyproject-init new --help
```

## Routine verification

Run:

```console
uv run python scripts/verify.py
```

This checks:

- the committed lockfile
- Ruff linting
- Ruff formatting
- MyPy
- pytest
- both CLI help entry points

For template changes:

```console
uv run python scripts/smoke_generated_project.py
```

For packaging/release changes:

```console
uv run python scripts/smoke_package.py
```

See [docs/testing.md](docs/testing.md) for what each script proves.

## Common development operations

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

Build the package:

```console
uv build
```

Format source:

```console
uv run ruff format src tests scripts
```

See [docs/development.md](docs/development.md) for the complete environment, architecture, dependency, template, and troubleshooting guide.

## Branch workflow

For coordinated releases, development flows through a temporary release branch:

```text
main
└── release/vX.Y.Z
    ├── feature/<issue>-...
    ├── fix/<issue>-...
    ├── chore/<issue>-...
    └── docs/<issue>-...
```

Feature PRs target the active release branch.

The final release PR targets `main`.

Protected release and main branches require the aggregate `CI` status check.

See [docs/releasing.md](docs/releasing.md) for the complete milestone-to-release procedure.

## Documentation ownership

Keep documentation responsibilities separated:

| File | Purpose |
| --- | --- |
| `README.md` | User-facing overview and basic usage |
| `README_DEV.md` | Fast developer re-entry |
| `docs/development.md` | Development architecture and workflows |
| `docs/testing.md` | Verification, smoke testing, and CI |
| `docs/releasing.md` | Release procedure |

Avoid duplicating detailed procedures across multiple files. Prefer one authoritative location and link to it elsewhere.
