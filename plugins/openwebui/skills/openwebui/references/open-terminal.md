# Open Terminal

Give your AI a real computer to work on.

Open Terminal connects a real computing environment to Open WebUI. The AI can write code, execute it, read the output, fix errors, and iterate, all without leaving the chat. It handles files, installs packages, runs servers, and returns results directly to you. Run it in a Docker container for isolation, or bare metal for direct access to your machine.

## Capabilities

- **Data analysis and reporting** - Upload spreadsheets, CSVs, or databases. The AI reads the data, runs analysis scripts, and generates charts or reports.
- **Document search and extraction** - Point the AI at a folder of PDFs, Word docs, or emails. It reads all of them and returns structured results: summaries, extracted fields, or cross-references.
- **Web development with live preview** - The AI builds HTML/CSS/JS projects, starts a preview server, and renders the result inside Open WebUI. Iterate by describing changes in chat.
- **Software development** - Clone repos, run test suites, debug failures, refactor code, and work with Git, all through natural language.
- **File and system automation** - Bulk rename, sort, deduplicate, convert, compress, and organize files. Manage disk space, schedule backups, process logs.

## Key Features

| Feature | Description |
| :--- | :--- |
| **Code execution** | Runs real commands and returns output |
| **File browser** | Browse, upload, download, and edit files in the sidebar |
| **Document reading** | PDF, Word, Excel, PowerPoint, RTF, EPUB, email |
| **Website preview** | Live preview of web projects inside Open WebUI |
| **Isolation optional** | Run in a Docker container for sandboxing, or bare metal for full access |

Open Terminal requires models with **native function calling** support. Frontier models (GPT-5.4, Claude Sonnet 4.6, Gemini 3.1 Pro) handle complex multi-step tasks well. Smaller models may work for simple commands but can struggle with longer workflows.

## Installation

Choose an installation method based on your needs:

| Method | When to use |
| :--- | :--- |
| **Docker** | Runs in an isolated container, separated from your host system |
| **Bare Metal** | The AI works directly on your machine -- your real files, tools, and environment |
| **Docker Compose** | You already run Open WebUI with Docker Compose and want to add Open Terminal to it |

### Docker

Requires Docker.

```bash
docker run -d \
  --name open-terminal \
  --restart unless-stopped \
  -p 8000:8000 \
  -v open-terminal:/home/user \
  -e OPEN_TERMINAL_API_KEY=your-secret-key \
  ghcr.io/open-webui/open-terminal
```

| Flag | Purpose |
| :--- | :--- |
| `-d` | Run in background |
| `--name open-terminal` | Container name for reference |
| `--restart unless-stopped` | Auto-restart on reboot |
| `-p 8000:8000` | Expose on `http://localhost:8000` |
| `-v open-terminal:/home/user` | Persist files across restarts |
| `-e OPEN_TERMINAL_API_KEY=...` | Authentication key |

Verify by opening `http://localhost:8000/docs` in your browser.

If no API key was set, one is generated automatically. Find it with: `docker logs open-terminal`

### Bare Metal

**Warning**: In this mode, the AI can do anything your user account can do, including modifying and deleting files.

**Option A -- Run without installing:**

```bash
uvx open-terminal run --host 0.0.0.0 --port 8000 --api-key your-secret-key
```

**Option B -- Install with pip:**

```bash
pip install open-terminal
open-terminal run --host 0.0.0.0 --port 8000 --api-key your-secret-key
```

Open Terminal serves files from the current directory. To scope it to a specific project:

```bash
cd /path/to/your/project
uvx open-terminal run --host 0.0.0.0 --port 8000 --api-key your-secret-key
```

Windows is supported via pywinpty with full PowerShell support.

### Docker Compose

Add Open Terminal as a service in your existing `docker-compose.yml`:

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:latest
    container_name: open-webui
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data

  open-terminal:
    image: ghcr.io/open-webui/open-terminal
    container_name: open-terminal
    volumes:
      - open-terminal:/home/user
    environment:
      - OPEN_TERMINAL_API_KEY=your-secret-key

volumes:
  open-webui:
  open-terminal:
```

When both services share a Docker Compose network, use the service name as the host: `http://open-terminal:8000` (`localhost` won't resolve between containers).

## Connecting to Open WebUI

### Recommended: Admin Panel

1. Click your **name** at the bottom of the left sidebar, then click **Admin Panel**.
2. Go to **Settings > Integrations**.
3. Find the **Open Terminal** section (do NOT add it under "External Tools" or "Tool Servers").
4. Click **+** and fill in: URL (`http://localhost:8000` or `http://open-terminal:8000`), API Key, Auth Type (Bearer).
5. Click **Save**. A green "Connected" indicator confirms the connection.
6. (Optional) Restrict access to specific groups via the access control button.
7. In the chat input, click the **terminal button** (cloud icon) and select your terminal under **System**.

### Enable native function calling

1. Go to **Workspace > Models**
2. Edit the model you're using
3. Under **Capabilities**, enable **Native Function Calling**
4. Save

Without native function calling, Open WebUI falls back to prompt-based tool calling, which is less reliable.

Pre-configure via environment variable: For Docker deployments, use `TERMINAL_SERVER_CONNECTIONS` to configure terminal connections automatically at startup.

### Personal Settings (testing only)

Adding a terminal via personal Settings sends the API key to your browser and routes requests directly from it. For anything beyond quick testing, use Admin Settings instead.

### Troubleshooting

**"Connection failed" or timeout** -- URL depends on your setup:

| Your setup | URL to use |
| :--- | :--- |
| Docker Compose (recommended) | `http://open-terminal:8000` |
| Separate Docker containers | `http://host.docker.internal:8000` |
| Both on same machine, no Docker | `http://localhost:8000` |
| Open Terminal on another machine | `http://that-machines-ip:8000` |

Quick connectivity check:
```bash
docker exec open-webui curl -s http://open-terminal:8000/health
```

**Terminal shows up but AI doesn't use it**: Ensure the toggle is on, refresh the page, and confirm your model supports tool calling.

**Wrong API key**: Check with `docker logs open-terminal` for the `API key:` line.

## File Browser

When Open Terminal is connected, a **file browser** appears in the sidebar of your chat.

- **Browsing**: Click folders to navigate, click files to preview. Breadcrumb bar at top.
- **Previewing**: Text/code files with syntax highlighting. PDFs render inline. CSVs render as formatted tables. Markdown shows rendered preview with raw toggle. Images display inline.
- **Uploading**: Drag and drop files onto the file browser. Files upload to whichever directory you're viewing.
- **Downloading**: Click the download button on any file to save results to your computer.
- **Editing**: Click the edit icon on text files to make quick changes.
- **Creating/Deleting**: Create new files and folders, or delete items directly from the file browser.

The file browser refreshes automatically when the AI creates or changes files, remembers which folder you were in across chat switches, and updates when switching between terminals.

## Enterprise Multi-User

For isolated, per-user terminal containers, see **Terminals** which provisions a dedicated Open Terminal instance for every user with automatic lifecycle management, resource controls, and policy-based environments.
