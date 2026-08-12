# Just Recipe Groups

Organize recipes into logical groups for better discoverability.

## Group Attribute Syntax

```just
[group('build')]
compile:
    cargo build

# Multiple groups
[group('build')]
[group('ci')]
compile-release:
    cargo build --release

# Shorthand syntax
[group: 'test']
unit:
    cargo test
```

## Listing Groups

```bash
just --groups              # List all group names
just --list                # Show recipes organized by group
just --list --unsorted     # Show in justfile order within groups
```

Example `just --list` output:
```
[build]
    compile
    compile-release

[ci]
    compile-release
    lint
    test-all
```

## Groups vs Modules

| Feature | Groups `[group]` | Modules `mod name` |
|---------|------------------|-------------------|
| Purpose | Organizational tags | Namespace isolation |
| Calling | `just recipe` | `just name::recipe` |
| Recipe can belong to | Multiple groups | One module only |

- Use **groups** for cross-cutting concerns (ci, dev, deploy)
- Use **modules** for separate domains (go, docker, lua)

## Recommended Groups

```just
[group('dev')]    # Local development (watch, run, setup)
[group('build')]  # Compilation, bundling
[group('test')]   # Testing (unit, integration, e2e)
[group('ci')]     # CI pipeline tasks (often overlaps)
[group('deploy')] # Deployment to environments
[group('maintenance')] # Cleanup, dependency updates
```

## Module + Group Combination

```just
# just/go.just
[group('build')]
build:
    go build ./...

[group('test')]
test:
    go test ./...

[group('ci')]
[group('build')]
build-ci:
    go build -trimpath ./...
```

`just --list` shows:
```
[build]
    go::build
    go::build-ci

[ci]
    go::build-ci

[test]
    go::test
```

## fzf-tab Integration

Groups appear as completion groups. Add zstyle for preview:

```zsh
# In ~/.config/zsh/styles.zsh
zstyle ':fzf-tab:complete:just:*' fzf-preview \
    'just --show $word 2>/dev/null | bat --color=always -l just --style=plain'
```

### Query Groups from JSON

```bash
just --dump --dump-format json | jq -r '
  .recipes | to_entries[] |
  "\(.value.namepath)\t\(.value.attributes.group // ["ungrouped"] | join(","))"
'
```
