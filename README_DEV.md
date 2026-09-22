# pyproject-init: development and release guide

`pyproject-init` renders a bundled Cookiecutter template into a new Python project.

Development work needs to preserve two separate but related things:

1. the generator itself must install, test, build, and run correctly; and
2. a fresh project produced by the bundled template must work without manual repair.

Both must be verified.

## Current v0.2.0 checkpoint

| Concern | Current state |
| --- | --- |
| Generator environment | uv-managed `.venv` |
| Generator Python | Python 3.14 for development; Python 3.12 minimum supported |
| Generator dependencies | `[project].dependencies`, `[dependency-groups].dev`, committed `uv.lock` |
| Generator build backend | `uv_build` |
| Generator version | Static `[project].version` |
| Generator commands | `uv run ...` |
| Generated project environment | uv-managed `.venv` |
| Generated project Python | User-selected 3.12, 3.13, or 3.14, pinned in `.python-version` |
| Generated project build backend | `uv_build` |
| Generated project version | Static `[project].version` |
| Generated project tooling | pytest, pytest-cov, pytest-randomly, Ruff, MyPy |
| Release integration | Feature PRs into `release/v0.2.0`, followed by final PR into `main` |
| CI modernization | Still pending separate v0.2.0 work |
| Local verification automation | Still pending separate v0.2.0 work |

The generator and the default generated project now both use uv-based workflows.

Hatch and Hatchling are no longer part of the normal generator or default-template toolchain.

Remaining v0.2.0 work includes generated repository metadata improvements, stronger template acceptance tests, CI modernization, local verification automation, and final documentation cleanup.

## Start here after a break

Before switching branches or pulling:

```console
git status
git branch -vv
git log --oneline --decorate -10
```

Verify the local toolchain:

```console
uv --version
uv sync
uv run python --version
uv run pyproject-init --help
uv run pyproject-init new --help
```

Run generator commands from the repository root.

`uv sync` creates or updates `.venv` and installs the generator plus its development dependencies.

Manual virtual-environment activation is unnecessary.

Keep these files in version control:

```text
.python-version
pyproject.toml
uv.lock
```

Do not commit:

```text
.venv/
dist/
coverage output
tool caches
temporary smoke-test projects
```

## Python setup

The generator:

- supports Python 3.12 and newer;
- normally develops on Python 3.14;
- pins its development interpreter in `.python-version`;
- configures Ruff and MyPy against the minimum supported version.

Install uv using its standalone installer.

Then:

```console
uv python install 3.14
uv python pin 3.14
uv sync
```

Verify:

```console
uv run python --version
```

The expected major/minor version is Python 3.14.

### Changing Python versions

Use uv:

```console
uv python install <version>
uv python pin <version>
uv sync
```

`uv python pin` updates `.python-version`.

If the interpreter changes, uv may recreate `.venv`. The virtual environment is disposable local state.

### Windows and pyenv-win

Avoid using both uv and `pyenv-win` as active Python-version managers for the same repository.

Both recognize `.python-version`, and `pyenv-win` can intercept commands through its shim directory.

Check what PowerShell resolves:

```powershell
where.exe uv
Get-Command uv -All
```

The preferred first result is a standalone uv installation such as:

```text
C:\Users\<user>\.local\bin\uv.exe
```

If `pyenv-win` remains installed for older repositories, its `bin` directory may remain available so the `pyenv` command can still be invoked deliberately.

Its shim directory should not intercept this project:

```text
C:\Users\<user>\.pyenv\pyenv-win\shims
```

If pyenv unexpectedly handles uv or Python commands, inspect both User and System PATH values.

## Dependency model

Runtime dependencies belong in:

```toml
[project]
dependencies = [
  ...
]
```

Development-only dependencies belong in:

```toml
[dependency-groups]
dev = [
  ...
]
```

A dependency is runtime if an installed user needs it for normal application behavior.

For example, the bundled Cookiecutter template declares:

```json
"_extensions": ["jinja2_time.TimeExtension"]
```

Therefore `jinja2-time` is a runtime dependency of `pyproject-init`.

This distinction matters because:

```text
uv sync
```

installs development dependencies, while a user installing a built wheel receives only declared runtime dependencies.

Use uv to manage dependencies:

```console
uv add <package>
uv add --dev <package>
uv remove <package>
```

After dependency changes:

```console
uv lock
uv sync
```

Verify the committed lockfile without modifying it:

```console
uv lock --check
```

Use:

```console
uv sync --locked
```

when synchronization should fail instead of changing a stale lockfile.

Do not hand-edit `uv.lock`.

## Repository architecture

```text
.python-version
pyproject.toml
uv.lock

src/pyproject_init/
    __init__.py
    pyproject_init.py
    templates/
        default/
            cookiecutter.json
            {{cookiecutter.project_name}}/
                .gitignore
                .python-version
                README.md
                pyproject.toml
                src/
                    {{cookiecutter.project_slug}}/
                        __init__.py
                        main.py
                tests/
                    test_main.py

scripts/
    clean.py

tests/
    test_clean.py
    test_pyproject_init.py

.github/workflows/
    ci.yml
```

Click handles CLI commands and options.

Cookiecutter renders projects from bundled templates.

uv manages Python versions, virtual environments, dependencies, locking, command execution, and build invocation.

`uv_build` builds both the generator and the default generated project.

The generator version comes from:

```toml
[project]
version = "..."
```

The default generated project also uses static `[project].version`.

## Python compatibility policy

The generator declares:

```toml
requires-python = ">=3.12"
```

Normal development uses:

```text
.python-version → 3.14
```

Tooling targets the minimum supported version:

```toml
[tool.ruff]
target-version = "py312"

[tool.mypy]
python_version = "3.12"
```

This lets development use a recent interpreter while avoiding accidental syntax incompatible with Python 3.12.

The generator currently advertises CPython 3.12, 3.13, and 3.14 support.

Do not advertise alternate implementations unless they are intentionally supported and tested.

## Generator checks

From the repository root:

```console
uv sync
uv lock --check
uv run ruff check src tests scripts
uv run ruff format src tests scripts --check
uv run mypy src tests scripts
uv run pytest
uv run pytest --cov=pyproject_init --cov-report=term-missing
uv run pyproject-init --help
uv run pyproject-init new --help
```

For formatting changes:

```console
uv run ruff format src tests scripts
```

Review the diff afterward.

There is currently no single aggregate verification command.

A later v0.2.0 tooling/CI issue should provide one routine local entry point and make CI execute the same logical checks.

## Building the generator

Build both source and wheel distributions with:

```console
uv build
```

Artifacts are written to:

```text
dist/
```

and should include:

```text
*.tar.gz
*.whl
```

The generator uses `uv_build`.

Its version comes from:

```toml
[project]
version = "..."
```

Do not bump the package to the planned release version merely because development is occurring on `release/v0.2.0`.

Change the version deliberately during release preparation.

## Why editable testing is not enough

Running:

```console
uv sync
uv run pyproject-init ...
```

tests an editable installation backed by the source checkout.

That does not prove that a release wheel contains:

- all required runtime dependencies;
- bundled templates;
- working entry-point metadata;
- all package data.

Release-quality verification must therefore test the built artifact itself.

## Inspect built artifacts

### Wheel

On Windows:

```powershell
uv run python -m zipfile -l `
    .\dist\pyproject_init-0.1.0-py3-none-any.whl
```

Confirm that the bundled template exists, including files such as:

```text
pyproject_init/templates/default/cookiecutter.json
pyproject_init/templates/default/{{cookiecutter.project_name}}/.gitignore
pyproject_init/templates/default/{{cookiecutter.project_name}}/.python-version
pyproject_init/templates/default/{{cookiecutter.project_name}}/README.md
pyproject_init/templates/default/{{cookiecutter.project_name}}/pyproject.toml
pyproject_init/templates/default/{{cookiecutter.project_name}}/src/...
pyproject_init/templates/default/{{cookiecutter.project_name}}/tests/...
```

### Source distribution

Inspect the sdist:

```powershell
tar -tf .\dist\pyproject_init-0.1.0.tar.gz
```

Confirm corresponding files beneath:

```text
src/pyproject_init/templates/
```

Use the actual artifact filename when the project version changes.

## Clean-wheel smoke test

This verifies what a user actually receives.

The workflow:

1. creates a clean temporary environment;
2. installs the built wheel rather than the source checkout;
3. leaves the repository directory;
4. invokes the installed CLI;
5. renders a project from the packaged template.

This can catch:

- missing package data;
- missing runtime dependencies;
- broken console entry points;
- template lookup that only works from the source checkout;
- packaging configuration errors.

### PowerShell procedure

Create a disposable directory:

```powershell
$testDir = Join-Path $env:TEMP "pyproject-init-wheel-test"

Remove-Item `
    -Recurse `
    -Force `
    $testDir `
    -ErrorAction SilentlyContinue

New-Item `
    -ItemType Directory `
    -Path $testDir |
    Out-Null
```

Create a clean environment:

```powershell
uv venv "$testDir\.venv" --python 3.14
```

Install the wheel:

```powershell
uv pip install `
    --python "$testDir\.venv\Scripts\python.exe" `
    ".\dist\pyproject_init-0.1.0-py3-none-any.whl"
```

Move outside the repository:

```powershell
Push-Location $testDir
```

Verify the installed CLI:

```powershell
& ".\.venv\Scripts\pyproject-init.exe" --help
```

Generate a project:

```powershell
& ".\.venv\Scripts\pyproject-init.exe" `
    new wheel-smoke `
    --output-dir $testDir `
    --template default `
    --no-input
```

Inspect the result:

```powershell
Get-ChildItem "$testDir\wheel-smoke" -Force
```

Return:

```powershell
Pop-Location
```

A later tooling issue should automate this workflow in a cross-platform Python script.

## PowerShell command equivalents

Some development examples use PowerShell-specific commands.

Useful comparisons:

```text
PowerShell                             Unix-style equivalent
-----------                            ---------------------
Get-ChildItem                         ls
Remove-Item                           rm
Remove-Item -Recurse -Force           rm -rf
New-Item -ItemType Directory          mkdir
Select-String                         grep
Push-Location                         pushd
Pop-Location                          popd
Join-Path                             build/join filesystem path
& <path>                              execute file at path
`                                      shell line continuation
```

Prefer project automation in Python when practical so workflows remain cross-platform.

## Default generated project

The default template now produces a uv-native Python project.

Generated projects contain:

```text
.gitignore
.python-version
README.md
pyproject.toml
src/
tests/
```

They do not require Hatch or pyenv.

### Python selection

Cookiecutter currently offers:

```text
3.12
3.13
3.14
```

The selected version is written to:

```text
.python-version
```

and used for:

```toml
requires-python = ">={{ cookiecutter.python_version }}"
```

Ruff and MyPy target the selected minimum version.

### Generated dependencies

Development dependencies are declared in:

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

Generated projects receive their own `uv.lock` after running:

```console
uv sync
```

### Generated console application

The template defines:

```toml
[project.scripts]
{{ cookiecutter.project_name }} = "{{ cookiecutter.project_slug }}.main:main"
```

The generated `main.py` defines both:

```python
hello_world()
main()
```

The console entry point must be tested directly because pytest alone does not prove entry-point metadata is correct.

## Generated-project acceptance test

Changes affecting the template must be tested by generating a completely fresh project.

Do not repair an already-generated project and treat that as proof the template works.

### Create a fresh project

From the generator repository:

```powershell
$testRoot = Join-Path $env:TEMP "pyproject-init-template-test"

Remove-Item `
    -Recurse `
    -Force `
    $testRoot `
    -ErrorAction SilentlyContinue

New-Item `
    -ItemType Directory `
    -Path $testRoot |
    Out-Null

uv run pyproject-init new `
    uv-template-smoke `
    --output-dir $testRoot `
    --template default `
    --no-input
```

Inspect generated files:

```powershell
Get-ChildItem "$testRoot\uv-template-smoke" -Force
```

Expected top-level files include:

```text
.gitignore
.python-version
README.md
pyproject.toml
src/
tests/
```

### Verify the generated project

Enter it:

```powershell
Push-Location "$testRoot\uv-template-smoke"
```

Then run:

```console
uv sync
uv run python --version
uv run uv-template-smoke
uv run pytest
uv run ruff check src tests
uv run ruff format src tests --check
uv run mypy src tests
uv build
```

Expected console output includes:

```text
Hello, World!
```

Return to the generator repository:

```powershell
Pop-Location
```

All generated-project checks should pass before template changes are accepted.

## Why the acceptance test checks multiple things

Different commands catch different failures.

For example:

```text
pytest
```

can pass even when the generated console entry point is broken.

Similarly:

```text
ruff check
```

can pass while:

```text
ruff format --check
```

fails.

The acceptance workflow therefore checks:

- environment creation;
- Python selection;
- installed console command;
- tests;
- linting;
- formatting;
- typing;
- package build.

Do not treat one successful check as evidence that all generated-project behavior works.

## Template maintenance

The key template values are:

| Value | Example | Used for |
| --- | --- | --- |
| `project_name` | `test-project` | Folder name, distribution name, console command, repository metadata |
| `project_slug` | `test_project` | Python package/import name |
| `python_version` | `3.12` | Minimum Python, `.python-version`, Ruff target, MyPy target |

When changing the template:

1. modify the template source;
2. update related paths and configuration together;
3. generate a fresh project outside the checkout;
4. run the full generated-project acceptance workflow;
5. fix the template itself;
6. regenerate and retest.

Do not rely on manually repairing generated output.

## Generated `.gitignore`

The default template excludes common disposable files including:

```text
__pycache__/
*.py[cod]
.venv/
.pytest_cache/
.coverage
coverage.xml
htmlcov/
.mypy_cache/
.ruff_cache/
build/
dist/
*.egg-info/
.vscode/
.idea/
.DS_Store
Thumbs.db
```

Keep generated repository defaults conservative and conventional.

Broader repository metadata belongs in the dedicated template/repository-files work.

## Troubleshooting

### Plain `python` is unavailable on Windows

A global Python command is not required.

Use:

```console
uv run python ...
```

or:

```console
uv python ...
```

### uv invokes pyenv unexpectedly

Inspect:

```powershell
where.exe uv
Get-Command uv -All
```

Check both User and System PATH values for:

```text
.pyenv\pyenv-win\shims
```

### Wrong Python version

Generator:

```powershell
Get-Content .python-version
uv python find 3.14
uv run python --version
```

Generated project:

```powershell
Get-Content .python-version
uv run python --version
```

### Stale `.venv`

Remove and recreate it:

```powershell
Remove-Item -Recurse -Force .venv
uv sync
```

### Generator works but built wheel fails

Inspect:

- runtime dependencies;
- wheel contents;
- template package data;
- entry-point metadata.

Then rerun the clean-wheel smoke test.

### Generated tests pass but the command fails

Run the generated console command directly:

```console
uv run <project-name>
```

Check:

```toml
[project.scripts]
```

against the actual function defined in the target module.

### Ruff lint passes but formatting fails

These are different checks:

```console
uv run ruff check src tests
uv run ruff format src tests --check
```

Fix formatting with:

```console
uv run ruff format src tests
```

## Release workflow

Use a temporary release integration branch for coordinated releases.

```text
main
└── release/v0.2.0
    ├── feature/<issue>-...
    ├── fix/<issue>-...
    └── docs/<issue>-...

feature/fix/docs PR → release/v0.2.0
final release PR    → main
validated main      → version tag → GitHub release
```

A permanent development branch is unnecessary.

### 1. Plan the milestone

Create the milestone first.

For this release:

```text
v0.2.0
```

Assign intended issues to it.

Keep unrelated work outside release scope.

Each issue should identify:

- intended behavior;
- affected areas;
- acceptance criteria;
- meaningful dependencies.

### 2. Create the release branch

From reviewed `main`:

```console
git switch main
git pull --ff-only
git status

git switch -c release/v0.2.0
git push -u origin release/v0.2.0
```

Do not recreate an existing release branch.

### 3. Protect release branches

`release/*` branches are integration branches.

Require:

- pull requests;
- resolved review conversations;
- blocked force pushes.

Do not commit ordinary implementation changes directly to release branches.

Release branches remain deletable because they are temporary.

Required CI checks should be enabled only after the modernized CI workflow actually runs for release-targeted PRs.

### 4. Create issue branches

Prefer GitHub's Issue **Create a branch** action.

During this release, the source must be:

```text
release/v0.2.0
```

Use:

```text
feature/<issue-number>-<description>
fix/<issue-number>-<description>
chore/<issue-number>-<description>
docs/<issue-number>-<description>
```

Release branches use:

```text
release/v<semver>
```

### 5. Implement and verify

Keep each branch focused.

Before committing:

```console
git status
git diff
```

For generator changes:

```console
uv lock --check
uv run ruff check src tests scripts
uv run ruff format src tests scripts --check
uv run mypy src tests scripts
uv run pytest
uv run pyproject-init --help
uv run pyproject-init new --help
```

For packaging changes:

```console
uv build
```

For template changes, run the full generated-project acceptance test.

A future tooling issue should replace repetitive command sequences with reusable local verification commands.

CI should execute the same logical checks.

### 6. Commit intentionally

Stage only intended files:

```console
git add <files>
git diff --cached
git status
git commit -m "<concise completed change>"
```

Push:

```console
git push -u origin <branch-name>
```

### 7. Open the PR into the release branch

Use:

```text
base: release/v0.2.0
```

not `main`.

Document:

- what changed;
- what intentionally did not change;
- checks performed;
- generated-project acceptance results where relevant;
- associated issue.

Merge through the PR.

### 8. Update the local release branch

After merge:

```console
git switch release/v0.2.0
git pull --ff-only
git branch -d <merged-feature-branch>
```

Start the next issue branch from the updated release branch.

### 9. Regression-test the integrated release

Before the final release PR:

1. run generator verification;
2. run coverage;
3. generate fresh projects;
4. test generated console commands;
5. test duplicate-destination handling;
6. test generated lint, format, typing, tests, and builds;
7. verify Python compatibility;
8. verify CI triggers and required checks;
9. review milestone completion;
10. review documentation;
11. build release artifacts;
12. run clean-wheel verification.

Fix regressions through dedicated branches rather than directly on the release branch.

### 10. Prepare the release version

The generator version is stored in:

```toml
[project]
version = "..."
```

Update it deliberately during release preparation.

Do not use the release branch name as the version source.

### 11. Build release artifacts

Run:

```console
uv build
```

Inspect:

```text
dist/*.whl
dist/*.tar.gz
```

Verify bundled templates exist in both distributions.

Install the exact wheel into a clean environment and generate a project from it.

Do not rely on editable installation alone.

### 12. Open the final release PR

Open:

```text
release/v0.2.0 → main
```

Summarize:

- completed milestone work;
- regression results;
- Python support;
- CI results;
- packaging verification;
- known limitations;
- deferred work.

### 13. Tag the validated release

After merge:

```console
git switch main
git pull --ff-only
git status
git log -1 --oneline
git tag --list v0.2.0
```

Confirm HEAD is the intended release commit and the tag does not already exist.

Then:

```console
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

If `main` has advanced beyond the reviewed release commit, tag the verified commit explicitly.

Do not replace an existing release tag.

### 14. Publish the GitHub Release

Create the GitHub Release from the validated tag.

Include:

- user-visible changes;
- important migration notes;
- known limitations;
- intended release artifacts.

A GitHub Release does not inherently publish the package to PyPI.

### 15. Clean up

After confirming the release:

- close completed issues;
- move deferred work out of the milestone;
- close the milestone;
- delete merged feature branches;
- delete the completed release branch;
- prune stale remote-tracking branches;
- remove disposable smoke-test projects;
- retain tags and release artifacts.
