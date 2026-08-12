# Documentation Sources: Hosting Platforms & Search Patterns

## Documentation Hosting Platforms

### Read the Docs

**URL patterns:**
```
https://[project].readthedocs.io
https://readthedocs.org/projects/[project]
```

Features: Version switching, multiple formats (HTML, PDF, ePub), search, often auto-generated from reStructuredText/Markdown.

### GitBook

**URL patterns:**
```
https://[org].gitbook.io/[project]
https://docs.[domain].com
```

Features: Clean interface, good navigation, often manually curated. May require API key for programmatic access.

### Docusaurus

**URL patterns:**
```
https://[project].io
https://docs.[project].com
```

Common in: React ecosystem, Meta/Facebook projects, modern open-source projects.
Features: React-based, fast static site, version management, good search.

### MkDocs

**URL patterns:**
```
https://[user].github.io/[project]
https://[custom-domain].com
```

Features: Python ecosystem, static site from Markdown, often on GitHub Pages, Material theme popular.

### VitePress

**URL patterns:**
```
https://[project].dev
https://docs.[project].com
```

Common in: Vue ecosystem, modern projects. Features: Vue-powered, very fast, clean design.

## Documentation Search Patterns

### Finding llms.txt

```
"[library] llms.txt site:[known-domain]"
```

Common domains to try:
```
site:docs.[library].com
site:[library].dev
site:[library].io
site:[library].org
```

### Finding Official Repository

```
"[library] official github repository"
"[library] source code github"
```

Verification: Check organization is official, verify star count, check last commit date, look for official links in README.

### Finding Official Documentation

```
"[library] official documentation"
"[library] docs site:official-domain"
"[library] API reference"
```

Domain patterns:
```
docs.[library].com
[library].dev/docs
docs.[library].io
[library].readthedocs.io
```

## Common Documentation Structures

### Typical Section Names

**Getting started:** Getting Started, Quick Start, Introduction, Installation, Setup

**Core concepts:** Core Concepts, Fundamentals, Basics, Key Concepts, Architecture

**Guides:** Guides, How-To Guides, Tutorials, Examples, Recipes

**Reference:** API Reference, API Documentation, Reference, CLI Reference

**Advanced:** Advanced, Advanced Topics, Deep Dives, Internals, Performance

### Common File Names

```
README.md, GETTING_STARTED.md, INSTALLATION.md
CONTRIBUTING.md, CHANGELOG.md, API.md
TUTORIAL.md, EXAMPLES.md, FAQ.md
```

## Framework-Specific Patterns

### React Ecosystem

- Uses Docusaurus
- Documentation at [project].dev or docs.[project].com
- Often has interactive examples (CodeSandbox/StackBlitz)

### Vue Ecosystem

- Uses VitePress
- Documentation at [project].vuejs.org
- Bilingual (English/Chinese)
- API reference auto-generated

### Python Ecosystem

- Read the Docs hosting
- Sphinx-generated, reStructuredText format
- [project].readthedocs.io

### Rust Ecosystem

- docs.rs for API docs
- Book format for guides ([project].rs/book)
- Markdown in repository, well-structured examples/
