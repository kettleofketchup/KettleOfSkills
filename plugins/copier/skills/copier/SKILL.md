---
name: copier
description: Copier templating — author copier.yml templates (questions, Jinja, _tasks, migrations), scaffold via `copier copy`, sync via `copier update`. Use for copier.yml, .copier-answers.yml, or .jinja.
---

# Copier

Copier renders project templates from Git repos and keeps generated projects in sync as the
template evolves. Templates are plain directories: a `copier.yml` config plus source files, where
`.jinja`-suffixed files (and `{{ var }}` in names) are rendered through Jinja2.

## Four Core Workflows

1. **Author** a template → `copier.yml` questions + a template tree → `references/copier-yml.md`, `references/templating.md`
2. **Generate** a project → `copier copy <src> <dst>` → `references/cli-api.md`
3. **Update** a project → `copier update` (three-way merge) → `references/update-migrations.md`
4. **Automate** in CI / Python → `copier.run_copy/run_update`, `--trust`, `--defaults` → `references/cli-api.md`

## Install

```bash
pipx install copier        # isolated CLI (recommended)
uv tool install copier     # or via uv
copier --version
```

## CLI Cheatsheet

| Command | Purpose |
|---------|---------|
| `copier copy <src> <dst>` | Scaffold a new project from a template |
| `copier update` | Sync project to latest template version (run inside project) |
| `copier recopy` | Re-apply template fresh, keeping answers (no smart diff) |
| `copier check-update` | Report whether a newer template version exists |

Common flags: `-r/--vcs-ref <tag|branch|HEAD>`, `-d/--data key=value`, `--defaults`,
`--pretend` (dry run), `--overwrite`/`-f`, `--exclude <pat>`, `--skip <q>`, `--trust`,
`--conflict inline|rej`, `-A/--skip-answered`. Full list: `references/cli-api.md`.

Template sources: local path, `gh:ns/repo`, `gl:ns/repo`, `git+https://…`, `git@…`, `*.git`.

## Minimal Template

```
my-template/
├── copier.yml
├── {{ project_name }}/            # folder name is templated
│   └── README.md.jinja            # rendered (suffix stripped)
└── {{ _copier_conf.answers_file }}.jinja   # records answers for updates
```

```yaml
# copier.yml
project_name:
  type: str
  help: Your project name
use_ci:
  type: bool
  default: true

_subdirectory: "."          # render from repo root (use a subdir to keep meta files out)
_min_copier_version: "9.0.0"
```

```jinja
{# {{ _copier_conf.answers_file }}.jinja — NEVER hand-edit the generated file #}
# Changes here will be overwritten by Copier; manual edits break `copier update`.
{{ _copier_answers|to_nice_yaml -}}
```

The answers file (`.copier-answers.yml`, committed) is what makes `copier update` work — it stores
`_src_path`, `_commit`, and every saved answer. Without it, updates are impossible.

## Key Conventions

- **Templated files**: end in `.jinja` (configurable via `_templates_suffix`). Names support `{{ var }}`.
- **Questions** are top-level keys in `copier.yml`; underscore-prefixed keys (`_tasks`, `_exclude`,
  `_migrations`, `_subdirectory`, …) are *settings*, not questions. See `references/copier-yml.md`.
- **Versioning**: tag the template repo (`git tag v1.0.0`). `copier update` picks the latest PEP 440 tag.
- **Safety**: templates with `_tasks` or extra `_jinja_extensions` need `--trust` to run.

## Gotchas

- `copier update` requires a **clean git working tree** in both template (tagged) and project.
- Never edit `.copier-answers.yml` by hand — it breaks the diff algorithm.
- Quote Jinja in YAML values (`default: "{{ x }}"`) so the YAML parser doesn't choke.
- Question order matters: a `default`/`when` can only reference questions declared *above* it.
- Add a pre-commit check to reject leftover conflict markers / `.rej` files after updates.

## References

- `references/copier-yml.md` — question types, choices, `when`, validators, all `_settings` keys
- `references/templating.md` — Jinja rendering, file/folder naming, `_exclude`, `_tasks`, context vars
- `references/update-migrations.md` — update algorithm, conflicts, `_migrations`, recopy
- `references/cli-api.md` — full CLI flag reference, Python API, CI patterns
