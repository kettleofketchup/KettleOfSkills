# Ansible VMware Modules Reference

## Collections

| Collection | SDK | Status | Install |
|------------|-----|--------|---------|
| `community.vmware` | pyVmomi (SOAP) | Mature, modules gradually deprecated | `ansible-galaxy collection install community.vmware` |
| `vmware.vmware` | REST + pyVmomi | Certified, actively developed (v2.7.0+) | `ansible-galaxy collection install vmware.vmware` |

Python dependency: `pip install pyvmomi` (required by community.vmware). Prefer `vmware.vmware` for new work.

## Connection Pattern

All modules share connection params. Store credentials in Ansible Vault:

```yaml
# Common vars (use vault for password)
vcenter_hostname: vcenter.example.com
vcenter_username: administrator@vsphere.local
vcenter_password: "{{ vault_vcenter_password }}"
```

## community.vmware -- Key Modules

### vmware_guest (VM lifecycle)

```yaml
# Create VM
- community.vmware.vmware_guest:
    hostname: "{{ vcenter_hostname }}"
    username: "{{ vcenter_username }}"
    password: "{{ vcenter_password }}"
    validate_certs: false
    name: my-vm
    state: poweredon
    guest_id: centos7_64Guest
    esxi_hostname: esxi01.example.com
    folder: /DC1/vm
    disk:
      - size_gb: 40
        type: thin
        datastore: DS1
    hardware: { memory_mb: 4096, num_cpus: 2 }
    networks:
      - name: VM Network
        ip: 192.168.1.100
        netmask: 255.255.255.0
        gateway: 192.168.1.1

# Clone from template (with customization)
- community.vmware.vmware_guest:
    # ... connection params ...
    name: cloned-vm
    template: ubuntu-template
    state: present
    cluster: Production
    datastore: DS1
    customization:
      domain: example.com
      dns_servers: [8.8.8.8, 8.8.4.4]

# Power: poweredon, poweredoff, present, absent, restarted, shutdownguest, rebootguest, suspended
- community.vmware.vmware_guest:
    # ... connection params ...
    name: my-vm
    state: absent
    force: true
```

### Snapshots (vmware_guest_snapshot)

```yaml
- community.vmware.vmware_guest_snapshot:
    # ... connection params ...
    datacenter: DC1
    name: my-vm
    state: present          # present, absent, revert, remove_all
    snapshot_name: pre-patch
    description: "Before patching"
    memory_dump: true
```

### Info Gathering

```yaml
- community.vmware.vmware_vm_info:          # All VMs
    # ... connection params ...
  register: vm_info

- community.vmware.vmware_guest_info:       # Specific VM
    # ... connection params ...
    datacenter: DC1
    name: my-vm

- community.vmware.vmware_host_facts:       # Host details
    # ... connection params ...
    esxi_hostname: esxi01.example.com

- community.vmware.vmware_datastore_info:   # Datastores
    # ... connection params ...
    datacenter: DC1
```

### Other community.vmware Modules

| Module | Purpose |
|--------|---------|
| `vmware_guest_disk` | Add/remove/resize VM disks |
| `vmware_guest_network` | Manage VM NICs |
| `vmware_guest_powerstate` | Power state operations |
| `vmware_guest_tools_wait` | Wait for VMware Tools |
| `vmware_guest_file_operation` | File transfer to/from guest |
| `vmware_host_service_manager` | Host services (SSH, NTP) |
| `vmware_portgroup` | Standard port groups |
| `vmware_vswitch` | Standard virtual switches |
| `vmware_content_library_manager` | Content library management |
| `vmware_deploy_ovf` | Deploy from OVF/OVA |

See `references/ansible-vmware-certified.md` for vmware.vmware certified collection (v2.7.0+) modules and module index.
