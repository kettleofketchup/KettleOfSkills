---
description: GitHub Actions CI pipeline for Foundry VTT modules, packaging ZIP for distribution, release manifest
last_updated: 2026-03-18
---

# CI Pipeline & Packaging

## GitHub Actions Example

```yaml
name: Test Module
on: [push, pull_request]
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm test            # Vitest unit tests

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx eslint src/
      - run: npx tsc --noEmit    # TypeScript type checking

  build:
    runs-on: ubuntu-latest
    needs: [unit-tests, lint]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: module-dist
          path: dist/
```

## Release Workflow

```yaml
name: Release
on:
  push:
    tags: ["v*"]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci && npm run build
      - name: Package ZIP
        run: cd dist && zip -r ../my-module.zip . && cd ..
      - uses: softprops/action-gh-release@v2
        with:
          files: |
            my-module.zip
            dist/module.json
```

## Packaging for Distribution

### Module ZIP Structure

ZIP must contain module files at root level (not nested in subdirectory):

```
my-module.zip
├── module.json
├── scripts/
├── styles/
├── templates/
├── lang/
└── packs/
```

```bash
# Build and package locally
npm run build
cd dist && zip -r ../my-module.zip . && cd ..
```

### Release Manifest URL

Point `manifest` and `download` in module.json to GitHub Releases:

```json
{
  "manifest": "https://github.com/user/my-module/releases/latest/download/module.json",
  "download": "https://github.com/user/my-module/releases/latest/download/my-module.zip"
}
```

Users install via: Setup > Add-on Modules > Install Module > paste manifest URL.

### Versioning

Follow semantic versioning. Bump `version` in module.json before tagging:

```bash
npm version patch    # 1.0.0 -> 1.0.1
npm version minor    # 1.0.0 -> 1.1.0
npm version major    # 1.0.0 -> 2.0.0
git push --follow-tags
```

### ESLint Config

```json
{
  "env": { "browser": true, "es2022": true },
  "extends": ["eslint:recommended"],
  "parserOptions": { "ecmaVersion": 2022, "sourceType": "module" },
  "globals": {
    "game": "readonly", "Hooks": "readonly", "Actor": "readonly",
    "Item": "readonly", "CONFIG": "readonly", "ui": "readonly",
    "foundry": "readonly", "canvas": "readonly"
  }
}
```
