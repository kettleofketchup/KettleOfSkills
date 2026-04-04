# Python Installation

## Installation with pip

### 1. Install Open WebUI

```bash
pip install open-webui
```

### 2. Start the server

```bash
open-webui serve
```

Open WebUI is now running at http://localhost:8080.

If you get `open-webui: command not found`:
1. If you used a virtual environment, make sure it's activated.
2. Try running directly: `python -m open_webui serve`
3. To store data in a specific location: `DATA_DIR=./data open-webui serve`

### Uninstall

```bash
pip uninstall open-webui
rm -rf ~/.open-webui    # optional, deletes all data
```

## Installation with uv

### 1. Install uv

- **macOS/Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- **Windows:**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 2. Run Open WebUI

- **macOS/Linux:**
  ```bash
  DATA_DIR=~/.open-webui uvx --python 3.11 open-webui@latest serve
  ```

- **Windows (PowerShell):**
  ```powershell
  $env:DATA_DIR="C:\open-webui\data"; uvx --python 3.11 open-webui@latest serve
  ```

Setting `DATA_DIR` ensures your chats and settings are saved in a predictable location. If you don't set it, `uvx` might store it in a temporary folder that gets deleted when the process ends.

### Uninstall

```bash
uv tool uninstall open-webui
uv cache clean
rm -rf ~/.open-webui    # optional, deletes all data
```

## Using Virtual Environments (venv)

1. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the Virtual Environment:**
   - Linux/macOS: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

3. **Install Open WebUI:**
   ```bash
   pip install open-webui
   ```

4. **Start the Server:**
   ```bash
   open-webui serve
   ```

### Uninstall

```bash
rm -rf venv
rm -rf ~/.open-webui    # optional, deletes all data
```

## Install with Conda

1. **Create a Conda Environment:**
   ```bash
   conda create -n open-webui python=3.11
   ```

2. **Activate the Environment:**
   ```bash
   conda activate open-webui
   ```

3. **Install Open WebUI:**
   ```bash
   pip install open-webui
   ```

4. **Start the Server:**
   ```bash
   open-webui serve
   ```

### Uninstall

```bash
conda remove --name open-webui --all
rm -rf ~/.open-webui    # optional, deletes all data
```

## Updating with Python

```bash
pip install -U open-webui
```

The `-U` (or `--upgrade`) flag upgrades to the latest available version. After upgrading, restart the server:

```bash
open-webui serve
```

If you run Open WebUI with `UVICORN_WORKERS > 1` (e.g., in a production environment), you MUST ensure the update migration runs on a single worker first to prevent database schema corruption:

1. Update `open-webui` using `pip`.
2. Start the application with `UVICORN_WORKERS=1` environment variable set.
3. Wait for the application to fully start and complete migrations.
4. Stop and restart the application with your desired number of workers.
