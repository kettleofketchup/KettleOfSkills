# Publishing a GitLab CI/CD Catalog Component

Lessons captured from publishing `inf/s3-sync` (graynet-edge GitLab 18.11.2-EE).
Use this when building a catalog component repo from scratch on self-managed GitLab.

## Repo layout

```
my-catalog/
├── README.md                   # catalog landing page (required for catalog publication)
├── CHANGELOG.md                # required if release.description points at it
├── LICENSE                     # SPDX-recognized (MIT/Apache-2.0) — required by catalog
├── .gitlab-ci.yml              # lint + publish-on-tag
├── .yamllint                   # config (see "yamllint quirks" below)
├── templates/
│   ├── <component-1>.yml       # one component per file, OR
│   └── <component-2>/template.yml  # directory form with template.yml
└── examples/
    └── consumer.gitlab-ci.yml  # copy-pasteable example
```

Component reference path for consumers: `$CI_SERVER_FQDN/<full-project-path>/<component-name>@<version>`. The component-name is the YAML filename without extension (or the directory name in the directory form).

## Project setup checklist

1. **GitLab version ≥ 17.0** for CI/CD Catalog support (Free tier on 17.6+; Premium-only on 17.0–17.5).
2. **Set project description** — surfaces as the one-line summary in catalog search results.
3. **Toggle "CI/CD Catalog project"** at *Settings → General → Visibility, project features, permissions*. Without this flag, tag-pipeline `release:` jobs still create GitLab Releases but the version isn't promoted to a catalog resource.
4. **LICENSE file at root** with SPDX-recognized identifier. Catalog publication fails without it.
5. **At least one git tag matching `vX.Y.Z`** (annotated preferred).

## CI/CD variables a component pipeline needs

When the component or its publish job touches the org's internal CA-signed GitLab (rather than gitlab.com), you'll likely need:

| Variable | Type | Purpose |
|---|---|---|
| `<ORG>_CA_PEM` | **File** | Org root CA so glab/release-cli/skopeo can verify the GitLab API's TLS cert. **Type must be File** — File-type stores the value as a file and exposes the *path* in the env var; `Variable` type passes the contents directly. Scripts that do `[ -f "$VAR" ]` only work with File type. |

Settings on the variable:
- **Protect: OFF** unless the publishing tag is on a *protected tag*. By default tag pipelines for `vX.Y.Z` are not on protected tags, and protected variables are filtered out of unprotected pipelines.
- **Mask: OFF** — file-type vars can't be masked anyway.
- **Environment scope: `*`** — restricting to e.g. `production` means jobs without matching `environment:` don't see the variable.

## The `.gitlab-ci.yml` for the catalog repo

```yaml
default:
  interruptible: true

stages:
  - validate
  - publish

# Dual-mode: handles shell executor (image: ignored, has nix) and docker executor.
yamllint:
  stage: validate
  image:
    name: pipelinecomponents/yamllint:latest
    entrypoint: [""]
  variables:
    LC_ALL: C.UTF-8
    LANG: C.UTF-8
  script:
    - |
      set -eu
      if command -v yamllint >/dev/null 2>&1; then
        yamllint -c .yamllint templates/ examples/
      elif command -v nix >/dev/null 2>&1; then
        nix shell nixpkgs#yamllint --command yamllint -c .yamllint templates/ examples/
      else
        echo "ERROR: neither yamllint nor nix is available"
        exit 1
      fi
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG

# image: REQUIRED — release-cli image bundles the binary for the release: keyword.
publish-component:
  stage: publish
  image: registry.gitlab.com/gitlab-org/release-cli:latest
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
  interruptible: false   # never auto-cancel a publish mid-flight
  script:
    - echo "Publishing $CI_PROJECT_PATH/$CI_COMMIT_TAG to ${CI_SERVER_FQDN}/explore/catalog"
    - test -f CHANGELOG.md || { echo "CHANGELOG.md missing"; exit 1; }
    # Build temp CA bundle + export SSL_CERT_FILE (works on docker and NixOS shell executors).
    - |
      if [ -n "${ORG_CA_PEM:-}" ] && [ -f "${ORG_CA_PEM}" ]; then
        BUNDLE=$(mktemp)
        if [ -r /etc/ssl/certs/ca-certificates.crt ]; then
          cat /etc/ssl/certs/ca-certificates.crt > "$BUNDLE"
        fi
        cat "$ORG_CA_PEM" >> "$BUNDLE"
        export SSL_CERT_FILE="$BUNDLE"
        echo "SSL_CERT_FILE=$BUNDLE" >> "${GITLAB_ENV:-/dev/null}"
      else
        echo "WARNING: ORG_CA_PEM not set; release-cli may fail TLS verification"
      fi
  release:
    tag_name: "$CI_COMMIT_TAG"
    name: "<project> $CI_COMMIT_TAG"
    description: |
      <project> catalog release $CI_COMMIT_TAG.

      Components: <list>
      Changelog:  $CI_PROJECT_URL/-/blob/$CI_COMMIT_TAG/CHANGELOG.md
```

## yamllint quirks for catalog component templates

GitLab catalog component templates use a `spec.inputs:` block that benefits from column-aligned inline-flow YAML for readability:

```yaml
spec:
  inputs:
    source:           { type: string }
    destination_repo: { type: string }
    destination_tag:    { type: string, default: "$CI_COMMIT_TAG" }
```

yamllint's default rules reject this alignment with `too many spaces after colon` / `too many spaces inside braces` / `too many spaces after comma`. Relax them in `.yamllint`:

```yaml
extends: default
rules:
  line-length:    { max: 200 }
  truthy:         { check-keys: false }
  document-start: disable
  colons:         { max-spaces-after: -1 }
  braces:         { max-spaces-inside: -1 }
  commas:         { max-spaces-after: -1 }
```

`-1` disables the max-spaces ceiling.

## More

- [Runner gotchas, verification steps, and failure recovery](cicd-catalog-publishing-ops.md)
- GitLab docs: [Components development](https://docs.gitlab.com/ci/components/), [Catalog](https://docs.gitlab.com/ci/components/#cicd-catalog)
