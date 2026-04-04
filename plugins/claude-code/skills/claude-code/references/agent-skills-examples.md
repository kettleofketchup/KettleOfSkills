# Agent Skills: Examples & API Usage

## Using Skills via API

### TypeScript Example
```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

const response = await client.messages.create({
  model: 'claude-sonnet-4-5-20250929',
  max_tokens: 4096,
  skills: [
    {
      type: 'custom',
      custom: {
        name: 'document-creator',
        description: 'Creates professional documents',
        instructions: 'Follow corporate style guide...'
      }
    }
  ],
  messages: [{
    role: 'user',
    content: 'Create a project proposal'
  }]
});
```

### Python Example
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    skills=[
        {
            "type": "custom",
            "custom": {
                "name": "code-reviewer",
                "description": "Reviews code for quality and security",
                "instructions": "Check for common issues..."
            }
        }
    ],
    messages=[{
        "role": "user",
        "content": "Review this code"
    }]
)
```

## Example Skills

### API Testing Skill

**skill.json:**
```json
{
  "name": "api-testing",
  "description": "Test REST APIs with automated requests",
  "version": "1.0.0",
  "author": "Team"
}
```

**skill.md:**
```markdown
# API Testing
Test REST APIs with comprehensive validation.

## When to Use
Use when testing API endpoints, validating responses, or creating API test suites.

## Instructions
1. Read API documentation from references/api-docs.md
2. Use scripts/test-api.py for making requests
3. Validate response status, headers, body
4. Generate test report
```

### Database Migration Skill

**skill.json:**
```json
{
  "name": "db-migrations",
  "description": "Create and manage database migrations",
  "version": "1.0.0"
}
```

**skill.md:**
```markdown
# Database Migrations
Create safe, reversible database schema changes.

## When to Use
Use when modifying database schema, adding tables, or changing column definitions.

## Instructions
1. Review current schema in references/schema.md
2. Create migration file in migrations/
3. Include both up and down migrations
4. Test migration on development database
5. Update references/schema.md
```

## Troubleshooting

### Skill Not Activating
- Check description specificity
- Verify skill.json format
- Ensure skill.md has clear activation criteria

### Resource Not Found
- Verify file paths in skill.md
- Check directory structure
- Use relative paths from skill root

### Conflicting Skills
- Make descriptions more specific
- Use unique names
- Scope skills narrowly

## See Also

- Skill creation guide: https://docs.claude.com/claude-code/skills
- Best practices: https://docs.claude.com/agents-and-tools/agent-skills/best-practices
- API usage: `references/api-reference.md`
- Plugin system: `references/hooks-and-plugins.md`
