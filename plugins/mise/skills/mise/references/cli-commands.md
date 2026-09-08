# Mise CLI Reference

## Project Setup

```bash
mise use node@22 python@3.12       # install + add to mise.toml
mise use --pin node@22.1.0         # exact version
mise use --global node@22          # global default
mise use npm:prettier cargo:starship  # package manager tools
mise install                       # install all tools from config
mise trust                         # trust config (required for env/hooks)
mise trust --all                   # trust all parent configs
```

## Tool Management

```bash
mise ls                            # list installed tools
mise ls node                       # specific tool
mise outdated                      # check for updates
mise upgrade                       # upgrade all tools
mise upgrade node                  # specific tool
mise upgrade --bump                # update mise.toml version too
mise ls-remote node                # available versions
mise ls-remote node 22             # filter by prefix
mise latest node                   # latest version
mise search postgres               # find tools
mise which node                    # binary path
mise where node                    # install path
mise uninstall node@20             # remove version
mise unuse node                    # remove from config
mise prune                         # remove unused versions
```

## Environment & Execution

```bash
mise set NODE_ENV=production       # set env var in mise.toml
mise unset NODE_ENV                # remove env var
mise env                           # show resolved environment
mise env --json                    # JSON output
mise exec node@22 -- node -v       # one-off execution
mise x node@22 -- npx vite         # short alias
MISE_ENV=staging mise run deploy   # environment-specific
MISE_NODE_VERSION=20 mise exec -- node -v  # override version
```

## Tasks

```bash
mise tasks                         # list tasks
mise run build                     # run task
mise run test -- --verbose         # pass args
mise run build test                # run multiple
mise watch build                   # re-run on file changes
mise watch -t test -g "src/**"     # watch glob, run task
mise tasks info build              # task details
```

## Trust

Mise requires explicit trust before executing potentially dangerous config
directives: `[env]` (_.file, _.source, templates), `[hooks]`, and `[tasks]`
with shell commands. Tool versions don't require trust.

```bash
mise trust                         # trust mise.toml in current directory
mise trust mise.local.toml         # trust a specific file
mise trust --all                   # trust all config files in parent dirs
mise trust --untrust               # revoke trust for current config
mise trust --untrust mise.toml     # revoke trust for specific file
```

### Auto-Trust Directories

Skip the `mise trust` prompt for known-safe paths:

```toml
# ~/.config/mise/config.toml
[settings]
trusted_config_paths = ["~/work", "~/projects"]
```

Or via environment variable:
```bash
export MISE_TRUSTED_CONFIG_PATHS="$HOME/work:$HOME/projects"
```

### What Happens Without Trust

- `[tools]` — installs and activates normally (no trust needed)
- `[env]` with `_.file`/`_.source` — **ignored** until trusted
- `[env]` templates (tera) — **ignored** until trusted
- `[hooks]` — **ignored** until trusted
- Mise shows a warning prompting you to run `mise trust`

## Configuration & Diagnostics

```bash
mise config ls                     # show active config files
mise edit                          # TUI config editor
mise fmt                           # format config
mise lock                          # create lockfile
mise completion zsh > _mise        # shell completions
mise doctor                        # health check
mise settings                      # show all settings
mise settings set jobs 4           # change setting
mise cache clear                   # clear cache
MISE_LOG_LEVEL=debug mise install  # debug output
```

## CI/CD Patterns

```bash
# GitHub Actions
- uses: jdx/mise-action@v2

# Generic CI (no shell activation needed)
mise install
mise exec -- npm test

# Or use shims
mise reshim
export PATH="$HOME/.local/share/mise/shims:$PATH"
```

## Common Workflows

```bash
# New project
mkdir myproject && cd myproject
mise use node@22 python@3.12
mise set NODE_ENV=development
mise trust

# Clone existing project
git clone repo && cd repo
mise install && mise trust

# Check what's active
mise doctor && mise config ls && mise ls
```
