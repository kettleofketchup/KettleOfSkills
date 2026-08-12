# Error Handling: llms.txt & Repository Issues

## llms.txt Not Accessible

**Symptoms:** 404, connection timeout, 403, empty response.

### Troubleshooting Steps

**1. Try alternative official domains:**
```
https://[name].dev/llms.txt
https://[name].io/llms.txt
https://[name].com/llms.txt
https://docs.[name].com/llms.txt
https://www.[name].com/llms.txt
```

**2. Check for redirects:**
- Old domain → new domain
- Non-HTTPS → HTTPS
- Root → /docs subdirectory

**3. Search for llms.txt mention:**
```
WebSearch: "[library] llms.txt"
WebSearch: "[library] documentation AI format"
```

**4. If all fail:**
- Fall back to repository analysis (Phase 3)
- Note in report: "llms.txt not available"

### Common Causes

- Documentation recently moved/redesigned
- llms.txt not yet implemented
- Rate limiting or IP blocking

### Example Resolution

```
Problem: https://example.dev/llms.txt returns 404

Steps:
1. Try: https://docs.example.dev/llms.txt ✓ Works!
2. Note: Documentation moved to docs subdomain
3. Proceed with Phase 2 using correct URL
```

## Repository Not Found

### Symptoms

- GitHub 404 error
- No official repository found
- Repository is private/requires auth
- Multiple competing repositories

### Troubleshooting Steps

**1. Search official website:**
```
WebSearch: "[library] official website"
```

**2. Check package registries:**
```
WebSearch: "[library] npm"
WebSearch: "[library] pypi"
WebSearch: "[library] crates.io"
```

**3. Look for organization GitHub:**
```
WebSearch: "[company] github organization"
WebSearch: "[library] github org:[known-org]"
```

**4. Verify through package manager:**
```bash
# npm example
npm info [package-name] repository

# pip example
pip show [package-name]
```

**5. If all fail:**
- Use Researcher agents (Phase 4)
- Note: "No public repository available"

### Common Causes

- Proprietary/closed-source software
- Documentation separate from code repository
- Company uses internal hosting (GitLab, Bitbucket, self-hosted)
- Repository renamed/moved

### Verification Checklist

When you find a repository, verify:
- [ ] Organization/user matches official entity
- [ ] Star count appropriate for library popularity
- [ ] Recent commits (active maintenance)
- [ ] README mentions official status
- [ ] Links back to official website

## Repomix Failures

**Symptoms:** Out of memory, command hangs, empty/corrupted output, network timeout during clone.

### Troubleshooting Steps

**1. Focus on documentation only:**
```bash
repomix --include "docs/**,README.md,*.md" --output docs.xml
```

**2. Exclude large files:**
```bash
repomix --exclude "*.png,*.jpg,*.pdf,*.zip,dist/**,node_modules/**" --output repomix-output.xml
```

**3. Use shallow clone:**
```bash
git clone --depth 1 [url] /tmp/docs-analysis
cd /tmp/docs-analysis && repomix --output repomix-output.xml
```

**4. Alternative: Explorer agents**
```
If Repomix fails completely:
1. Read README.md directly
2. List /docs directory structure
3. Launch Explorer agents for key files
```

### Size Guidelines

| Repo Size | Strategy |
|-----------|----------|
| less than 50MB | Full Repomix |
| 50-500MB | Exclude binaries / focus on /docs |
| 500MB-1GB | Shallow clone + focused include |
| more than 1GB | Explorer agents only |
