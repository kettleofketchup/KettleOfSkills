---
last_updated: 2026-03-09
---
# Patches

Patches modify resources after accumulation. They target resources by their **original** names (before namePrefix/nameSuffix transformers run).

## Strategic Merge Patch (file)

Merge fields by matching `apiVersion`, `kind`, and `metadata.name`. SMP patches are self-targeting via their metadata (no `target:` field needed):

```yaml
# patch-replicas.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 5
```

```yaml
# kustomization.yaml
patches:
  - path: patch-replicas.yaml
```

### Delete a field
Set value to `null`:
```yaml
spec:
  template:
    spec:
      nodeSelector: null
```

### Delete a list item
Use `$patch: delete` directive:
```yaml
spec:
  containers:
    - name: sidecar
      $patch: delete
```

## Strategic Merge Patch (inline)

```yaml
patches:
  - patch: |-
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: myapp
      spec:
        replicas: 5
```

## JSON Patch (inline)

RFC 6902 operations: `add`, `remove`, `replace`, `move`, `copy`, `test`.

```yaml
patches:
  - target:
      kind: Deployment
      name: myapp
    patch: |-
      - op: replace
        path: /spec/replicas
        value: 5
      - op: add
        path: /spec/template/spec/containers/0/env/-
        value:
          name: ENV
          value: production
```

## JSON Patch (file)

```yaml
patches:
  - path: patch.json
    target:
      kind: Deployment
      name: myapp
```

## Target Selectors

Match multiple resources with selectors on `patches`:

```yaml
patches:
  - target:
      kind: Deployment                   # By kind
      name: "myapp.*"                    # By name (supports regex)
      namespace: default                 # By namespace
      group: apps                        # By API group
      version: v1                        # By API version
      labelSelector: "app=myapp"         # By label
      annotationSelector: "managed=true" # By annotation
    patch: |-
      - op: replace
        path: /spec/replicas
        value: 3
```

All fields are optional and ANDed together. Omit `name` to match all resources of a kind. The `name` field supports regex (e.g., `".*"` for all names).

## Multi-Container Patching

JSON patches target specific array indices (`containers/0`), which only affects one container. For pods with init containers, sidecars, or multiple containers:

### Strategic merge patch (preferred for known containers)
Merges by container `name`, so it works regardless of array position:
```yaml
patches:
  - target:
      kind: Deployment
    patch: |-
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: ignored
      spec:
        template:
          spec:
            containers:
              - name: app
                imagePullPolicy: Never
              - name: sidecar
                imagePullPolicy: Never
            initContainers:
              - name: init
                imagePullPolicy: Never
```

### Multiple JSON patches (for index-based)
```yaml
patches:
  - target:
      kind: Deployment
    patch: |-
      - op: add
        path: /spec/template/spec/containers/0/imagePullPolicy
        value: Never
      - op: add
        path: /spec/template/spec/initContainers/0/imagePullPolicy
        value: Never
```

### Post-processing (universal, for unknown container counts)
```bash
kustomize build . | \
  yq '(.. | select(has("containers")).containers[].imagePullPolicy) = "Never"' | \
  yq '(.. | select(has("initContainers")).initContainers[].imagePullPolicy) = "Never"'
```

## Patch Order

Patches apply in order listed in `patches` array. Later patches see results of earlier ones. If two patches modify the same field, last one wins.
