# Error Handling: Conflicts, Rate Limits & Network Issues

## Multiple Conflicting Sources

### Symptoms

- Different installation instructions, conflicting API signatures, version mismatches

### Resolution Steps

**1. Check version of each source:** Note version number, last-updated date, URL version indicator.

**2. Prioritize sources:**
```
1. Official docs (latest version)
2. Official docs (specified version)
3. Package registry (verified)
4. Official repository README
5. Community tutorials (recent)
6. Stack Overflow (recent, high votes)
```

**3. Present both with context:**
```markdown
## Installation (v1.x - Legacy)
[old method]
Source: [link] (Last updated: [date])

## Installation (v2.x - Current)
[new method]
Note: v2.x is recommended for new projects.
```

**4. Document discrepancy:**
```markdown
## Conflicting Information Found

**Source 1** (official docs): Method A
**Source 2** (repository): Method B

**Analysis**: Source 1 reflects v2.x API. Source 2 README not yet updated.
**Recommendation**: Use Method A (official docs).
```

### Version Identification

Check: URL path `/docs/v2/`, page header/footer, version selector dropdown, Git branch/tag, CHANGELOG.md dates.

## Rate Limiting

### Symptoms

- 429 Too Many Requests, 403 Forbidden (temporary), slow responses

### Solutions

**1. Use alternative sources:**
```
Priority: GitHub → Official docs → Package registry → Archive
```

**2. Batch operations — launch Explorer agents instead of sequential WebFetch.**

**3. Cache aggressively:** Reuse fetched content within session, don't re-fetch same URLs.

**GitHub API:** Anonymous: 60 requests/hour. Switch to alternative source immediately on 429.

## Network Timeouts

### Symptoms

- Request hangs indefinitely, connection timeout, no response received

### Solutions

**1. Set explicit timeouts:**
```
WebSearch: 30 seconds max
WebFetch: 60 seconds max
Repository clone: 5 minutes max
Repomix processing: 10 minutes max
```

**2. Retry sequence:**
```
1st attempt: 60 seconds
2nd attempt: 90 seconds
3rd attempt: Switch to alternative method
```

**3. Use alternative endpoints:** CDN version, regional mirror, cached version (Archive.org).

## Incomplete Documentation

### Handling Strategy

**Identify gaps:**
```markdown
Available: Installation guide, basic usage examples
Incomplete: Advanced features (stub page)
Missing: Migration guide
```

**Supplement from repository:** Check /examples, read test files, analyze TypeScript definitions, check CHANGELOG.

**Note limitations:**
```markdown
Official docs incomplete (as of [date]).
Information inferred from: repository examples, TypeScript definitions.
May not reflect official recommendations.
```

## General Error Principles

1. **Fail fast**: Don't retry same method repeatedly
2. **Fall back**: Have alternative strategies ready
3. **Document**: Note what failed and why
4. **Partial success**: Deliver what you can find

### Recovery Decision Tree

```
Error encountered
  ↓
Is there an obvious alternative?
  YES → Try alternative immediately
  NO → Try next method in sequence
  ↓
Is partial information useful?
  YES → Deliver partial results with notes
  NO → Inform user, request guidance
```
