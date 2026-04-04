---
last_updated: 2026-03-09
---
# Replacements

Modern alternative to deprecated `vars`. Copy values from source fields to target fields. Replacements run last in the build order (after patches and transformers).

## Basic Syntax

```yaml
replacements:
  - source:
      kind: ConfigMap
      name: cluster-config
      fieldPath: data.BASE_DOMAIN
    targets:
      - select:
          kind: IngressRoute
        fieldPaths:
          - spec.routes.0.match
        options:
          delimiter: "`"
          index: 1
```

## Source

```yaml
source:
  kind: <Kind>              # Resource kind (required)
  name: <name>              # Resource name (omit if only one of kind exists)
  namespace: <ns>           # Optional
  group: <group>            # API group (optional)
  version: <version>        # API version (optional)
  fieldPath: <dot.path>     # Field to read (required)
```

### fieldPath examples
- `data.mykey` - ConfigMap data field
- `spec.clusterIP` - Service cluster IP
- `metadata.name` - Resource name
- `metadata.annotations.my-annotation`
- `spec.template.spec.containers.0.image` - First container image

## Targets

```yaml
targets:
  - select:
      kind: <Kind>          # Required
      name: <name>          # Optional (omit = all of kind)
      namespace: <ns>       # Optional
      group: <group>        # Optional
      version: <version>    # Optional
    reject:                 # Exclude matches (uses same selector fields as select)
      - kind: ConfigMap
        name: excluded
    fieldPaths:
      - spec.some.field     # Dot-separated path(s) to write
    options:
      delimiter: <string>   # Split field value on delimiter
      index: <int>          # Replace Nth segment (0-based)
      create: true          # Create field if missing (default false)
```

## Options Detail

### delimiter + index
Partial string replacement - split the target field value by delimiter and replace one segment:

```yaml
# Target field: Host(`PLACEHOLDER`)
# Source value: myapp.example.com
# Result: Host(`myapp.example.com`)
options:
  delimiter: "`"
  index: 1        # 0="Host(", 1="PLACEHOLDER", 2=")"
```

### create
Create the target field path if it doesn't exist:
```yaml
options:
  create: true
```

## From File

Extract replacements to a file for reuse across kustomizations:

```yaml
# kustomization.yaml
replacements:
  - path: replacements.yaml
```

```yaml
# replacements.yaml
- source:
    kind: ConfigMap
    name: cluster-config
    fieldPath: data.BASE_DOMAIN
  targets:
    - select:
        kind: IngressRoute
      fieldPaths:
        - spec.routes.0.match
      options:
        delimiter: "`"
        index: 1
```

## Common Patterns

### Inject namespace into RoleBinding subjects
```yaml
replacements:
  - source:
      kind: ConfigMap
      name: cluster-config
      fieldPath: data.app_namespace
    targets:
      - select:
          kind: RoleBinding
        fieldPaths:
          - subjects.0.namespace
```

### Copy Secret name to env var
```yaml
replacements:
  - source:
      kind: Secret
      name: db-credentials
      fieldPath: metadata.name
    targets:
      - select:
          kind: Deployment
        fieldPaths:
          - spec.template.spec.containers.0.envFrom.0.secretRef.name
        options:
          create: true
```

### Propagate image tag across resources
```yaml
replacements:
  - source:
      kind: ConfigMap
      name: versions
      fieldPath: data.app_version
    targets:
      - select:
          kind: Deployment
        fieldPaths:
          - spec.template.spec.containers.0.image
        options:
          delimiter: ":"
          index: 1
```
