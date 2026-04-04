---
name: vsphere
description: VMware vSphere infrastructure management with govc CLI and Ansible. This skill should be used when running govc commands (VM lifecycle, snapshots, datastore operations, OVA/ISO deployment, inventory navigation), writing Ansible playbooks with community.vmware or vmware.vmware collections, managing ESXi hosts via esxcli/SSH, working with vSphere REST API via curl, configuring vCenter authentication, understanding vSphere inventory hierarchy (Datacenter/Cluster/Host/VM), or automating VM provisioning and infrastructure operations.
---

# vSphere Infrastructure Management

Manage VMware vSphere and ESXi infrastructure using govc CLI for ad-hoc operations and Ansible for declarative automation.

## Tool Selection

| Task | Tool | Reference |
|------|------|-----------|
| Ad-hoc VM ops, scripting, CI/CD | govc | [references/govc.md](references/govc.md) |
| Declarative provisioning, IaC | Ansible | [references/ansible-vmware.md](references/ansible-vmware.md) |
| On-host troubleshooting, patching | esxcli | [references/esxcli.md](references/esxcli.md) |
| REST API scripting (curl) | vSphere REST API | [references/vsphere-api.md](references/vsphere-api.md) |

## vSphere Hierarchy

```
vCenter Server
└── Datacenter
    ├── vm/           ← VMs and templates
    ├── host/         ← Clusters and ESXi hosts
    │   └── Cluster/
    │       ├── Host1
    │       └── Resources/  ← Resource pools
    ├── datastore/    ← Storage
    └── network/      ← Networks and DVS
```

govc paths: `/<DC>/vm/<name>`, `/<DC>/host/<cluster>`, `/<DC>/datastore/<name>`, `/<DC>/network/<name>`

## API Landscape

| API | Format | Coverage | Available On |
|-----|--------|----------|-------------|
| SOAP/VIM (`/sdk`) | XML | 100% | ESXi + vCenter |
| REST (`/api/`) | JSON | ~70% | vCenter only |
| VI/JSON (`/sdk/vim25/`) | JSON | 100% | vCenter only (8.0 U1+) |

Standalone ESXi has **no REST API** -- use SOAP via govc/pyVmomi, or esxcli via SSH.

## govc Quick Reference

Install: `nix shell nixpkgs#govc` or `brew install govc`

```bash
export GOVC_URL="https://vcenter.example.com/sdk"
export GOVC_USERNAME="administrator@vsphere.local"
export GOVC_PASSWORD="password"
export GOVC_INSECURE=true
export GOVC_DATACENTER="DC1"
```

Common operations:

```bash
govc about                                    # Connection test
govc ls /DC1/vm/                              # List VMs
govc vm.info my-vm                            # VM details
govc vm.power -on my-vm                       # Power on
govc vm.power -s my-vm                        # Graceful shutdown
govc vm.create -m 4096 -c 2 -disk 40GB my-vm # Create VM
govc vm.clone -vm template -on=false new-vm   # Clone
govc vm.destroy my-vm                         # Delete
govc snapshot.create -vm my-vm "snap-name"    # Snapshot
govc datastore.upload local.iso isos/file.iso # Upload file
govc import.ova -options=spec.json app.ova    # Deploy OVA
govc find / -type m -runtime.powerState poweredOn  # Find running VMs
```

JSON output: append `-json` to any command, pipe to `jq`.

Full reference: [references/govc.md](references/govc.md)

## Ansible Quick Reference

Collections: `community.vmware` (SOAP, mature) and `vmware.vmware` (REST, certified, newer)

```yaml
- name: Deploy VM from template
  community.vmware.vmware_guest:
    hostname: "{{ vcenter_hostname }}"
    username: "{{ vcenter_username }}"
    password: "{{ vcenter_password }}"
    validate_certs: false
    name: my-vm
    template: ubuntu-template
    state: poweredon
    cluster: Production
    datastore: DS1
    hardware:
      memory_mb: 4096
      num_cpus: 2
```

Full reference: [references/ansible-vmware.md](references/ansible-vmware.md)

## Authentication

All tools authenticate via username/password to vCenter SSO or ESXi local accounts.

- **govc**: `GOVC_URL`, `GOVC_USERNAME`, `GOVC_PASSWORD` env vars
- **Ansible**: `hostname`, `username`, `password` module params (use vault for secrets)
- **REST API**: `POST /api/session` with basic auth, returns `vmware-api-session-id` token
- **esxcli**: SSH to ESXi host as `root`

## Useful Web Interfaces

- **vSphere Client**: `https://<vcenter>/ui`
- **ESXi Host Client**: `https://<esxi>/ui`
- **API Explorer**: `https://<vcenter>/apiexplorer` (Swagger UI)
- **Managed Object Browser**: `https://<vcenter-or-esxi>/mob`
