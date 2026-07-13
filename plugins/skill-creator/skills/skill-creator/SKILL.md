---
name: skill-creator
description: Create or update Claude skills. Use for new skills, skill references, skill scripts, optimizing existing skills, extending Claude's capabilities.
license: Complete terms in LICENSE.txt
version: 2.0.0
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing
specialized knowledge, workflows, and tools. They transform Claude from a general-purpose agent
into a specialized agent equipped with procedural knowledge.

**IMPORTANT:**
- Skills are practical instructions for Claude Code to use tools/packages/plugins/APIs — not documentation
- Each skill teaches Claude how to perform a specific development task, not what a tool does
- Claude Code can activate multiple skills automatically to achieve the user's request

For full anatomy details, structure requirements, and bundled resource guidelines:
→ `references/skill-anatomy.md`

### Key Constraints

- Combine related topics into one skill (e.g. `cloudflare`, `docker`, `gcloud` → `devops`)
- `SKILL.md` body: **under 150 lines**; split overflow to `references/` (<150 lines each)
- `description`: **under 200 characters**; specific, not generic/vague
- Writing style: imperative/infinitive form (verb-first), objective, instructional

### Progressive Disclosure Loading

1. **Metadata (name + description)** — always in context (under 200 chars)
2. **SKILL.md body** — loaded when skill triggers (keep under 150 lines)
3. **Bundled resources** — loaded as needed by Claude (unlimited*)

*Scripts can be executed without reading into context window.

## Skill Creation Process

Follow these 6 steps in order. Detailed guidance: `references/creation-process.md`

### Step 1: Understand the Skill with Concrete Examples

Use `AskUserQuestion` to gather concrete usage examples and validate understanding before proceeding.
Conclude when functionality is clearly defined.

### Step 2: Research on the Internet

Activate `/docs-seeker` for documentation. Activate `/research` for best practices, CLI tools,
workflows, and edge cases. Write research reports for use in Step 3.

### Step 3: Plan Reusable Skill Contents

Analyze each concrete example to identify reusable resources:
- `scripts/` — code that gets rewritten repeatedly or needs deterministic reliability
- `references/` — schemas, policies, API docs, workflow guides
- `assets/` — templates, images, boilerplate used in output

Prefer existing CLI tools (via `npx`, `bunx`, `pipx`) over writing custom code.
Scripts must: follow `.env` resolution order (see `references/skill-anatomy.md`), have tests, pass all tests.

### Step 4: Initialize the Skill

Run the init script (skip if skill already exists):
```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```
Customize or remove generated example files afterward.

### Step 5: Edit the Skill

**Start with reusable resources** (`scripts/`, `references/`, `assets/`). Delete unneeded example files.

**Update SKILL.md** — answer: purpose, when to use, how Claude uses it (reference all resources).

**Package when ready:**
```bash
scripts/package_skill.py <path/to/skill-folder>
```
Packaging validates frontmatter, structure, description (≤200 chars), then creates a distributable zip.

### Step 6: Iterate

After testing: use on real tasks → notice struggles/token usage → identify updates → implement → test again.

## Validation Criteria

- **Quick checklist**: `references/validation-checklist.md`
- **Metadata quality**: `references/metadata-quality-criteria.md`
- **Token efficiency**: `references/token-efficiency-criteria.md`
- **Script quality**: `references/script-quality-criteria.md`
- **Structure & organization**: `references/structure-organization-criteria.md`

## Plugin Marketplaces

For distributing skills as plugins via marketplaces, see:
- **Overview**: `references/plugin-marketplace-overview.md`
- **Schema**: `references/plugin-marketplace-schema.md`
- **Sources**: `references/plugin-marketplace-sources.md`
- **Hosting**: `references/plugin-marketplace-hosting.md`
- **Troubleshooting**: `references/plugin-marketplace-troubleshooting.md`

## References
- [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills.md)
- [Agent Skills Spec](../agent_skills_spec.md)
- [Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview.md)
- [Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md)
- [Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces.md)
