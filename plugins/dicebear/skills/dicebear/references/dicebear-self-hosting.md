# DiceBear Self-Hosting

Source: [github.com/dicebear/api](https://github.com/dicebear/api) (TypeScript, Fastify)

## Docker

```bash
docker run --tmpfs /run --tmpfs /tmp -p 3000:3000 -i -t dicebear/api:3
```

docker-compose.yml:
```yaml
services:
  dicebear:
    image: dicebear/api:3
    restart: always
    ports:
      - '3000:3000'
    tmpfs:
      - '/run'
      - '/tmp'
```

## Without Docker

```bash
git clone git@github.com:dicebear/api.git
cd api
npm install
npm run build
npm start
```

Requires Node.js.

## Environment Variables

### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | Listen port |
| `HOST` | `0.0.0.0` | Bind address |
| `LOGGER` | `0` | Request logging (1=on) |
| `WORKERS` | `1` | Node.js worker threads |
| `VERSIONS` | `5,6,7,8,9` | Supported DiceBear major versions |
| `CACHE_CONTROL_AVATARS` | `31536000` | Cache duration seconds (1 year default) |

### Format Toggles & Size Limits

Each format (PNG, JPEG, WEBP, AVIF) has identical env vars:

| Variable | Default | Description |
|----------|---------|-------------|
| `{FORMAT}` | `1` | Enable format endpoint (1=on, 0=off) |
| `{FORMAT}_SIZE_MIN` | `1` | Min allowed size (px) |
| `{FORMAT}_SIZE_MAX` | `128` | Max allowed size (px) |
| `{FORMAT}_SIZE_DEFAULT` | `128` | Default size (px) |
| `{FORMAT}_EXIF` | `1` | EXIF metadata (1=on). Requires Perl + procps |

Where `{FORMAT}` = `PNG`, `JPEG`, `WEBP`, or `AVIF`.

### Query String Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `QUERY_STRING_ARRAY_LIMIT_MIN` | `20` | Min values per array param |
| `QUERY_STRING_PARAMETER_LIMIT_MIN` | `100` | Min query string params |

## Production Recommendations

- Increase `{FORMAT}_SIZE_MAX` for higher-res avatars (e.g., `512` or `1024`)
- Set `WORKERS` to match CPU cores for throughput
- Disable unused formats to reduce attack surface
- Put behind reverse proxy (Traefik/Nginx) for TLS and rate limiting
- Use `CACHE_CONTROL_AVATARS` to leverage CDN/browser caching
- EXIF requires Perl and procps installed — disable if not needed

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dicebear
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dicebear
  template:
    metadata:
      labels:
        app: dicebear
    spec:
      containers:
        - name: dicebear
          image: dicebear/api:3
          ports:
            - containerPort: 3000
          env:
            - name: PNG_SIZE_MAX
              value: "512"
            - name: JPEG_SIZE_MAX
              value: "512"
            - name: WORKERS
              value: "2"
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: dicebear
spec:
  selector:
    app: dicebear
  ports:
    - port: 3000
      targetPort: 3000
```
