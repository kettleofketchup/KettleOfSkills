---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_urls:
  - https://zensical.org/docs/usage/cli/
  - https://zensical.org/docs/usage/preview/
  - https://zensical.org/docs/usage/build/
---

# Development Workflow

## CLI

```
zensical COMMAND [OPTIONS] [ARGS]...
zensical --help
zensical <command> --help
```

Commands: `new`, `serve`, `build`

## Live Preview

```bash
zensical serve
```

Starts local server at `localhost:8000` with auto-reload on file changes.

| Option | Short | Purpose |
|--------|-------|---------|
| `--config-file` | `-f` | Specify config file path |
| `--open` | `-o` | Open browser automatically |
| `--dev-addr <IP:PORT>` | `-a` | Custom bind address (default: localhost:8000) |

**Warning:** Built-in server is for preview only. Use nginx/Apache for production.

### Docker live preview

```bash
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs zensical/zensical serve -a 0.0.0.0:8000
```

## Build

```bash
zensical build
```

Generates static site in `site_dir` (default: `site/`).

| Option | Short | Purpose |
|--------|-------|---------|
| `--config-file` | `-f` | Specify config file path |
| `--clean` | `-c` | Clear cache before building |

### Production Docker build

```bash
docker run --rm -v ${PWD}:/docs zensical/zensical build --clean
```

## New Project

```bash
zensical new .
```

Creates `zensical.toml`, `docs/index.md`, `docs/markdown.md`, and `.github/` directory.
