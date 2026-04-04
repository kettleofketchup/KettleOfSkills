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

[test]
    unit
    integration
```

## Groups vs Modules

| Feature | Groups `[group]` | Modules `mod name` |
|---------|------------------|-------------------|
| Purpose | Organizational tags | Namespace isolation |
| Calling | `just recipe` | `just name::recipe` |
| Listing | Grouped in `--list` | Collapsed by default |
| Recipe can belong to | Multiple groups | One module only |
| File structure | Same file or any | Separate `.just` file |

**When to use groups:**
- Cross-cutting concerns (ci, dev, deploy)
- Recipes from different modules that relate
- Organizing a flat justfile

**When to use modules:**
- Separate domains (go, docker, lua)
- Recipes that share variables/settings
- Large justfiles needing file separation

## Intelligent Grouping Strategy

### Recommended Groups

```just
# Development workflow
[group('dev')]
dev: setup
[group('dev')]
watch:

# Build/compile tasks
[group('build')]
build:
[group('build')]
build-release:

# Testing
[group('test')]
test:
[group('test')]
test-integration:

# CI/CD (often overlaps with others)
[group('ci')]
[group('build')]
build-release:
[group('ci')]
[group('test')]
test-all:

# Deployment
[group('deploy')]
deploy-staging:
[group('deploy')]
deploy-prod:

# Maintenance/cleanup
[group('maintenance')]
clean:
[group('maintenance')]
update-deps:
```

### Module + Group Combination

Use modules for namespacing, groups for cross-cutting organization:

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

Now `just --list` shows:
```
[build]
    go::build
    go::build-ci

[ci]
    go::build-ci
    docker::push

[test]
    go::test
```

## Shell Completion Grouping

### fzf-tab Integration

Groups appear as completion groups. Add zstyle for preview:

```zsh
# In ~/.config/zsh/styles.zsh
zstyle ':fzf-tab:complete:just:*' fzf-preview \
    'just --show $word 2>/dev/null | bat --color=always -l just --style=plain'
```

### _just Completion Enhancement

The completion can group recipes by:
1. Built-in groups (from `[group]` attribute via `just --dump --dump-format json`)
2. Module prefix (demo::, db::) from namepath
3. Variables vs recipes (default)

Query groups from JSON:
```bash
just --dump --dump-format json | jq -r '
  .recipes | to_entries[] |
  "\(.value.namepath)\t\(.value.attributes.group // ["ungrouped"] | join(","))"
'
```
