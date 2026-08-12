# Talos v1.12 Networking: Interfaces Reference

## Config Document Types

| Kind | Purpose |
|------|---------|
| `LinkConfig` | Physical interface: MTU, up/down |
| `LinkAliasConfig` | Alias physical link by MAC selector |
| `VLANConfig` | VLAN on physical/logical parent |
| `BondConfig` | Link aggregation (NIC teaming) |
| `BridgeConfig` | Bridge multiple interfaces |
| `ResolverConfig` | DNS nameservers + search domains |
| `HostnameConfig` | Static/auto hostname |
| `NetworkDefaultActionConfig` | Firewall default: `accept`/`block` |
| `NetworkRuleConfig` | Firewall allow/block rules |
| `KubespanEndpointsConfig` | Extra KubeSpan announced endpoints |

All use `apiVersion: v1alpha1`. No network config = DHCP on primary interface.
Explicit link config disables default DHCP; re-enable manually if needed.

## Static IP

```yaml
apiVersion: v1alpha1
kind: LinkConfig
name: enp0s3
addresses:
  - address: 192.168.1.100/24
routes:
  - gateway: 192.168.1.1
```

Point-to-point (gateway outside subnet): use `/32` address + on-link route to gateway + default route.
Route fields: `destination` (CIDR), `gateway`, `metric`, `mtu`, `routePriority`.

## Physical Links

```yaml
apiVersion: v1alpha1
kind: LinkAliasConfig
name: mgmt
selector:
  match: mac(link.permanent_addr) == "00:1a:2b:3c:4d:5e"
---
apiVersion: v1alpha1
kind: LinkConfig
name: mgmt
mtu: 9000
up: true
```

## VLANs

```yaml
apiVersion: v1alpha1
kind: VLANConfig
name: enp0s3.2
vlanID: 2
vlanMode: 802.1q
parent: enp0s3   # physical link, bond, or alias
up: true
addresses:
  - address: 192.168.1.100/32
```

## Bonds

```yaml
apiVersion: v1alpha1
kind: BondConfig
name: agg.0
links: [enp0s2, enp0s3]
bondMode: 802.3ad
miimon: 100
updelay: 200
downdelay: 200
xmitHashPolicy: layer3+4
lacpRate: slow
up: true
addresses:
  - address: 1.2.3.4/24
```

Other fields: `resendIGMP`, `packetsPerSlave`, `mtu`, `hardwareAddr`, `adActorSysPrio`.

## Bridges

```yaml
apiVersion: v1alpha1
kind: BridgeConfig
name: bridge.1
links: [eno1, eno5]
stp: {enabled: true}
vlan: {filtering: false}
up: true
addresses:
  - address: 1.2.3.5/32
```

## DNS / Resolvers

Defaults: `8.8.8.8`, `1.1.1.1`. Override:
```yaml
apiVersion: v1alpha1
kind: ResolverConfig
nameservers:
  - address: 10.0.0.1
searchDomains:
  domains: [example.org]
```
Inspect: `talosctl get resolvers`.

## Hostname

`HostnameConfig` with `hostname: my-node` and `auto: off` (or `stable`, default from machine ID).

## Host DNS

```yaml
machine:
  features:
    hostDNS:
      enabled: true                  # listens 127.0.0.53:53
      forwardKubeDNSToHost: true     # kube-dns -> host DNS (addr 169.254.116.108)
      resolveMemberNames: true       # resolve cluster member hostnames
```

Debug: `talosctl logs dns-resolve-cache`, `talosctl get dnsupstream`.

## Useful Commands
`talosctl get addresses`, `talosctl get routespecs`, `talosctl get links`, `talosctl get resolvers`, `talosctl get members`.

See `references/networking-advanced.md` for corporate proxies, KubeSpan, ingress firewall, multihoming.
