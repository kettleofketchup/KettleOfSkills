# Cluster Health Dashboard

uid: `k8s-cluster-health`, folder: `Kubernetes`

## Variables

```
$datasource: type=datasource, query=prometheus
$namespace: label_values(kube_pod_info, namespace), multi, includeAll
$node: label_values(kube_node_info, node), multi, includeAll
```

## Row 1: Cluster Overview (stat panels, y=0, h=4)

| Panel | w | Query | Thresholds |
|-------|---|-------|------------|
| Node Count | 4 | `count(kube_node_info)` | -- |
| Ready Nodes | 4 | `sum(kube_node_status_condition{condition="Ready",status="true"})` | green=total, red otherwise |
| Running Pods | 4 | `sum(kube_pod_status_phase{phase="Running"})` | -- |
| CPU Capacity | 4 | `sum(kube_node_status_capacity{resource="cpu"})` | -- |
| Memory Capacity | 4 | `sum(kube_node_status_capacity{resource="memory"})` | unit: bytes |
| CPU Utilization % | 4 | `1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m]))` | gauge: green<0.7, yellow<0.85, red |

## Row 2: Node CPU & Memory (y=4, h=8)

**CPU Usage per Node** (w=12, timeseries):
```promql
1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))
```

**Memory Usage per Node** (w=12, timeseries):
```promql
1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)
```
Thresholds: green<0.8, yellow<0.9, red

## Row 3: Disk & I/O (y=12, h=8)

**Disk Usage per Node** (w=12, timeseries):
```promql
1 - (node_filesystem_avail_bytes{mountpoint="/",fstype!="rootfs"} / node_filesystem_size_bytes{mountpoint="/",fstype!="rootfs"})
```

**Disk I/O** (w=12, timeseries, two queries):
```promql
rate(node_disk_read_bytes_total[5m])     # legend: Read {{device}}
rate(node_disk_written_bytes_total[5m])  # legend: Write {{device}}
```

## Row 4: Pod Status (y=20, h=8)

**Pods by Namespace** (w=12, table):
```promql
sum by (namespace) (kube_pod_status_phase{phase="Running"})
```

**Pod Phase Distribution** (w=6, piechart):
```promql
sum by (phase) (kube_pod_status_phase)
```

**Container Restarts Top 10** (w=6, table):
```promql
topk(10, sum by (namespace, pod, container) (increase(kube_pod_container_status_restarts_total[1h])) > 0)
```

## Row 5: Workload Status (y=28, h=8)

**Deployment Status** (w=8, table):
```promql
kube_deployment_spec_replicas                    # Desired
kube_deployment_status_replicas_available        # Available
kube_deployment_status_replicas_unavailable      # Unavailable
```

**StatefulSet Status** (w=8, table):
```promql
kube_statefulset_replicas                        # Desired
kube_statefulset_status_replicas_ready           # Ready
```

**DaemonSet Status** (w=8, table):
```promql
kube_daemonset_status_desired_number_scheduled   # Desired
kube_daemonset_status_number_ready               # Ready
```

## Row 6: PV/PVC Usage (y=36, h=8)

**PVC Usage %** (w=12, table, instant):
```promql
kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes
```
Labels: `namespace`, `persistentvolumeclaim`. Thresholds: green<0.75, yellow<0.9, red

**PVC Available Space** (w=12, timeseries):
```promql
kubelet_volume_stats_available_bytes
```
Legend: `{{namespace}}/{{persistentvolumeclaim}}`

## Key Metrics Reference

```
# Node Exporter
node_cpu_seconds_total{mode}           node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes         node_filesystem_size_bytes{mountpoint,fstype}
node_filesystem_avail_bytes            node_disk_read_bytes_total{device}
node_disk_written_bytes_total          node_network_receive_bytes_total{device}
node_network_transmit_bytes_total

# cAdvisor / kubelet
container_cpu_usage_seconds_total{namespace,pod,container}
container_memory_working_set_bytes     container_memory_rss
container_network_receive_bytes_total  container_network_transmit_bytes_total

# kubelet volume stats
kubelet_volume_stats_capacity_bytes{namespace,persistentvolumeclaim}
kubelet_volume_stats_available_bytes   kubelet_volume_stats_used_bytes

# kube-state-metrics
kube_node_info{node}                   kube_node_status_condition{condition,status}
kube_node_status_capacity{resource}    kube_node_status_allocatable{resource}
kube_pod_info{namespace,pod,node}      kube_pod_status_phase{phase}
kube_pod_container_status_restarts_total
kube_pod_container_resource_requests{resource}
kube_pod_container_resource_limits{resource}
kube_deployment_spec_replicas          kube_deployment_status_replicas_available
kube_statefulset_replicas              kube_statefulset_status_replicas_ready
kube_daemonset_status_desired_number_scheduled
kube_daemonset_status_number_ready
kube_persistentvolumeclaim_info{storageclass}
kube_persistentvolume_status_phase{phase}
```
