# Ansible vmware.vmware Certified Collection (v2.7.0+)

Certified collection using REST + pyVmomi. Actively developed, preferred for new work.
Install: `ansible-galaxy collection install vmware.vmware`

## VM Operations

```yaml
- vmware.vmware.vm_powerstate:
    # ... connection params ...
    name: my-vm
    state: powered-on  # powered-on, powered-off, shutdown-guest, reboot-guest, suspended

- vmware.vmware.vm_snapshot:
    # ... connection params ...
    name: my-vm
    snapshot_name: pre-patch
    state: present  # present, absent

- vmware.vmware.vm_snapshot_revert:
    # ... connection params ...
    name: my-vm
    snapshot_name: pre-patch
```

## Host & Cluster

```yaml
- vmware.vmware.esxi_host:               # Add host to vCenter
    # ... connection params ...
    esxi_hostname: esxi01.example.com
    esxi_username: root
    esxi_password: "{{ esxi_root_pass }}"
    datacenter: DC1
    cluster: Production
    state: present

- vmware.vmware.esxi_maintenance_mode:   # present=enter, absent=exit
    # ... connection params ...
    esxi_hostname: esxi01.example.com
    state: present

- vmware.vmware.cluster_ha:
    # ... connection params ...
    cluster_name: Production
    datacenter: DC1
    enable: true

- vmware.vmware.cluster_drs:
    # ... connection params ...
    cluster_name: Production
    datacenter: DC1
    enable: true
    drs_default_vm_behavior: fullyAutomated
```

## Content Library

```yaml
- vmware.vmware.local_content_library:
    library_name: templates
    datastore: DS1
    state: present

- vmware.vmware.deploy_content_library_template:
    template: golden-image
    library: templates
    name: new-vm
    datacenter: DC1
    cluster: Production
    datastore: DS1

- vmware.vmware.import_content_library_iso:
    library_name: templates
    iso_name: ubuntu-22.04
    iso_path: /tmp/ubuntu-22.04-server.iso
```

## Tags

```yaml
- vmware.vmware.tag_categories:
    category_name: Environment
    cardinality: SINGLE
    state: present

- vmware.vmware.tags:
    tag_name: Production
    category_name: Environment
    state: present

- vmware.vmware.tag_associations:
    tag_name: Production
    category_name: Environment
    object_name: my-vm
    object_type: VirtualMachine
    state: present
```

## Module Index

**Cluster**: `cluster`, `cluster_dpm`, `cluster_drs`, `cluster_drs_recommendations`, `cluster_ha`, `cluster_info`, `cluster_vcls`
**VM**: `vm`, `vm_advanced_settings`, `vm_powerstate`, `vm_snapshot`, `vm_snapshot_revert`, `guest_info`
**Content Library**: `local_content_library`, `subscribed_content_library`, `content_library_item_info`, `deploy_content_library_ovf`, `deploy_content_library_template`, `import_content_library_iso`, `import_content_library_ovf`
**Host**: `esxi_host`, `esxi_connection`, `esxi_maintenance_mode`
**Infra**: `folder`, `appliance_info`, `license_info`, `vcsa_backup_schedule`, `vcsa_settings`
**Tags**: `tags`, `tag_categories`, `tag_associations`
**Inventory plugins**: `esxi_hosts`, `vms` | **Lookup**: `moid_from_path`
