# Vault Issuer

Signs certificates using HashiCorp Vault PKI secrets engine.

## Prerequisites

- Vault PKI secrets engine enabled
- PKI role configured with allowed domains
- Authentication method configured (AppRole, Kubernetes, Token, JWT)

## Vault Issuer Spec

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: vault-issuer
  namespace: sandbox
spec:
  vault:
    server: https://vault.example.com
    path: pki_int/sign/example-role  # Must use 'sign' endpoint
    caBundle: <base64-encoded-ca-bundle>
    auth:
      kubernetes:
        role: cert-manager
        mountPath: /v1/auth/kubernetes
        serviceAccountRef:
          name: cert-manager
```

## Auth Methods

| Method | Use Case |
|--------|----------|
| `kubernetes` | Vault inside cluster or can reach K8s API |
| `appRole` | RoleID/SecretID stored in K8s Secret |
| `tokenSecretRef` | Pre-generated token (requires external refresh) |
| `jwt` | OIDC discovery reachable from Vault |

## Debugging

```bash
# Verify issuer readiness
kubectl get issuer vault-issuer -n sandbox -o wide

# Check Vault connectivity (issuer tests v1/sys/health)
kubectl describe issuer vault-issuer -n sandbox
```

Common errors:
- `permission denied` - Vault policy doesn't allow cert signing
- `unknown role` - PKI role name incorrect in path
- `token expired` - Refresh token or use Kubernetes auth
