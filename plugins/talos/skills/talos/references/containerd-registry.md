# Talos Containerd & Registry Mirror Reference (v1.12)

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
