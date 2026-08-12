# GitHub Actions: Services & Container Jobs

## Services (Containers)

Run sidecar containers (databases, caches) alongside jobs.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379
```

## Container Jobs

Run the entire job inside a container.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: node:20
      env:
        NODE_ENV: test
      volumes:
        - /data:/data
      options: --cpus 2
```

## Combining Services and Container Jobs

```yaml
jobs:
  integration-test:
    runs-on: ubuntu-latest
    container:
      image: node:20
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: --health-cmd pg_isready --health-interval 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:integration
        env:
          DATABASE_URL: postgres://postgres:test@postgres:5432/testdb
```

## Notes

- Service hostnames match the service label (e.g., `postgres`, `redis`)
- Health checks are important to ensure services are ready before steps run
- Use `options` for Docker flags like `--health-cmd`, `--cpus`, memory limits
- Container jobs run all steps inside the container; no need for Docker CLI in steps
