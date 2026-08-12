# Best Practices: Discovery & Source Verification

## 1. Prioritize llms.txt Discovery

### Why

- **AI-friendly format**: Standardized documentation for LLM consumption
- **Efficient**: Single file indexes all documentation URLs
- **Growing adoption**: Increasingly available across popular libraries

### Implementation

```
Step 1: WebSearch for llms.txt
  ↓
Known domain?
  YES → Try https://docs.[library].com/llms.txt
  NO → WebSearch: "[library] llms.txt"
  ↓
Found?
  YES → Use as primary source
  NO → Fall back to repository analysis
```

### Examples

```
Good approach:
1. WebSearch: "Next.js llms.txt site:nextjs.org"
2. Found → WebFetch llms.txt
3. Launch Explorer agents for URLs
Total time: ~30 seconds

Poor approach:
1. Search for various documentation pages
2. Manually collect URLs
3. Process one by one
Total time: ~5 minutes
```

### When Not Available

- If WebSearch finds nothing in 30 seconds → move to repository
- If domain is incorrect → try 2-3 alternatives, then move on
- If documentation is very old → likely doesn't have llms.txt

## 3. Verify Official Sources

### Why

- **Accuracy**: Avoid outdated information
- **Security**: Prevent malicious content
- **Credibility**: Maintain trust
- **Relevance**: Match user's version/needs

### Verification Checklist

**For llms.txt:**
```
[ ] Domain matches official site
[ ] HTTPS connection
[ ] Content format is valid
[ ] URLs point to official docs
[ ] Last-Modified header is recent (if available)
```

**For repositories:**
```
[ ] Organization matches official entity
[ ] Star count appropriate for library
[ ] Recent commits (last 6 months)
[ ] README mentions official status
[ ] Links back to official website
[ ] License matches expectations
```

**For documentation:**
```
[ ] Domain is official
[ ] Version matches user request
[ ] Last updated date visible
[ ] Content is complete (not stubs)
[ ] Links work (not 404s)
```

### Red Flags

- Personal GitHub forks
- Outdated tutorials (more than 2 years old)
- Unmaintained repositories
- Suspicious domains
- No version information
- Conflicting with official docs

### When to Use Unofficial Sources

Acceptable when:
- No official documentation exists
- Clearly labeled as community resource
- Recent and well-maintained
- Cross-referenced with official info
- User is aware of unofficial status

## 5. Handle Versions Explicitly

### Version Detection

**Check these sources:**
```
1. URL path: /docs/v2/
2. Page header/title
3. Version selector on page
4. Git tag/branch name
5. Package.json or equivalent
6. Release date correlation
```

### Version Handling Rules

**User specifies version:**
```
Request: "Documentation for React 18"
→ Search: "React v18 documentation"
→ Verify: Check version in content
→ Report: "Documentation for React v18.2.0"
```

**User doesn't specify:**
```
Request: "Documentation for Next.js"
→ Default: Assume latest
→ Confirm: "I'll find the latest Next.js documentation"
→ Report: "Documentation for Next.js 14.0 (latest as of [date])"
```

**Version mismatch found:**
```
Request: "Docs for v2"
Found: Only v3 documentation
→ Report: "Requested v2, but only v3 docs available. Here's v3 with migration guide."
```
