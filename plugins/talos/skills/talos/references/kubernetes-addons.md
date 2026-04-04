# Talos Kubernetes Addons Reference

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

## MetalLB

Not in official Talos guides but commonly used. Install via Helm or manifests. Label namespace privileged.

**L2 mode** - announce IPs via ARP/NDP. Simple, no router config. Single node handles traffic.
**BGP mode** - announce IPs via BGP to routers. True load distribution.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: main-pool
  namespace: metallb-system
spec:
  addresses: ["192.168.1.200-192.168.1.250"]
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: l2-advert
  namespace: metallb-system
spec:
  ipAddressPools: ["main-pool"]
```

Install: `kubectl label namespace metallb-system pod-security.kubernetes.io/enforce=privileged`

## Metrics Server

Requires kubelet serving cert rotation + cert approver.

Machine config (all nodes):
```yaml
machine:
  kubelet:
    extraArgs:
      rotate-server-certificates: true
```

Install both components:
```yaml
cluster:
  extraManifests:
    - https://raw.githubusercontent.com/alex1989hu/kubelet-serving-cert-approver/main/deploy/standalone-install.yaml
    - https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Or post-bootstrap: `kubectl apply -f <url>` for each.

## InlineManifests & ExtraManifests

```yaml
cluster:
  inlineManifests:          # embedded in machine config, controlplane only
    - name: my-app
      contents: |
        # full K8s manifest YAML
  extraManifests:           # external URLs, requires network
    - "https://example.com/manifest.yaml"
```

Apply order: Namespaces, then CRDs, then all other resources (alpha by name). Reconciled on boot/failure/config change. **Additive-only** -- never edits/deletes existing resources. Update existing: `talosctl upgrade-k8s` with same K8s version. Ensure identical inlineManifests across all controlplane nodes.

## KubePrism

In-cluster HA API server endpoint. Default enabled since Talos 1.6. TCP loadbalancer on `localhost:7445`.

```yaml
machine:
  features:
    kubePrism:
      enabled: true
      port: 7445
```

Balances across: external endpoint, local API server (controlplane), discovered controlplane IPs. Filters unhealthy, prefers low latency. Auto-reconfigures kubelet/scheduler/controller-manager. Update kube-proxy: `talosctl upgrade-k8s`. CNI must use `k8sServiceHost=localhost`, `k8sServicePort=7445`. Localhost-only binding.

## Node Labels & Taints

### Labels
```yaml
machine:
  nodeLabels:
    topology.kubernetes.io/zone: "rack-1"
    topology.kubernetes.io/region: "dc-east"
```

NodeRestriction limits self-assignable labels to: `topology.kubernetes.io/*`, `kubernetes.io/hostname`, `kubernetes.io/arch`, `kubernetes.io/os`, select `node.kubernetes.io/*`.

Role labels (`node-role.kubernetes.io/<role>`) require cluster-admin:
```bash
kubectl label node <node> node-role.kubernetes.io/worker=""
```

### Taints (registration-time only)
```yaml
machine:
  kubelet:
    extraConfig:
      registerWithTaints:
        - key: node.kubernetes.io/assignment
          value: infra
          effect: NoSchedule
```

Post-registration taint changes require cluster-admin: `kubectl taint nodes <node> key=value:NoSchedule`. Workers cannot self-modify taints after registration.
