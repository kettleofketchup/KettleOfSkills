# Updating Projects & Migrations

## How `copier update` Works

`copier update` keeps a generated project in sync with its template via a smart three-way merge.

Prerequisites (all required):
1. The project has a valid `.copier-answers.yml` (created by the original `copier copy`).
2. The template repo is Git-versioned and **tagged** (PEP 440 versions, e.g. `v1.2.0`).
3. The project is itself a Git repo with a **clean** working tree (`git status` shows nothing).

Algorithm:
1. Regenerate the project from the **old** template version using saved answers.
2. Diff that against the current on-disk project → captures the user's local changes.
3. Run **pre-migrations**.
4. Regenerate from the **new** template version (re-prompting for new/changed questions).
5. Re-apply the user's diff on top (three-way merge).
6. Run **post-migrations**.

```bash
copier update                       # update to latest tag
copier update -r v2.0.0             # update to a specific version
copier update --vcs-ref=HEAD        # update to latest commit (untagged)
copier update --defaults            # reuse all prior answers, no prompts
copier update --defaults -d env=prod  # change one answer, keep the rest
copier update -A                    # --skip-answered: don't re-ask answered questions
```

## Conflicts

When the merge can't auto-resolve, Copier marks conflicts:

- `--conflict inline` (default): Git-style `<<<<<<<`/`>>>>>>>` markers in the file.
- `--conflict rej`: writes `<file>.rej` reject files alongside the originals.

Resolve manually, then commit. Add a CI/pre-commit guard that fails on leftover markers or `.rej`:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: forbidden-files
      name: no copier conflict leftovers
      entry: bash -c '! git ls-files | grep -E "\.rej$"'
      language: system
```

## Recovery & Edge Cases

- **Deleted template files**: files you removed in the project stay removed on update. Run
  `copier recopy` to bring them back.
- **Broken update** (external dep failed, weird state): `copier recopy` regenerates fresh from the
  current template using saved answers, discarding the smart-diff history.
- **Abort an update** mid-way:
  ```bash
  git reset && git checkout . && git clean -di
  ```

## Migrations (`_migrations`)

Run version-gated commands during `update` to fix up projects when the template changes shape
(rename files, move config, etc.). A migration runs when the **old** project version is below its
`version` and the **new** version is at/above it.

```yaml
_migrations:
  # simple: run once when crossing this version (after, by default)
  - "rm -f legacy.cfg"

  # full form
  - version: v2.0.0
    command: "python migrations/v2.py"
    when: "{{ _stage == 'before' }}"        # before vs after the file update
    working_directory: "."
```

Migration context variables (also exported as env vars):

| Variable | Env | Meaning |
|----------|-----|---------|
| `_stage` | `$STAGE` | `before` or `after` the template files are applied |
| `_version_from` | `$VERSION_FROM` | project's previous template version |
| `_version_to` | `$VERSION_TO` | template version being applied |
| `_version_pep440_from` / `_to` | — | PEP 440-normalized forms |
| `_version_current` | `$VERSION_CURRENT` | the migration's own `version` value |

Migrations need `--trust` (they run shell). Test them by tagging the template and running
`copier update` against a sample project across versions.

## Checking for Updates

```bash
copier check-update                 # human-readable; exit 0 = up to date, 2 = update available
copier check-update --quiet         # CI: rely on exit code
copier check-update --prereleases   # include pre-release tags
```
