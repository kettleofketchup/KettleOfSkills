# Just Module Directory Patterns

## Directory Structures

### Flat Structure

```
project/
├── justfile         # mod docker, mod go
├── docker.just
├── go.just
└── release.just
```

### Nested Structure (Recommended)

```
project/
├── justfile         # import 'just/justfile'
└── just/
    ├── justfile     # mod docker, mod go, import 'dev.just'
    ├── dev.just     # Imported (no namespace)
    ├── docker.just  # Module (docker::*)
    ├── go.just      # Module (go::*)
    └── release.just # Module (release::*)
```

## Common Patterns

### Top-level Aliases

```just
# justfile
mod go
mod docker

# Convenience aliases for common commands
build:
    just go::build myapp

test:
    just go::test myapp

lint:
    just go::lint
```

### Module with Variables

```just
# go.just - recipes called as go::build, go::test
VERSION := `git describe --tags --always 2>/dev/null || echo "dev"`
BIN_DIR := env_var("PWD") / "bin"

[group('go')]
build tool:
    @mkdir -p {{BIN_DIR}}
    go build -o {{BIN_DIR}}/{{tool}} .

[group('go')]
test:
    go test -race -cover ./...

[group('go')]
lint:
    golangci-lint run
```

### Multi-Platform Release Module

```just
# release.just
DIST := env_var("PWD") / "dist"

all: linux darwin windows

linux:
    GOOS=linux GOARCH=amd64 go build -o {{DIST}}/app-linux .

darwin:
    GOOS=darwin GOARCH=arm64 go build -o {{DIST}}/app-darwin .

windows:
    GOOS=windows GOARCH=amd64 go build -o {{DIST}}/app.exe .
```

```bash
just release::all
just release::linux
```

### Tool Module (lua example)

```just
# just/lua.just - Called as lua::install, lua::check, etc.
lua_version := env("LUA_VERSION", "5.4.6")
prefix := env("PREFIX", "/usr/local")

[group('lua')]
default: check install
    echo "Lua environment setup complete"

[group('lua')]
check:
    command -v lua >/dev/null 2>&1 || echo "lua not found"

[group('lua')]
install: install-deps install-lua install-luarocks
    echo "Lua installation complete"

[group('lua')]
clean:
    rm -rf /tmp/lua-build/*
```

### Dev Module (Imported, No Namespace)

```just
# just/dev.just - Imported (no namespace) for common recipes

# Bootstrap the development environment
dev:
    echo "Installing dependencies..."
    echo "Done!"

# Clean build artifacts
clean:
    rm -rf dist/ build/ target/
```
