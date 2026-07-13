# Skill Anatomy & Structure

## What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Directory Structure

```
.claude/skills/
└── skill-name/
    ├── SKILL.md (required)
    │   ├── YAML frontmatter metadata (required)
    │   │   ├── name: (required)
    │   │   ├── description: (required)
    │   │   ├── license: (optional)
    │   │   └── version: (optional)
    │   └── Markdown instructions (required)
    └── Bundled Resources (optional)
        ├── scripts/          - Executable code (Python/Bash/etc.)
        ├── references/       - Documentation loaded into context as needed
        └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

## Key Requirements

- Combine related topics (e.g. `cloudflare`, `docker`, `gcloud` → `devops`)
- `SKILL.md` body: **under 150 lines**; split overflow to `references/` (<150 lines each)
- `description`: **under 200 characters**; specific, not generic/vague
- Writing style: imperative/infinitive form (verb-first), not second person

## Progressive Disclosure Loading

1. **Metadata (name + description)** - Always in context (under 200 chars)
2. **SKILL.md body** - Loaded when skill triggers (keep under 150 lines / ~5k words)
3. **Bundled resources** - Loaded as needed by Claude (unlimited*)

*Scripts can be executed without reading into context window.

## Bundled Resource Types

### scripts/

Executable code for tasks requiring deterministic reliability or repeated rewriting.
- Prefer Node.js or Python over Bash (Windows compatibility)
- Python scripts: include `requirements.txt`
- `.env` resolution order: `process.env` > `~/.claude/skills/${SKILL}/.env` > `~/.claude/skills/.env` > `~/.claude/.env` > `./.claude/skills/${SKILL}/.env` > `./.claude/skills/.env` > `./.claude/.env`
- Include `.env.example` for required env vars
- Write and run tests; fix failures before shipping

### references/

Documentation loaded into context to inform Claude's thinking.
- Use for: schemas, best practices, workflows, cheatsheets, API docs, policies
- Keeps SKILL.md lean; avoid duplicating info between SKILL.md and references
- Split files over 150 lines into multiple smaller files

### assets/

Files used in skill output, not loaded into context.
- Use for: templates, images, icons, boilerplate code, fonts, sample documents
