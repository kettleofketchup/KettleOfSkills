# Just Modules Reference

Modules provide namespaced recipe organization. Unlike `import`, `mod` creates separate namespaces called with `::` syntax.

## Basic Usage

```just
# justfile
mod docker    # Loads docker.just, recipes called as docker::*
mod go        # Loads go.just, recipes called as go::*
```

```just
# docker.just
build:
    docker build -t myapp .

push:
    docker push myapp
```

```bash
just docker::build
just docker::push
```

## Module Declaration

```just
mod name                    # Loads name.just
mod name 'path/to/name.just' # Custom path
mod? optional               # Optional (no error if missing)
```

## Import vs Module

| Feature | `import` | `mod` |
|---------|----------|-------|
| Syntax | `import 'file.just'` | `mod name` |
| Namespace | Merged into parent | Separate (`name::*`) |
| Calling | `just recipe` | `just name::recipe` |
| Use case | Shared settings, dev recipes | Categorized tooling |

## Variables in Modules

Modules have their own variable scope. Use `source_directory()` for relative paths:

```just
# automation/just/ansible.just
automation_root := source_directory() / ".."

[working-directory(automation_root)]
deploy:
    ansible-playbook ansible/playbooks/deploy.yml
```

`justfile_directory()` always returns the ROOT justfile's directory. Use `source_directory()` in modules.

## Working Directory (no-cd)

Module recipes run from the module's directory. Add `[no-cd]` for project-root commands:

```just
[no-cd]
status:
    git submodule status

[no-cd]
update:
    git submodule update --remote --merge
```

## Calling Between Modules

```just
# justfile
mod go
mod docker

release: (go::build "myapp")
    just docker::build
```

## Nested Modules

```just
# cloud.just
mod aws
mod gcp
```

```bash
just cloud::aws::deploy
just cloud::gcp::deploy
```

## Listing

```bash
just --list              # Shows all including module::recipe
just --list --unsorted   # Preserve definition order
```

See `modules-patterns.md` for directory structures and common patterns.
