# Ceph Storage Dashboard

uid: `ceph-storage`, folder: `Storage`

Requires `monitoring.enabled: true` in rook-ceph-cluster Helm values.
Community dashboards: `2842` (Cluster), `5336` (OSD), `5342` (Pools) from grafana.com.

## Variables

```
$datasource: type=datasource, query=prometheus
```

## Row 1: Cluster Health (stat panels, y=0, h=4)

| Panel | w | Query | Config |
|-------|---|-------|--------|
| Health Status | 4 | `ceph_health_status` | mappings: 0=HEALTH_OK, 1=WARN, 2=ERR. green=0, yellow=1, red=2 |
| Total Capacity | 4 | `ceph_cluster_total_bytes` | unit: bytes |
| Used Capacity | 4 | `ceph_cluster_total_used_bytes` | unit: bytes |
| Usage % | 4 | `ceph_cluster_total_used_bytes / ceph_cluster_total_bytes` | gauge: green<0.65, yellow<0.8, red |
| OSDs Up | 4 | `count(ceph_osd_up == 1)` | -- |
| OSDs In | 4 | `count(ceph_osd_in == 1)` | -- |

## Row 2: Monitor & PG Status (y=4, h=6)

**Health Detail Alerts** (w=12, table):
```promql
ceph_health_detail
```
Labels: `name`, `severity`

**Monitor Quorum** (w=6, stat):
```promql
count(ceph_mon_quorum_status == 1)   # In quorum
count(ceph_mon_metadata)              # Total monitors
```

**PG States** (w=6, stat):
```promql
ceph_pg_active    # Active PGs
ceph_pg_clean     # Clean PGs
ceph_pg_total     # Total PGs
```

## Row 3: IOPS & Throughput (y=10, h=8)

**Cluster IOPS** (w=12, timeseries):
```promql
sum(rate(ceph_osd_op_r[5m]))   # Read IOPS
sum(rate(ceph_osd_op_w[5m]))   # Write IOPS
```

**Cluster Throughput** (w=12, timeseries, unit: Bps):
```promql
sum(rate(ceph_osd_op_r_out_bytes[5m]))  # Read throughput
sum(rate(ceph_osd_op_w_in_bytes[5m]))   # Write throughput
```

## Row 4: OSD Latency (y=18, h=8)

**Apply Latency** (w=12, timeseries, unit: ms):
```promql
ceph_osd_apply_latency_ms   # legend: osd.{{ceph_daemon}}
```

**Commit Latency** (w=12, timeseries, unit: ms):
```promql
ceph_osd_commit_latency_ms  # legend: osd.{{ceph_daemon}}
```

## Row 5: OSD Distribution (y=26, h=8)

**OSD PG Distribution** (w=12, bargauge):
```promql
ceph_osd_numpg   # legend: {{ceph_daemon}}
```

**Recovery Operations** (w=12, timeseries):
```promql
rate(ceph_osd_recovery_ops[5m])
```

## Row 6: Pool Usage (y=34, h=8)

**Pool Usage Table** (w=24, table, instant):
```promql
ceph_pool_stored{pool_id=~".+"}       # Stored bytes
ceph_pool_percent_used{pool_id=~".+"} # Usage %
ceph_pool_metadata                     # Pool names (join on pool_id)
```
Transformation: merge by `pool_id`, display `name` from `ceph_pool_metadata`.

## Key Metrics Reference

```
# Cluster
ceph_health_status                    # 0=OK, 1=WARN, 2=ERR
ceph_health_detail{name,severity}     # active health checks
ceph_cluster_total_bytes              ceph_cluster_total_used_bytes

# Monitors
ceph_mon_quorum_status{ceph_daemon}   # 1=in quorum
ceph_mon_metadata{ceph_daemon}

# OSDs
ceph_osd_up{ceph_daemon}             ceph_osd_in{ceph_daemon}
ceph_osd_metadata{ceph_daemon,device_class}
ceph_osd_numpg{ceph_daemon}          ceph_osd_apply_latency_ms
ceph_osd_commit_latency_ms           ceph_osd_op_r (counter)
ceph_osd_op_w (counter)              ceph_osd_op_r_out_bytes (counter)
ceph_osd_op_w_in_bytes (counter)     ceph_osd_recovery_ops (counter)

# Placement Groups
ceph_pg_total    ceph_pg_active    ceph_pg_clean

# Pools
ceph_pool_metadata{pool_id,name}     ceph_pool_stored{pool_id}
ceph_pool_percent_used{pool_id}
```
