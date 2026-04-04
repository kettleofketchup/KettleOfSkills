# Open Terminal Advanced Configuration

## Configuration Reference

Settings are applied in this order (later ones override earlier ones):

1. Built-in defaults
2. System config file (`/etc/open-terminal/config.toml`)
3. User config file (`~/.config/open-terminal/config.toml`)
4. Environment variables (`OPEN_TERMINAL_*`)
5. CLI flags (`--host`, `--port`, etc.)

### All settings

| Setting | Default | Environment Variable | Description |
| :--- | :--- | :--- | :--- |
| **Host** | `0.0.0.0` | -- | Network address to listen on |
| **Port** | `8000` | -- | Port number |
| **API Key** | Auto-generated | `OPEN_TERMINAL_API_KEY` | Password for connecting |
| **API Key File** | -- | `OPEN_TERMINAL_API_KEY_FILE` | Load the key from a file (for Docker secrets) |
| **Log Directory** | `~/.local/state/open-terminal/logs` | `OPEN_TERMINAL_LOG_DIR` | Where to save log files |
| **Max Sessions** | `16` | `OPEN_TERMINAL_MAX_SESSIONS` | Maximum concurrent terminal sessions |
| **Enable Terminal** | `true` | `OPEN_TERMINAL_ENABLE_TERMINAL` | Turn the interactive terminal on/off |
| **Enable Notebooks** | `true` | `OPEN_TERMINAL_ENABLE_NOTEBOOKS` | Turn Jupyter notebook execution on/off |
| **TERM** | `xterm-256color` | `OPEN_TERMINAL_TERM` | Terminal color support |
| **Execute Timeout** | Unset | `OPEN_TERMINAL_EXECUTE_TIMEOUT` | How long (seconds) to wait for command output |
| **Execute Description** | -- | `OPEN_TERMINAL_EXECUTE_DESCRIPTION` | Custom text telling the AI about installed tools |
| **Multi-User** | `false` | `OPEN_TERMINAL_MULTI_USER` | Enable per-user isolation |
| **CORS Origins** | -- | `OPEN_TERMINAL_CORS_ALLOWED_ORIGINS` | Allowed cross-origin domains |
| **Allowed Domains** | -- | `OPEN_TERMINAL_ALLOWED_DOMAINS` | Egress firewall: only allow outbound connections to these domains |

### Docker-only settings

| Setting | Environment Variable | Description |
| :--- | :--- | :--- |
| **System Packages** | `OPEN_TERMINAL_PACKAGES` | Space-separated list of system packages to install at startup |
| **Python Packages** | `OPEN_TERMINAL_PIP_PACKAGES` | Space-separated list of Python packages to install at startup |

These packages are reinstalled every time the container starts. For many packages, consider building a custom image instead.

### Config file

```toml
# ~/.config/open-terminal/config.toml
host = "0.0.0.0"
port = 8000
api_key = "your-secret-key"
log_dir = "/var/log/open-terminal"
max_terminal_sessions = 16
enable_terminal = true
enable_notebooks = true
execute_timeout = 5
execute_description = "This terminal has ffmpeg and ImageMagick installed."
```

Use a custom location: `open-terminal run --config /path/to/my-config.toml`

Config files keep your API key out of the command line and shell history.

### Docker secrets

```yaml
services:
  open-terminal:
    image: ghcr.io/open-webui/open-terminal
    environment:
      - OPEN_TERMINAL_API_KEY_FILE=/run/secrets/terminal_api_key
    secrets:
      - terminal_api_key

secrets:
  terminal_api_key:
    file: ./terminal_api_key.txt
```

### Image variants

| | `latest` | `slim` | `alpine` |
| :--- | :--- | :--- | :--- |
| **Best for** | General use, AI agents | Smaller footprint | Smallest footprint |
| **Size** | ~4 GB | ~430 MB | ~230 MB |
| **Includes** | Node.js, Python, compilers, ffmpeg, Docker CLI, data science libs | git, curl, jq | git, curl, jq |
| **Can install packages** | Yes (has sudo) | No | No |
| **Multi-user** | Yes | No | No |

If you're not sure, use `latest`.

## Multi-User Setup

### Option 1: Built-in multi-user mode

One container, separate accounts inside. Add one setting:

```bash
docker run -d --name open-terminal -p 8000:8000 \
  -v open-terminal:/home \
  -e OPEN_TERMINAL_MULTI_USER=true \
  -e OPEN_TERMINAL_API_KEY=your-secret-key \
  ghcr.io/open-webui/open-terminal
```

When someone uses the terminal through Open WebUI, Open Terminal automatically:

1. Creates a personal account for that user (based on their Open WebUI user ID)
2. Sets up a private home folder at `/home/{user-id}`
3. Runs all their commands under their own account
4. Restricts their file access to their own folder

| | Separate per user | Shared |
| :--- | :--- | :--- |
| Home folder and files | Yes | |
| Running commands | Yes | |
| System packages | | Yes |
| CPU and memory | | Yes |
| Network access | | Yes |

**Warning**: Good for small teams, not production. Everyone shares the same container. If one user runs a resource-heavy script, it affects everyone.

### Option 2: Per-user containers with Terminals

For larger deployments or real isolation, **Terminals** gives each user their own container:

- Full isolation -- each user's container is independent
- On-demand provisioning -- containers created when users start a session, cleaned up when idle
- Resource controls -- CPU, memory, and storage limits per user or per environment
- Multiple environments -- different setups for different teams
- Kubernetes support -- works with Docker, Kubernetes, and k3s

Two deployment backends: **Docker Backend** (single Docker host) and **Kubernetes Operator** (CRD-based, production-grade).

Terminals requires an Open WebUI Enterprise License.

## Security Best Practices

### Use Docker

Always use Docker unless you specifically need direct access to your machine. Docker isolates Open Terminal in its own container.

```bash
docker run -d --name open-terminal -p 8000:8000 \
  --memory 2g --cpus 2 \
  -v open-terminal:/home/user \
  -e OPEN_TERMINAL_API_KEY=your-secret-key \
  ghcr.io/open-webui/open-terminal
```

The `--memory 2g` and `--cpus 2` flags prevent runaway processes from consuming all your machine's resources.

**Warning**: Without Docker (bare metal mode), the AI can run any command with your user's permissions.

### Always set a password

Without an API key, anyone who can reach the port has full access. For production, use a config file or Docker secrets.

### Use admin connections (not user connections)

| | Admin-configured | User-configured |
| :--- | :--- | :--- |
| API key visibility | Hidden on the server | Stored in the user's browser |
| Requests go through | Open WebUI's backend | Directly from the browser |
| Terminal network access needed from | Just the Open WebUI server | Every user's computer |

### Limit resources

```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: "2.0"
```

### Network isolation

Put Open Terminal on a private Docker network (`internal: true`) that only Open WebUI can reach. This prevents Open Terminal from being accessible from the internet and from making outbound internet requests.

### Egress filtering

Restrict outbound connections to specific domains: `-e OPEN_TERMINAL_ALLOWED_DOMAINS="pypi.org,github.com,*.npmjs.org"`

### Docker socket warning

Mounting the Docker socket (`-v /var/run/docker.sock:/var/run/docker.sock`) gives the container **full control** over your host's Docker. This is effectively root access. Only do this if you fully trust everyone who has access.

### Security checklist

- Use Docker, not bare metal
- Set a strong API key
- Use admin-configured connections
- Set memory and CPU limits
- Use network isolation (internal Docker network)
- Enable egress filtering if internet access isn't needed
- Don't mount the Docker socket unless necessary
- Use `slim` or `alpine` images if you don't need runtime package installs
