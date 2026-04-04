# vSphere REST API Reference

## API Surfaces

| API | Base Path | Format | Coverage | Min Version |
|-----|-----------|--------|----------|-------------|
| **Automation REST** | `/api/` | Clean JSON | ~70% of features | vSphere 7.0 U2 |
| **Legacy REST** | `/rest/` | JSON wrapped in `{"value":...}` | Same | vSphere 6.5 (deprecated) |
| **VI/JSON** | `/sdk/vim25/{ver}/` | JSON | 100% (SOAP parity) | vSphere 8.0 U1 |
| **SOAP/VIM** | `/sdk/` | XML | 100% | All versions |

Prefer `/api/` for standard operations. Use VI/JSON for advanced ops (snapshots, custom attributes, DRS rules) not in REST. Standalone ESXi only has SOAP.

## Authentication

```bash
# Create session (returns plain token string)
SESSION=$(curl -sk -X POST "https://$VC/api/session" \
  -u 'administrator@vsphere.local:Password')
SESSION=$(echo $SESSION | tr -d '"')

# Use token in requests
curl -sk "https://$VC/api/vcenter/vm" \
  -H "vmware-api-session-id: $SESSION"

# Delete session when done
curl -sk -X DELETE "https://$VC/api/session" \
  -H "vmware-api-session-id: $SESSION"
```

Sessions timeout after ~300s of inactivity. The `vmware-api-session-id` header is used for all subsequent requests.

## Key Endpoints

### VM Lifecycle (`/api/vcenter/vm`)

```bash
# List VMs (with filters)
curl -sk "https://$VC/api/vcenter/vm" -H "vmware-api-session-id: $SID"
curl -sk "https://$VC/api/vcenter/vm?power_states=POWERED_ON" -H "vmware-api-session-id: $SID"
curl -sk "https://$VC/api/vcenter/vm?names=web-01,web-02" -H "vmware-api-session-id: $SID"
curl -sk "https://$VC/api/vcenter/vm?clusters=domain-c8" -H "vmware-api-session-id: $SID"

# Get VM details
curl -sk "https://$VC/api/vcenter/vm/vm-42" -H "vmware-api-session-id: $SID"

# Create VM
curl -sk -X POST "https://$VC/api/vcenter/vm" \
  -H "vmware-api-session-id: $SID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-vm",
    "guest_OS": "OTHER_LINUX_64",
    "placement": {"datastore":"datastore-11","folder":"group-v224","resource_pool":"resgroup-182"},
    "memory": {"size_MiB": 4096},
    "cpu": {"count": 2},
    "disks": [{"new_vmdk": {"capacity": 42949672960}}],
    "nics": [{"backing": {"type":"STANDARD_PORTGROUP","network":"network-14"}}]
  }'

# Clone VM
curl -sk -X POST "https://$VC/api/vcenter/vm?action=clone" \
  -H "vmware-api-session-id: $SID" \
  -H "Content-Type: application/json" \
  -d '{"name":"clone","source":"vm-42","placement":{"datastore":"datastore-11","folder":"group-v224","resource_pool":"resgroup-182"},"power_on":false}'

# Power operations
curl -sk -X POST "https://$VC/api/vcenter/vm/vm-42/power?action=start" -H "vmware-api-session-id: $SID"
curl -sk -X POST "https://$VC/api/vcenter/vm/vm-42/power?action=stop" -H "vmware-api-session-id: $SID"
curl -sk -X POST "https://$VC/api/vcenter/vm/vm-42/power?action=reset" -H "vmware-api-session-id: $SID"

# Delete VM
curl -sk -X DELETE "https://$VC/api/vcenter/vm/vm-42" -H "vmware-api-session-id: $SID"
```

### VM Hardware Sub-resources

| Endpoint | Purpose |
|----------|---------|
| `/api/vcenter/vm/{vm}/hardware` | Overall hardware config |
| `/api/vcenter/vm/{vm}/hardware/cpu` | CPU settings |
| `/api/vcenter/vm/{vm}/hardware/memory` | Memory settings |
| `/api/vcenter/vm/{vm}/hardware/disk` | Virtual disks |
| `/api/vcenter/vm/{vm}/hardware/ethernet` | NICs |
| `/api/vcenter/vm/{vm}/hardware/cdrom` | CD-ROM devices |
| `/api/vcenter/vm/{vm}/hardware/boot` | Boot options |
| `/api/vcenter/vm/{vm}/guest/identity` | Guest OS identity |
| `/api/vcenter/vm/{vm}/guest/networking` | Guest networking |

### Infrastructure

```bash
# Hosts
curl -sk "https://$VC/api/vcenter/host" -H "vmware-api-session-id: $SID"

# Datastores
curl -sk "https://$VC/api/vcenter/datastore" -H "vmware-api-session-id: $SID"

# Networks
curl -sk "https://$VC/api/vcenter/network" -H "vmware-api-session-id: $SID"

# Clusters
curl -sk "https://$VC/api/vcenter/cluster" -H "vmware-api-session-id: $SID"

# Folders
curl -sk "https://$VC/api/vcenter/folder" -H "vmware-api-session-id: $SID"

# Resource pools
curl -sk "https://$VC/api/vcenter/resource-pool" -H "vmware-api-session-id: $SID"
```

### Content Library

```bash
# List libraries
curl -sk "https://$VC/api/content/library" -H "vmware-api-session-id: $SID"

# Find items in library
curl -sk -X POST "https://$VC/api/content/library/item?action=find" \
  -H "vmware-api-session-id: $SID" \
  -H "Content-Type: application/json" \
  -d '{"library_id": "<library-id>"}'

# Deploy VM template from content library
curl -sk -X POST "https://$VC/api/vcenter/vm-template/library-items/<template-id>?action=deploy" \
  -H "vmware-api-session-id: $SID" \
  -H "Content-Type: application/json" \
  -d '{"name":"new-vm","placement":{"resource_pool":"resgroup-182","folder":"group-v224"},"powered_on":false}'
```

### Tags

```bash
# List tag categories
curl -sk "https://$VC/api/cis/tagging/category" -H "vmware-api-session-id: $SID"

# List tags
curl -sk "https://$VC/api/cis/tagging/tag" -H "vmware-api-session-id: $SID"

# Attach tag to object
curl -sk -X POST "https://$VC/api/cis/tagging/tag-association/{tag_id}?action=attach" \
  -H "vmware-api-session-id: $SID" \
  -H "Content-Type: application/json" \
  -d '{"object_id":{"id":"vm-42","type":"VirtualMachine"}}'
```

### Appliance Management

```bash
curl -sk "https://$VC/api/appliance/health/system" -H "vmware-api-session-id: $SID"
curl -sk "https://$VC/api/appliance/system/version" -H "vmware-api-session-id: $SID"
curl -sk "https://$VC/api/appliance/networking" -H "vmware-api-session-id: $SID"
curl -sk "https://$VC/api/appliance/recovery/backup/schedules" -H "vmware-api-session-id: $SID"
```

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
