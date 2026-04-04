---
last_updated: 2026-03-11
---

# Felix Configuration

Felix is the per-node daemon in calico-node responsible for programming routes and ACLs (iptables/BPF).

## FelixConfiguration Resource

Cluster-wide defaults (must be named `default`):

```yaml
apiVersion: projectcalico.org/v3
kind: FelixConfiguration
metadata:
  name: default
spec:
  # Dataplane mode
  bpfEnabled: false                    # true for eBPF dataplane

  # Logging
  logSeverityScreen: Info              # Debug, Info, Warning, Error, Fatal
  logSeverityFile: ""                  # Empty = no file logging
  logFilePath: /var/log/calico/felix.log

  # Tunneling
  ipipEnabled: true
  vxlanEnabled: true
  vxlanPort: 4789

  # Connection tracking
  flowLogsFlushInterval: 300s
  flowLogsFileEnabled: false

  # Timeouts
  ipipMTU: 1440
  vxlanMTU: 1410
  wireguardMTU: 1440
```

## BPF Dataplane

eBPF replaces iptables for higher performance. Requirements: Linux 5.3+, no other CNI kube-proxy replacement.

### Enable BPF

```yaml
apiVersion: projectcalico.org/v3
kind: FelixConfiguration
metadata:
  name: default
spec:
  bpfEnabled: true
  bpfExternalServiceMode: DSR          # Direct Server Return (or Tunnel)
  bpfKubeProxyIptablesCleanupEnabled: true
  bpfLogLevel: ""                      # Debug, Info, Off
  bpfKubeProxyMinSyncPeriod: 1s
```

### Disable kube-proxy (required for BPF)

```bash
# Patch kubeproxy to disable
kubectl patch ds -n kube-system kube-proxy -p '{"spec":{"template":{"spec":{"nodeSelector":{"non-calico": "true"}}}}}'
```

### BPF vs iptables comparison

| Feature | iptables | BPF |
|---------|----------|-----|
| Performance | O(n) rule evaluation | O(1) map lookup |
| DSR | No | Yes |
| Connect-time LB | No | Yes |
| kube-proxy needed | Yes | No |
| Linux kernel | Any | 5.3+ |
| Debugging | iptables -L | `tc filter show`, BPF maps |

## MTU Configuration

Set based on underlying network MTU minus encapsulation overhead:

| Encapsulation | Overhead | MTU (1500 base) |
|---------------|----------|-----------------|
| VXLAN | 50 bytes | 1450 |
| IPIP | 20 bytes | 1480 |
| WireGuard | 60 bytes | 1440 |
| VXLAN+WireGuard | 110 bytes | 1390 |
| None | 0 bytes | 1500 |

```yaml
spec:
  vxlanMTU: 1450
  ipipMTU: 1480
  wireguardMTU: 1440
```

## WireGuard Encryption

Encrypt pod-to-pod traffic with WireGuard:

```yaml
apiVersion: projectcalico.org/v3
kind: FelixConfiguration
metadata:
  name: default
spec:
  wireguardEnabled: true              # IPv4
  wireguardEnabledV6: true            # IPv6
  wireguardListeningPort: 51820
  wireguardMTU: 1440
```

Requires WireGuard kernel module on all nodes:
```bash
# Verify
lsmod | grep wireguard
# Check Calico WireGuard status
calicoctl get node -o yaml | grep -A5 wireguard
```

## Flow Logs

Track network flows for observability:

```yaml
spec:
  flowLogsFlushInterval: 300s
  flowLogsFileEnabled: true
  flowLogsFileDirectory: /var/log/calico/flowlogs
  flowLogsFileAggregationKindForAllowed: 1    # 0=off, 1=per-prefix, 2=per-port
  flowLogsFileAggregationKindForDenied: 1
```

## Per-Node Override

Override specific Felix settings on individual nodes:

```bash
# Set node-specific config via annotation
kubectl annotate node node1 projectcalico.org/logSeverityScreen=Debug
```

## Connection Tracking Tuning

For high-connection environments:

```yaml
spec:
  natOutgoingAddress: ""               # Auto-detect
  failsafeInboundHostPorts:            # Always-allowed inbound
    - protocol: tcp
      port: 22                         # SSH
    - protocol: tcp
      port: 6443                       # K8s API
  failsafeOutboundHostPorts:           # Always-allowed outbound
    - protocol: udp
      port: 53                         # DNS
    - protocol: tcp
      port: 443                        # HTTPS
```

## Key Felix Metrics (Prometheus)

```
felix_iptables_save_time_seconds        # Time to save iptables
felix_iptables_restore_time_seconds     # Time to restore iptables
felix_active_local_endpoints            # Active workload endpoints
felix_active_local_policies             # Policies applied to node
felix_calc_graph_update_time_seconds    # Policy calculation time
felix_int_dataplane_apply_time_seconds  # Dataplane programming time
```

## Troubleshooting Felix

```bash
# Check Felix status
kubectl exec -n calico-system <calico-node-pod> -- calico-node -felix-live

# Enable debug logging temporarily
calicoctl patch felixconfiguration default -p '{"spec":{"logSeverityScreen":"Debug"}}'

# Reset to Info after debugging
calicoctl patch felixconfiguration default -p '{"spec":{"logSeverityScreen":"Info"}}'
```
