# Talos v1.12 Machine Configuration Reference

## Config Document Structure
Single YAML file, multi-document (`---` separated). `v1alpha1` document mandatory.
- **Unnamed** documents: appear once (e.g., `v1alpha1` config)
- **Named** documents: multiple allowed with unique `name:` (e.g., `NetworkRuleConfig`)
- Special YAML chars (`!`, `?`, `*`, `&`) require quoting

## v1alpha1 Root: `version: v1alpha1`, `debug: false`, `machine: {}`, `cluster: {}`

### Machine Section Key Fields
```yaml
machine:
  type: controlplane                    # controlplane | worker
  token: <pki-join-token>
  ca: {crt: <b64>, key: <b64>}
  certSANs: [alt-name]
  install:
    disk: /dev/sda                      # or diskSelector: {size: '>= 1TB', type: ssd}
    image: ghcr.io/siderolabs/installer:latest
    wipe: false
  kubelet:
    image: ghcr.io/siderolabs/kubelet:v1.35.0
    clusterDNS: [10.96.0.10]
    extraArgs: {feature-gates: ServerSideApply=true}
    extraMounts: [{destination: /var/lib/ex, type: bind, source: /var/lib/ex, options: [bind,rshared,rw]}]
    nodeIP: {validSubnets: [10.0.0.0/8, '!10.0.0.3/32']}
    registerWithFQDN: true
  controlPlane: {controllerManager: {disabled: false}, scheduler: {disabled: false}}
  network: {kubespan: {enabled: true, mtu: 1420}}
  files: [{path: /tmp/f.txt, permissions: 0o666, content: data, op: create}]  # op: create|append|overwrite
  env: {http_proxy: 'http://proxy:8080'}
  sysctls: {net.ipv4.ip_forward: '1'}
  sysfs: {devices/system/cpu/cpu0/cpufreq/scaling_governor: performance}
  kernel: {modules: [{name: btrfs, parameters: [p1]}]}
  nodeLabels: {workload-type: general}
  nodeAnnotations: {custom.io/meta: val}
  nodeTaints: {workload-type: 'special:NoSchedule'}
  logging: {destinations: [{endpoint: 'tcp://1.2.3.4:12345', format: json_lines}]}
  features:
    kubePrism: {enabled: true, port: 7445}
    hostDNS: {enabled: true, forwardKubeDNSToHost: false}
    kubernetesTalosAPIAccess: {enabled: true, allowedRoles: [os:reader], allowedKubernetesNamespaces: [kube-system]}
    imageCache: {localEnabled: true}
    nodeAddressSortAlgorithm: v2
    diskQuotaSupport: true
  seccompProfiles: [{name: audit.json, value: {defaultAction: SCMP_ACT_LOG}}]
```

### Cluster Section Key Fields
```yaml
cluster:
  clusterName: my-cluster
  controlPlane: {endpoint: 'https://1.2.3.4:6443', localAPIServerPort: 6443}
  network:
    cni: {name: flannel}                # flannel | custom | none
    dnsDomain: cluster.local
    podSubnets: [10.244.0.0/16]
    serviceSubnets: [10.96.0.0/12]
  apiServer:
    image: registry.k8s.io/kube-apiserver:v1.35.0
    certSANs: [1.2.3.4, api.example.com]
    extraArgs: {feature-gates: ServerSideApply=true}
    admissionControl: [{name: PodSecurity, configuration: {}}]
  controllerManager: {image: registry.k8s.io/kube-controller-manager:v1.35.0}
  scheduler: {image: registry.k8s.io/kube-scheduler:v1.35.0}
  proxy: {image: registry.k8s.io/kube-proxy:v1.35.0, mode: ipvs, disabled: false}
  etcd: {image: registry.k8s.io/etcd:v3.6.7, advertisedSubnets: [10.0.0.0/8]}
  coreDNS: {image: registry.k8s.io/coredns/coredns:v1.13.2, disabled: false}
  discovery: {enabled: true, registries: {service: {endpoint: 'https://discovery.talos.dev/'}}}
  allowSchedulingOnControlPlanes: true
  extraManifests: [https://example.com/manifest.yaml]
  inlineManifests: [{name: ns-ci, contents: "apiVersion: v1\nkind: Namespace\nmetadata:\n  name: ci\n"}]
  externalCloudProvider: {enabled: true, manifests: [<url>]}
  adminKubeconfig: {certLifetime: 1h0m0s}
```

## Config Generation
```bash
talosctl gen secrets -o secrets.yaml    # generate once, store permanently
talosctl gen config <cluster-name> <endpoint> \
  --with-secrets secrets.yaml \
  --kubernetes-version 1.35.0 --talos-version v1.12 \
  --config-patch @patches/common.yaml \
  --config-patch-control-plane @patches/cp.yaml \
  --config-patch-worker @patches/worker.yaml \
  --output-types controlplane --output controlplane.yaml
```
Keep `--talos-version` at original generation version to avoid config drift. Regenerate from secrets+patches; never commit generated configs.

## Strategic Merge Patching
Patches = incomplete config merged with base. Patch values override base.
```yaml
# patch.yaml
machine:
  nodeLabels: {env: production}
  kubelet: {extraArgs: {rotate-server-certificates: "true"}}
```
**Merge rules**: lists appended by default. Exceptions (overwritten): `podSubnets`, `serviceSubnets`. Interfaces merge by `interface:`/`deviceSelector:`. VLANs merge by `vlanId:`. `auditPolicy` replaced entirely.

**Delete directive**: `$patch: delete` on matched item (e.g., `{interface: eth0, $patch: delete}`).

### Apply patches
```bash
talosctl gen config <name> <endpoint> --config-patch @patch.yaml   # at gen time
talosctl machineconfig patch base.yaml --patch @patch.yaml -o out.yaml  # offline
talosctl patch mc -n <ip> --patch @patch.yaml                      # live node
talosctl patch mc -n <ip> -p '{"machine":{"kubelet":{"image":"..."}}}'  # inline
talosctl patch mc -n <ip> -p @p1.yaml -p @p2.yaml                 # multiple, ordered
```
Multi-document patches match by `kind`, `apiVersion`, `name`. Unmatched documents appended.

## Config Editing & Apply
```bash
talosctl edit machineconfig -n <ip>              # edit in $EDITOR
talosctl edit mc -n <ip1>,<ip2>                  # multi-node
talosctl apply-config -n <ip> -f config.yaml     # apply from file
talosctl get machineconfig v1alpha1 -o jsonpath='{.spec}'  # retrieve current
```

### Apply modes (`--mode=`)
| Mode | Behavior |
|------|----------|
| `auto` (default) | reboot if necessary, else apply immediately |
| `no-reboot` | apply immediately; fail if reboot-required fields changed |
| `reboot` | update config and reboot |
| `staged` | stage for next reboot, don't reboot now |
| `try` | apply immediately, auto-revert after 1min if unconfirmed |

**No-reboot safe paths**: `.debug`, `.cluster`, `.machine.time`, `.machine.ca`, `.machine.acceptedCAs`, `.machine.certSANs`, `.machine.network`, `.machine.nodeAnnotations`, `.machine.nodeLabels`, `.machine.nodeTaints`, `.machine.sysfs`, `.machine.sysctls`, `.machine.logging`, `.machine.controlplane`, `.machine.kubelet`, `.machine.pods`, `.machine.kernel`, `.machine.features.*`

## Insecure / Maintenance Mode
Nodes in maintenance mode use self-signed certs, no mTLS. Use `--insecure` for initial apply.
```bash
talosctl apply-config -n <ip> -f config.yaml --insecure
talosctl apply-config -n <ip> -f config.yaml --insecure --cert-fingerprint <fp>
talosctl apply-config -n <ip> -f config.yaml --insecure --patch @patch.yaml
```
Supported insecure commands: `apply-config`, `version`, `get`, `meta`, `reset`, `wipe disk`.
Drop `--insecure` after config applied and mTLS active.
