# pyproject-init: development and release guide

`pyproject-init` renders a bundled Cookiecutter template into a new Python project.

Development work needs to preserve two distinct things:

1. the generator itself must install, test, build, and run correctly; and
2. a fresh project produced by the bundled template must work without manual repair.

These are related but separate verification targets.

## Current v0.2.0 checkpoint

| Concern | Current state |
| --- | --- |
| Generator environment and dependencies | uv, `.venv`, `[dependency-groups].dev`, and committed `uv.lock` |
| Generator Python | Python 3.14 for development; Python 3.12 minimum supported |
| Generator commands | `uv run ...` |
| Generator build backend | `uv_build` |
| Generator version | Static `[project].version` metadata |
| Generator runtime dependencies | Click, Cookiecutter, and `jinja2-time` |
| Generator development dependencies | MyPy, pytest, pytest-cov, pytest-randomly, Ruff |
| Generated default project | Still Hatch/Hatchling-based at this checkpoint |
| Release integration | Feature PRs into `release/v0.2.0`, followed by a final release PR into `main` |
| CI modernization | Still pending separate v0.2.0 work |

The generator no longer uses Hatch or Hatchling for its own development or packaging workflow.

The generated default project still does. Do not confuse generator modernization with generated-template modernization.

The planned generated-template migration, repository/template metadata improvements, expanded acceptance tests, CI migration, local verification automation, and final documentation pass remain separate v0.2.0 work.

## Start here after a break

Before switching branches or pulling, inspect your current state:

```console
git status
git branch -vv
git log --oneline --decorate -10
```

Confirm the local toolchain:

```console
uv --version
uv sync
uv run python --version
uv run pyproject-init --help
uv run pyproject-init new --help
```

Run generator commands from the repository root.

`uv sync` creates or updates `.venv` and installs the project plus its development dependencies. Manual environment activation is unnecessary.

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

The generator currently:

- supports Python 3.12 and newer;
- uses Python 3.14 as its normal development interpreter;
- records the development interpreter in `.python-version`;
- configures Ruff and MyPy against the minimum supported Python version.

Install uv using the standalone installer.

Then install and pin Python:

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

Use uv rather than manually managing the virtual environment:

```console
uv python install <version>
uv python pin <version>
uv sync
```

`uv python pin` updates `.python-version`.

If the interpreter changes, uv may recreate `.venv`. The virtual environment is disposable local state.

### Windows and pyenv-win

Avoid using both uv and `pyenv-win` as active version managers for the same repository.

Both recognize `.python-version`, and `pyenv-win` can intercept commands through its shim directory.

Check which uv executable PowerShell resolves:

```powershell
where.exe uv
Get-Command uv -All
```

The preferred result should begin with a standalone uv installation such as:

```text
C:\Users\<user>\.local\bin\uv.exe
```

If `pyenv-win` is retained for older repositories, its `bin` directory may remain available so `pyenv` itself can still be run deliberately.

Its shim directory should not intercept this project's commands:

```text
C:\Users\<user>\.pyenv\pyenv-win\shims
```

Check both User and System PATH variables if pyenv unexpectedly handles uv or Python commands.

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

A dependency is runtime if the installed package needs it to perform normal user-facing behavior.

For example, the bundled Cookiecutter template declares:

```json
"_extensions": ["jinja2_time.TimeExtension"]
```

Therefore `jinja2-time` is a runtime dependency of `pyproject-init`, not merely a development dependency.

This matters because development environments can hide dependency mistakes: `uv sync` installs development dependencies, while an end user installing a built wheel receives only declared runtime dependencies.

Use uv to modify dependencies:

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

For synchronization that must fail instead of updating a stale lockfile:

```console
uv sync --locked
```

Do not hand-edit `uv.lock`.

## Architecture and repository map

Click parses CLI commands and options.

Cookiecutter renders projects from bundled templates.

uv manages the generator's Python installation, environment, dependencies, lockfile, command execution, and package build frontend.

`uv_build` builds the generator package.

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
                README.md
                pyproject.toml
                pytest.ini
                src/
                    {{cookiecutter.project_slug}}/
                        __about__.py
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

The generator no longer stores its own version in `src/pyproject_init/__about__.py`.

Its version now comes directly from:

```toml
[project]
version = "..."
```

The generated template still contains its own `__about__.py` because the template has not yet been migrated away from its existing Hatch/Hatchling versioning model.

## Python compatibility policy

The generator currently declares:

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

This allows development on a modern interpreter while avoiding accidental syntax or assumptions that break Python 3.12 support.

The generator currently advertises CPython 3.12, 3.13, and 3.14 support.

Do not advertise additional implementations unless they are deliberately supported and tested.

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

A later v0.2.0 tooling/CI issue should provide one routine local entry point and make CI execute the same logical verification.

## Building the package

Build both source and wheel distributions with:

```console
uv build
```

Expected output is written to:

```text
dist/
```

and should contain both:

```text
*.tar.gz
*.whl
```

At this checkpoint, uv is the build frontend and `uv_build` is the configured build backend.

The generator's package version comes from:

```toml
[project]
version = "..."
```

Do not bump the package to a planned release version simply because development is occurring on a release branch.

The release version should be changed deliberately as part of release preparation.

## Why editable testing is not enough

Running:

```console
uv sync
uv run pyproject-init ...
```

tests an editable installation backed by the source checkout.

That does not prove that a published wheel contains all required files or dependencies.

A packaging regression can therefore pass every ordinary development test while still producing a broken release.

For `pyproject-init`, this is especially important because the package must ship its entire Cookiecutter template tree.

Release-quality verification must therefore test the built package itself.

## Inspect built artifacts

### Wheel

On Windows, use the uv-managed Python interpreter:

```powershell
uv run python -m zipfile -l `
    .\dist\pyproject_init-0.1.0-py3-none-any.whl
```

Do not assume a global `python` command exists.

Confirm that the wheel includes the bundled template tree, especially files such as:

```text
pyproject_init/templates/default/cookiecutter.json
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

Confirm that the corresponding template files exist beneath:

```text
src/pyproject_init/templates/
```

When the version changes, substitute the actual artifact filename rather than assuming `0.1.0`.

## Clean-wheel smoke test

This test approximates what an actual user receives.

It deliberately:

1. creates an isolated temporary environment;
2. installs the built wheel rather than the source checkout;
3. leaves the repository directory;
4. runs the installed CLI;
5. renders a project using the bundled template.

### Why this matters

This test catches problems such as:

- missing package data;
- missing runtime dependencies;
- broken console entry points;
- template lookup that only works from a source checkout;
- packaging configuration errors.

During the v0.2.0 packaging migration, this test exposed that `jinja2-time` was incorrectly classified as a development dependency even though the bundled template requires it at runtime.

### PowerShell procedure

From the generator repository:

```powershell
$testDir = Join-Path $env:TEMP "pyproject-init-wheel-test"

Remove-Item -Recurse -Force $testDir -ErrorAction SilentlyContinue

New-Item `
    -ItemType Directory `
    -Path $testDir |
    Out-Null
```

PowerShell equivalents:

```text
Join-Path                              build a filesystem path safely
Remove-Item -Recurse -Force            roughly rm -rf
New-Item -ItemType Directory           roughly mkdir
Push-Location                          roughly pushd
Pop-Location                           roughly popd
Get-ChildItem                          roughly ls
Select-String                          roughly grep
& <path>                               execute the command at that path
```

Create a clean environment:

```powershell
uv venv "$testDir\.venv" --python 3.14
```

Install the built wheel into that environment:

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

Confirm output exists:

```powershell
Get-ChildItem "$testDir\wheel-smoke"
```

Return to the original directory:

```powershell
Pop-Location
```

The generated project should contain at least:

```text
README.md
pyproject.toml
pytest.ini
src/
tests/
```

A later tooling issue should automate this workflow in a cross-platform Python script rather than requiring developers to reproduce the entire PowerShell sequence manually.

## Template maintenance

The generated template remains a separate project configuration.

At this checkpoint it still uses Hatch/Hatchling.

| Template value | Example | Used for |
| --- | --- | --- |
| `project_name` | `test-project` | Project folder, distribution name, user-facing command, repository metadata |
| `project_slug` | `test_project` | Python package/import name |

The current template contains version configuration such as:

```toml
dynamic = ["version"]

[tool.hatch.version]
path = "src/{{ cookiecutter.project_slug }}/__about__.py"
```

Do not remove this merely because the generator itself migrated to static version metadata.

The generated template will be migrated in its dedicated v0.2.0 issue.

When changing template files:

1. update template configuration;
2. update affected paths and contents together;
3. run generator checks;
4. generate a fresh project outside the repository;
5. test that generated project;
6. fix the template itself rather than repairing generated output manually.

## Fresh-project acceptance testing

The current generated template still uses Hatch.

Until its migration lands, generated-project checks remain separate from the generator's uv workflow.

Generate a fresh project outside the checkout:

```powershell
$generatorRoot = (Get-Location).Path

$smokeOutput = Join-Path `
    (Split-Path -Parent $generatorRoot) `
    "pyproject-init-test-output"

New-Item `
    -ItemType Directory `
    -Force `
    -Path $smokeOutput |
    Out-Null

$smokeName = "release-smoke-" + `
    (Get-Date -Format "yyyyMMdd-HHmmss")

uv run pyproject-init new `
    $smokeName `
    --output-dir $smokeOutput `
    --template default `
    --no-input
```

A second invocation using the same destination should reject the existing project without overwriting it.

Then enter the generated project and follow its current README.

Until the template migration lands, its development workflow remains Hatch-based.

## Troubleshooting

### Plain `python` is not found on Windows

A global Python executable is not required for this repository.

Prefer:

```console
uv run python ...
```

or:

```console
uv python ...
```

rather than relying on a global `python` command.

### uv unexpectedly invokes pyenv-win

Inspect:

```powershell
where.exe uv
Get-Command uv -All
```

Standalone uv should resolve before any pyenv shim.

Check both User and System PATH values for:

```text
.pyenv\pyenv-win\shims
```

### Wrong interpreter selected

Check:

```powershell
Get-Content .python-version
uv python find 3.14
uv run python --version
```

Restore the development interpreter with:

```console
uv python install 3.14
uv python pin 3.14
uv sync
```

### Stale `.venv`

The project environment is disposable.

Recreate it if necessary:

```powershell
Remove-Item -Recurse -Force .venv
uv sync
```

### CLI works from source but installed wheel fails

Do not assume the build is valid.

Check:

- runtime dependencies;
- wheel contents;
- template package data;
- entry-point metadata;
- clean-wheel installation.

Repeat the clean-wheel smoke test.

### Generated project fails but generator tests pass

Generator checks intentionally exclude the raw template directory.

Generate and test a fresh project outside the checkout.

The template and generator require separate validation.

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

Assign intended issues to it and keep unrelated work outside release scope.

Each issue should describe:

- intended behavior;
- affected areas;
- acceptance criteria;
- dependencies on other work.

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

Required CI status checks should be enabled only after the modernized CI workflow actually runs for release-targeted PRs.

### 4. Create issue branches

Prefer GitHub's Issue **Create a branch** action.

During this release, ensure the branch source is:

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

Keep branches focused.

Before committing:

```console
git status
git diff
```

Run relevant checks.

For ordinary generator changes:

```console
uv lock --check
uv run ruff check src tests scripts
uv run ruff format src tests scripts --check
uv run mypy src tests scripts
uv run pytest
uv run pyproject-init --help
uv run pyproject-init new --help
```

For packaging changes, additionally:

```console
uv build
```

and perform clean-artifact verification.

A future tooling issue should replace repetitive manual invocation with one local verification command plus a dedicated packaging smoke-test command.

CI should use those same logical checks.

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
- packaging tests if relevant;
- associated issue.

Merge through the PR.

### 8. Update the local release branch

After merge:

```console
git switch release/v0.2.0
git pull --ff-only
git branch -d <merged-feature-branch>
```

Start the next feature branch from the updated release branch.

### 9. Regression-test the integrated release

Before the final release PR:

1. run generator verification;
2. run coverage;
3. exercise project generation;
4. test duplicate-destination handling;
5. test fresh generated projects;
6. verify Python compatibility;
7. verify CI triggers and required checks;
8. review milestone completion;
9. review documentation;
10. build release artifacts;
11. run clean-wheel verification.

Fix regressions on dedicated branches, never directly on the release branch.

### 10. Prepare the release version

The generator version is now stored directly in:

```toml
[project]
version = "..."
```

Update it deliberately through the normal review process when preparing the actual release.

Do not use the release branch name as the version source.

### 11. Build release artifacts

Build:

```console
uv build
```

Inspect both:

```text
dist/*.whl
dist/*.tar.gz
```

Verify bundled templates exist in both distributions.

Install the exact wheel into a clean environment and generate a project from it.

Do not rely on an editable installation as proof that the release artifact works.

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

Merge only after required review and checks.

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

Publishing a GitHub Release does not automatically imply PyPI publication.

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
