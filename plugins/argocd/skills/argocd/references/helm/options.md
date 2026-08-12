# ArgoCD Helm Options

## Helm Options

```yaml
spec:
  source:
    helm:
      releaseName: myapp
      version: v3  # Helm version
      passCredentials: true  # Pass repo creds to subcharts
      skipCrds: false

      # Validation
      skipSchemaValidation: false

      # API versions for template rendering
      apiVersions:
        - monitoring.coreos.com/v1
      kubeVersion: "1.28.0"
```

## Handling Random Values

Helm functions like `randAlphaNum` cause perpetual drift. Override with explicit values:

```yaml
spec:
  source:
    helm:
      valuesObject:
        secretKey: "my-fixed-secret-value"
```

## Helm Hooks Mapping

ArgoCD auto-maps Helm hooks to ArgoCD hooks:

| Helm Hook | ArgoCD Hook |
|-----------|-------------|
| pre-install, pre-upgrade | PreSync |
| post-install, post-upgrade | PostSync |
| pre-delete | PreSync (with delete policy) |
| post-delete | PostSync (with delete policy) |
