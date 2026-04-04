# Talos Linux Troubleshooting Reference

## Diagnostic Workflow

1. Check cluster health: `talosctl health`
2. Check services: `talosctl services`
3. Check kernel logs: `talosctl dmesg`
4. Check service logs: `talosctl logs <service>`
5. Check etcd: `talosctl etcd status && talosctl etcd members`
6. Check resources: `talosctl get members`, `talosctl get staticpods`
7. Check events: `talosctl events --tail 50`
8. Gather support bundle: `talosctl support --nodes <node-list>`

## Key talosctl Commands

```bash
# Kernel / system logs
talosctl dmesg                          # kernel messages
talosctl dmesg -f                       # stream kernel logs
talosctl dmesg -f --tail                # only new messages

# Service logs
talosctl logs <service>                 # view service logs (etcd, kubelet, apid, etc.)
talosctl logs -f <service>              # stream service logs
talosctl logs -k <pod-id>              # kubernetes container logs
talosctl logs controller-runtime        # controller runtime logs
talosctl logs syslogd                   # syslog from extensions/host workloads

# Services and containers
talosctl services                       # list all services + health
talosctl containers                     # list system containers
talosctl containers -k                  # list kubernetes containers

# Resource inspection
talosctl get <type> [<id>]              # get OS resources (table output)
talosctl get rd                         # list all resource definitions
talosctl get members                    # cluster membership
talosctl get staticpods                 # static pod status
talosctl get manifests                  # bootstrap manifests
talosctl get manifests <id> --namespace=controlplane -o yaml

# Cluster health
talosctl health                                         # basic health check
talosctl health --wait-timeout 5m                       # custom timeout (default 20m)
talosctl health --control-plane-nodes 10.0.0.1,10.0.0.2 --worker-nodes 10.0.0.3
talosctl health --run-e2e                               # include k8s e2e tests

# Interactive dashboard (TUI)
talosctl dashboard                      # overview, logs, metrics

# etcd operations
talosctl etcd status                    # member status
talosctl etcd members                   # list members
talosctl etcd alarm list                # check alarms
talosctl etcd defrag                    # defragment DB (resource-intensive)
talosctl etcd snapshot <path>           # backup snapshot

# Configuration
talosctl edit machineconfig             # edit config in $EDITOR
talosctl edit machineconfig --dry-run   # preview changes
talosctl apply-config -f <file>         # apply config file
talosctl apply-config -f <file> -m try --timeout 1m   # try mode with rollback
talosctl apply-config -f <file> -p @patch.yaml         # apply with patch

# Bootstrap and recovery
talosctl bootstrap                                      # bootstrap etcd (one CP node only)
talosctl bootstrap --recover-from <snapshot>            # recover from etcd snapshot
talosctl bootstrap --recover-from <snap> --recover-skip-hash-check

# System info
talosctl version                        # talos version
talosctl kubeconfig                     # fetch/renew kubeconfig
talosctl read /proc/config.gz           # read kernel config
talosctl read /proc/config.gz | zgrep <PATTERN>
talosctl copy <src> <local-dst>         # extract files (.tar.gz)
talosctl cgroups --preset memory        # cgroup usage (cpu|memory|io|process|swap)
talosctl events --duration 10m          # events from last 10m
talosctl events --actor-id <id>         # filter events by actor

# Cluster info
talosctl cluster show                   # local cluster info
talosctl config info                    # current context
talosctl config contexts                # list contexts
```

Global flags: `-n/--nodes`, `-e/--endpoints`, `-c/--cluster`, `--talosconfig`, `--context`

## Common Issues and Solutions

### Bootstrap Failures
- "All services stuck in Pre state" -- bootstrap not completed; run `talosctl bootstrap` on ONE control plane node; check image pulls with `talosctl dmesg`
- "Some services stuck in Pre state" -- verify port 2380 open between CP nodes; check etcd quorum

### etcd Issues
- Crashing etcd -- check `talosctl logs etcd` for invalid `extraArgs`; may need to wipe `/var/lib/etcd`
- Check alarms: `talosctl etcd alarm list`
- Recovery: `talosctl bootstrap --recover-from <snapshot>`

### Network / API Connectivity
- Talos API on port 50000; verify firewall allows 50000/50001
- "certificate IPs are empty" -- subnet conflict; never overlap k8s CIDRs (10.244.0.0/16, 10.96.0.0/12) with host network
- Never use VIP or worker nodes as Talos API endpoints
- TCP LB endpoints must be in `.machine.certSANs`
- Specify config path: `--talosconfig <path>` (default `~/.talos/config`)

### kubelet / Node Registration
- "Node Not Found" -- expected during bootstrap; resolves when API server healthy
- Wrong internal IP -- set `.machine.kubelet.nodeIP`
- Wrong node name -- derived from hostname; update via machine config / cloud config / DHCP
- "Node Not Ready" -- wait for CNI pod startup; verify CNI in `kube-system`
- Check CSRs: `kubectl get csr`
- Check nodes: `kubectl get nodes -o wide`

### Static Pods / Control Plane
- Dependency chain: etcd -> kube-apiserver -> kube-controller-manager + kube-scheduler
- Verify: `talosctl get staticpods`, `talosctl containers -k`, `talosctl logs -k <pod-id>`
- Check rendering: `talosctl dmesg | grep 'rendered new'`

### Disk Issues
- Minimum system requirements must be met; unmet specs cause random failures or image pull errors

## Interactive Dashboard

- Physical console only (not serial); 2nd virtual TTY
- Switch TTY: `Alt+F1` (kernel logs), `Alt+F2` (dashboard)
- Disable: kernel param `talos.dashboard.disabled=1`
- Screens: `F1` Summary (hostname, version, uptime, CPU/mem, UUID, stage, k8s version, network), `F2` Monitor (CPU/mem/disk/net realtime), `F3` Network Config (metal only; hostname, DNS, NTP, DHCP/static)

## Logging Configuration

### Forward Service Logs
```yaml
machine:
  logging:
    destinations:
      - endpoint: "udp://host:port/"   # or tcp://
        format: "json_lines"
        extraTags:
          server: s03-rack07
```
- Protocols: UDP (one msg/packet), TCP (newline-separated)
- Only format: `json_lines`; fields: `msg`, `talos-level`, `talos-service`, `talos-time`
- Multiple destinations supported

### Forward Kernel Logs
Via kernel args:
```yaml
machine:
  install:
    extraKernelArgs:
      - talos.logging.kernel=tcp://host:5044/
```
Via runtime document:
```yaml
apiVersion: v1alpha1
kind: KmsgLogConfig
name: remote-log
url: tcp://host:5044/
```
Fields: `clock`, `facility`, `msg`, `priority`, `seq`, `talos-level`, `talos-time`

### Collect Logs (Receiver)
```bash
nc -k -l 5140 | tee -a logs.txt
```

## FAQs

- **No SSH/shell** -- all access via gRPC API (port 50000); by design for security
- **talosconfig vs kubeconfig** -- talosconfig for Talos API (always available); kubeconfig for k8s API
- **Certificates** -- CAs valid 10yr; client certs (talosconfig/kubeconfig) default 1yr; server certs auto-rotate; renew kubeconfig via `talosctl kubeconfig`
- **Timezone** -- always UTC; not configurable
- **Kernel config** -- `talosctl read /proc/config.gz | zgrep <PATTERN>`
