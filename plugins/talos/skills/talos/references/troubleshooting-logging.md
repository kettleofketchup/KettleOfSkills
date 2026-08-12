# Talos Linux Log Forwarding Reference

## Forward Service Logs

```yaml
machine:
  logging:
    destinations:
      - endpoint: "udp://host:port/"   # or tcp://
        format: "json_lines"
        extraTags:
          server: s03-rack07
```
- Protocols: UDP (one msg/packet), TCP (newline-separated)
- Only format: `json_lines`; fields: `msg`, `talos-level`, `talos-service`, `talos-time`
- Multiple destinations supported

## Forward Kernel Logs

Via kernel args:
```yaml
machine:
  install:
    extraKernelArgs:
      - talos.logging.kernel=tcp://host:5044/
```
Via runtime document:
```yaml
apiVersion: v1alpha1
kind: KmsgLogConfig
name: remote-log
url: tcp://host:5044/
```
Fields: `clock`, `facility`, `msg`, `priority`, `seq`, `talos-level`, `talos-time`

## Collect Logs (Receiver)
```bash
nc -k -l 5140 | tee -a logs.txt
```
