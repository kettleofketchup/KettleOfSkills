# Docker Bake (Multi-Target Builds)

## docker-bake.hcl

```hcl
group "default" {
  targets = ["api", "worker", "frontend"]
}

target "base" {
  dockerfile = "Dockerfile"
  context = "."
}

target "api" {
  inherits = ["base"]
  target = "api"
  tags = ["myapp/api:latest"]
}

target "worker" {
  inherits = ["base"]
  target = "worker"
  tags = ["myapp/worker:latest"]
}

target "frontend" {
  dockerfile = "frontend/Dockerfile"
  context = "frontend"
  tags = ["myapp/frontend:latest"]
}

# Variables
variable "TAG" {
  default = "latest"
}

target "production" {
  inherits = ["base"]
  tags = ["myapp:${TAG}"]
  platforms = ["linux/amd64", "linux/arm64"]
  cache-from = ["type=registry,ref=myapp:cache"]
  cache-to = ["type=registry,ref=myapp:cache,mode=max"]
}
```

## Usage

```bash
# Build all targets
docker buildx bake

# Build specific target
docker buildx bake api

# Build with variables
docker buildx bake --set *.tags=myapp:v1.0.0

# Push to registry
docker buildx bake --push
```
