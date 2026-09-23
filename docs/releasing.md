# Releasing

`pyproject-init` uses a temporary release-integration branch for coordinated releases.

This keeps `main` stable while related milestone work is developed and tested together.

## Release model

```text
main
└── release/vX.Y.Z
    ├── feature/<issue>-...
    ├── fix/<issue>-...
    ├── chore/<issue>-...
    └── docs/<issue>-...

feature/fix/chore/docs PR
            ↓
      release/vX.Y.Z
            ↓
       final PR
            ↓
          main
            ↓
           tag
            ↓
      GitHub Release
```

A permanent `dev` branch is not required.

## 1. Plan the release milestone

Create the milestone before implementation work begins.

Example:

```text
v0.2.0
```

The milestone should describe the intended release scope and acceptance criteria.

Create or reuse focused issues for each logical piece of work.

For each issue:

- assign the milestone;
- assign the maintainer where appropriate;
- add useful labels;
- describe intended behavior;
- describe acceptance criteria;
- note meaningful dependencies.

Avoid expanding release scope opportunistically.

Deferred work should remain outside the milestone or be explicitly moved out with an explanation.

## 2. Create the release branch

Start from current reviewed `main`.

```console
git switch main
git pull --ff-only
git status
```

Confirm the working tree is clean.

Create:

```console
git switch -c release/v0.2.0
git push -u origin release/v0.2.0
```

Do not recreate an already-existing release branch.

## 3. Protect release branches

The repository's `release/*` rules should require:

- pull requests;
- resolved review conversations;
- the aggregate `CI` status check;
- blocked force pushes.

Release branches are temporary, so deletion should remain possible after the release is complete.

`main` should likewise require the current aggregate `CI` status rather than obsolete historical check names.

## 4. Create working branches from issues

Prefer GitHub's **Create a branch** action on the relevant issue.

During an active coordinated release, explicitly choose the release branch as the source:

```text
release/v0.2.0
```

Do not accept GitHub's default `main` source without checking it.

Use conventions such as:

```text
feature/<issue-number>-<description>
fix/<issue-number>-<description>
chore/<issue-number>-<description>
docs/<issue-number>-<description>
```

Example:

```text
feature/21-uv-ci
```

Release branches use:

```text
release/v<semver>
```

Branch naming is a lightweight convention rather than a reason for disproportionate repository automation.

## 5. Implement one focused issue

Keep the branch scoped to its issue.

Inspect work before committing:

```console
git status
git diff
```

Run the appropriate verification.

Normal generator change:

```console
uv run python scripts/verify.py
```

Template change:

```console
uv run python scripts/verify.py
uv run python scripts/smoke_generated_project.py
```

Packaging-sensitive change:

```console
uv run python scripts/verify.py
uv run python scripts/smoke_generated_project.py
uv run python scripts/smoke_package.py
```

See [Testing](testing.md) for details.

## 6. Commit deliberately

Stage only intended files.

```console
git add <files>
git diff --cached
git status
```

Commit with a concise completed-change message:

```console
git commit -m "<message>"
```

Push:

```console
git push -u origin <branch-name>
```

## 7. Open the feature PR

The PR base must be the active release branch:

```text
release/v0.2.0
```

not `main`.

The PR should describe:

- what changed;
- what intentionally did not change;
- verification performed;
- relevant issue.

Wait for CI.

The aggregate check named:

```text
CI
```

must pass.

Review the Files Changed tab before merging.

Resolve review conversations.

Merge through the PR rather than pushing implementation commits directly to the protected release branch.

## 8. Update the local release branch

After merging:

```console
git switch release/v0.2.0
git pull --ff-only
git branch -d <merged-feature-branch>
```

Start subsequent work from this updated release branch so it includes already-integrated milestone changes.

## 9. Fix integration regressions through PRs

If combined release work exposes a regression:

1. create a new fix branch from the release branch;
2. make the correction;
3. run verification;
4. open a PR back into the release branch.

Do not patch the protected release branch directly.

## 10. Review milestone completion

Before preparing the final release:

- verify every milestone issue;
- close completed work;
- identify intentionally deferred work;
- move deferred issues out of the milestone if appropriate;
- confirm documentation reflects the implemented state.

Do not describe planned work as completed merely because it exists in a release milestone.

## 11. Set the release version

The generator version is stored in:

```toml
[project]
version = "..."
```

For the v0.2.0 release, update it deliberately to:

```toml
version = "0.2.0"
```

Make this change through the normal reviewed branch/PR process rather than editing the release branch directly.

After changing the version:

```console
uv lock
uv sync
uv run python scripts/verify.py
```

Review the resulting `pyproject.toml` and `uv.lock` changes.

## 12. Run integrated release verification

On the completed release branch, run all three layers:

```console
uv run python scripts/verify.py
uv run python scripts/smoke_generated_project.py
uv run python scripts/smoke_package.py
```

CI should also be green.

These checks establish:

```text
generator source works
+
fresh generated project works
+
built release wheel works
```

## 13. Review release artifacts

The package smoke test already builds fresh artifacts, but release preparation should still confirm the final `dist/` contents.

Expected:

```text
dist/
    pyproject_init-<version>-py3-none-any.whl
    pyproject_init-<version>.tar.gz
```

Ensure the artifacts correspond to the intended release version.

Do not publish stale artifacts from an earlier build.

## 14. Open the final release PR

Open:

```text
release/v0.2.0 → main
```

The PR should summarize:

- completed milestone work;
- Python support;
- local regression results;
- CI results;
- generated-project verification;
- built-package verification;
- known limitations;
- intentionally deferred work.

Do not merge until required reviews and the aggregate `CI` status pass.

## 15. Update local `main`

After the final PR merges:

```console
git switch main
git pull --ff-only
git status
git log -1 --oneline
```

Confirm:

- the working tree is clean;
- HEAD is the intended release commit;
- the version is correct;
- final CI passed.

## 16. Confirm the tag does not already exist

Check:

```console
git tag --list v0.2.0
```

Do not replace an existing release tag merely to simplify a failed release procedure.

## 17. Tag the verified release

Create an annotated tag:

```console
git tag -a v0.2.0 -m "Release v0.2.0"
```

Push it:

```console
git push origin v0.2.0
```

If `main` has advanced beyond the reviewed release commit, tag the explicitly verified commit rather than blindly tagging the newest HEAD.

## 18. Create the GitHub Release

Create a GitHub Release from:

```text
v0.2.0
```

Release notes should cover:

- important user-visible changes;
- development/toolchain changes worth knowing;
- supported Python versions;
- known limitations;
- relevant migration notes.

Attach or expose only artifacts known to correspond to the validated release.

A GitHub Release does not automatically imply PyPI publication unless publishing automation is explicitly configured.

## 19. PyPI publishing

Treat PyPI publication as a separate explicit release action.

If publishing is configured:

1. publish the validated build;
2. install the published package into a clean environment;
3. verify the CLI;
4. generate a project;
5. confirm the published distribution behaves like the locally verified artifact.

Do not assume a successful GitHub Release proves the package is available or valid on PyPI.

## 20. Close the milestone

After the release is confirmed:

- ensure completed issues are closed;
- account for deferred issues;
- close the milestone.

The milestone should not remain open indefinitely after all included work has been dispositioned.

## 21. Delete merged working branches

Remove merged feature/fix/docs branches when no longer needed.

Locally:

```console
git branch -d <branch>
```

Delete corresponding remote branches through the normal GitHub workflow where appropriate.

## 22. Delete the release branch

After the release is safely merged, tagged, and published:

```console
git switch main
git branch -d release/v0.2.0
```

Delete the remote release branch as well.

The release tag preserves the release point; the integration branch is no longer needed.

## 23. Clean local release artifacts

Remove disposable artifacts and temporary test output when no longer needed.

Examples include:

```text
dist/
temporary smoke-test projects
temporary virtual environments
```

Prune stale remote-tracking branches if useful:

```console
git fetch --prune
```

## 24. Start the next release from stable main

A future release begins with:

- current stable `main`;
- a new milestone;
- a new `release/vX.Y.Z` branch;
- newly scoped issues.

Do not reuse an old release branch.
