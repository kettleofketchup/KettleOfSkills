# Enterprise Features

Enterprise deployment, security, compliance, and monitoring for Claude Code.

- **IAM, Security, and Compliance** — SSO (Okta/Azure AD/Google), RBAC, sandboxing, audit logging, data governance, network config: `references/enterprise-iam-security.md`
- **Deployment, Monitoring, and HA** — Bedrock, Vertex AI, self-hosted (Docker/Kubernetes), LiteLLM gateway, OpenTelemetry, cost management, load balancing: `references/enterprise-deployment.md`

## Compliance Certifications

SOC 2 Type II, HIPAA, GDPR, ISO 27001

## Quick Reference

```bash
# User management
claude admin user add user@company.com --role developer
claude admin user list

# Analytics
claude analytics usage --start 2025-11-01 --end 2025-11-06
claude analytics cost --group-by user
```

## See Also

- Network configuration: https://docs.claude.com/claude-code/network-config
- Compliance: https://docs.claude.com/claude-code/legal-and-compliance
