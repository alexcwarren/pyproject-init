# pyproject-init: development and release guide

`pyproject-init` renders a bundled Cookiecutter template into a new Python project. Maintain both the generator and the generated project's working development experience: a fresh default project should pass its checks and run its starter application without manual repairs.

## Current v0.2.0 checkpoint

| Concern | Current state |
| --- | --- |
| Generator environment and dependencies | uv, `.venv`, `[dependency-groups].dev`, and committed `uv.lock` |
| Generator commands | Explicit `uv run ...` commands; root Hatch environments/scripts have been removed |
| Generator build backend | `hatchling.build` |
| Generator version | Dynamic, read from `src/pyproject_init/__about__.py` through `[tool.hatch.version]` |
| Generator Python minimum | `>=3.10`; Ruff targets `py310`, MyPy targets `3.10` |
| Generated default project | Hatch environments/tasks and Hatchling packaging |
| Release integration | Feature PRs into protected `release/v0.2.0`, followed by a final release PR into `main` |
| CI migration | Separate pending work; do not assume CI already uses uv or runs for release-targeted PRs |

The lockfile records the editable generator and its runtime and development dependencies. Runtime dependencies remain Click and Cookiecutter. The dev group contains `jinja2-time`, MyPy, pytest, pytest-cov, pytest-randomly, and Ruff.

The planned build-backend migration, Python modernization, template migration, template-file improvements, expanded template acceptance tests, CI migration, and final documentation pass are separate work. Do not describe those goals as completed merely because `uv sync` works. The integration branch name is a release target, not proof that the package version is already 0.2.0 or that a release has been published.

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

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if needed. Run generator commands from the repository root. `uv sync` prepares the project environment and includes the dev group by default; manual environment activation is unnecessary.

Keep `pyproject.toml` and `uv.lock` together in version control. Do not commit `.venv`, caches, test output, or build artifacts. After intentional dependency changes, synchronize and review both configuration and lockfile changes. For verification against the committed lockfile, use `uv sync --locked`; it fails if the lockfile needs updating. See [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/).

Python 3.10 remains the configured minimum at this checkpoint. The previous CI matrix covered 3.10, 3.11, and 3.12; inspect `.github/workflows/ci.yml` for the actual current matrix and triggers. Neither a newer local interpreter nor lockfile resolution markers establish tested support for additional Python versions.

## Architecture and repository map

Click parses commands and options. The CLI validates/selects the destination and template, then Cookiecutter resolves metadata and renders file contents and paths. The rendered project has its own configuration and environment.

| Component | Responsibility |
| --- | --- |
| uv | Generator environment, dependency synchronization, and command execution |
| Click | CLI arguments, options, help, and user-facing errors |
| Cookiecutter | Prompts, derived metadata, and template rendering |
| Hatch | Development environments/tasks in the generated default project only |
| Hatchling | Current packaging backend for the generator and default template |
| Ruff / MyPy / pytest | Lint, format, typing, and behavior checks |
| GitHub Actions | Automated checks defined in the workflow files |

```text
pyproject.toml                         Generator metadata, dev dependencies, build/tool settings
uv.lock                                Generator dependency resolution
src/pyproject_init/
    __about__.py                       Current generator version source
    pyproject_init.py                  Click CLI and generation orchestration
    templates/default/
        cookiecutter.json              Defaults, prompts, derived metadata
        {{cookiecutter.project_name}}/ Generated project root
            README.md
            pyproject.toml
            src/{{cookiecutter.project_slug}}/
                __about__.py
                __init__.py
                main.py
            tests/test_main.py
scripts/clean.py                       Repository cleanup utility
tests/test_pyproject_init.py           Generator/CLI tests
tests/test_clean.py                    Cleanup utility tests
.github/workflows/ci.yml               CI jobs and triggers
```

Keep `[build-system]` and `[tool.hatch.version]` in the generator configuration until the dedicated packaging migration replaces them. Hatchling configuration is still necessary even though the Hatch task runner has been removed from the generator workflow.

## Generator checks

Run the replacement development workflow from the generator root:

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

For formatting changes, run `uv run ruff format src tests scripts`, then review the diff and rerun the relevant checks. Add `--locked` immediately after `uv run` when checking the committed dependency resolution without allowing lockfile updates.

There is no root `hatch run all` replacement alias: run the explicit commands above. Confirm removal of root Hatch task definitions in PowerShell with:

```powershell
Select-String -Path pyproject.toml -Pattern "tool.hatch.envs"
```

That search should produce no matches. Hatch configuration within the bundled template is expected at this checkpoint.

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

The version file defines `__version__`. Imports and coverage package names use the slug; a hyphenated distribution name is not a valid Python import name.

1. Edit the bundled template and, when needed, `cookiecutter.json`.
2. Update affected file contents and directory/file names together.
3. Check entry points, package paths, version metadata, coverage paths, generated documentation, and test imports.
4. Run generator checks.
5. Generate a fresh project outside the repository and run its checks and application.
6. Put permanent fixes in the template, then regenerate; do not rely on repairs to a previously generated project.

Useful searches:

```console
rg "package_name|project_name|project_slug" src/pyproject_init/templates
rg --files src/pyproject_init/templates
```

## Fresh-project acceptance test

Install Hatch separately if it is unavailable (`python -m pip install hatch`). It is required for the current generated template, not for generator development commands.

This PowerShell example starts in the generator root and uses a unique project name in a sibling directory:

```powershell
$generatorRoot = (Get-Location).Path
$smokeOutput = Join-Path (Split-Path -Parent $generatorRoot) "pyproject-init-test-output"
New-Item -ItemType Directory -Force -Path $smokeOutput | Out-Null
$smokeName = "release-smoke-" + (Get-Date -Format "yyyyMMdd-HHmmss")
uv run pyproject-init new $smokeName --output-dir $smokeOutput --template default --no-input
```

Confirm generation succeeds before continuing. Repeat the command while still in the generator root; this invocation should reject the existing destination without altering its contents:

```powershell
uv run pyproject-init new $smokeName --output-dir $smokeOutput --template default --no-input
```

Then test the generated project:

```powershell
Push-Location (Join-Path $smokeOutput $smokeName)
try {
    hatch run all
    hatch run $smokeName
    $smokeSlug = $smokeName.Replace("-", "_")
    hatch run python -c "import importlib; m = importlib.import_module('$smokeSlug'); print(m.__file__)"
} finally {
    Pop-Location
}
```

Check each command's result; PowerShell does not necessarily stop on a native command's nonzero exit code. Follow the generated README if its application command differs. Confirm the imported module resolves to the generated project's source.

Inspect the generated metadata, version source, package folder, entry point, and test imports. Also test interactive generation with a different fresh name. For an explicitly supplied existing name, rejection should occur before prompts; when a name is chosen during prompts, verify final destination handling separately.

Until the template migration lands, `hatch run all` remains the generated-project acceptance command. Update this procedure with that migration.

## Troubleshooting

- **Wrong working directory:** The generator uses uv; the generated project uses Hatch. Check which `pyproject.toml` applies. Keep generated test projects outside the generator checkout.
- **Stale generated Hatch environment:** Prefer unique smoke-test names. If diagnosing a regenerated project at the same path, run `hatch env remove default`, `hatch env create`, then `hatch run all` from that generated project. Remove the relevant named environment if the failure occurs elsewhere.
- **Import failures:** Inspect the package folder, wheel package target, version path, and installed environment. Do not mask packaging errors by adding `src` to pytest's import path.
- **Dynamic version errors:** Both current projects need a matching version source and Hatchling version configuration. The generator uses `src/pyproject_init/__about__.py`.
- **Generation errors:** Check template filenames as well as contents for undefined variables. Preserve useful user-facing errors when fixing the cause.
- **Output paths:** Use an absolute parent output directory. Relative-path support remains follow-up work.
- **Defaults:** Review author and package metadata before publishing. Broader custom-template support is not yet an established acceptance path.

## Release workflow

Use a temporary release integration branch for each coordinated release. Keep `main` stable while related changes are developed and tested together.

```text
main
└── release/v0.2.0
    ├── feature/uv-workflow
    ├── feature/modern-python
    ├── feature/uv-build
    ├── feature/uv-template
    ├── feature/template-files
    ├── feature/template-tests
    ├── feature/uv-ci
    └── docs/v0.2.0

feature or fix PR → release/v0.2.0
final release PR  → main
validated main commit → v0.2.0 tag → GitHub release
```

These branch names describe the planned work; they do not indicate that every branch or implementation already exists.

### 1. Plan the milestone and issues

Create the `v0.2.0` milestone with a concise scope and acceptance criteria. Create or reuse focused issues for each migration step, assign them to the milestone, and apply relevant repository labels. Include existing template-testing work where appropriate. Record dependencies between issues and leave unrelated work outside the milestone. A due date is optional.

Each issue should explain the intended behavior, files or areas involved, and checks required to accept it. Include CI coverage for release-targeted PRs and enabling required release-branch status checks in the CI issue.

### 2. Create and protect the integration branch

For a new release, create `release/v0.2.0` from the reviewed, current `main` and push it. Do not recreate an existing release branch. Inspect uncommitted changes before switching branches.

**`release/*` branches are protected.** The established release ruleset requires a PR and resolved review conversations and blocks force pushes. Do not commit or push implementation changes directly to release branches. Release branches are temporary, so the release ruleset intentionally allows deletion after completion.

At this intermediate checkpoint, required status checks on the release ruleset were deferred because the existing CI only targeted PRs into `main`. The CI migration must make checks run on PRs into release branches, verify their reported names, and then enable the appropriate required checks. Do not treat an absent CI run as a pass or enable required checks that cannot run. Until that work lands, record local verification in each feature PR.

Keep the existing `main` protections. Verify actual repository settings when preparing a release; this document is not evidence of a live ruleset audit.

### 3. Create feature branches from issues

Use the issue's **Create a branch** action. Explicitly verify the destination repository, branch name, and branch source. For this release the source must be `release/v0.2.0`.

Use focused names such as `feature/uv-workflow`, `fix/<short-description>`, or `docs/v0.2.0`. An issue number may be included for traceability, for example `feature/<issue-number>-uv-workflow`. Existing branch names need not be renamed solely to adopt that convention.

Fetch and switch to the created branch locally. Start later feature branches from the updated release branch so they include already integrated work.

### 4. Implement, verify, commit, and open a PR

Keep each branch scoped to its issue. Run generator checks and any affected fresh-project or packaging checks. Review `git diff` and `git status`, stage only the intended files, and use a commit message describing the completed change.

For the current uv-workflow checkpoint, if all four files are still uncommitted and contain only this issue's changes:

```console
git add pyproject.toml uv.lock README.md README_DEV.md
git diff --cached
git commit -m "Migrate generator development workflow to uv"
git push -u origin feature/uv-workflow
```

If configuration/lockfile work was already committed, stage only the two READMEs and use `docs: document intermediate uv workflow and release process`. Use the actual branch name if it differs.

Open the PR with **base `release/v0.2.0`**, not `main`. Link the issue, describe the intermediate boundary, and list checks actually run. State explicitly that Hatchling packaging and the Hatch-based template remain.

Do not rely on `Closes #...` to close an issue when the PR targets a non-default release branch. Link it explicitly and update its state after verifying the integration. See [GitHub's issue-linking behavior](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue).

Review and resolve conversations, satisfy applicable checks, then merge through the PR. Remove merged feature branches when no longer needed. If deletion is blocked by a branch ruleset, use the repository's approved maintainer cleanup process; do not weaken protections for routine development.

### 5. Regress the integrated release

After related feature PRs merge, update the local release branch with a clean working tree and test the combined state. Fix failures on a new branch from the release branch and merge the fix by PR.

Before the final release PR:

1. Run the full generator checks and coverage against the committed lockfile.
2. Exercise interactive and noninteractive generation, hyphenated names, the generated application, and safe duplicate-destination rejection outside the checkout.
3. Run the generated project's current documented workflow. Revalidate it after any template migration.
4. Verify the supported Python matrix and CI triggers. Complete release-branch CI requirements before declaring the release ready.
5. Review milestone issues, deferred work, documentation, known limitations, and release notes.
6. Set the release version through a feature/fix PR using the version source configured at that point. At this checkpoint that source is `src/pyproject_init/__about__.py`; a later packaging issue may change it.
7. Build and test the distributable artifacts.

### 6. Verify distributable artifacts

From the generator root:

```console
uv build
```

This uses the configured Hatchling backend at this checkpoint. Using the uv build frontend does not mean the backend has migrated to `uv_build`. See [uv build-backend documentation](https://docs.astral.sh/uv/concepts/build-backend/).

Inspect the resulting wheel and source distribution for bundled templates, including templated paths and necessary hidden files. Install the exact newly built wheel in a separate clean environment outside the checkout, then run its CLI help and generate a project using that installed CLI. Test the resulting project. Also verify the source distribution can build successfully. An editable source installation alone does not prove packaged templates are available.

Record the artifact names and test results in the release PR. Do not publish stale artifacts from earlier builds.

### 7. Merge, tag, and publish the release

Open the final PR from `release/v0.2.0` into `main`. Summarize completed milestone work, regression and artifact results, known limitations, and deferred issues. Obtain passing required checks and resolve review conversations before merging.

Update local `main`, verify it contains the intended release, and validate the final merged state. Only after that validation, create the tag on the reviewed release commit:

```console
git switch main
git pull --ff-only
git status
git log -1 --oneline
git tag --list v0.2.0
```

Confirm the working tree is clean, HEAD is the intended release commit, and the tag does not already exist. Then:

```console
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

If `main` has advanced beyond the reviewed release commit, tag the verified commit explicitly instead of blindly tagging HEAD. Do not replace an existing release tag.

Create the GitHub release from that tag with release notes, known limitations, and intended artifacts. PyPI publishing is a separate action: use the configured publishing process only when ready, then verify installation of the published package. A GitHub release does not publish to PyPI automatically unless explicitly configured to do so.

### 8. Clean up

After confirming the final merge, tag, and release:

- Verify completed issues are closed and move explicitly deferred work out of the milestone with an explanation.
- Close the milestone when all included work is accounted for.
- Delete the completed remote and local release branch and any remaining merged feature branches after confirming they contain no unique work. Switch to `main` before deleting a local release branch.
- Prune stale remote-tracking branches and remove disposable acceptance-test environments/projects when no longer needed.
- Retain the release tag, notes, and intended release artifacts. Keep the reusable `release/*` protection ruleset for the next release.

The next release starts with a new milestone and integration branch from stable `main`.
