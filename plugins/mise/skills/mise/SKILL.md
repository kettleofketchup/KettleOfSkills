---
name: mise
description: Set up mise.toml in project directories with dev tool versions, env vars, tasks, and hooks for reproducible dev environments.
---

# Mise Project Setup

Mise manages dev tool versions, environment variables, tasks, and hooks per directory via `mise.toml`.

## Quick Setup Flow

1. Initialize: `mise use node@22 python@3.12` (creates `mise.toml` + installs tools)
2. Add env vars: `mise set DATABASE_URL=postgres://localhost/mydb`
3. Define tasks in `mise.toml` under `[tasks]`
4. Trust config: `mise trust` (required for env directives and hooks)
5. Verify: `mise doctor`

## Shell Activation

Required for `mise use` workflow to function — tools won't appear in PATH without it.

```bash
# zsh
eval "$(mise activate zsh)"
# bash
eval "$(mise activate bash)"
# fish
mise activate fish | source
```

## Config File Precedence (closest wins)

```
mise.local.toml     # local overrides, gitignored
mise.toml           # primary project config, committed
mise.<env>.toml     # environment-specific (staging, production)
~/.config/mise/config.toml  # global defaults
/etc/mise/config.toml       # system-wide
```

## Essential Commands

| Command | Purpose |
|---------|---------|
| `mise use <tool>@<ver>` | Install tool + add to mise.toml |
| `mise use --global <tool>` | Set global default |
| `mise install` | Install all tools from config |
| `mise set KEY=VAL` | Add env var to mise.toml |
| `mise run <task>` | Run a defined task |
| `mise exec <tool>@<ver> -- cmd` | One-off execution |
| `mise trust` | Trust current config file |
| `mise doctor` | Diagnose issues |
| `mise ls` | List installed tools |
| `mise outdated` | Check for updates |
| `mise upgrade` | Upgrade tools |
| `mise config ls` | Show active config files |

## mise.toml Minimal Example

```toml
[tools]
node = "22"
python = "3.12"

[env]
NODE_ENV = "development"

[tasks]
dev = "npm run dev"
test = "npm test"
```

## Key Patterns

- **Version pinning**: `mise use --pin node@22.1.0` for exact versions
- **Lockfiles**: `mise lock` creates `mise.lock` for reproducible installs
- **Multiple versions**: `python = ['3.11', '3.12']`
- **Package managers**: `mise use npm:prettier cargo:starship`
- **Idiomatic files**: Enable `.node-version`, `.python-version` support via settings

## References

Detailed configuration patterns, task/hook definitions, and CLI usage:

- `references/config-patterns.md` — tools, env vars, settings, backends, idiomatic version files
- `references/tasks-hooks.md` — task definitions, dependencies, arguments, hooks, file watchers
- `references/cli-commands.md` — full CLI reference with flags and usage examples

## Gotchas

- `mise install` alone won't activate tools — use `mise use` instead
- Config files must be trusted before env/hooks execute: `mise trust`
- Add `mise.local.toml` to `.gitignore` for local overrides
- Commit `mise.toml` (and optionally `mise.lock`) to version control
