---
last_updated: 2026-03-09
---
# Generators

Create ConfigMaps and Secrets declaratively with optional hash suffixes for immutable rollouts.

## ConfigMapGenerator

### From literals
```yaml
configMapGenerator:
  - name: app-config
    literals:
      - DATABASE_HOST=postgres.default.svc
      - DATABASE_PORT=5432
      - LOG_LEVEL=info
```

### From files
```yaml
configMapGenerator:
  - name: app-config
    files:
      - config.json                    # Key = filename
      - app.properties
      - custom-key=path/to/file.txt    # Key = custom-key
```

### From env file
```yaml
configMapGenerator:
  - name: app-config
    envs:
      - .env                           # KEY=VALUE lines
      - config.env
```

### Combined sources
```yaml
configMapGenerator:
  - name: app-config
    literals:
      - EXTRA_KEY=value
    files:
      - config.json
    envs:
      - .env
```

## SecretGenerator

Same syntax as ConfigMapGenerator. Values base64-encoded automatically.

```yaml
secretGenerator:
  - name: db-credentials
    type: Opaque                       # Default
    literals:
      - username=admin
      - password=secret123
  - name: tls-cert
    type: kubernetes.io/tls
    files:
      - tls.crt=certs/server.crt
      - tls.key=certs/server.key
```

## Generator Options

### Per-generator options
```yaml
configMapGenerator:
  - name: app-config
    literals:
      - KEY=value
    options:
      disableNameSuffixHash: true      # No hash suffix
      labels:
        app: myapp
      annotations:
        note: generated
```

### Global options
```yaml
generatorOptions:
  disableNameSuffixHash: true          # Applies to ALL generators
  labels:
    generated: "true"
  annotations:
    note: auto-generated
```

## Hash Suffixes

By default, generators append a hash suffix (e.g., `app-config-5k2m7h`) to the name. When content changes, the hash changes, triggering pod rollouts.

**How it works:**
1. Generator creates `ConfigMap/app-config-abc123`
2. All references to `app-config` in Deployments/etc. are auto-updated to `app-config-abc123`
3. Content change -> new hash -> new name -> pods restart

**Disable when:**
- External tools reference the ConfigMap/Secret by exact name
- Using with tools that don't understand kustomize name references
- The resource is referenced by replacements (replacements run after generators)

```yaml
generatorOptions:
  disableNameSuffixHash: true
```

## Merge Behavior

Control how generated resources interact with existing ones:

```yaml
configMapGenerator:
  - name: app-config
    behavior: merge    # merge | replace | create (default)
    literals:
      - NEW_KEY=value
```

- `create` (default): Error if resource already exists
- `merge`: Merge with existing resource from `resources`
- `replace`: Replace existing resource entirely
