# Agent Skills: Creating & Managing

## What Are Agent Skills?

Agent Skills are modular capabilities that extend Claude's functionality. Each Skill packages:
- Instructions and procedural knowledge
- Metadata (name, description)
- Optional resources (scripts, templates, references)

Skills are automatically discovered and used by Claude when relevant.

## Skill Structure

### Basic Structure
```
.claude/skills/
└── my-skill/
    ├── skill.md       # Instructions (required)
    └── skill.json     # Metadata (required)
```

### With Resources
```
.claude/skills/
└── my-skill/
    ├── skill.md
    ├── skill.json
    ├── scripts/       # Executable code
    ├── references/    # Documentation
    └── assets/        # Templates, images
```

## Creating Skills

### skill.json
```json
{
  "name": "my-skill",
  "description": "Brief description of when to use this skill",
  "version": "1.0.0",
  "author": "Your Name"
}
```

**Key fields:**
- `name`: Unique identifier (kebab-case)
- `description`: When Claude should activate this skill
- `version`: Semantic version

### skill.md
```markdown
# Skill Name

Description of what this skill does.

## When to Use This Skill
Specific scenarios when Claude should activate.

## Instructions
Step-by-step instructions for Claude.

## Examples
Concrete examples of skill usage.
```

## Best Practices

### Clear Activation Criteria
**Good:** `Use when creating React components with TypeScript and Tailwind CSS.`
**Bad:** `Use for frontend development.`

### Concise Instructions
**Good:** Numbered steps with specific actions
**Bad:** Verbose, uncertain language

### Scope Limitation
**Good:** `api-testing`, `db-migrations` (focused)
**Bad:** `general-development` (too broad)

## Resource Types

### Scripts (`scripts/`)
Executable code for deterministic tasks.
Use for: repeated code generation, deterministic transformations, external tool integrations.

### References (`references/`)
Documentation loaded into context as needed.
Use for: API docs, database schemas, domain knowledge, detailed workflows.

### Assets (`assets/`)
Files used in output (templates, images, boilerplate).

## Skill Discovery

Claude automatically discovers skills from:
1. **Global skills**: `~/.claude/skills/`
2. **Project skills**: `.claude/skills/`
3. **Plugin skills**: From installed plugins

Skills activate when: task matches description, user explicitly invokes, or context suggests relevance.

## Managing Skills

```bash
claude skills list              # List skills
claude --skill my-skill "task"  # Test skill

# Package and share
cd .claude/skills/my-skill
tar -czf my-skill.tar.gz .

# Install
cd .claude/skills/
tar -xzf my-skill.tar.gz
```

## Progressive Disclosure

Keep skill.md concise (<200 lines):
1. **Core instructions** in skill.md
2. **Detailed docs** in references/
3. **Executable code** in scripts/
4. **Templates** in assets/
