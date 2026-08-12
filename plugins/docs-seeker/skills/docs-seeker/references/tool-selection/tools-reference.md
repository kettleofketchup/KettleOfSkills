# Tool Selection: Tools Reference

## WebSearch

**Use when:**
- Searching for llms.txt URLs
- Finding GitHub repository URLs
- Locating official documentation sites
- Identifying package registries
- Searching for specific versions

**Best practices:**
- Include domain in query: `site:docs.example.com`
- Specify version when needed: `v2.0 llms.txt`
- Use official terms: "official repository" "documentation"
- Check multiple domains if first fails

**Example queries:**
```
Good: "Next.js llms.txt site:nextjs.org"
Good: "React v18 documentation site:react.dev"
Good: "Vue 3 official github repository"

Avoid: "how to use react" (too vague)
Avoid: "best react tutorial" (not official)
```

## WebFetch

**Use when:**
- Reading llms.txt content
- Accessing single documentation pages
- Verifying content availability

**Best practices:**
- Use specific prompt: "Extract all documentation URLs"
- Handle redirects properly
- Check for rate limiting
- Note last-modified dates when available

**Limitations:**
- Single URL at a time (use Explorer for multiple)
- May timeout on very large pages
- Cannot handle dynamic content

## Task Tool with Explore Subagent

**Use when:**
- Multiple URLs to read (3+)
- Need parallel exploration
- Time-sensitive requests

**Best practices:**
- Launch all agents in single message
- Distribute workload evenly
- Group related URLs per agent
- Maximum 7 agents per batch

**Example prompt:**
```
"Read the following URLs and extract:
1. Installation instructions
2. Core API methods
3. Configuration options
4. Common usage examples

URLs: [url1], [url2], [url3]"
```

## Task Tool with Researcher Subagent

**Use when:**
- No structured documentation found
- Need diverse information sources
- Scattered documentation

**Best practices:**
- Assign specific research areas per agent
- Request source verification
- Ask for date/version information
- Prioritize official sources

## Repomix

**Use when:**
- GitHub repository available
- Documentation scattered in repository
- API documentation in code comments

**Installation:**
```bash
npm install -g repomix  # if needed
repomix --version
```

**Usage:**
```bash
git clone [repo-url] /tmp/docs-analysis
cd /tmp/docs-analysis
repomix --output repomix-output.xml

# Focus on specific directory
repomix --include "docs/**" --output docs-only.xml

# Exclude large files
repomix --exclude "*.png,*.jpg,*.pdf" --output repomix-output.xml
```

**When Repomix may fail:**
- Repository more than 1GB
- Private repository (requires auth)
- Limited disk space

## Quick Reference

| Tool | Best For | Speed | Coverage | Complexity |
|------|----------|-------|----------|------------|
| WebSearch | Finding URLs/llms.txt | Fast | Narrow | Low |
| WebFetch | Single page | Fast | Single | Low |
| Explorer | Multiple URLs | Fast | Medium | Medium |
| Researcher | Scattered info | Slow | Wide | High |
| Repomix | Repository | Medium | Complete | Medium |
