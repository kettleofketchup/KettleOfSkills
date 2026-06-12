# copier.yml Reference

`copier.yml` (or `copier.yaml`) lives at the template repo root. Top-level keys are either
**questions** (any non-underscore key) or **settings** (underscore-prefixed keys).

## Question Syntax

```yaml
question_name:
  type: str            # str | int | float | bool | json | yaml (default: yaml)
  help: "Shown to the user above the prompt"
  default: "{{ other_answer }}"   # static value or Jinja expression
  placeholder: "hint shown when empty"
  multiline: false     # allow multi-line text input
  secret: true         # hide input; NOT written to the answers file
  when: "{{ cond }}"    # skip question (and use default) when falsey
  validator: "{% if not value %}Required{% endif %}"  # non-empty output = error msg
```

- `type` controls casting. `json`/`yaml` parse structured input; `bool` renders a yes/no toggle.
- `default` is evaluated as Jinja with access to all previously-answered variables.
- A question with `when` evaluating false is not asked; its `default` is recorded silently.

## Choices

```yaml
# 1. Simple list — value == label
favorite:
  type: str
  choices: [red, green, blue]

# 2. Mapping — show key, store value
license:
  type: str
  choices:
    MIT License: mit
    Apache 2.0: apache-2.0
  default: mit

# 3. Rich form — per-choice value + validator (gate options)
language:
  type: str
  choices:
    Python:
      value: python
    Rust:
      value: rust
      validator: "{% if not rust_ok %}Rust toolchain missing{% endif %}"

# 4. Dynamic / conditional choices (templated YAML)
manager:
  type: str
  choices: |
    {%- if language == "python" %}
    - poetry
    - uv
    {%- endif %}

# 5. Multiselect → returns a list
frameworks:
  type: str
  multiselect: true
  choices: [django, fastapi, flask]
  default: [django]
```

## Conditional Questions

```yaml
project_license:
  type: str
  choices: [MIT, Proprietary, Public Domain]

copyright_holder:
  type: str
  when: "{{ project_license != 'Public Domain' }}"
  default: "{{ project_author }}"
```

## Settings Keys (not questions)

| Key | Description | Example |
|-----|-------------|---------|
| `_subdirectory` | Render only this subdir of the repo (keeps `copier.yml`/CI out of output) | `_subdirectory: template` |
| `_templates_suffix` | Suffix marking files for Jinja rendering | `_templates_suffix: .jinja` |
| `_envops` | Jinja `Environment` options | `_envops: {keep_trailing_newline: true}` |
| `_exclude` | Glob patterns to skip (supports `!` negation) | see `templating.md` |
| `_skip_if_exists` | Don't overwrite these if they already exist | `_skip_if_exists: [.env]` |
| `_tasks` | Shell/cmd list run after copy/update (needs `--trust`) | see `templating.md` |
| `_migrations` | Version-gated upgrade commands run during `update` | see `update-migrations.md` |
| `_jinja_extensions` | Extra Jinja2 extensions to load (needs `--trust`) | `[jinja2_time.TimeExtension]` |
| `_secret_questions` | Mark question vars as secret (alt to per-question `secret`) | `_secret_questions: [token]` |
| `_preserve_symlinks` | Copy symlinks as symlinks, not their targets | `_preserve_symlinks: true` |
| `_answers_file` | Path of the recorded answers file | `_answers_file: .copier-answers.yml` |
| `_external_data` | Load external YAML/JSON into render context | `_external_data: {parent: .parent.yml}` |
| `_message_before_copy` / `_after_copy` | Banner shown around `copier copy` | `"Welcome to {{ project_name }}"` |
| `_message_before_update` / `_after_update` | Banner shown around `copier update` | `"Resolve any conflicts."` |
| `_min_copier_version` | Minimum Copier version (PEP 440) | `_min_copier_version: "9.1.0"` |

## YAML / Jinja Rules

- Only **string values** are templated — keys are never templated.
- Variables must already be declared above where they're used (top-to-bottom evaluation).
- Wrap Jinja in quotes when the result could confuse the YAML parser.
- `{{ UNSET }}` as a default forces the user to answer even a `when`-skipped question if re-enabled.
