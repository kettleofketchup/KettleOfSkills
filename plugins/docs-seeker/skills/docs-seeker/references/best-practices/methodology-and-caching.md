# Best Practices: Methodology & Caching

## 4. Report Methodology

### Why

- **Transparency**: User knows how you found info
- **Reproducibility**: User can verify
- **Troubleshooting**: Helps debug issues
- **Trust**: Builds confidence in results

### What to Include

**Always report:**
```markdown
## Source

**Method**: llms.txt / Repository / Research / Mixed
**Primary source**: [main URL or repository]
**Additional sources**: [list]
**Date accessed**: [current date]
**Version**: [documentation version]
```

**For llms.txt:**
```markdown
**Method**: llms.txt
**URL**: https://docs.astro.build/llms.txt
**URLs processed**: 8
**Date accessed**: 2025-10-26
**Version**: Latest (as of Oct 2025)
```

**For repository:**
```markdown
**Method**: Repository analysis (Repomix)
**Repository**: https://github.com/org/library
**Commit**: abc123f (2025-10-20)
**Analysis date**: 2025-10-26
```

### Limitations Disclosure

Always note:
```markdown
## Limitations

- Documentation for v2.x (user may need v3.x)
- API reference section incomplete
- Examples based on TypeScript (Python unavailable)
- Last updated 6 months ago
```

## 7. Time Management

### Timeouts

```
WebSearch: 30 seconds
WebFetch: 60 seconds
Repository clone: 5 minutes
Repomix processing: 10 minutes
Explorer agent: 5 minutes per URL
Researcher agent: 10 minutes
```

### When to Give Up

Move to next method after:
- 3 failed attempts on same approach
- Timeout exceeded by 2x
- No progress for 30 seconds
- Error indicates permanent failure (404, auth required)

## 8. Cache Findings

### What to Cache

**High value (always cache):**
```
- Repomix output (large, expensive to generate)
- llms.txt content (static, frequently referenced)
- Repository README (relatively static)
- Package registry metadata (changes rarely)
```

**Low value (don't cache):**
```
- Real-time data (latest releases)
- User-specific content
- Time-sensitive information
```

### Cache Duration

```
Within conversation:
- All fetched content (reuse freely)

Within session:
- Repomix output (until conversation ends)
- llms.txt content (until new version requested)

Across sessions:
- Don't cache (start fresh each time)
```

### Cache Invalidation

Refresh cache when:
```
- User requests specific different version
- User says "get latest" or "refresh"
- Explicit time reference ("docs from today")
- Previous cache is from different library
```

### Cache Hit Messages

```markdown
Using cached llms.txt from 5 minutes ago.
To fetch fresh, say "refresh" or "get latest".
```

## Quality Gates

Ask before presenting:
- [ ] Is information accurate?
- [ ] Are sources official?
- [ ] Does version match request?
- [ ] Are all key topics covered?
- [ ] Are limitations noted?
- [ ] Is methodology documented?
- [ ] Is output well-organized?
