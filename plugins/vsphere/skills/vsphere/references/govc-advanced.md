# govc — Host Operations, Guest Ops, Scripting

## Host Operations

```bash
govc host.info
govc host.maintenance.enter -host esxi1
govc host.maintenance.exit -host esxi1
govc host.service -host esxi1                          # List services
govc host.esxcli -host esxi1 system version get        # Remote esxcli
govc host.vswitch.add -host esxi1 vSwitch1
govc host.portgroup.add -host esxi1 -vswitch vSwitch0 -vlan 100 "VLAN100"
```

## Guest Operations

Require VMware Tools running. Set `GOVC_GUEST_LOGIN="user:pass"`.

```bash
govc guest.upload -vm my-vm -f -perm 0755 script.sh /tmp/script.sh
govc guest.download -vm my-vm /var/log/syslog ./syslog.log
govc guest.run -vm my-vm /tmp/script.sh
govc guest.run -vm my-vm bash -c "echo hello"
tar -cf- mydir/ | govc guest.run -vm my-vm -d - tar -C /tmp -xf-
govc guest.ps -vm my-vm
govc guest.ls -vm my-vm /tmp/
govc guest.df -vm my-vm
```

## Scripting Patterns

```bash
# Batch power off VMs in folder
govc find /DC1/vm/Testing -type m | while read -r vm; do
  govc vm.power -off "$vm"
done

# Wait for IP then SSH
govc vm.power -on my-vm
IP=$(govc vm.ip -wait 5m my-vm)
ssh user@"$IP"

# JSON processing
govc vm.info -json my-vm | jq -r '.virtualMachines[0].guest.ipAddress'
govc datastore.info -json | jq '.datastores[] | {name, freeGB: (.freeSpace / 1073741824 | floor)}'
```

## Command Group Index

| Group | Coverage |
|-------|----------|
| `dvs.*` | Distributed virtual switches |
| `pool.*` | Resource pools |
| `folder.*` | Inventory folders |
| `cluster.*` | Cluster operations |
| `object.*` | Generic object operations |
| `tags.*` | Tag management |
| `metric.*` | Performance counters |
| `library.*` | Content library |
| `device.*` | VM device management |
