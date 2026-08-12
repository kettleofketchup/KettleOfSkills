---
last_updated: 2026-03-09
---
# Components

Reusable mixins shared across multiple kustomizations. Components can add resources, patches, transformers, and replacements.

## Component vs Kustomization

| | Kustomization | Component |
|---|---|---|
| **kind** | `Kustomization` | `Component` |
| **apiVersion** | `kustomize.config.k8s.io/v1beta1` | `kustomize.config.k8s.io/v1alpha1` |
| **Usage** | `resources:` | `components:` |
| **Purpose** | Base or overlay | Reusable mixin |
| **Can add resources** | Yes | Yes |
| **Can add patches** | Yes | Yes |
| **Can add replacements** | Yes | Yes |
| **Can be built standalone** | Yes | No |

## Minimal Component

```yaml
# _components/monitoring/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component
resources:
  - service-monitor.yaml
patches:
  - path: add-prometheus-annotations.yaml
```

## Consuming Components

```yaml
# apps/myapp/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
components:
  - ../../_components/monitoring
  - ../../_components/domain
```

## Single Source of Truth Pattern

Store shared cluster config in a Component. Each app references it and uses `replacements` to inject values.

### Directory structure
```
apps/
  _components/
    domain/
      kustomization.yaml    # kind: Component
      cluster-config.yaml   # ConfigMap with shared values
  myapp/
    kustomization.yaml      # references component + defines replacements
    ingressroute.yaml
```

### Shared Component
```yaml
# _components/domain/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component
resources:
  - cluster-config.yaml
```

```yaml
# _components/domain/cluster-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-config
data:
  BASE_DOMAIN: home.kettle.sh
  argocd_host: argocd.home.kettle.sh
  auth_host: auth.home.kettle.sh
```

### Consuming with replacements
```yaml
# apps/myapp/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ingressroute.yaml
components:
  - ../_components/domain
replacements:
  - source:
      kind: ConfigMap
      name: cluster-config
      fieldPath: data.myapp_host
    targets:
      - select:
          kind: IngressRoute
          name: myapp
        fieldPaths:
          - spec.routes.0.match
        options:
          delimiter: "`"
          index: 1
```

## Common Component Patterns

See [components-patterns.md](components-patterns.md) for airgap/imagePullPolicy override, shared labels, and namespace-scoped RBAC patterns.
