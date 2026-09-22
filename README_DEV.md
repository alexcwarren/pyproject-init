# pyproject-init: development and release guide

`pyproject-init` renders a bundled Cookiecutter template into a new Python project. Maintain both the generator and the generated project's working development experience: a fresh default project should pass its checks and run its starter application without manual repairs.

## Current v0.2.0 checkpoint

| Concern | Current state |
| --- | --- |
| Generator environment and dependencies | uv, `.venv`, `[dependency-groups].dev`, and committed `uv.lock` |
| Generator commands | Explicit `uv run ...` commands; root Hatch environments/scripts have been removed |
| Generator development Python | Python 3.14, pinned by `.python-version` |
| Generator minimum supported Python | Python 3.12 |
| Generator tool compatibility target | Ruff `py312`; MyPy Python 3.12 |
| Generator build backend | `hatchling.build` |
| Generator version | Dynamic, read from `src/pyproject_init/__about__.py` through `[tool.hatch.version]` |
| Generated default project | Hatch environments/tasks and Hatchling packaging; Python-version choices have not yet been migrated |
| Release integration | Feature PRs into protected `release/v0.2.0`, followed by a final release PR into `main` |
| CI migration | Separate pending work; the current workflow still reflects the pre-v0.2 Python/Hatch configuration |

The generator repository now uses uv for Python installation, interpreter selection, virtual-environment management, dependency synchronization, locking, and command execution.

Runtime dependencies remain Click and Cookiecutter. The development dependency group contains `jinja2-time`, MyPy, pytest, pytest-cov, pytest-randomly, and Ruff.

The planned build-backend migration, generated-template migration, template-file improvements, expanded template acceptance tests, CI migration, and final documentation pass are separate work. Do not describe those goals as completed merely because the generator itself now uses uv and Python 3.14.

The integration branch name is a release target, not proof that the package version is already 0.2.0 or that a release has been published.

## Start here after a break

Inspect local work before switching branches or pulling:

```console
git status
git branch -vv
git log --oneline --decorate -10
uv --version
uv sync
uv run python --version
uv run pyproject-init --help
uv run pyproject-init new --help
```

Run generator commands from the repository root.

`uv sync` prepares the project environment and includes the `dev` dependency group by default. Manual virtual-environment activation is unnecessary.

Keep `pyproject.toml`, `.python-version`, and `uv.lock` together in version control. Do not commit `.venv`, caches, test output, or build artifacts.

## Python setup

The generator currently:

- supports Python 3.12 and newer;
- uses Python 3.14 as the normal development interpreter;
- records the development interpreter in `.python-version`;
- configures Ruff and MyPy against the minimum supported Python version, not the newest development interpreter.

For a new development machine, install uv using its standalone installer rather than through a Python environment.

Then install and pin the development interpreter:

```console
uv python install 3.14
uv python pin 3.14
uv sync
```

Verify the selected interpreter:

```console
uv run python --version
```

The expected major/minor version is Python 3.14.

### Changing the pinned Python version

Use uv rather than editing environment state manually:

```console
uv python install <version>
uv python pin <version>
uv sync
```

`uv python pin` writes the project's `.python-version` file.

Changing the pinned interpreter may cause uv to recreate `.venv`. The virtual environment is disposable project state and should not be committed.

### Windows and pyenv-win

Avoid using both uv and `pyenv-win` as active Python-version managers for the same project.

Both tools recognize `.python-version`, and `pyenv-win` can intercept commands through its `shims` directory before uv has a chance to manage the project interpreter.

On Windows, prefer the standalone uv executable and ensure uv resolves independently:

```powershell
where.exe uv
Get-Command uv -All
```

The preferred result should begin with a standalone uv path such as:

```text
C:\Users\<user>\.local\bin\uv.exe
```

If `pyenv-win` is still installed for older projects, its `bin` directory may remain available so the `pyenv` command can still be used deliberately. Its `shims` directory should not precede standalone uv on either the User or System `PATH`.

A problematic PATH entry looks like:

```text
C:\Users\<user>\.pyenv\pyenv-win\shims
```

If uv commands unexpectedly produce pyenv errors such as requests to run `pyenv global` or `pyenv local`, inspect both the User and System PATH values for a pyenv shim entry.

Do not document pyenv as a prerequisite for this project. uv is the Python-version manager for the v0.2 development workflow.

## Dependencies and locking

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

Use uv to modify dependencies rather than editing resolved lock data manually.

For example:

```console
uv add <package>
uv add --dev <package>
uv remove <package>
```

After intentional dependency or Python-compatibility changes, synchronize and review both `pyproject.toml` and `uv.lock`.

Check whether the committed lockfile is current with:

```console
uv lock --check
```

Use:

```console
uv sync --locked
```

when verification must fail rather than modify an out-of-date lockfile.

Never hand-edit `uv.lock`.

## Architecture and repository map

Click parses commands and options. The CLI validates/selects the destination and template, then Cookiecutter resolves metadata and renders file contents and paths. The rendered project has its own configuration and environment.

| Component | Responsibility |
| --- | --- |
| uv | Generator Python versions, environment, dependency synchronization, locking, and command execution |
| Click | CLI arguments, options, help, and user-facing errors |
| Cookiecutter | Prompts, derived metadata, and template rendering |
| Hatch | Development environments/tasks in the generated default project only |
| Hatchling | Current packaging backend for the generator and default template |
| Ruff / MyPy / pytest | Linting, formatting, typing, and behavior checks |
| GitHub Actions | Automated checks defined in the workflow files |

```text
.python-version                       Generator development Python pin
pyproject.toml                        Generator metadata, dependencies, build/tool settings
uv.lock                               Generator dependency resolution
src/pyproject_init/
    __about__.py                      Current generator version source
    pyproject_init.py                 Click CLI and generation orchestration
    templates/default/
        cookiecutter.json             Defaults, prompts, derived metadata
        {{cookiecutter.project_name}}/
            README.md
            pyproject.toml
            src/{{cookiecutter.project_slug}}/
                __about__.py
                __init__.py
                main.py
            tests/test_main.py
scripts/clean.py                      Repository cleanup utility
tests/test_pyproject_init.py          Generator/CLI tests
tests/test_clean.py                   Cleanup utility tests
.github/workflows/ci.yml              CI jobs and triggers
```

Keep `[build-system]` and `[tool.hatch.version]` in the generator configuration until the dedicated packaging migration replaces them.

Hatchling configuration is still necessary even though Hatch no longer manages the generator development environment.

## Python compatibility policy

Do not confuse the development interpreter with the minimum supported interpreter.

The generator currently declares:

```toml
requires-python = ">=3.12"
```

The repository develops normally with:

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

This allows development to use a contemporary interpreter without accidentally introducing syntax or assumptions incompatible with Python 3.12.

The generator currently advertises CPython 3.12, 3.13, and 3.14 support.

Do not advertise PyPy support unless it is deliberately tested and supported.

The generated project template has its own Python-version configuration and has not yet been migrated as part of this checkpoint.

## Generator checks

Run the development checks from the generator root:

```console
uv sync
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

Review the resulting diff and rerun the relevant checks.

There is currently no single aggregate local command replacing the old `hatch run all`. Automating the routine verification workflow and keeping local checks aligned with CI is part of the v0.2.0 CI/tooling work.

Until that lands, avoid inventing multiple competing task entry points.

Confirm removal of root Hatch task definitions in PowerShell with:

```powershell
Select-String -Path pyproject.toml -Pattern "tool.hatch.envs"
```

That search should produce no matches.

Hatch configuration within the bundled project template is expected at this checkpoint.

Ruff, MyPy, and pytest exclude the raw template directory in the current root configuration. Passing generator checks therefore does not prove rendered files work. Always include fresh-project acceptance testing for changes affecting generation or packaging.

## Template maintenance

| Template value | Example | Used for |
| --- | --- | --- |
| `project_name` | `test-project` | Outer folder, distribution name, user-facing command, repository URLs |
| `project_slug` | `test_project` | Import package, entry-point module, package/version paths, coverage module |

The default template currently connects these values as follows:

```toml
[project]
name = "{{ cookiecutter.project_name }}"
dynamic = ["version"]

[project.scripts]
{{ cookiecutter.project_name }} = "{{ cookiecutter.project_slug }}.main:main"

[tool.hatch.version]
path = "src/{{ cookiecutter.project_slug }}/__about__.py"

[tool.hatch.build.targets.wheel]
packages = ["src/{{ cookiecutter.project_slug }}"]
```

The generated version file defines `__version__`.

Imports and coverage package names use the slug. A hyphenated distribution name is not a valid Python import name.

When changing the template:

1. Edit the bundled template and, when needed, `cookiecutter.json`.
2. Update affected file contents and directory/file names together.
3. Check entry points, package paths, version metadata, coverage paths, generated documentation, and test imports.
4. Run generator checks.
5. Generate a fresh project outside the repository.
6. Run the generated project's checks and starter application.
7. Put permanent fixes in the template, then regenerate; do not rely on repairs to a previously generated project.

Useful searches:

```console
rg "package_name|project_name|project_slug" src/pyproject_init/templates
rg --files src/pyproject_init/templates
```

## Fresh-project acceptance test

The current generated template still uses Hatch.

Install Hatch separately if it is unavailable:

```console
python -m pip install hatch
```

This is required for the current generated template, not for generator development commands.

This PowerShell example starts in the generator root and uses a unique project name in a sibling directory:

```powershell
$generatorRoot = (Get-Location).Path
$smokeOutput = Join-Path (Split-Path -Parent $generatorRoot) "pyproject-init-test-output"
New-Item -ItemType Directory -Force -Path $smokeOutput | Out-Null
$smokeName = "release-smoke-" + (Get-Date -Format "yyyyMMdd-HHmmss")

uv run pyproject-init new `
    $smokeName `
    --output-dir $smokeOutput `
    --template default `
    --no-input
```

Confirm generation succeeds before continuing.

Repeat the command while still in the generator root. The second invocation should reject the existing destination without altering it:

```powershell
uv run pyproject-init new `
    $smokeName `
    --output-dir $smokeOutput `
    --template default `
    --no-input
```

Then test the generated project:

```powershell
Push-Location (Join-Path $smokeOutput $smokeName)

try {
    hatch run all
    hatch run $smokeName

    $smokeSlug = $smokeName.Replace("-", "_")

    hatch run python -c `
        "import importlib; m = importlib.import_module('$smokeSlug'); print(m.__file__)"
}
finally {
    Pop-Location
}
```

Check each command's result. PowerShell does not necessarily stop on a native command's nonzero exit code.

Follow the generated README if its application command differs. Confirm the imported module resolves to the generated project's source.

Inspect:

- generated project metadata;
- version source;
- package folder;
- console entry point;
- test imports;
- duplicate-destination handling.

Also exercise interactive generation with a different fresh name.

For an explicitly supplied existing name, rejection should occur before prompts. When a name is chosen during prompting, verify final destination handling separately.

Until the template migration lands, `hatch run all` remains the generated-project acceptance command.

## Troubleshooting

### Wrong working directory

The generator uses uv while the generated project still uses Hatch.

Check which repository and `pyproject.toml` you are operating against before diagnosing tooling behavior.

Keep generated test projects outside the generator checkout.

### uv invokes pyenv unexpectedly on Windows

Check:

```powershell
where.exe uv
Get-Command uv -All
```

Standalone uv should resolve before any pyenv shims.

Inspect both User and System PATH variables for:

```text
.pyenv\pyenv-win\shims
```

Using pyenv shims and uv's `.python-version` management simultaneously can cause pyenv to intercept commands inside the repository.

### Wrong Python selected

Check:

```console
cat .python-version
uv python find 3.14
uv run python --version
```

On PowerShell:

```powershell
Get-Content .python-version
uv python find 3.14
uv run python --version
```

Re-establish the expected development interpreter with:

```console
uv python install 3.14
uv python pin 3.14
uv sync
```

### Stale virtual environment

`.venv` is disposable.

If an environment was created using an old interpreter or incompatible setup, remove it and allow uv to recreate it:

```powershell
Remove-Item -Recurse -Force .venv
uv sync
```

### Stale generated Hatch environment

Prefer unique smoke-test names.

If diagnosing a regenerated project at the same path:

```console
hatch env remove default
hatch env create
hatch run all
```

Run those commands from the generated project, not the generator repository.

### Import failures

Inspect:

- the package folder;
- wheel package target;
- version path;
- installed environment.

Do not mask packaging errors by adding `src` to pytest's import path.

### Dynamic version errors

Both the generator and current generated template still use dynamic Hatchling version configuration.

The generator version currently comes from:

```text
src/pyproject_init/__about__.py
```

The dedicated packaging migration will revisit this.

### Generation errors

Check template filenames as well as file contents for undefined Cookiecutter variables.

Preserve useful user-facing errors when fixing the underlying cause.

### Output paths

Use an absolute parent output directory.

Relative-path support remains follow-up work.

### Template defaults

Review generated author and package metadata before publishing.

Broader custom-template support is not yet an established acceptance path.

## Release workflow

Use a temporary release integration branch for each coordinated release. Keep `main` stable while related changes are developed and regression-tested together.

```text
main
└── release/v0.2.0
    ├── feature/<issue>-...
    ├── fix/<issue>-...
    └── docs/<issue>-...

feature/fix/docs PR → release/v0.2.0
final release PR    → main
validated main      → v0.2.0 tag → GitHub release
```

The release branch is temporary. A permanent `dev` branch is not required.

### 1. Plan the milestone and issues

Create the release milestone first.

For v0.2.0:

```text
v0.2.0
```

Create or reuse focused issues for the planned work.

For each issue:

- assign the release milestone;
- assign the maintainer;
- add appropriate labels;
- describe the intended behavior;
- define acceptance criteria;
- identify meaningful dependencies on other issues.

Leave unrelated work outside the milestone rather than expanding release scope opportunistically.

A due date is optional.

### 2. Create the integration branch

Start from reviewed, current `main`:

```console
git switch main
git pull --ff-only
git status
```

Create the release branch:

```console
git switch -c release/v0.2.0
git push -u origin release/v0.2.0
```

Do not recreate an existing release branch.

### 3. Protect the release branch

`release/*` branches are protected integration branches.

The release ruleset should:

- require changes to arrive through pull requests;
- require review conversations to be resolved;
- block force pushes.

Do not make ordinary implementation commits directly to `release/*`.

Release branches are deliberately temporary, so they should remain deletable after the release is complete.

Required CI checks should be enabled only after the CI workflow actually runs for release-targeted PRs and the correct check names have been verified.

### 4. Create working branches from GitHub Issues

Prefer the Issue's **Create a branch** action.

Verify all populated values before creating the branch, especially:

- branch name;
- destination repository;
- branch source.

During an active release, the source must be the current release branch rather than `main`.

Use the repository branch convention:

```text
feature/<issue-number>-<short-description>
fix/<issue-number>-<short-description>
chore/<issue-number>-<short-description>
docs/<issue-number>-<short-description>
```

Release branches use:

```text
release/v<major>.<minor>.<patch>
```

Examples:

```text
feature/17-modernize-python
fix/24-relative-output-path
docs/22-v0-2-docs
release/v0.2.0
```

Branch naming is a convention rather than a reason to add disproportionate repository automation. Review the generated Issue branch name before accepting it.

Start later feature branches from the updated release branch so they include already integrated v0.2.0 work.

### 5. Implement and verify the issue

Keep each branch focused on one issue.

Before committing:

```console
git status
git diff
```

Run the checks relevant to the change.

For generator changes, the current full manual verification set is:

```console
uv lock --check
uv run ruff check src tests scripts
uv run ruff format src tests scripts --check
uv run mypy src tests scripts
uv run pytest
uv run pyproject-init --help
uv run pyproject-init new --help
```

The v0.2.0 tooling/CI work should reduce this repetitive sequence to a single routine local verification entry point while preserving the underlying checks.

CI should ultimately execute the same logical validation as local development.

### 6. Commit deliberately

Stage only the files belonging to the issue.

Example:

```console
git add <intended-files>
git diff --cached
git status
git commit -m "<concise completed change>"
```

Avoid mixing unrelated cleanup into the same commit merely because it was noticed while working on the issue.

Push the branch:

```console
git push -u origin <branch-name>
```

### 7. Open the feature PR into the release branch

The PR base must be:

```text
release/v0.2.0
```

not `main`.

Describe:

- what changed;
- what intentionally did not change;
- how the work was verified;
- which issue it corresponds to.

Link the Issue explicitly.

Because the PR targets a non-default integration branch, do not assume `Closes #...` alone will close the Issue at the desired time. Confirm Issue state after integration.

Review the Files Changed tab before merging.

Resolve applicable review conversations and satisfy available checks.

Merge through the PR rather than pushing the feature changes directly onto the release branch.

### 8. Update the local release branch

After merging:

```console
git switch release/v0.2.0
git pull --ff-only
git branch -d <merged-feature-branch>
```

Then create the next issue branch from the newly updated release branch.

### 9. Regression-test the integrated release

As related feature PRs accumulate, verify the combined release branch rather than only individual feature branches.

If integration reveals a regression:

1. create a new branch from `release/v0.2.0`;
2. fix the problem there;
3. verify it;
4. merge it back by PR.

Do not patch the release branch directly.

Before the final release PR:

1. Run the full generator verification workflow.
2. Run coverage.
3. Exercise interactive and noninteractive project generation.
4. Test duplicate-destination handling.
5. Test generated projects outside the checkout.
6. Verify supported Python versions.
7. Verify CI triggers and required checks.
8. Review milestone completion and deferred work.
9. Review README and README_DEV accuracy.
10. Build and test distributable artifacts.

### 10. Verify distributable artifacts

From the generator root:

```console
uv build
```

At the current checkpoint, uv is the build frontend while Hatchling remains the configured build backend.

Do not describe this as an `uv_build` migration until the dedicated packaging issue lands.

Inspect both the wheel and source distribution.

Verify that bundled templates are included in the package.

Install the newly built wheel into a clean environment outside the checkout and verify:

```console
pyproject-init --help
pyproject-init new ...
```

Generate a project with the installed artifact and test that generated project.

An editable source installation alone does not prove packaged templates are correct.

Do not publish stale artifacts from an earlier build.

### 11. Prepare the final release PR

When milestone work is complete, open:

```text
release/v0.2.0 → main
```

The PR should summarize:

- completed milestone work;
- regression results;
- Python compatibility;
- CI results;
- artifact verification;
- known limitations;
- intentionally deferred work.

Resolve review conversations and obtain all required checks before merging.

### 12. Tag the validated release

After the final PR is merged:

```console
git switch main
git pull --ff-only
git status
git log -1 --oneline
git tag --list v0.2.0
```

Confirm:

- the working tree is clean;
- HEAD is the intended release commit;
- the tag does not already exist.

Then:

```console
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

If `main` has advanced beyond the reviewed release commit, tag the verified commit explicitly instead of blindly tagging HEAD.

Never replace an existing release tag merely to simplify release repair.

### 13. Create the GitHub release

Create the GitHub Release from the validated tag.

Include:

- concise release notes;
- important user-visible changes;
- known limitations;
- appropriate release artifacts.

A GitHub Release does not inherently publish the package to PyPI.

If PyPI publishing is configured, treat publishing and post-publish installation verification as explicit release steps.

### 14. Clean up

After confirming the release:

- verify completed milestone Issues are closed;
- move deferred work out of the milestone with an explanation;
- close the milestone;
- delete merged feature branches;
- delete the completed `release/v0.2.0` branch;
- prune stale remote-tracking branches;
- remove disposable smoke-test projects and environments;
- retain the release tag and GitHub Release.

The next release begins from stable `main` with a new milestone and a new temporary release integration branch.
