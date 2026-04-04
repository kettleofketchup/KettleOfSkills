# K3s Airgap Deployment

Three methods for running K3s without internet access. Can be combined.

## Method A: Manually Deploy Images

Simplest approach for edge/single-node. Pre-load images into K3s containerd.

### Prepare (internet-connected machine)

1. Download K3s binary + images archive matching your version:

```bash
VERSION="v1.33.3+k3s1"
ARCH="amd64"

# Binary
curl -Lo k3s "https://github.com/k3s-io/k3s/releases/download/${VERSION}/k3s"

# Images archive (zstd-compressed)
curl -Lo k3s-airgap-images-${ARCH}.tar.zst \
  "https://github.com/k3s-io/k3s/releases/download/${VERSION}/k3s-airgap-images-${ARCH}.tar.zst"

# Install script
curl -Lo install.sh https://get.k3s.io
```

2. Transfer all three files to airgap node.

### Install (airgap node)

```bash
# Place binary
sudo cp k3s /usr/local/bin/k3s && sudo chmod +x /usr/local/bin/k3s

# Place images (K3s auto-imports on startup)
sudo mkdir -p /var/lib/rancher/k3s/agent/images/
sudo cp k3s-airgap-images-*.tar.zst /var/lib/rancher/k3s/agent/images/

# Install (skip download, binary already in place)
INSTALL_K3S_SKIP_DOWNLOAD=true ./install.sh
```

K3s accepts `.tar`, `.tar.gz`, `.tar.zst` in the images directory.

### Conditional Image Imports (v1.33.1+)

Avoid re-importing unchanged archives on every restart:

```bash
touch /var/lib/rancher/k3s/agent/images/.cache.json
```

**Warning**: If images are garbage-collected, they won't be re-imported. Recovery:
- `touch <archive>` to force re-import
- `rm .cache.json` and restart K3s
- `ctr -n k8s.io image import <archive>` manually

## Method B: Private Registry

Mirror images to a local registry accessible from airgap network.

### Push Images to Registry

```bash
# Load K3s images
docker image load < k3s-airgap-images-amd64.tar.zst

# Get image list for version
curl -Lo k3s-images.txt \
  "https://github.com/k3s-io/k3s/releases/download/${VERSION}/k3s-images.txt"

# Retag and push each image
while read img; do
  docker tag "$img" "registry.local:5000/${img#*/}"
  docker push "registry.local:5000/${img#*/}"
done < k3s-images.txt
```

### Configure registries.yaml

```yaml
# /etc/rancher/k3s/registries.yaml
mirrors:
  docker.io:
    endpoint:
      - "https://registry.local:5000"
  ghcr.io:
    endpoint:
      - "https://registry.local:5000"
configs:
  "registry.local:5000":
    tls:
      ca_file: /etc/ssl/certs/registry-ca.pem
```

See `references/registries.md` for full format.

## Method C: Embedded Registry Mirror (v1.33+)

K3s includes a distributed OCI mirror — images in any node's containerd store are available to all nodes. Best for multi-node clusters.

Refer to official docs: `https://docs.k3s.io/installation/registry-mirror`

## Airgap + Custom CNI

Additional images needed beyond `k3s-airgap-images`. Example for Calico:

1. Download tigera-operator + calico node/cni images
2. Bundle into tarball or push to private registry
3. Place in `/var/lib/rancher/k3s/agent/images/` alongside K3s images

Set `imagePullPolicy: Never` or `IfNotPresent` on all workloads to prevent pull attempts.

### Kustomize Component Pattern

Generic component to patch all workload types:

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

## NixOS Airgap Integration

Reference the `nixos` skill. Key patterns:
- `oci-bundle.nix` library packages images as Nix derivations
- `images.list` file lists all required images per repo
- `bundleImages` creates combined tarball for `/var/lib/rancher/k3s/agent/images/`
- NixOS service copies images before K3s starts (systemd ordering)
- ISO can bake images + manifests into `/opt/airgap/`
