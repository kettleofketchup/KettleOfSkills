---
name: kustomize
description: Kustomize Kubernetes manifest composition without templating. This skill should be used when writing kustomization.yaml files, creating base/overlay directory structures, using Components for shared config (single source of truth pattern), applying strategic merge or JSON patches, using replacements (modern vars alternative) to inject values across resources, configuring generators (ConfigMapGenerator, SecretGenerator), inflating Helm charts (helmCharts/helmGlobals), applying common transformers (namespace, namePrefix, labels, images), CRD field configurations, debugging kustomize build output, or structuring multi-app repositories with shared components.
last_updated: 2026-03-09
---

# Kustomize

Build Kubernetes manifests from bases + overlays without templating. Compose resources declaratively using patches, transformers, and replacements.

## Core Concepts

| Kind | API Version | Purpose |
|------|-------------|---------|
| **Kustomization** | `kustomize.config.k8s.io/v1beta1` | Base or overlay - lists resources, patches, config |
| **Component** | `kustomize.config.k8s.io/v1alpha1` | Reusable mixin - shared across multiple kustomizations |

## Directory Conventions

```
apps/
  _components/          # Shared components (prefixed _ to sort first)
    domain/
      kustomization.yaml    # kind: Component
      cluster-config.yaml
    airgap/
      kustomization.yaml    # kind: Component - imagePullPolicy overrides
  myapp/
    base/
      kustomization.yaml
      deployment.yaml
      service.yaml
    overlays/
      dev/kustomization.yaml
      prod/kustomization.yaml
    kustomization.yaml      # Top-level, may reference base + components
```

Flat layout (no base/overlays) is fine for apps without environment variants.

## Minimal Kustomization

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
  - ../base              # Can reference other kustomizations
```

## Base / Overlay Pattern

```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namespace: production
patches:
  - path: patch-replicas.yaml
    target:
      kind: Deployment
      name: myapp
```

## CLI

```bash
kustomize build .                     # Render manifests to stdout
kustomize build . | kubectl apply -f -
kubectl apply -k .                    # Built-in kustomize support
kubectl kustomize .                   # Preview without applying
kustomize build --enable-helm .       # Enable Helm chart inflation
```

## Task Reference

### Composition
- Components, single source of truth pattern -> [references/composition/components.md](references/composition/components.md)
- ConfigMapGenerator, SecretGenerator, hash suffixes -> [references/composition/generators.md](references/composition/generators.md)
- Helm chart inflation via helmCharts/helmGlobals -> [references/composition/helm-charts.md](references/composition/helm-charts.md)

### Transforms
- Strategic merge patches, JSON patches, target selectors -> [references/transforms/patches.md](references/transforms/patches.md)
- Common transformers (namespace, labels, images) -> [references/transforms/transformers.md](references/transforms/transformers.md)
- Replacements (modern `vars` alternative) -> [references/transforms/replacements.md](references/transforms/replacements.md)

### Troubleshooting
- Common errors, build validation, build order -> [references/troubleshooting/debugging.md](references/troubleshooting/debugging.md)

## Build Order

1. Accumulate `resources` (recursively)
2. Apply `components`
3. Run `generators` (ConfigMapGenerator, SecretGenerator)
4. Apply `patches`
5. Apply `transformers` (namespace, namePrefix, labels, images)
6. Apply `replacements`

Patches target resources by their **original** names (before namePrefix/nameSuffix).

## Key Rules

- Never use deprecated `vars` - use `replacements` instead
- `commonLabels` applies to selectors too (can break updates) - prefer `labels` field (kustomize v5.0+) which skips selectors
- Resources must have unique `group/kind/namespace/name` tuples
- Relative paths in `resources` resolve from the kustomization.yaml location
- `patches` with `target` selectors can match multiple resources; `name` supports regex
- Order of fields in kustomization.yaml does not affect build order

## Integration

- For deploying kustomize apps via ArgoCD (overrides, multi-source, Helm inflation), see the **argocd** skill
