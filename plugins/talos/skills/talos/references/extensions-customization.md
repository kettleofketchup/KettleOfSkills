# Talos Extensions & Customization Reference (v1.12)

## System Extensions

Customize root filesystem while maintaining immutability. Add container runtimes, firmware, drivers, tools.

### Install Methods
- **Boot media**: generate ISO/PXE/disk images with extensions baked in via Image Factory
- **Installer image**: custom installer container with extensions, used during `talosctl upgrade`
- Generic ISO boots node, then custom installer pulls extensions during install

### Query Installed Extensions
```bash
talosctl get extensions
talosctl -n <NODE> get extensions <ID> -o yaml
```

### Support Tiers
| Tier | Support |
|------|---------|
| Core | Full Sidero Labs support + maintenance |
| Extra | Best-effort support, Sidero-maintained |
| Contrib | Community-supported + maintained |

Extensions are OCI container images with specific folder structure. Build with Docker/Podman.
Official repo: `github.com/siderolabs/extensions`

## Extension Services

Run custom system services as privileged containers early in boot. Config at `/usr/local/etc/containers/*.yaml`, binaries at `/usr/local/lib/containers/<name>/`.

Register as `ext-<name>` in service registry.

### Manifest Format
```yaml
name: hello-world
container:
  entrypoint: ./hello
  args: [--config, config.ini]
  environment: [FOO=bar]
  mounts:
    - {source: /var/data, destination: /data, type: bind, options: [rshared, rw]}
  security: {writeableRootfs: false, writeableSysfs: false}
depends:
  - service: containerd       # wait for service health
  - network: [addresses, connectivity, hostname, etcfiles]
  - time: true                # wait for NTP sync
restart: always               # always | never | untilSuccess
```
Manage: `talosctl service ext-<name> start|restart|stop`, `talosctl logs ext-<name>`

## Kernel Modules

Modules must be signed with trusted key; build alongside kernel using same signing key.

### Build Process
1. Create `pkg.yaml` + register in `.kres.yaml`
2. Build kernel + module together: `make kernel my-module REGISTRY=... PUSH=true`
3. Package as system extension with `manifest.yaml`

### Load via Machine Config
```yaml
machine:
  kernel:
    modules:
      - name: my-module
```

Deploy via fresh install (custom installer image) or upgrade existing nodes.

## Overlays

Customize boot images for specific hardware (SBCs). Hook into installation steps for custom boot assets, kernel args, board-specific configs.

**Overlays vs extensions**: overlays customize installation process; extensions customize root filesystem.

Components: firmware, bootloader (U-Boot), DTB, installer binary, disk profile.
Official repo: `github.com/siderolabs/overlays` (sbc-rockchip, sbc-raspberrypi, etc.)

Use via Image Factory schematic ID: `factory.talos.dev/installer/<schematic-id>:<version>`
Pass options: `--overlay-option` flag or `@<path>` for YAML file input.

## Containerd Configuration

Customizations merge into base config at `/etc/cri/conf.d/20-customization.part`.

All customizations use `machine.files` writing to `/etc/cri/conf.d/20-customization.part` with `op: create`.

Common TOML snippets:
- **Metrics**: `[metrics]\n  address = "0.0.0.0:11234"`
- **Pause image**: `[plugins."io.containerd.cri.v1.images".pinned_images]\n  sandbox = "registry.k8s.io/pause:3.8"`
- **CDI dirs**: `[plugins."io.containerd.cri.v1.runtime"]\n  cdi_spec_dirs = ["/var/cdi/static", "/var/cdi/dynamic"]`
- **NRI plugins**: `[plugins."io.containerd.nri.v1.nri"]\n  disable = false`

## Registry Mirrors / Pull-Through Cache

Use `RegistryMirrorConfig` document. Endpoints tried sequentially; last implicit = upstream.

### Mirror Config
```yaml
apiVersion: v1alpha1
kind: RegistryMirrorConfig
name: docker.io
endpoints:
  - url: http://10.5.0.1:5000
```

Options: `skipFallback: true` (no upstream fallback), `overridePath: true` (when URL includes `/v2`).

### Auth Config
```yaml
apiVersion: v1alpha1
kind: RegistryAuthConfig
name: my-registry.io
username: user
password: "****"
```

### TLS Config (self-signed certs)
```yaml
apiVersion: v1alpha1
kind: RegistryTLSConfig
name: my-registry.io
ca: |-
  -----BEGIN CERTIFICATE-----
  ...
  -----END CERTIFICATE-----
```

### Harbor Setup
Single endpoint for multiple upstream registries. Use `overridePath: true`:
```yaml
apiVersion: v1alpha1
kind: RegistryMirrorConfig
name: docker.io
endpoints:
  - url: http://harbor/v2/proxy-docker.io
    overridePath: true
```

Deploy one Docker Registry container per upstream (ports 5000-5003) with `REGISTRY_PROXY_REMOTEURL`.

## Static Pods

Defined in machine config under `machine.pods`. Talos renders to kubelet via local HTTP server (not disk files). No reboot required. No Talos-side validation (errors in kubelet logs).

```yaml
machine:
  pods:
    - apiVersion: v1
      kind: Pod
      metadata:
        name: nginx
      spec:
        containers:
          - name: nginx
            image: nginx
```

Inspect: `talosctl get staticpods`, `talosctl get staticpodstatus`
Debug (no API server): `talosctl containers --kubernetes`, `talosctl logs --kubernetes`
User pod IDs: `<namespace>-<name>`

## Performance Tuning

Kernel args set via `.machine.install.extraKernelArgs`. Post-install requires no-op upgrade to apply.

### CPU Governors
```
cpufreq.default_governor=performance   # max throughput (default: schedutil)
```

### Processor-Specific
```
amd_pstate=active     # AMD: minimize latency during state transitions
intel_idle.max_cstate=0  # Intel: disable idle driver, reduce wake-up latency
```

### Security vs Performance
```
mitigations=off       # disable ALL hw vuln mitigations (security tradeoff)
```

### I/O Memory (v1.8.2+)
```
iommu.passthrough=1   # bypass IOMMU for DMA operations
```

### Microcode Extensions
Install `amd-ucode` and `intel-ucode` system extensions to reduce performance overhead from processor-specific mitigations.
