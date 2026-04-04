# Slash Commands: Docs, Git, Planning & More

Documentation, git, planning, content, design, deployment, and custom commands.

## Documentation Commands

### /docs:init
Create initial documentation structure.
**When to use**: New projects needing documentation

### /docs:update
Update existing documentation based on code changes.
**When to use**: After significant code changes

### /docs:summarize
Summarize codebase and create overview.
**When to use**: Generate project summaries

## Git Commands

### /git:cm
Stage all files and create commit.
**When to use**: Commit changes with automatic message

### /git:cp
Stage, commit, and push all code in current branch.
**When to use**: Commit and push in one command

### /git:pr [branch] [from-branch]
Create pull request.
```bash
/git:pr feature-branch main
```
**When to use**: Creating PRs with automatic descriptions

## Planning Commands

| Command | Description |
|---------|-------------|
| `/plan:two [task]` | Plan with 2 alternative approaches |
| `/plan:ci [url]` | Analyze GitHub Actions logs, create fix plan |
| `/plan:cro [issue]` | Conversion rate optimization plan |

## Content Commands

| Command | Description |
|---------|-------------|
| `/content:fast [request]` | Quick copy writing |
| `/content:good [request]` | High-quality, conversion-focused copy |
| `/content:enhance [issue]` | Enhance existing content |
| `/content:cro [issue]` | Conversion rate optimization for content |

## Design Commands

| Command | Description |
|---------|-------------|
| `/design:fast [task]` | Quick design implementation |
| `/design:good [task]` | High-quality, polished design |
| `/design:3d [task]` | 3D designs with Three.js |
| `/design:screenshot [path]` | Design based on screenshot |
| `/design:video [path]` | Design based on video |

## Deployment Commands

| Command | Description |
|---------|-------------|
| `/deploy` | Deploy using deployment tool |
| `/deploy-check` | Check deployment readiness |

## Integration Commands

| Command | Description |
|---------|-------------|
| `/integrate:polar [tasks]` | Polar.sh payment integration |
| `/integrate:sepay [tasks]` | SePay.vn payment integration |

## Other Commands

| Command | Description |
|---------|-------------|
| `/brainstorm [question]` | Brainstorm features and ideas |
| `/ask [question]` | Answer technical/architectural questions |
| `/scout [prompt] [scale]` | Scout directories |
| `/watzup` | Review recent changes, wrap up |
| `/bootstrap [requirements]` | Bootstrap new project step by step |
| `/bootstrap:auto [requirements]` | Bootstrap automatically |
| `/journal` | Write journal entries |
| `/review:codebase [prompt]` | Scan and analyze codebase |
| `/skill:create [prompt]` | Create new agent skill |

## Creating Custom Slash Commands

### Command File Structure
```
.claude/commands/
└── my-command.md
```

### Example Command File
```markdown
# File: .claude/commands/my-command.md
Create comprehensive test suite for {{feature}}.

Include:
- Unit tests
- Integration tests
- Edge cases
- Mocking examples
```

### Usage
```bash
/my-command authentication
# Expands to: "Create comprehensive test suite for authentication..."
```

### Best Practices
- **Clear prompts**: Write specific, actionable prompts
- **Use variables**: `{{variable}}` for dynamic content
- **Document usage**: Add comments explaining the command
- **Test thoroughly**: Verify commands work as expected

### Command Arguments

**Single:** `/cook implement user auth` -> `"implement user auth"`
**Multiple:** `/git:pr feature-branch main` -> `"feature-branch"`, `"main"`
**Optional:** `/test` (all) or `/test user.test.js` (specific)
