# Talos Kubernetes Addons: CNI Reference

## CNI: Cilium

Disable default CNI + optionally kube-proxy in machine config patch:
```yaml
cluster:
  network:
    cni:
      name: none
  proxy:
    disabled: true  # optional, for kube-proxy replacement
```

Helm install (kube-proxy replacement mode):
```bash
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium --version 1.18.0 --namespace kube-system \
  --set ipam.mode=kubernetes --set kubeProxyReplacement=true \
  --set securityContext.capabilities.ciliumAgent="{CHOWN,KILL,NET_ADMIN,NET_RAW,IPC_LOCK,SYS_ADMIN,SYS_RESOURCE,DAC_OVERRIDE,FOWNER,SETGID,SETUID}" \
  --set securityContext.capabilities.cleanCiliumState="{NET_ADMIN,SYS_ADMIN,SYS_RESOURCE}" \
  --set cgroup.autoMount.enabled=false --set cgroup.hostRoot=/sys/fs/cgroup \
  --set k8sServiceHost=localhost --set k8sServicePort=7445
```

Without kube-proxy replacement: `kubeProxyReplacement=false`, omit k8sServiceHost/Port.
Gateway API: add `--set gatewayAPI.enabled=true --set gatewayAPI.enableAlpn=true --set gatewayAPI.enableAppProtocol=true`.

**Talos-specific**: `cgroup.autoMount.enabled=false` + `cgroup.hostRoot=/sys/fs/cgroup` (Talos manages cgroup v2). SYS_MODULE dropped (Talos blocks module loading). `localhost:7445` = KubePrism (required when proxy disabled).

**Inline manifest method**: `helm template` output into `cluster.inlineManifests[].contents`. Controlplane only. Must include namespace YAML. Update via `talosctl upgrade-k8s`.

## CNI: Calico

Disable default CNI same as Cilium. Install Tigera operator:
```bash
kubectl create -f https://docs.tigera.io/calico/latest/manifests/tigera-operator.yaml
```

NFTables + VXLAN Installation CR:
```yaml
apiVersion: operator.tigera.io/v1
kind: Installation
metadata: {name: default}
spec:
  calicoNetwork:
    bgp: Disabled
    linuxDataplane: Nftables  # or BPF for eBPF mode
    ipPools:
      - {name: default-ipv4-ippool, blockSize: 26, cidr: 10.244.0.0/16, encapsulation: VXLAN, natOutgoing: Enabled, nodeSelector: "all()"}
  kubeletVolumePluginPath: None
```

eBPF mode: `linuxDataplane: BPF`, add `bpfNetworkBootstrap: Enabled`, `kubeProxyManagement: Enabled`. Requires FelixConfiguration `cgroupV2Path: "/sys/fs/cgroup"`. Also create `APIServer` CR `metadata: {name: default}`.

## Traefik (Gateway API)

```bash
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/standard-install.yaml
helm repo add traefik https://traefik.github.io/charts
helm upgrade --install traefik traefik/traefik -n traefik --create-namespace \
  --set providers.kubernetesGateway.enabled=true
```

Gateway + HTTPRoute example:
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata: {name: traefik-gateway}
spec:
  gatewayClassName: traefik
  listeners:
    - {name: web, protocol: HTTP, port: 8000, allowedRoutes: {namespaces: {from: Same}}}
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: {name: myapp}
spec:
  parentRefs: [{name: traefik-gateway, sectionName: web}]
  hostnames: ["myapp.example.com"]
  rules:
    - matches: [{path: {type: PathPrefix, value: /}}]
      backendRefs: [{name: myapp, port: 80}]
```

See `references/kubernetes-addons-services.md` for MetalLB, Metrics Server, KubePrism, node labels/taints.
