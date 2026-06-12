# Templating, Files & Tasks

## Rendering Rules

- A file is rendered through Jinja2 only if its name ends with the templates suffix (default
  `.jinja`). The suffix is stripped from the output name. Non-suffixed files are copied verbatim.
- File and directory **names** are always templated: `{{ project_name }}/`, `{{ module }}.py.jinja`.
- A path segment that renders to an **empty string** causes that file/dir to be skipped entirely —
  a clean way to make whole paths conditional without `_exclude`.

```
template/
├── {{ project_name }}/
│   ├── __init__.py.jinja
│   └── {% if use_cli %}cli.py.jinja{% endif %}   # skipped when use_cli is false
├── README.md.jinja
└── {{ _copier_conf.answers_file }}.jinja
```

## Jinja Syntax

Copier uses **standard Jinja delimiters**: `{{ expr }}`, `{% statement %}`, `{# comment #}`. If a
target language clashes (e.g. templating Jinja/Go templates), change them with `_envops`:

```yaml
_envops:
  block_start_string: "[%"
  block_end_string: "%]"
  variable_start_string: "[["
  variable_end_string: "]]"
```

Tune whitespace handling (also via `_envops`):

```yaml
_envops:
  trim_blocks: true
  lstrip_blocks: true
  keep_trailing_newline: true
```

## Context Variables

Available in every templated file, name, and `copier.yml` expression:

| Variable | Meaning |
|----------|---------|
| `<question>` | Each answered question by its name |
| `_copier_answers` | Sanitized answers dict — dump into the answers file |
| `_copier_conf` | Render config: `answers_file`, `src_path`, `dst_path`, `vcs_ref`, `os`, `sep` |
| `_copier_python` | Absolute path to the Python running Copier (use in `_tasks`) |
| `_copier_operation` | `"copy"` or `"update"` — branch behavior in tasks/exclude |
| `_copier_phase` | `"prompt"`, `"render"`, `"tasks"`, or `"migrate"` |
| `_folder_name` | Name of the destination project root folder |
| `_external_data` | Data loaded via the `_external_data` setting |

## Excluding Files

```yaml
_exclude:
  - "*.tmp"
  - "__pycache__"
  - ".git"
  - "copier.yml"          # exclude meta files if not using _subdirectory
  - "!keep-me.tmp"         # ! re-includes a previously excluded path
  # exclude conditionally via Jinja:
  - "{% if not use_docker %}Dockerfile{% endif %}"
```

`_skip_if_exists` is gentler — listed paths are written on first copy but never overwritten on update
(good for `.env`, secrets, user-edited config).

## Post-Generation Tasks

`_tasks` run after files are written, in order. They require `--trust` (tasks execute arbitrary
shell). Each entry is a string (shell), a list (argv, no shell), or a mapping with `when`.

```yaml
_tasks:
  - "git init -q"
  - ["{{ _copier_python }}", "scripts/bootstrap.py"]   # argv form, no shell
  - command: "pre-commit install"
    when: "{{ use_precommit }}"
  - command: "echo 'fresh project'"
    when: "{{ _copier_operation == 'copy' }}"          # only on first copy, not updates
```

Tasks run from the destination directory. `_copier_python` guarantees the same interpreter Copier
uses. Use `_copier_operation`/`_copier_phase` to distinguish copy vs update runs.

## External Data

```yaml
_external_data:
  parent: "{{ _copier_conf.dst_path }}/.copier-answers.parent.yml"
```

Then reference `{{ _external_data.parent.some_key }}` — useful for layered/child templates that read
a parent template's answers.
