# ArgoCD ApplicationSets

ApplicationSets generate multiple Applications from templates using generators.

## Basic Structure

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: myappset
  namespace: argocd
spec:
  generators:
    - <generator>
  template:
    metadata:
      name: '{{name}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/org/repo.git
        targetRevision: HEAD
        path: '{{path}}'
      destination:
        server: '{{server}}'
        namespace: '{{namespace}}'
```

## List Generator

Fixed list of parameter sets:

```yaml
spec:
  generators:
    - list:
        elements:
          - cluster: production
            url: https://prod.example.com
            namespace: prod
          - cluster: staging
            url: https://staging.example.com
            namespace: staging
  template:
    metadata:
      name: 'myapp-{{cluster}}'
    spec:
      destination:
        server: '{{url}}'
        namespace: '{{namespace}}'
```

## Cluster Generator

Generate from registered ArgoCD clusters:

```yaml
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            env: production
        # Or match all clusters:
        # selector: {}
  template:
    metadata:
      name: 'myapp-{{name}}'
    spec:
      destination:
        server: '{{server}}'
        namespace: myapp
```

Built-in parameters: `{{name}}`, `{{server}}`, `{{metadata.labels.<key>}}`, `{{metadata.annotations.<key>}}`

## Git Generator - Directory

Generate from directories in a Git repo:

```yaml
spec:
  generators:
    - git:
        repoURL: https://github.com/org/repo.git
        revision: HEAD
        directories:
          - path: apps/*
          - path: apps/excluded
            exclude: true
  template:
    metadata:
      name: '{{path.basename}}'
    spec:
      source:
        path: '{{path}}'
```

Parameters: `{{path}}`, `{{path.basename}}`, `{{path[n]}}`

## Git Generator - Files

Generate from JSON/YAML files:

```yaml
spec:
  generators:
    - git:
        repoURL: https://github.com/org/repo.git
        revision: HEAD
        files:
          - path: "config/**/config.json"
  template:
    metadata:
      name: '{{name}}'
    spec:
      source:
        path: '{{path}}'
      destination:
        namespace: '{{namespace}}'
```

File content fields become template parameters.

See [applicationsets/advanced.md](applicationsets/advanced.md) for Matrix, Merge, Pull Request generators, Go templating, and Progressive Syncs.
