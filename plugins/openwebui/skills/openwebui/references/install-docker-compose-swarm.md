# Docker Compose and Swarm Installation

## Docker Compose Setup

Docker Compose requires an additional package, `docker-compose-v2`.

Older Docker Compose tutorials may reference version 1 syntax, which uses commands like `docker-compose build`. Ensure you use version 2 syntax, which uses commands like `docker compose build` (note the space instead of a hyphen).

### Example `docker-compose.yml`

```yaml
services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
volumes:
  open-webui:
```

### Using Slim Images

```yaml
services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main-slim
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
volumes:
  open-webui:
```

Slim images download required models (whisper, embedding models) on first use, which may result in longer initial startup times but significantly smaller image sizes.

### Starting the Services

```bash
docker compose up -d
```

### Nvidia GPU Support

Change the image from `ghcr.io/open-webui/open-webui:main` to `ghcr.io/open-webui/open-webui:cuda` and add the following to your service definition:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### Uninstall

1. **Stop and Remove the Services:**
    ```bash
    docker compose down
    ```

2. **Remove the Volume (Optional, deletes all data):**
    ```bash
    docker compose down -v
    ```
    Or manually:
    ```bash
    docker volume rm <your_project_name>_open-webui
    ```

3. **Remove the Image (Optional):**
    ```bash
    docker rmi ghcr.io/open-webui/open-webui:main
    ```

## Docker Swarm

This method uses a stack file to deploy 3 separate containers as services in a Docker Swarm: ChromaDB, Ollama, and OpenWebUI.

This stack deploys ChromaDB as a separate HTTP server container, with Open WebUI connecting to it via `CHROMA_HTTP_HOST` and `CHROMA_HTTP_PORT`. This is required for any multi-worker or multi-replica deployment. The default ChromaDB mode uses a local SQLite-backed PersistentClient that is not fork-safe.

### Before Starting

Create directories for volumes:

```bash
mkdir -p data/open-webui data/chromadb data/ollama
```

### Docker Stack with GPU Support

```yaml
version: '3.9'

services:
  openWebUI:
    image: ghcr.io/open-webui/open-webui:main
    depends_on:
        - chromadb
        - ollama
    volumes:
      - ./data/open-webui:/app/backend/data
    environment:
      DATA_DIR: /app/backend/data
      OLLAMA_BASE_URLS: http://ollama:11434
      CHROMA_HTTP_PORT: 8000
      CHROMA_HTTP_HOST: chromadb
      CHROMA_TENANT: default_tenant
      VECTOR_DB: chroma
      WEBUI_NAME: Awesome ChatBot
      CORS_ALLOW_ORIGIN: "*"
      RAG_EMBEDDING_ENGINE: ollama
      RAG_EMBEDDING_MODEL: nomic-embed-text-v1.5
      RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE: "True"
    ports:
      - target: 8080
        published: 8080
        mode: overlay
    deploy:
      replicas: 1
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3

  chromadb:
    hostname: chromadb
    image: chromadb/chroma:0.5.15
    volumes:
      - ./data/chromadb:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - ALLOW_RESET=TRUE
      - PERSIST_DIRECTORY=/chroma/chroma
    ports:
      - target: 8000
        published: 8000
        mode: overlay
    deploy:
      replicas: 1
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD-SHELL", "curl localhost:8000/api/v1/heartbeat || exit 1"]
      interval: 10s
      retries: 2
      start_period: 5s
      timeout: 10s

  ollama:
    image: ollama/ollama:latest
    hostname: ollama
    ports:
      - target: 11434
        published: 11434
        mode: overlay
    deploy:
      resources:
        reservations:
          generic_resources:
            - discrete_resource_spec:
                kind: "NVIDIA-GPU"
                value: 0
      replicas: 1
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
    volumes:
      - ./data/ollama:/root/.ollama
```

### Additional GPU Requirements

1. Ensure CUDA is Enabled
2. Enable Docker GPU support via [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
3. Configure Docker Swarm for GPU: ensure GPU Resource is enabled in `/etc/nvidia-container-runtime/config.toml` and uncomment `swarm-resource = "DOCKER_RESOURCE_GPU"`. Restart docker daemon after changes.

### CPU Only

Remove the `generic_resources` section from the ollama service.

### Deploy Docker Stack

```bash
docker stack deploy -c docker-stack.yaml -d super-awesome-ai
```
