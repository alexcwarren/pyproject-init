# pyproject-init: maintainer re-onboarding guide

`pyproject-init` is a CLI that renders a bundled Cookiecutter template into a new Python project. Its main acceptance criterion is simple: a freshly generated project should immediately pass `hatch run all` and run its starter application.

## Where we left off

The release-preparation PR was submitted and all checks passed in the last recorded conversation. That conversation did **not** confirm that the PR was merged or that a release was published. Check GitHub before assuming either happened.

The completed work included template/package naming fixes, starter code and a real generated test, Hatch build/version configuration, and duplicate-destination protection. A fresh generated project was verified outside the generator repository. `v0.1.0` was the proposed first release, subject to the repository's existing version and tag history.

The next step is to confirm the merge state, validate the merged code, and finish release preparation. Relative output paths, broader template handling, and extra validation are follow-up work.

## Start here after a break

From your existing checkout:

```console
git status
git branch -vv
git log --oneline --decorate -10
python --version
python -m pip install hatch
hatch env show
hatch env create
hatch run all
hatch run coverage:cov
hatch run pyproject-init --help
hatch run pyproject-init new --help
```

Inspect uncommitted work before switching branches or updating the checkout. Read `pyproject.toml` to see the Python requirement, dependencies, environment names, and exact script definitions. CI currently covers 3.10, 3.11, and 3.12; the old local setup used Python 3.10.5, but that patch version is not a general setup requirement.

## Architecture and responsibilities

```text
pyproject-init new ...
    → Click parses arguments and options
    → the CLI selects/validates the template and destination
    → Cookiecutter resolves defaults, asks questions, and renders files
    → the generated project has its own pyproject.toml
    → Hatch runs that project's development tasks
    → Hatchling builds/installs that project's Python package
```

| Component | Role | Where to look |
| --- | --- | --- |
| Click | Commands, options, help, and user-facing errors | `src/pyproject_init/pyproject_init.py` |
| Cookiecutter | Metadata prompts, derived values, and file/path rendering | `src/pyproject_init/templates/default/` |
| Hatch | Named environments, dependency installation, and task scripts | Each project's `pyproject.toml` |
| Hatchling | Packaging build backend, package selection, and version metadata | `[build-system]` and `[tool.hatch.*]` |
| Ruff / MyPy / pytest | Linting, type checking, and behavior checks | Hatch scripts and tool configuration |
| GitHub Actions | Automated checks across supported Python versions | `.github/workflows/ci.yml` |

There are two separate projects to keep track of: the generator itself and each generated application. Both use Hatch, but each has its own configuration and environments. Running a command from the generated project's root should use that project's configuration.

`pyenv` selects an interpreter. Hatch manages project environments and runs tasks, so you usually do not need to activate a virtual environment manually.

## Repository map

```text
pyproject.toml                         Generator metadata and Hatch/tool configuration
src/pyproject_init/
    pyproject_init.py                  Click CLI and generation orchestration
    templates/default/
        cookiecutter.json              Defaults, prompts, and derived metadata
        {{cookiecutter.project_name}}/ Generated project root
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
.github/workflows/ci.yml              CI jobs
```

The old README's reference to `cli.py` and its description of templates as future work were stale. The recorded implementation lives in `pyproject_init.py`, and the bundled default template already exists. Confirm the current console entry point in `[project.scripts]` if files have since moved.

## project_name versus project_slug

Use the final two-name convention from the release-preparation work:

| Value | Example | Use for |
| --- | --- | --- |
| `project_name` | `test-project` | Outer folder, distribution name, user-facing command name, repository URLs |
| `project_slug` | `test_project` | Python package folder, imports, entry-point module targets, package/build/version paths, coverage module names |

Earlier discussion temporarily introduced `package_name` and used `project_slug` for a hyphenated name. That approach was superseded. Avoid reintroducing it accidentally.

For example, the generated configuration should consistently connect the distribution to the import package:

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

The version file must define `__version__`. Tests should import the slug, for example `from test_project.main import hello_world`. Coverage package names and paths under `src/` must also use the slug. A hyphenated name is not a valid Python import identifier.

## Template maintenance workflow

1. Edit the bundled template under `src/pyproject_init/templates/default/`, including `cookiecutter.json` when changing metadata or derivation.
2. Update every affected reference in file contents **and in directory/file names**. Cookiecutter renders both.
3. Check package paths, entry points, version configuration, coverage paths, generated README commands, and generated test imports together.
4. Run the generator's own checks.
5. Generate a project at a fresh path outside this repository.
6. Run its checks and starter command; verify its metadata and duplicate-destination behavior.

Editing a previously generated project is useful for diagnosing a failure, but the permanent fix belongs in the template. Regenerate to prove it works without manual repairs.

Useful searches from the generator root:

```console
rg "package_name|project_name|project_slug" src/pyproject_init/templates
rg --files src/pyproject_init/templates
```

If generation produces a generic failure message, inspect the underlying exception during local debugging. An undefined variable can remain in a filename even when a content search looks clean. Keep useful user-facing errors when finishing the fix.

## Tests and checks

| Command | Purpose |
| --- | --- |
| `hatch run all` | Generator's aggregate checks |
| `hatch run test` | Normal test suite |
| `hatch run lint:all` | Scripts in the lint environment |
| `hatch run type:typecheck` | Dedicated type-checking script |
| `hatch run coverage:cov` | Coverage run in the coverage environment |
| `hatch env show` | Inspect configured environments |
| `hatch run pyproject-init new --help` | Verify CLI options locally |

These command names come from the recorded configuration; `pyproject.toml` is authoritative if they change.

Hatch's script syntax is `hatch run [environment:]script`. `hatch run coverage` launches a command named `coverage` in the default environment; it does not select the coverage environment's `cov` script. Use `hatch run coverage:cov`.

The recorded test files cover the CLI/generator and `scripts/clean.py`. Passing those tests does not replace checking the rendered project's packaging and development workflow. When adding tests, confirm that CI's targeted commands include them.

For the `main` ruleset, the agreed required jobs were `lint`, `typecheck`, `test-pyproject-init`, and `test-clean`, including all exposed matrix variants for Python 3.10, 3.11, and 3.12. Use the actual check names shown by GitHub. `precheck` is an orchestration job. Coverage was considered optional because no minimum threshold was established in the conversation.

## Fresh-project acceptance test

Use an absolute output directory outside the generator checkout and a unique project name. This PowerShell example uses a sibling output directory:

```powershell
# Run from the pyproject-init repository root.
$smokeOutput = Join-Path (Split-Path -Parent (Get-Location).Path) "pyproject-init-test-output"
New-Item -ItemType Directory -Force -Path $smokeOutput | Out-Null
$smokeName = "release-smoke-" + (Get-Date -Format "yyyyMMdd-HHmmss")
hatch run pyproject-init new $smokeName --output-dir $smokeOutput --template default --no-input

# Repeat before changing directory: this should fail safely.
hatch run pyproject-init new $smokeName --output-dir $smokeOutput --template default --no-input

Set-Location (Join-Path $smokeOutput $smokeName)
hatch run all
```

Then follow the generated README to run the application. Inspect the rendered `pyproject.toml`, package folder, version file, and test imports. Verify the installed package resolves from the expected project. For a project named `test-project`, for example:

```console
hatch run python -c "import test_project; print(test_project.__file__)"
```

Also exercise interactive generation with a different fresh name. When the name is supplied explicitly, duplicate-destination rejection should happen before Cookiecutter prompts. If the name is chosen during prompting, check the final destination behavior separately.

## Common gotchas

### Hatch can reuse an environment after regeneration

Deleting and recreating a project at the same path does not necessarily remove its Hatch environment. After package/build metadata changes, a stale environment can preserve a broken install even when the generated files are correct.

From the affected project's root:

```console
hatch env remove default
hatch env create
hatch run all
```

Remove the relevant named environment instead if the failure occurs there. Prefer unique generated project names for acceptance testing. Environment recreation is a troubleshooting step; a fresh project should pass without it.

### Generate test projects outside this repository

Nested projects can pollute Git status, searches, lint/type-check inputs, and debugging context. Both projects have their own Hatch state. Before running checks, confirm your working directory and which `pyproject.toml` you are using.

### Use absolute output paths

Relative `--output-dir` paths were a confirmed limitation. Use an absolute parent directory; the generator appends the project name. Keep relative-path support on the follow-up list until implemented and tested.

### Import errors can be packaging errors

If Ruff and MyPy pass but pytest cannot import the generated package, check the wheel package target, version path, `src/` folder name, and installed environment. Recreate stale state before concluding the template is still broken. Do not hide a packaging failure merely by adding `src` to pytest's import path.

### Dynamic versioning needs a source

`dynamic = ["version"]` requires matching Hatch version configuration and a version file. A missing `[tool.hatch.version]` caused an earlier generated-project installation failure.

### Defaults still need review

`--no-input` is convenient for smoke tests, but author information and other placeholder metadata must be reviewed before publishing a generated project. Broader custom-template support is not yet an established acceptance path, even if help text describes additional template inputs.

## Release preparation

1. Confirm the release-preparation PR is merged and inspect existing releases/tags before choosing a version.
2. With a clean working tree, update `main`:

   ```console
   git switch main
   git pull --ff-only
   git status
   git tag --list
   ```

3. Run `hatch run all` and `hatch run coverage:cov` on the release candidate.
4. Run the fresh-project acceptance test outside the repository. Check interactive creation, defaults, the generated application, and safe rejection of an existing destination.
5. Review version metadata, both READMEs, and release notes. The intended first release was `0.1.0`; follow the configured version source and existing history.
6. Build distributable artifacts:

   ```console
   hatch build
   ```

7. Inspect the wheel and source distribution to ensure the bundled template is included. In a clean environment, install the built wheel and repeat CLI help and project generation. A working source checkout alone does not prove the packaged templates are available.
8. Commit any final release changes and obtain passing checks. Tag the reviewed release commit according to repository convention and create the GitHub release with concise notes and known limitations.
9. If publishing to PyPI, follow the repository's configured publishing process and verify the published installation workflow. A GitHub release does not itself publish a Python package.

Keep release preparation focused on the existing core workflow. Capture relative output paths, additional validation, broader templates, Hatch script simplification, and possible consolidation of targeted test jobs as future issues.
