# Enterprise Features — IAM, Security, and Compliance

Identity management, RBAC, sandboxing, audit logging, and data governance.

## Identity & Access Management

### SSO Integration

SAML 2.0 and OAuth 2.0 support:

```json
{
  "auth": {
    "type": "saml",
    "provider": "okta",
    "entityId": "claude-code",
    "ssoUrl": "https://company.okta.com/app/saml",
    "certificate": "/path/to/cert.pem"
  }
}
```

Supported providers: Okta, Azure AD, Google Workspace, OneLogin, Auth0

### RBAC

```json
{
  "rbac": {
    "roles": {
      "developer": { "permissions": ["code:read", "code:write", "tools:use"] },
      "reviewer":  { "permissions": ["code:read", "code:review"] },
      "admin":     { "permissions": ["*"] }
    }
  }
}
```

User management:
```bash
claude admin user add user@company.com --role developer
claude admin user remove user@company.com
claude admin user list
```

## Security & Compliance

### Sandboxing

```json
{
  "sandboxing": {
    "enabled": true, "mode": "strict",
    "filesystem": {
      "allowedPaths": ["/workspace"],
      "readOnlyPaths": ["/usr/lib"],
      "deniedPaths": ["/etc/passwd", "/etc/shadow"]
    },
    "network": { "enabled": false, "allowedDomains": ["api.anthropic.com"] }
  }
}
```

### Audit Logging

```json
{
  "auditLog": {
    "enabled": true,
    "destination": "syslog",
    "syslogHost": "logs.company.com:514",
    "includeToolCalls": true,
    "includePrompts": false,
    "retention": "90d"
  }
}
```

### Compliance Certifications

SOC 2 Type II, HIPAA, GDPR, ISO 27001

### Data Governance

**Data Retention:**
```json
{
  "dataRetention": {
    "conversations": "30d", "logs": "90d", "metrics": "1y"
  }
}
```

**Encryption:**
```json
{
  "encryption": {
    "atRest": { "enabled": true, "algorithm": "AES-256-GCM", "keyManagement": "aws-kms" },
    "inTransit": { "tlsVersion": "1.3" }
  }
}
```

**PII Protection:**
```json
{
  "piiProtection": {
    "enabled": true,
    "detectPatterns": ["email", "ssn", "credit_card"],
    "action": "redact"
  }
}
```

## Network Configuration

### Proxy and CA

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1,company.internal
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/company-ca.crt
```

### mTLS and IP Allowlist

```json
{
  "mtls": {
    "enabled": true,
    "clientCert": "/path/to/client-cert.pem",
    "clientKey": "/path/to/client-key.pem"
  },
  "ipAllowlist": {
    "enabled": true,
    "addresses": ["10.0.0.0/8", "192.168.1.0/24"]
  }
}
```

## See Also

- Deployment options: `references/enterprise-deployment.md`
- Monitoring: https://docs.claude.com/claude-code/monitoring
- Compliance: https://docs.claude.com/claude-code/legal-and-compliance
