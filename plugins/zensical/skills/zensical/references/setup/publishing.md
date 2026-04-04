---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_url: https://zensical.org/docs/publish-your-site/
related_skills:
  - /github
  - /gitlab-ci
---

# Publishing

## GitHub Pages

Create `.github/workflows/docs.yml`:

```yaml
name: Documentation
on:
  push:
    branches:
      - master
      - main
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/configure-pages@v5
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: 3.x
      - run: pip install zensical
      - run: zensical build --clean
      - uses: actions/upload-pages-artifact@v4
        with:
          path: site
      - uses: actions/deploy-pages@v4
        id: deployment
```

Deploys to `<username>.github.io/<repository>`.

For advanced GitHub Actions patterns (caching, matrix builds, workflow optimization), invoke the `/github` skill.

## GitLab Pages

Create `.gitlab-ci.yml`:

```yaml
pages:
  stage: deploy
  image: python:latest
  script:
    - pip install zensical
    - zensical build --clean
  pages:
    publish: public
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

**Important:** Set `site_dir` to `public` in `zensical.toml` — GitLab requires this directory name:

```toml
[project]
site_dir = "public"
```

Deploys to `<username>.gitlab.io/<repository>`.

For multi-project pipelines, cross-pipeline dependencies, or advanced GitLab CI patterns, invoke the `/gitlab-ci` skill.

## uv-based CI

Replace `pip install zensical` with:

```yaml
- run: pip install uv
- run: uv run zensical build --clean
```

Or use a `pyproject.toml` with zensical as a dev dependency.
