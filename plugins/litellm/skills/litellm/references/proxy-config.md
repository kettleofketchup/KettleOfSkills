# Proxy Config & Deployment

## config.yaml Deep Dive

```yaml
model_list:
  - model_name: gpt-4                    # Alias clients use
    litellm_params:
      model: azure/gpt-4-deployment      # provider/model format
      api_base: https://my-azure.openai.azure.com
      api_key: os.environ/AZURE_API_KEY  # Reference env vars
    model_info:
      supported_environments: ["production"]

router_settings:
  routing_strategy: "simple-shuffle"      # or least-busy, usage-based-routing, latency-based-routing
  num_retries: 3
  timeout: 30
  redis_host: redis-host                  # Required for HA
  redis_port: 6379
  redis_password: pass

litellm_settings:
  drop_params: true                       # Drop unsupported params silently
  success_callback: ["langfuse"]
  failure_callback: ["sentry"]
  num_retries: 3
  request_timeout: 60
  fallbacks: [{"gpt-3.5-turbo": ["gpt-4"]}]
  context_window_fallbacks: [{"claude-2": ["larger-model"]}]
  cache: true
  cache_params:
    type: redis
    ttl: 600

general_settings:
  master_key: sk-1234
  database_url: "postgresql://user:pass@host:5432/litellm"
  background_health_checks: true
  health_check_interval: 300

environment_variables:
  REDIS_HOST: redis
  LANGFUSE_PUBLIC_KEY: pk_xxx
```

## Docker Compose

```yaml
version: "3.9"
services:
  litellm:
    image: docker.litellm.ai/berriai/litellm:main-stable
    command: --config /app/config.yaml --num_workers 4
    volumes:
      - ./config.yaml:/app/config.yaml
    env_file: .env
    ports:
      - "4000:4000"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/health/liveliness"]
      interval: 30s
      start_period: 120s

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: litellm
      POSTGRES_USER: litellm
      POSTGRES_PASSWORD: changeme
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U litellm"]
      interval: 10s

volumes:
  pgdata:
```

Required `.env`:
```
LITELLM_MASTER_KEY=sk-your-master-key
LITELLM_SALT_KEY=your-salt-key
DATABASE_URL=postgresql://litellm:changeme@db:5432/litellm
```

## Helm Deployment

```bash
helm install litellm oci://docker.litellm.ai/berriai/litellm-helm \
  --set masterkey=sk-1234 \
  --set db.deployStandalone=true
```

ConfigMap for config.yaml, Secret for API keys. Probes: liveness=`/health/liveliness`, readiness=`/health/readiness`, `initialDelaySeconds: 120`.

## Redis for HA

Required for >1000 RPS or multi-replica shared state:

```yaml
general_settings:
  use_redis_transaction_buffer: true
litellm_settings:
  cache: true
  cache_params:
    type: redis
    host: redis-host
    port: 6379
    password: pass
router_settings:
  redis_host: redis-host
  redis_password: pass
  redis_port: 6379
```

## Worker Tuning

```bash
--num_workers 8                        # Match CPU cores
--keepalive_timeout 75                 # Seconds
--max_requests_before_restart 10000    # Memory recycling
```

## Config from Cloud Storage

For Fargate/serverless: load config from S3 or GCS bucket instead of volume mount. Set `CONFIG_FILE_PATH` env var.
