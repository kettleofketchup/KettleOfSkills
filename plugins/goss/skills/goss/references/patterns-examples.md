---
description: Common goss test pattern examples - web server, security baseline, container smoke test
last_updated: 2026-03-18
---

# Goss Common Test Pattern Examples

## Web Server Validation

```yaml
package:
  nginx: {installed: true}
service:
  nginx: {enabled: true, running: true}
port:
  tcp:80: {listening: true}
  tcp:443: {listening: true}
process:
  nginx: {running: true}
file:
  /etc/nginx/nginx.conf:
    exists: true
    mode: "0644"
http:
  http://localhost:80/:
    status: 200
    body: ["Welcome"]
```

## Security Baseline

```yaml
file:
  /etc/shadow: {exists: true, mode: "0640", owner: root, group: shadow}
  /etc/passwd: {exists: true, mode: "0644", owner: root}
  /etc/ssh/sshd_config:
    exists: true
    contents:
      - "PermitRootLogin no"
      - "PasswordAuthentication no"
      - "/^MaxAuthTries [1-5]$/"
kernel-param:
  net.ipv4.ip_forward: {value: "1"}
  net.ipv4.conf.all.rp_filter: {value: "1"}
port:
  tcp:22:
    listening: true
    ip: ["0.0.0.0"]
```

## Docker Container Smoke Test

```yaml
# goss_wait.yaml
http:
  http://localhost:8080/health:
    status: 200
    timeout: 5000

# goss.yaml
process:
  app: {running: true}
port:
  tcp:8080: {listening: true}
http:
  http://localhost:8080/api/version:
    status: 200
    body:
      - gjson:
          path: version
          content:
            semver-constraint: ">=1.0.0"
user:
  appuser:
    exists: true
    uid: 1000
file:
  /app/config.yaml:
    exists: true
command:
  check-no-root:
    exec: whoami
    exit-status: 0
    stdout: ["!root"]
```
