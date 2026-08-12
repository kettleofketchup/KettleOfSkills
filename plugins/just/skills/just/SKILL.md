---
name: just
description: Bootstrap repos with just command runner. Use when writing justfiles, automating tasks, or organizing recipes into groups and modules. Provides ./dev bootstrap, modular just/ layout, fzf-tab groups.
---

# Just Command Runner

Task automation using [just](https://github.com/casey/just) with a standardized project structure.

## Project Structure

```
project/
├── dev                 # Bootstrap script (installs just, runs `just dev`)
├── justfile            # Root: settings, imports, and modules
└── just/
    ├── dev.just        # Development recipes (imported, no namespace)
    ├── go.just         # Go module (go::build, go::test)
    └── docker.just     # Docker module (docker::build, docker::push)
```

## Bootstrapping a New Repo

1. Copy `assets/dev` to project root, make executable: `chmod +x dev`
2. Copy `assets/just/` directory to project root
3. Create root `justfile` with imports and modules
4. Edit `just/dev.just` with project-specific setup commands

## Root Justfile Pattern

**Put everything in root justfile** for tab completion to work:

```just
set quiet
set dotenv-load

import 'just/dev.just'           # Merged into root namespace

mod go 'just/go.just'           # go::build, go::test
mod docker 'just/docker.just'   # docker::build, docker::push

default:
    just --list
```

## Import vs Module

| Feature | `import 'file.just'` | `mod name 'name.just'` |
|---------|----------------------|------------------------|
| Namespace | Merged into parent | Separate (`name::*`) |
| Calling | `just recipe` | `just name::recipe` |
| Best for | dev.just only | All other modules |

**Rule:** Use `import` only for `dev.just`. Use `mod` for everything else.

## Module Working Directory

Module recipes run from the module's directory. Use `[no-cd]` for project-root commands:

```just
[no-cd]
status:
    git submodule status
```

Or use `{{invocation_directory()}}` for specific paths. See `references/modules.md`.

## Recipe Groups

Use `[group]` for cross-cutting organization:

```just
[group('dev')]
dev: setup
    ./run-dev.sh

[group('dev')]
[group('ci')]
test:
    cargo test
```

Standard groups: `dev`, `build`, `test`, `ci`, `deploy`, `maintenance`.
See `references/groups.md` for fzf-tab integration.

## Shell Completions Setup

```bash
# Check if completions exist
type _just &>/dev/null

# Generate if missing
JUST_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/just"
mkdir -p "$JUST_CONFIG_DIR"
just --completions zsh > "$JUST_CONFIG_DIR/completions.zsh"
```

Add to `~/.zshrc`:
```bash
if command -v just &>/dev/null; then
    [[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/just/completions.zsh" ]] && \
        source "${XDG_CONFIG_HOME:-$HOME/.config}/just/completions.zsh"
fi
```

See `references/completions.md` for bash setup and verification.

## References

| File | Contents |
|------|----------|
| `groups.md` | Groups, fzf-tab integration, grouping strategy |
| `modules.md` | Module system, namespacing, patterns |
| `settings.md` | All justfile settings |
| `recipes.md` | Recipe syntax, parameters, dependencies |
| `attributes.md` | Recipe attributes (`[group]`, `[confirm]`, etc.) |
| `functions.md` | Built-in functions (paths, strings, OS) |
| `functions-advanced.md` | Hashing, datetime, shell execution |
| `syntax.md` | Variables, strings, conditionals, imports |
| `completions.md` | Shell completions setup (zsh/bash) |
