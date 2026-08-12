---
last_updated: 2026-03-09
---
# Common Component Patterns

## Airgap / imagePullPolicy Override (Multi-Container Safe)

JSON patches target specific array indices (`containers/0`), which only sets the policy on the first container. For pods with init containers, sidecars, or multiple containers, use **strategic merge patches** that merge by container `name`:

```yaml
# _components/airgap/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component
patches:
  # Strategic merge patch - targets ALL containers by name
  # Requires knowing container names; add entries as needed
  - target:
      kind: Deployment
    patch: |-
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: __ignored__
      spec:
        template:
          spec:
            initContainers:
              - name: "*"
                $patch: strategic
            containers:
              - name: "*"
                $patch: strategic
  # JSON patch approach - explicit per-index (fragile for variable containers)
  # Use when you need to cover index 0 universally:
  - target:
      kind: Deployment
    patch: |-
      - op: add
        path: /spec/template/spec/containers/0/imagePullPolicy
        value: Never
  - target:
      kind: StatefulSet
    patch: |-
      - op: add
        path: /spec/template/spec/containers/0/imagePullPolicy
        value: Never
```

**Recommended approach for multi-container:** Use one strategic merge patch per known container name. For unknown/variable containers, post-process with yq after `kustomize build`:

```bash
# Universal: set imagePullPolicy on ALL containers after build
kustomize build . | yq '(.. | select(has("containers")).containers[].imagePullPolicy) = "Never"' | \
  yq '(.. | select(has("initContainers")).initContainers[].imagePullPolicy) = "Never"'
```

## Shared Labels

```yaml
# _components/team-labels/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component
labels:
  - pairs:
      team: platform
      managed-by: kustomize
    includeTemplates: true   # Also adds to pod template labels
```

## Namespace-Scoped RBAC

```yaml
# _components/rbac/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component
resources:
  - role.yaml
  - rolebinding.yaml
```
