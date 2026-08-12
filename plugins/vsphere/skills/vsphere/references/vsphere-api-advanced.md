# vSphere REST API — Filtering, VI/JSON, Web Interfaces

## Filtering

List endpoints support query parameter filters. No pagination on most endpoints (hard limit ~4000 results). Use filters to narrow results in large environments.

VM filters: `power_states`, `names`, `folders`, `datacenters`, `hosts`, `clusters`, `resource_pools`

```bash
curl -sk "https://$VC/api/vcenter/vm?power_states=POWERED_ON&clusters=domain-c8" \
  -H "vmware-api-session-id: $SID"
```

## VI/JSON API (vSphere 8.0 U1+)

Full SOAP API parity via JSON. URL pattern: `POST /sdk/vim25/{version}/{Type}/{moid}/{Operation}`

```bash
# Power on VM via VI/JSON
curl -sk -X POST "https://$VC/sdk/vim25/8.0.1.0/VirtualMachine/vm-42/PowerOnVM_Task" \
  -H "vmware-api-session-id: $SID" \
  -H "Content-Type: application/json"
```

Use for operations not in the REST API: snapshots, advanced settings, custom attributes, DRS rules, performance counters.

## Web Interfaces

- **API Explorer**: `https://<vcenter>/apiexplorer` -- interactive Swagger UI
- **MOB**: `https://<vcenter-or-esxi>/mob` -- browse live object model
- **vSphere Client**: `https://<vcenter>/ui`
- **ESXi Host Client**: `https://<esxi>/ui`
