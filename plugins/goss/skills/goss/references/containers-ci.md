---
description: CI/CD integration for goss container testing - GitLab CI, GitHub Actions, Dockerfile HEALTHCHECK
last_updated: 2026-03-18
---

# Goss Container CI/CD Integration

## GitLab CI

```yaml
test:
  image: myapp:latest
  script:
    - goss validate --format junit > report.xml
  artifacts:
    reports:
      junit: report.xml
```

## GitHub Actions

```yaml
- name: Test with goss
  run: |
    dgoss run myapp:${{ github.sha }}
  env:
    GOSS_OPTS: "--format junit"
```

## Dockerfile Integration

Embed goss in image for self-testing:

```dockerfile
FROM alpine:3.19
COPY --from=aelsabbahy/goss:latest /usr/local/bin/goss /usr/local/bin/goss
COPY goss.yaml /goss/goss.yaml
HEALTHCHECK --interval=30s CMD goss -g /goss/goss.yaml validate
```
