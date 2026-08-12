# Talos v1.12 Networking: Advanced Reference

## Corporate Proxies

```yaml
machine:
  env:
    http_proxy: http://proxy.corp:8080
    https_proxy: http://proxy.corp:8080
    no_proxy: 10.0.0.0/8,192.168.0.0/16
  time:
    servers: [ntp.corp.local]
  network:
    nameservers: [10.0.0.1]
```

Boot-time proxy (before machine config): kernel args
`talos.environment=http_proxy=<url> talos.environment=https_proxy=<url>`.
Append corporate CA certs via custom certificate authorities config.

## KubeSpan (WireGuard Mesh)

Requires: UDP 51820, cluster discovery enabled.
```yaml
machine:
  network:
    kubespan:
      enabled: true
      mtu: 1420                          # underlying_mtu - 80
      advertiseKubernetesNetworks: false
cluster:
  discovery:
    enabled: true
```
Options: `allowDownPeerBypass`, `filters.endpoints`. Inspect: `talosctl get kubespanpeerstatuses`.
Caveats: GCP/Azure need LB for public IP; avoid pod hostPort 51820; Cilium WireGuard incompatible.

## Ingress Firewall

```yaml
apiVersion: v1alpha1
kind: NetworkDefaultActionConfig
ingress: block       # default is "accept"
---
apiVersion: v1alpha1
kind: NetworkRuleConfig
name: allow-kubelet
portSelector:
  ports: [10250]
  protocol: tcp
ingress:
  - subnet: 172.20.0.0/24
    except: 172.20.0.1/32
```

Port formats: single `10250`, range `10300-10400`. Always allowed: `lo`, `siderolink`, `kubespan`.
Common ports: apid=50000, trustd=50001, kubelet=10250, k8s-api=6443, etcd=2379-2380.

## Multihoming

```yaml
machine:
  kubelet:
    nodeIP:
      validSubnets: [192.168.0.0/16]
cluster:
  etcd:
    advertisedSubnets: [192.168.0.0/16]
```
Without explicit config, etcd/kubelet may pick inconsistent addresses across reboots.
