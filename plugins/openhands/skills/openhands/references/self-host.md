# Self-Hosting OpenHands

## Install Paths

```bash
# uv — recommended
uv tool install openhands --python 3.12
openhands serve
openhands serve --gpu           # expose host GPUs to sandboxes
openhands serve --mount-cwd     # mount the current directory as the workspace
uv tool upgrade openhands --python 3.12

# pip
pip install openhands && openhands serve

# CLI-only headless binary
# → github.com/OpenHands/OpenHands-CLI
```

## CLI & Headless Mode

```bash
openhands                       # interactive TUI
openhands -t "Fix the bug in auth.py"    # inline task
openhands -f task.txt           # task from file
openhands --headless            # non-interactive, for scripting/CI
openhands web                   # web UI
openhands serve                 # GUI server
openhands acp                   # IDE integration (Agent Client Protocol)
openhands --resume --last       # resume the previous conversation
openhands --resume <id>
```

Keys in the TUI: `Ctrl+P` command palette, `Esc` pause the agent, `Ctrl+Q` or `/exit` quit.

`--headless` is the CI entry point — combine with `MAX_ITERATIONS` and `MAX_BUDGET_PER_TASK` so an
unattended run can't loop indefinitely. On Windows the CLI requires WSL. For repo automation triggered by
issues and PRs, use the OpenHands GitHub Action
(`docs.openhands.dev/openhands/usage/run-openhands/github-action`) rather than self-hosting a runner loop.

## Docker

```bash
docker run -it --rm --pull=always \
  -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server \
  -e AGENT_SERVER_IMAGE_TAG=1.26.0-python \
  -e LOG_ALL_EVENTS=true \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/.openhands \
  -p 3000:3000 \
  --add-host host.docker.internal:host-gateway \
  --name openhands-app \
  docker.openhands.dev/openhands/openhands:1.8
```

UI at http://localhost:3000. Configure the LLM in Settings, or pre-seed with `LLM_MODEL` / `LLM_API_KEY`.

| Flag | Why it's there |
|------|----------------|
| `-v /var/run/docker.sock` | The server creates sibling containers for sandboxes |
| `-v ~/.openhands:/.openhands` | Settings, secrets, conversation history — omit and lose everything on restart |
| `--add-host host.docker.internal:host-gateway` | Lets sandboxes reach services on the host |
| `AGENT_SERVER_IMAGE_*` | Which sandbox image to spawn; must match the server version |

Binding `-p 3000:3000` publishes on all interfaces. Use `-p 127.0.0.1:3000:3000` unless an authenticating
proxy sits in front.

## Docker Compose

```yaml
services:
  openhands:
    image: docker.openhands.dev/openhands/openhands:1.8
    container_name: openhands-app
    restart: unless-stopped
    ports: ["127.0.0.1:3000:3000"]
    extra_hosts: ["host.docker.internal:host-gateway"]
    environment:
      AGENT_SERVER_IMAGE_REPOSITORY: ghcr.io/openhands/agent-server
      AGENT_SERVER_IMAGE_TAG: 1.26.0-python
      LLM_MODEL: litellm_proxy/claude-sonnet-4-5
      LLM_BASE_URL: http://litellm:4000
      LLM_API_KEY: ${LLM_API_KEY:?set LLM_API_KEY}
      MAX_BUDGET_PER_TASK: "5.0"
      MAX_ITERATIONS: "100"
      SANDBOX_CLOSE_DELAY: "300"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data/openhands:/.openhands
```

## Sandbox Providers

Selected with `RUNTIME` (the name predates the "sandbox" terminology).

| `RUNTIME` | Isolation | Use when |
|-----------|-----------|----------|
| `docker` (default) | Container per conversation | Almost always |
| `process` (alias `local`) | **None** — runs on the host | Disposable VM/CI only |
| `remote` | Managed remote sandbox service | Hosted/enterprise deployments |

`process` gives the agent your shell, your SSH keys, and your cloud credentials. Treat it as equivalent to
running an untrusted script as yourself.

Remote sandboxes:

```
RUNTIME=remote
SANDBOX_REMOTE_RUNTIME_API_URL=https://runtime-api.example.com
SANDBOX_API_KEY=...
```

## Workspace Mounting

`SANDBOX_VOLUMES` replaces the deprecated `WORKSPACE_*` variables. Format `host:container[:mode]`,
comma-separated:

```bash
-e SANDBOX_VOLUMES="/home/me/projects:/workspace:rw,/home/me/data:/data:ro"
```

Mount the narrowest path that works. `/workspace` is the conventional target; mounting `$HOME` hands the agent
your entire profile.

## Sandbox Lifecycle

Full variable table in `env-vars.md` (Sandbox section). The operational point: defaults destroy the sandbox
`SANDBOX_CLOSE_DELAY=300` seconds after it goes idle. Setting `SANDBOX_KEEP_RUNTIME_ALIVE=true` on a shared
host accumulates idle containers until the disk fills — use `SANDBOX_PAUSE_CLOSED_RUNTIMES=true` instead if
you want fast resume without unbounded growth.

## Custom Sandbox Image

```bash
-e SANDBOX_BASE_CONTAINER_IMAGE=my-registry.example.com/dev-base:2026.08
-e SANDBOX_RUNTIME_EXTRA_DEPS="ripgrep fd-find postgresql-client"
```

Default base is `nikolaik/python-nodejs:python3.12-nodejs22`. A prebuilt image with your toolchain beats
`RUNTIME_EXTRA_DEPS` — the latter reinstalls on every sandbox start.

## GPU

```bash
openhands serve --gpu
# or
-e SANDBOX_ENABLE_GPU=true -e SANDBOX_CUDA_VISIBLE_DEVICES=0
```

Requires the NVIDIA container toolkit on the host.

## Health & Logs

```bash
docker logs -f openhands-app
docker exec openhands-app ls /.openhands
```

```
DEBUG=true          # verbose, also enables file logging
DEBUG_LLM=true      # full prompts/responses — leaks secrets, local debugging only
DEBUG_RUNTIME=true  # sandbox lifecycle
LOG_ALL_EVENTS=true # event stream
```

## Upgrading

```bash
docker compose pull && docker compose up -d
# or
uv tool upgrade openhands --python 3.12
```

Bump `AGENT_SERVER_IMAGE_TAG` alongside the server image. Back up `~/.openhands` first — it holds settings,
secrets, and conversation history.
