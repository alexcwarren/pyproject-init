# Testing

`pyproject-init` uses layered verification because different classes of failure require different tests.

The repository provides three local automation entry points:

```text
scripts/verify.py
scripts/smoke_generated_project.py
scripts/smoke_package.py
```

These same workflows are used by GitHub Actions.

## Verification philosophy

There are three distinct things to prove:

```text
1. Does the generator source work?

2. Does a project freshly produced by the generator work?

3. Does the built pyproject-init wheel work independently of the source checkout?
```

Passing one layer does not prove the others.

For example:

- pytest can pass while the generated console script is broken;
- generator tests can pass while bundled template files are missing from the wheel;
- an editable source checkout can work while a runtime dependency is missing from package metadata.

## Routine verification

Run:

```console
uv run python scripts/verify.py
```

The script runs the repository's standard checks from the repository root.

It verifies:

```text
uv lock --check
Ruff lint
Ruff format --check
MyPy
pytest
pyproject-init --help
pyproject-init new --help
```

The exact checked source directories are defined once in the script so they can be updated without editing every command.

A successful run ends with:

```text
All verification checks passed.
```

The script exits with:

```text
0       success
nonzero failure
```

This makes it suitable for both local development and CI.

## Why lockfile verification comes first

The routine verifier starts with:

```console
uv lock --check
```

This confirms that the committed `uv.lock` matches project metadata without changing it.

A stale lockfile should fail verification rather than be silently repaired by CI.

## Ruff

Linting:

```console
uv run ruff check src tests scripts
```

Formatting verification:

```console
uv run ruff format src tests scripts --check
```

These are separate checks.

Passing Ruff lint does not imply that Ruff formatting passes.

Import sorting is already included in the configured Ruff lint rule set, so no separate isort command is necessary.

## MyPy

Run:

```console
uv run mypy src tests scripts
```

MyPy is configured against Python 3.12 because that is the generator's minimum supported Python version.

## pytest

Run:

```console
uv run pytest
```

Coverage can be inspected separately with:

```console
uv run pytest --cov=pyproject_init --cov-report=term-missing
```

## Generated-project smoke test

Run:

```console
uv run python scripts/smoke_generated_project.py
```

This creates a temporary fresh project from the default template.

The smoke project intentionally uses a hyphenated name:

```text
generated-smoke
```

with import package:

```text
generated_smoke
```

This exercises the distinction between project/distribution naming and Python package naming.

The script verifies the presence of expected top-level output such as:

```text
.gitignore
.python-version
LICENSE
README.md
pyproject.toml
src/
tests/
```

It then runs, inside the generated project:

```text
uv sync
generated console command
pytest
Ruff lint
Ruff format check
MyPy
uv build
```

Finally, it confirms that the generated project produced both:

```text
*.whl
*.tar.gz
```

A successful run ends with:

```text
Generated-project smoke test passed.
```

## Why `--no-active` appears in generated-project checks

The smoke test itself is launched from the generator's uv environment.

Without extra guidance, the nested generated-project commands can see the outer repository's active environment and emit warnings about a mismatched `VIRTUAL_ENV`.

The generated-project script uses:

```text
uv ... --no-active
```

where appropriate so the generated project's own environment is authoritative.

This keeps the smoke test isolated and avoids misleading environment warnings.

## Package smoke test

Run:

```console
uv run python scripts/smoke_package.py
```

This is the strongest package-level test.

It deliberately does not rely on the editable source installation.

The script:

1. removes any existing `dist/`;
2. builds fresh artifacts;
3. requires exactly one wheel and one source distribution;
4. creates a temporary clean virtual environment;
5. installs the built wheel into that environment;
6. runs the installed `pyproject-init` executable outside the source checkout;
7. generates a project using the template packaged inside the wheel;
8. verifies the generated project structure.

A successful run ends with:

```text
Package smoke test passed.
```

## Why the package smoke test matters

Editable development can hide packaging errors.

This smoke test can catch:

- missing runtime dependencies;
- missing bundled template files;
- broken console-script metadata;
- path assumptions that only work in the source checkout;
- broken wheel packaging.

During the v0.2.0 modernization, this test exposed that `jinja2-time` had been treated as a development dependency even though the packaged Cookiecutter template required it at runtime.

That failure would not have been reliably caught by ordinary source-level testing.

## Build artifacts

Build manually with:

```console
uv build
```

Expected output:

```text
dist/
    *.whl
    *.tar.gz
```

The package smoke test deletes `dist/` before building so stale artifacts cannot cause a false pass.

## Continuous integration

The workflow lives in:

```text
.github/workflows/ci.yml
```

It runs for pushes to:

```text
main
release/**
```

and pull requests targeting:

```text
main
release/**
```

The main job structure is:

```text
Quality
Python 3.12
Python 3.13
Python 3.14
Generated project
Package
CI
```

## Quality job

The `Quality` job runs once rather than once per Python version.

It:

1. installs uv;
2. installs Python 3.14;
3. synchronizes the locked environment;
4. runs:

```console
uv run python scripts/verify.py
```

Linting, formatting, MyPy, and CLI checks do not need to be redundantly repeated for every supported Python version.

## Compatibility matrix

Compatibility tests run pytest on:

```text
3.12
3.13
3.14
```

Each matrix entry uses the committed lockfile:

```console
uv run --locked --python <version> pytest
```

This verifies the Python versions advertised by the package.

## Generated-project CI job

The `Generated project` job runs:

```console
uv run python scripts/smoke_generated_project.py
```

This proves that the checked-in default template generates a usable project.

## Package CI job

The `Package` job runs:

```console
uv run python scripts/smoke_package.py
```

This proves that the built wheel, not merely the source checkout, can install and generate a project.

## Aggregate CI status

The workflow includes a final job named:

```text
CI
```

It depends on:

```text
Quality
compatibility matrix
Generated project
Package
```

If any dependency fails, the aggregate `CI` check fails.

Branch protection can therefore require one stable status name rather than depending directly on every implementation detail of the workflow.

## Action pinning

GitHub Actions are pinned to exact commit SHAs with comments identifying their release versions.

This improves reproducibility and avoids failures caused by unresolved or unexpectedly moved action tags.

When upgrading an action:

1. choose the intended released version;
2. resolve its trusted commit SHA;
3. update the workflow SHA;
4. update the adjacent version comment;
5. verify the PR workflow succeeds.

## When to run what

For a normal source change:

```console
uv run python scripts/verify.py
```

For a template change:

```console
uv run python scripts/verify.py
uv run python scripts/smoke_generated_project.py
```

For packaging or release preparation:

```console
uv run python scripts/verify.py
uv run python scripts/smoke_generated_project.py
uv run python scripts/smoke_package.py
```

CI runs the relevant layers automatically on protected integration paths.
