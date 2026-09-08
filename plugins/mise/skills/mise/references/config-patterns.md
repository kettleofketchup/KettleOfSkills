# Mise Configuration Patterns

## Tool Version Syntax

```toml
[tools]
node = "22"                    # fuzzy — latest 22.x
node = "22.1.0"                # exact
python = "latest"              # latest stable
ruby = "lts"                   # latest LTS
go = "prefix:1.22"             # latest 1.22.x
rust = "ref:master"            # compile from git ref
erlang = "path:~/custom-otp"   # use local build
node = "sub-2:lts"             # 2 versions behind LTS
python = ['3.11', '3.12']      # multiple versions
```

## Tool Options (Object Syntax)

```toml
[tools]
node = { version = "22", postinstall = "corepack enable" }
python = { version = "3.12", depends = ["openssl"] }

# OS-specific
terraform = { version = "1.7", os = ["linux", "macos"] }
```

Options: `version`, `os`, `depends`, `install_env`, `postinstall`

## Package Manager Backends

```toml
[tools]
"npm:prettier" = "latest"
"npm:@anthropic-ai/claude-code" = "latest"
"cargo:starship" = "latest"
"pipx:black" = "latest"
"go:golang.org/x/tools/gopls" = "latest"
```

## Environment Variables

```toml
[env]
NODE_ENV = "development"
DATABASE_URL = "postgres://localhost/mydb"
_.path = ["./node_modules/.bin", "./bin"]  # prepend to PATH
_.file = ".env"                            # load dotenv
_.source = "./setup-env.sh"                # source shell script
```

Template support (tera syntax):
```toml
[env]
PROJECT_NAME = "{{config_root | basename}}"
LOG_DIR = "{{env.HOME}}/logs/{{config_root | basename}}"
```

## Settings

```toml
[settings]
auto_install = true                          # auto-install missing tools
jobs = 8                                     # parallel installs
experimental = true                          # enable experimental features
idiomatic_version_file_enable_tools = ["node", "python"]  # .node-version support
trusted_config_paths = ["~/work"]            # auto-trust directories
task.output = "prefix"                       # task output mode
offline = false                              # block HTTP requests
```

## Environment-Specific Config

Use `mise.<env>.toml` files, activated by `MISE_ENV`:

```bash
MISE_ENV=staging mise run deploy
```

```toml
# mise.staging.toml
[env]
API_URL = "https://staging.example.com"
```

## Idiomatic Version Files

Supported files (disabled by default):
- node: `.nvmrc`, `.node-version`, `package.json`
- python: `.python-version`, `.python-versions`
- ruby: `.ruby-version`, `Gemfile`
- go: `.go-version`
- java: `.java-version`, `.sdkmanrc`
- rust: `rust-toolchain.toml`

Enable: `mise settings add idiomatic_version_file_enable_tools node python`

## Version Aliases

```toml
[tool_alias.node.versions]
stable = "22"
legacy = "18"
```

Usage: `mise use node@stable`

## Shell Aliases

```toml
[shell_alias]
ll = "ls -la"
gs = "git status"
```

## Minimum Version Requirement

```toml
min_version = "2024.11.1"               # hard fail
min_version = { soft = "2024.11.1" }    # warning only
```

## JSON Schema for IDE Support

Add to VSCode `settings.json`:
```json
{
  "json.schemas": [
    { "url": "https://mise.jdx.dev/schema/mise.json", "fileMatch": ["mise.toml", "mise.*.toml"] }
  ]
}
```

## Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `MISE_ENV` | Activate environment-specific config |
| `MISE_TRUSTED_CONFIG_PATHS` | Auto-trust paths (`:` separated) |
| `MISE_NODE_VERSION` | Override tool version |
| `MISE_LOG_LEVEL` | trace/debug/info/warn/error |
| `MISE_DATA_DIR` | Tool install location |
| `MISE_CACHE_DIR` | Cache storage |
