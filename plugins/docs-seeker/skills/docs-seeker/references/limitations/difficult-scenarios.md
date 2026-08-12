# Limitations: Difficult Scenarios

Scenarios where documentation discovery may struggle, with mitigation strategies and success rates.

## Very Large Repositories (more than 1GB)

**Challenge:** Repomix may fail or hang; output file too large to read. **Success rate:** ~30%.

**Mitigation:**
```
1. Try shallow clone: git clone --depth 1
2. Focus on docs only: repomix --include "docs/**"
3. Exclude binaries: --exclude "*.png,*.jpg,dist/**"
4. If fails: Use Explorer agents on specific files
```

**Skip Repomix when:** Clone shows more than 1GB download, contains large binaries, or has extensive history (more than 10k commits). Use targeted exploration instead.

## Documentation in Images/PDFs

**Challenge:** Cannot reliably extract text from images; PDF parsing limited; code snippets may be corrupted. **Success rate:** ~50% for PDFs, ~10% for images.

**Mitigation:**
```
1. Search for text alternative
2. Try OCR if critical (low quality)
3. Provide image URL instead
4. Note content not extractable
5. Recommend manual review
```

**Report template:**
```markdown
Image-Based Documentation

Primary documentation in PDF/images: [url]

Extraction quality: Limited
Recommendation: Download and review manually

Text alternatives found:
- [any alternatives]
```

## Non-English Documentation

**Challenge:**
- No automatic translation
- May miss context/nuance
- Technical terms may not translate well

**Success rate:** Variable (depends on user needs)

**Mitigation:**
```
1. Note language in report
2. Offer key section translation if user requests
3. Search for English version
4. Check if bilingual docs exist
5. Provide original with language note
```

**Report template:**
```markdown
Language Notice

Primary documentation in: Japanese

English availability:
- Partial translation: [url]
- No official English version found

Recommendation: Use translation tool or request community help.
```

## Scattered Documentation

**Challenge:**
- Multiple sites/repositories
- Inconsistent structure
- Conflicting information

**Success rate:** ~60% coverage

**Mitigation:**
```
1. Use Researcher agents
2. Prioritize official sources
3. Cross-reference findings
4. Note conflicts clearly
5. Take longer but be thorough
```

**Report template:**
```markdown
Fragmented Documentation

Information found across multiple sources:

Official (incomplete):
- Website: [url]
- Package registry: [url]

Community (supplementary):
- Stack Overflow: [url]
- Tutorial: [url]

Note: No centralized documentation. Conflicts resolved by prioritizing official sources.
```

## Deprecated/Legacy Libraries

**Challenge:**
- Documentation removed or archived
- Only old versions available

**Success rate:** ~40% for fully deprecated libraries

**Mitigation:**
```
1. Use Internet Archive (Wayback Machine)
2. Search GitHub repository history
3. Check package registry for old README
4. Look for fork with docs
5. Note legacy status clearly
```

**Report template:**
```markdown
Legacy Library

Status: Deprecated as of [date]
Last update: [date]

Documentation sources:
- Archived docs (via Wayback): [url]
- Repository (last commit [date]): [url]

Recommendation: Consider modern alternative: [suggestion]
Migration path: [if available]
```
