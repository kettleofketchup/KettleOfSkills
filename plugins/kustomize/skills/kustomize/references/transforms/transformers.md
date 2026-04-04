---
last_updated: 2026-03-09
---
# Transformers

Transformers modify resource fields globally. They run **after** patches, so patches target original resource names.

## Namespace

```yaml
namespace: production          # Set namespace on all resources
```

## Name Prefix / Suffix

```yaml
namePrefix: prod-
nameSuffix: -v2
```

## Labels

### labels (kustomize v5.0+) - preferred
Does NOT modify selectors by default (safe for rolling updates):

```yaml
labels:
  - pairs:
      env: production
      team: platform
    includeSelectors: false     # Default; set true to also add to selectors
    includeTemplates: true      # Add to pod template labels (default false)
```

### commonLabels - legacy
ALSO modifies selectors (can break rolling updates if changed after deploy):

```yaml
commonLabels:
  legacy-label: value
```

## Annotations

```yaml
commonAnnotations:
  owner: platform-team
```

## Images

```yaml
images:
  - name: myapp                           # Match image name
    newName: registry.example.com/myapp   # Replace registry/name
    newTag: v2.0.0                        # Replace tag
  - name: nginx
    newTag: "1.25"                        # Tag only (keep name)
  - name: busybox
    digest: sha256:abc123                 # Pin to digest
```

### Image transformer notes
- `images` matches on the image name portion (before `:` or `@`)
- Works across all container specs (containers, initContainers, ephemeralContainers)
- `newTag` and `digest` are mutually exclusive

## Build Metadata

Add origin tracking annotations to output resources (useful for debugging):

```yaml
buildMetadata:
  - managedByLabel          # Adds app.kubernetes.io/managed-by: kustomize-v5.x.x
  - originAnnotations       # Adds config.kubernetes.io/origin with file path
  - transformerAnnotations  # Adds alpha.config.kubernetes.io/transformations
```

## CRD Field Configurations

Tell kustomize which CRD fields are name references, namespace references, or prefix/suffix targets. Without this, kustomize won't update name references inside CRDs when generators add hash suffixes:

```yaml
configurations:
  - kustomize-config.yaml
```

```yaml
# kustomize-config.yaml
nameReference:
  - kind: ConfigMap
    fieldSpecs:
      - kind: MyCustomResource
        path: spec/configMapRef/name
  - kind: Secret
    fieldSpecs:
      - kind: MyCustomResource
        path: spec/secretRef/name

namespace:
  - kind: MyCustomResource
    path: spec/targetNamespace
    create: true
```

This ensures that when a ConfigMapGenerator adds a hash suffix, references to that ConfigMap inside CRDs are updated too.
