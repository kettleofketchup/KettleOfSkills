# CLI & Python API

## Commands

| Command | Purpose |
|---------|---------|
| `copier copy <src> <dst>` | Generate a new project from a template |
| `copier update [dst]` | Update an existing project to a newer template version |
| `copier recopy [dst]` | Re-apply the template fresh, keeping answers (no smart diff) |
| `copier check-update [dst]` | Report if a newer template version is available (exit 0/2) |

## Common Flags

| Flag | Applies to | Description |
|------|-----------|-------------|
| `-r, --vcs-ref <ref>` | copy/update | Git tag, branch, or commit to render from |
| `-d, --data key=value` | all | Provide an answer non-interactively (repeatable) |
| `--data-file <yaml>` | all | Load answers from a YAML/JSON file |
| `--defaults` | all | Accept all default answers; only prompt where no default exists |
| `-f, --overwrite` | copy/recopy | Overwrite existing files without asking (implied by `--defaults` in some flows) |
| `--pretend` | all | Dry run — show what would happen, write nothing |
| `--exclude <pattern>` | copy/update | Extra exclude pattern (adds to `_exclude`) |
| `--skip <path>` | copy/update | Skip a specific output file if it exists |
| `-A, --skip-answered` | update | Don't re-prompt questions already answered |
| `--conflict inline\|rej` | update | Conflict style (default `inline`) |
| `--trust` | all | Allow `_tasks` and unsafe `_jinja_extensions` to run |
| `--vcs-ref=:current:` | update | Update answers only, not template version |
| `-q, --quiet` | all | Suppress output |

Pass `--trust` only for templates you control or audited — tasks run arbitrary shell.

## Source URLs

```bash
copier copy gh:org/template ./myproj          # GitHub shortcut
copier copy gl:org/template ./myproj          # GitLab shortcut
copier copy git+https://example.com/t.git .   # any Git URL
copier copy ./local/template ./myproj         # local path (no version tracking unless it's a git repo)
copier copy -r v1.4.0 gh:org/template ./out   # pin a version
```

## Non-Interactive / Scripted

```bash
copier copy --defaults --trust \
  -d project_name=acme \
  -d use_ci=true \
  gh:org/template ./acme
```

## Python API

```python
from copier import run_copy, run_update, run_recopy

# Generate
run_copy(
    src_path="gh:org/template",
    dst_path="./acme",
    data={"project_name": "acme", "use_ci": True},
    defaults=True,        # don't prompt for anything with a default
    unsafe=True,          # equivalent to --trust (run _tasks / extensions)
    vcs_ref="v1.4.0",     # pin version
    quiet=True,
)

# Update an existing project
run_update(
    dst_path="./acme",
    defaults=True,
    unsafe=True,
    conflict="inline",
    skip_answered=True,
)

# Re-apply fresh, keep answers
run_recopy(dst_path="./acme", defaults=True, unsafe=True)
```

Key kwargs mirror the CLI: `data`, `defaults`, `overwrite`, `pretend`, `exclude`, `skip_if_exists`,
`vcs_ref`, `unsafe` (=`--trust`), `quiet`. `run_*` raise on error; wrap in try/except in pipelines.

## CI Patterns

**Generate in CI** (e.g. scaffold then test):
```yaml
- run: pipx install copier
- run: copier copy --defaults --trust -d name=ci-test gh:org/template ./out
```

**Auto-update bot** (open a PR when the template advances):
```bash
copier check-update --quiet || {           # exit 2 → update available
  copier update --defaults --skip-answered --conflict rej --trust
  # then: detect *.rej, create branch + PR
}
```

**Guard against unresolved conflicts** in pre-commit / CI:
```bash
git ls-files | grep -E '\.rej$' && { echo "unresolved copier conflicts"; exit 1; } || true
grep -RIl '^<<<<<<< ' . && { echo "merge markers present"; exit 1; } || true
```
