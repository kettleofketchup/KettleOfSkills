# ArgoCD ApplicationSets - Advanced

## Merge Generator

Combine generators with override priority:

```yaml
spec:
  generators:
    - merge:
        mergeKeys:
          - cluster
        generators:
          - clusters: {}
          - list:
              elements:
                - cluster: production
                  replicas: "5"
```

## Pull Request Generator

Generate from open PRs:

```yaml
spec:
  generators:
    - pullRequest:
        github:
          owner: org
          repo: myrepo
          tokenRef:
            secretName: github-token
            key: token
        filters:
          - branchMatch: "feature-.*"
  template:
    metadata:
      name: 'pr-{{number}}'
    spec:
      source:
        targetRevision: '{{head_sha}}'
```

## Sync Policy

```yaml
spec:
  syncPolicy:
    preserveResourcesOnDeletion: true  # Don't delete apps when AppSet deleted
  template:
    spec:
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

## Go Templating

Enable Go templates for advanced logic:

```yaml
spec:
  goTemplate: true
  goTemplateOptions: ["missingkey=error"]
  template:
    metadata:
      name: '{{.name | lower}}'
      {{- if .labels }}
      labels:
        {{- range $k, $v := .labels }}
        {{ $k }}: {{ $v }}
        {{- end }}
      {{- end }}
```

## Progressive Syncs (Rolling Update)

```yaml
spec:
  strategy:
    type: RollingSync
    rollingSync:
      steps:
        - matchExpressions:
            - key: env
              operator: In
              values: [staging]
        - matchExpressions:
            - key: env
              operator: In
              values: [production]
          maxUpdate: 25%  # Update 25% at a time
```
