# ArgoCD Health Checks, Notifications & Cluster Management

## Health Checks

### Built-in Health Status

| Status | Meaning |
|--------|---------|
| Healthy | Resource functioning properly |
| Progressing | Working toward healthy state |
| Degraded | Resource has problems |
| Suspended | Awaiting external event |
| Missing | Resource not found |
| Unknown | Health not determined |

### Custom Health Check (Lua)

```yaml
# argocd-cm ConfigMap
data:
  resource.customizations.health.mycrd.example.com_MyResource: |
    hs = {}
    if obj.status ~= nil then
      if obj.status.phase == "Running" then
        hs.status = "Healthy"
        hs.message = "Resource is running"
      elseif obj.status.phase == "Pending" then
        hs.status = "Progressing"
        hs.message = "Resource is starting"
      else
        hs.status = "Degraded"
        hs.message = obj.status.message or "Unknown issue"
      end
    end
    return hs
```

### Ignore Health Check

```yaml
metadata:
  annotations:
    argocd.argoproj.io/ignore-healthcheck: "true"
```

## Notifications

### Setup

```yaml
# argocd-notifications-cm ConfigMap
data:
  service.slack: |
    token: $slack-token

  trigger.on-sync-succeeded: |
    - when: app.status.sync.status == 'Synced'
      send: [app-sync-succeeded]

  template.app-sync-succeeded: |
    message: |
      Application {{.app.metadata.name}} synced successfully.
      Revision: {{.app.status.sync.revision}}
```

### Subscribe Application

```yaml
metadata:
  annotations:
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: my-channel
```

### Common Triggers

- `on-sync-succeeded`
- `on-sync-failed`
- `on-sync-status-unknown`
- `on-health-degraded`
- `on-deployed`

Supported services: Slack, Teams, Email, PagerDuty, Webhook, Telegram, Opsgenie, Grafana, Mattermost, Rocket.Chat, Google Chat, AWS SQS, GitHub

## Cluster Management

```bash
# Add cluster (uses current kubeconfig context)
argocd cluster add my-context --name production

# List clusters
argocd cluster list

# Remove cluster
argocd cluster rm https://production.example.com
```

### Cluster Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-cluster
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: cluster
type: Opaque
stringData:
  name: production
  server: https://production.example.com
  config: |
    {
      "bearerToken": "...",
      "tlsClientConfig": {
        "insecure": false,
        "caData": "..."
      }
    }
```
