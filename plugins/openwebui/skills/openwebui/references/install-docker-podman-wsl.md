# Podman, WSL, and Docker Desktop Extension

## Using Podman

Podman is a daemonless container engine for developing, managing, and running OCI Containers.

### Basic Commands

```bash
podman run -d --name openwebui -p 3000:8080 -v open-webui:/app/backend/data ghcr.io/open-webui/open-webui:main
```

List running containers:

```bash
podman ps
```

### Networking with Podman

`slirp4netns` is being deprecated and will be removed in Podman 6. The modern successor is **pasta**, which is the default in Podman 5.0+.

### Accessing the Host (Local Services)

Use the special DNS name `host.containers.internal` to point to your computer.

**Modern Approach (Pasta - Default in Podman 5+):** No special flags needed.

**Legacy Approach (Slirp4netns):** For older versions of Podman:

```bash
podman run -d --network=slirp4netns:allow_host_loopback=true --name openwebui -p 3000:8080 -v open-webui:/app/backend/data ghcr.io/open-webui/open-webui:main
```

### Connection Configuration

In Open WebUI, navigate to **Settings > Admin Settings > Connections** and set your Ollama API connection to: `http://host.containers.internal:11434`

### Uninstall

```bash
podman rm -f openwebui
podman rmi ghcr.io/open-webui/open-webui:main    # optional
podman volume rm open-webui                        # optional, deletes all data
```

## Podman Kube Play

Podman supports Kubernetes-like syntax for deploying resources such as pods and volumes without a full Kubernetes cluster.

### Example `play.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: open-webui
spec:
  containers:
    - name: container
      image: ghcr.io/open-webui/open-webui:main
      ports:
        - name: http
          containerPort: 8080
          hostPort: 3000
      volumeMounts:
        - mountPath: /app/backend/data
          name: data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName:  open-webui-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: open-webui-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### Starting

```bash
podman kube play ./play.yaml
```

### GPU Support

Replace the image with `ghcr.io/open-webui/open-webui:cuda` and add GPU resources:

```yaml
resources:
  limits:
    nvidia.com/gpu=all: 1
```

You will need the Container Device Interface (CDI) for the GPU installed in your Podman Machine. See [Podman GPU container access](https://podman-desktop.io/docs/podman/gpu).

## Podman Quadlets (systemd)

Manage containers as native systemd services. Recommended for production on Linux with systemd.

### Setup

1. Create the configuration directory:
   ```bash
   mkdir -p ~/.config/containers/systemd/
   ```

2. Create `~/.config/containers/systemd/open-webui.container`:

   ```ini
   [Unit]
   Description=Open WebUI Container
   After=network-online.target

   [Container]
   Image=ghcr.io/open-webui/open-webui:main
   ContainerName=open-webui
   PublishPort=3000:8080
   Volume=open-webui:/app/backend/data
   AddHost=host.containers.internal:host-gateway

   [Service]
   Restart=always

   [Install]
   WantedBy=default.target
   ```

3. Reload and start:
   ```bash
   systemctl --user daemon-reload
   systemctl --user start open-webui
   systemctl --user enable open-webui
   ```

### Management

```bash
systemctl --user status open-webui     # Check status
journalctl --user -u open-webui -f     # View logs
systemctl --user stop open-webui       # Stop service
```

To update: `podman pull ghcr.io/open-webui/open-webui:main` then `systemctl --user restart open-webui`.

## Docker with WSL (Windows Subsystem for Linux)

### Step 1: Install WSL

Follow the [official Microsoft documentation](https://learn.microsoft.com/en-us/windows/wsl/install).

### Step 2: Install Docker Desktop

Download from [docker.com](https://www.docker.com/products/docker-desktop/). Select the "WSL 2" backend during setup.

### Step 3: Configure Docker Desktop for WSL

Go to **Settings > Resources > WSL Integration**. Enable integration with your default WSL distro.

### Step 4: Run Open WebUI

From your WSL terminal:

```bash
docker pull ghcr.io/open-webui/open-webui:main
docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
```

Always run `docker` commands from your WSL terminal, not from PowerShell or Command Prompt. When using volume mounts, ensure paths are accessible from your WSL distribution.

## Docker Desktop Extension

Docker has released an Open WebUI Docker extension that uses Docker Model Runner for inference. See the [blog post](https://www.docker.com/blog/open-webui-docker-desktop-model-runner/).

This is not an officially supported installation method. You cannot log in as different users in the extension since it is designed for a single local user. For issues, submit them on the [extension's GitHub repository](https://github.com/rw4lll/open-webui-docker-extension).
