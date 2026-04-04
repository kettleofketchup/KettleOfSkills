---
last_updated: 2026-03-11
---

# Troubleshooting Calico

## First Commands

```bash
kubectl get tigerastatus                           # Overall health
kubectl get pods -n calico-system -o wide          # Component pods
kubectl get pods -n tigera-operator                # Operator pod
kubectl get installation default -o yaml           # Installation CR status
kubectl get ippool -o yaml                         # IP pool config
```

## Node Not Ready

Nodes stay NotReady until CNI is functional.

```bash
# 1. Check calico-node pod on affected node
kubectl describe pod -n calico-system -l k8s-app=calico-node --field-selector spec.nodeName=<node>

# 2. Common causes
# - calico-node crashloop: check logs
kubectl logs -n calico-system -l k8s-app=calico-node --field-selector spec.nodeName=<node>

# - IP pool CIDR doesn't match cluster-cidr
kubectl get ippool -o jsonpath='{.items[*].spec.cidr}'
# Compare with: ps aux | grep cluster-cidr (on control plane)

# - Missing CNI config
ls /etc/cni/net.d/
cat /etc/cni/net.d/10-calico.conflist

# - Image pull failure (airgap)
kubectl describe pod -n calico-system <pod> | grep -A5 Events
```

## Pod-to-Pod Cross-Node Failure

Pods on same node communicate but not across nodes.

```bash
# 1. Check encapsulation ports
# VXLAN: UDP 4789, IPIP: IP protocol 4
iptables -L -n | grep -i vxlan
ip -d link show vxlan.calico

# 2. Verify tunnel interface exists
ip link show | grep -E 'vxlan|tunl0'

# 3. Check routes
ip route | grep calico
ip route | grep bird

# 4. Test connectivity from calico-node
kubectl exec -n calico-system <calico-node-pod> -- ping <other-node-pod-ip>

# 5. Packet capture on tunnel interface
tcpdump -i vxlan.calico -nn host <dest-pod-ip>
```

## DNS Resolution Fails

```bash
# 1. Check if CoreDNS pods are running
kubectl get pods -n kube-system -l k8s-app=kube-dns

# 2. Test DNS from a debug pod
kubectl run debug --rm -it --image=busybox -- nslookup kubernetes.default

# 3. Check if NetworkPolicy blocks DNS
calicoctl get networkpolicy -A -o yaml | grep -B10 -A10 "53"
calicoctl get globalnetworkpolicy -o yaml | grep -B10 -A10 "53"

# 4. Verify kube-dns service endpoint
kubectl get endpoints -n kube-system kube-dns
```

## Calico-Node CrashLoopBackOff

```bash
# 1. Check logs
kubectl logs -n calico-system <calico-node-pod> -c calico-node --previous

# 2. Common errors:
# "Unable to auto-detect host IPv4 address" → set IP_AUTODETECTION_METHOD
# "Calico node 'xxx' already exists" → stale node registration
# "Felix is not live" → Felix startup failure

# 3. Check environment variables
kubectl get ds -n calico-system calico-node -o yaml | grep -A2 IP_AUTODETECTION

# 4. IP autodetection fix (Installation CR)
# spec.calicoNetwork.nodeAddressAutodetectionV4:
#   interface: eth0
#   # or: cidrs: ["10.0.0.0/8"]
#   # or: canReach: "8.8.8.8"
```

## Tigera Operator Issues

```bash
# 1. Check operator logs
kubectl logs -n tigera-operator -l k8s-app=tigera-operator

# 2. Check Installation CR status
kubectl get installation default -o jsonpath='{.status.conditions}' | python3 -m json.tool

# 3. Common issues:
# "Installation validation failed" → invalid values in Installation CR
# "CRD not found" → operator version mismatch with CRDs
```

### "Failed to discover tenancy mode"

Operator crashes on startup with `Failed to discovery tenancy mode` and exits.

**Affected versions:** operator v1.34.8+, v1.36.4+, v1.37.0+ (Calico 3.28.3+, 3.29.2+, 3.30.0+).
Not present in operator v1.34.0-v1.34.5 (Calico 3.28.0-3.28.2).

**Cause:** At boot, operator queries `operator.tigera.io/v1` API discovery to check if `Manager` CRD is cluster-scoped (standalone) or namespaced (multi-tenant/Enterprise). If CRDs are not registered, the call fails fatally.

**Triggers:**
1. Helm upgrade where new CRDs were added — Helm never updates CRDs on `helm upgrade`
2. Running operator with `-manage-crds=false` (GitOps/Renovate) without pre-applying CRDs

**Fix:** Apply operator CRDs before the operator starts:

```bash
kubectl apply --server-side --force-conflicts -f \
  https://raw.githubusercontent.com/projectcalico/calico/v<VERSION>/manifests/operator-crds.yaml
```

For Helm upgrades, always apply CRDs as a pre-upgrade step:

```bash
# Step 1: CRDs for target version
kubectl apply --server-side --force-conflicts -f \
  https://raw.githubusercontent.com/projectcalico/calico/v3.29.3/manifests/operator-crds.yaml
# Step 2: Helm upgrade
helm upgrade calico projectcalico/tigera-operator --version v3.29.3 \
  --namespace tigera-operator -f values.yaml
```

## IPAM Issues

```bash
# IP exhaustion
calicoctl ipam show
calicoctl ipam show --show-blocks

# Leaked IPs (pod deleted but IP not released)
calicoctl ipam check
calicoctl ipam release --ip=<leaked-ip>

# Block affinity stuck on deleted node
calicoctl get blockaffinity -o yaml
calicoctl delete blockaffinity <name>
```

## Performance Issues

```bash
# 1. Check Felix metrics
kubectl exec -n calico-system <calico-node-pod> -- wget -qO- http://localhost:9091/metrics | grep felix_int_dataplane

# 2. High CPU: likely too many iptables rules
# Check rule count
kubectl exec -n calico-system <calico-node-pod> -- iptables-save | wc -l

# 3. Consider BPF dataplane for large policy sets (see felix.md)

# 4. Check typha connection (reduces datastore load)
kubectl logs -n calico-system -l k8s-app=calico-typha | tail -20
```

## Airgap-Specific Issues

```bash
# Verify all images are pre-loaded
crictl images | grep -E 'calico|tigera'

# Check imagePullPolicy is Never (for airgap)
kubectl get ds -n calico-system calico-node -o yaml | grep imagePullPolicy

# Verify operator image
kubectl get deployment -n tigera-operator tigera-operator -o yaml | grep image:
```

## calicoctl Installation

```bash
# Install matching version
curl -L https://github.com/projectcalico/calico/releases/download/v3.29.3/calicoctl-linux-amd64 -o calicoctl
chmod +x calicoctl
mv calicoctl /usr/local/bin/

# Configure to use Kubernetes datastore
export DATASTORE_TYPE=kubernetes
export KUBECONFIG=~/.kube/config

# Or use as kubectl plugin
kubectl calico -h
```

## Useful Debug Commands Summary

```bash
calicoctl node status                    # BGP peering state
calicoctl get wep -A -o wide             # All workload endpoints
calicoctl get ippool -o yaml             # IP pool details
calicoctl get felixconfiguration -o yaml # Felix config
calicoctl get bgppeer -o wide            # BGP peers
kubectl get tigerastatus                 # Component health
```
