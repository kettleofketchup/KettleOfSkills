---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_url: https://zensical.org/docs/get-started/
---

# Installation

Prerequisites: Python and a package manager (pip or uv).

## pip

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
pip install zensical

# Windows
python -m venv .venv
.venv\Scripts\activate
pip install zensical
```

## uv (recommended)

```bash
uv init
uv add --dev zensical
uv run zensical
```

When using uv, always prefix commands with `uv run` or activate the project's virtualenv manually.

## Docker

Official image: `zensical/zensical` on Docker Hub.

### Development (live preview)

```bash
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs zensical/zensical serve -a 0.0.0.0:8000
```

### Production build

```bash
docker run --rm -v ${PWD}:/docs zensical/zensical build --clean
```

### Production multi-stage Dockerfile

```dockerfile
FROM python:3.12-slim AS builder
RUN pip install zensical
WORKDIR /docs
COPY . .
RUN zensical build --clean

FROM nginx:alpine
COPY --from=builder /docs/site /usr/share/nginx/html
EXPOSE 80
```

### docker-compose.yml (dev)

```yaml
services:
  docs:
    image: zensical/zensical
    command: serve -a 0.0.0.0:8000
    ports:
      - "8000:8000"
    volumes:
      - .:/docs
```

## Upgrading

```bash
# pip
pip install --upgrade zensical
pip show zensical  # check version

# uv
uv lock --upgrade-package zensical
uv run zensical --version
```

Zensical follows semantic versioning, currently 0.0.x (alpha/development releases).
