# K3s Registry — Combined Examples, Troubleshooting, NixOS

## Combined Examples

### Full production setup

```yaml
mirrors:
  docker.io:
    endpoint:
      - "https://registry.local:5000"
  "registry.gitlab.example.com":
    endpoint:
      - "https://registry.gitlab.example.com"
configs:
  "registry.local:5000":
    auth:
      username: k3s
      password: pull-secret
    tls:
      ca_file: /etc/ssl/certs/internal-ca.pem
  "registry.gitlab.example.com":
    auth:
      token: "glpat-xxxxxxxxxxxx"
    tls:
      ca_file: /etc/ssl/certs/internal-ca.pem
```

### Airgap with no external fallback

```yaml
mirrors:
  "*":
    endpoint:
      - "https://registry.local:5000"
```

Use `--disable-default-registry-endpoint` flag to prevent fallback to public registries.

## Default Endpoint Behavior

Containerd always tries the default endpoint as fallback:
- `docker.io` → `https://index.docker.io/v2`
- Other registries → `https://<registry>/v2`

Disable with: `--disable-default-registry-endpoint` (prevents any external pull attempts in airgap).

## Troubleshooting

Check containerd pull logs:
```bash
cat /var/lib/rancher/k3s/agent/containerd/containerd.log | grep -i pull
```

Verify which node runs a pod: `kubectl get pod -o wide`

Check generated containerd config after editing registries.yaml:
```bash
cat /var/lib/rancher/k3s/agent/etc/containerd/config.toml
```

## NixOS Integration

Reference the `nixos` skill. NixOS K3s module generates `registries.yaml` from:
```nix
services.k3s-cluster.registries = {
  mirrors = { "docker.io".endpoint = ["https://registry.local:5000"]; };
  configs = { "registry.local:5000".auth = { username = "k3s"; password = "..."; }; };
};
```
