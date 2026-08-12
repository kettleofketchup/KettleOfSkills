# Enterprise Features — Deployment, Monitoring, and HA

Deployment options, monitoring, analytics, and high availability.

## Deployment Options

### Amazon Bedrock

```json
{
  "provider": "bedrock",
  "region": "us-east-1",
  "model": "anthropic.claude-sonnet-4-5",
  "credentials": {
    "accessKeyId": "${AWS_ACCESS_KEY_ID}",
    "secretAccessKey": "${AWS_SECRET_ACCESS_KEY}"
  }
}
```

### Google Vertex AI

```json
{
  "provider": "vertex",
  "project": "company-project",
  "location": "us-central1",
  "model": "claude-sonnet-4-5",
  "credentials": "/path/to/service-account.json"
}
```

### Self-Hosted

Docker: `docker run -d -v /workspace:/workspace -e ANTHROPIC_API_KEY=$API_KEY anthropic/claude-code:latest`

Kubernetes: deploy with `anthropic/claude-code:latest` image, inject `ANTHROPIC_API_KEY` from a Secret.

LiteLLM gateway:
```json
{ "gateway": { "enabled": true, "url": "http://litellm-proxy:4000", "apiKey": "${GATEWAY_API_KEY}" } }
```

Data residency:
```json
{ "region": "us-east-1", "dataResidency": { "enabled": true, "allowedRegions": ["us-east-1"] } }
```

## Monitoring & Analytics

### OpenTelemetry

```json
{
  "telemetry": {
    "enabled": true, "exporter": "otlp",
    "endpoint": "http://otel-collector:4317",
    "metrics": true, "traces": true, "logs": true
  }
}
```

### Usage Analytics

```bash
claude analytics usage --start 2025-11-01 --end 2025-11-06
claude analytics cost --group-by user
claude analytics export --format csv > metrics.csv
```

Metrics tracked: requests/user/project, token usage, tool invocations, session duration, error rates, cost.

### Cost Management

```json
{
  "costControl": {
    "enabled": true,
    "budgets": { "monthly": 10000, "perUser": 500 },
    "alerts": { "threshold": 0.8, "recipients": ["admin@company.com"] }
  }
}
```

## High Availability

### Load Balancing (HAProxy)

```
frontend claude_front
  bind *:443 ssl crt /etc/ssl/certs/claude.pem
  default_backend claude_back

backend claude_back
  balance roundrobin
  server claude1 10.0.1.10:8080 check
  server claude2 10.0.1.11:8080 check
```

### Failover Configuration

```json
{
  "highAvailability": {
    "enabled": true,
    "primaryRegion": "us-east-1",
    "failoverRegions": ["us-west-2", "eu-west-1"],
    "healthCheck": { "interval": "30s", "timeout": "5s" }
  }
}
```

### Backup & Recovery

```bash
claude admin backup configure \
  --schedule "0 2 * * *" --retention 30d \
  --destination s3://backups/claude-code

claude admin backup create
claude admin backup restore backup-20251106
```

## See Also

- IAM and security: `references/enterprise-iam-security.md`
- Monitoring: https://docs.claude.com/claude-code/monitoring
- Network config: https://docs.claude.com/claude-code/network-config
