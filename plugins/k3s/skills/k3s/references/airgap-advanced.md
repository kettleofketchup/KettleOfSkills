# K3s Airgap — Upgrades and NixOS Integration

## Upgrading Airgap Clusters

### Manual Upgrade

1. Download new version's images tarball + binary
2. Replace images in `/var/lib/rancher/k3s/agent/images/` (remove old tarball)
3. Replace `/usr/local/bin/k3s` binary
4. Re-run install script: `INSTALL_K3S_SKIP_DOWNLOAD=true ./install.sh`
5. K3s restarts automatically

### Automated Upgrade (system-upgrade-controller)

Requires additional images pre-loaded:
- `rancher/k3s-upgrade:<version>` (replace `+` with `-` in tag)
- `rancher/system-upgrade-controller:<version>`
- `rancher/kubectl:<version>`

## Kustomize imagePullPolicy Component

Generic component to patch all workload types for airgap (prevent external pull attempts):

```yaml
# _components/airgap/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component
patches:
  - target:
      kind: Deployment
    patch: |-
      - op: add
        path: /spec/template/spec/containers/0/imagePullPolicy
        value: Never
  - target:
      kind: DaemonSet
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

Reference in overlays: `components: ["../../_components/airgap"]`

## NixOS Airgap Integration

Reference the `nixos` skill. Key patterns:
- `oci-bundle.nix` library packages images as Nix derivations
- `images.list` file lists all required images per repo
- `bundleImages` creates combined tarball for `/var/lib/rancher/k3s/agent/images/`
- NixOS service copies images before K3s starts (systemd ordering)
- ISO can bake images + manifests into `/opt/airgap/`
