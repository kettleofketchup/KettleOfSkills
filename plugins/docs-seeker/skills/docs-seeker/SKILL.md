---
name: docs-seeker
description: "Searches technical docs via llms.txt standard, GitHub repositories via Repomix, and parallel Explorer agents. Use for library docs, llms.txt format, GitHub repo analysis, or multi-source research."
version: 1.0.0
---

# Documentation Discovery & Analysis

## Overview

Intelligent discovery and analysis of technical documentation through multiple strategies:

1. **llms.txt-first**: Search for standardized AI-friendly documentation
2. **Repository analysis**: Use Repomix to analyze GitHub repositories
3. **Parallel exploration**: Deploy multiple Explorer agents for comprehensive coverage
4. **Fallback research**: Use Researcher agents when other methods unavailable

## Core Workflow

### Phase 1: Initial Discovery

1. Extract library/framework name from user request
2. Note version requirements (default: latest)
3. Identify if target is GitHub repository or website
4. Search for llms.txt:
   ```
   WebSearch: "[library name] llms.txt site:[docs domain]"
   ```
   Common patterns: `https://docs.[library].com/llms.txt`, `https://[library].dev/llms.txt`

### Phase 2: llms.txt Processing

- **Single URL**: WebFetch to retrieve content
- **Multiple URLs (3+)**: Launch multiple Explorer agents in parallel (max 5 per batch)

### Phase 3: Repository Analysis

When llms.txt not found:
1. Find GitHub repository via WebSearch
2. Clone and run Repomix:
   ```bash
   git clone [repo-url] /tmp/docs-analysis
   cd /tmp/docs-analysis && repomix --output repomix-output.xml
   ```
3. Read repomix-output.xml and extract documentation

### Phase 4: Fallback Research

When no GitHub repository: Launch multiple Researcher agents in parallel, aggregate findings.

## Agent Distribution Guidelines

- **1-3 URLs**: Single Explorer agent
- **4-10 URLs**: 3-5 Explorer agents (2-3 URLs each)
- **11+ URLs**: 5-7 Explorer agents (prioritize most relevant)

## Output Format

```markdown
# Documentation for [Library] [Version]

## Source
- Method: [llms.txt / Repository / Research]
- URLs: [list of sources]
- Date accessed: [current date]

## Key Information
[Extracted relevant information organized by topic]

## Additional Resources
[Related links, examples, references]

## Notes
[Any limitations, missing information, or caveats]
```

## Quick Reference

**Tool selection:**
- WebSearch → Find llms.txt URLs, GitHub repositories
- WebFetch → Read single documentation pages
- Task (Explore) → Multiple URLs, parallel exploration
- Task (Researcher) → Scattered documentation, diverse sources
- Repomix → Complete codebase analysis

**Popular llms.txt locations:**
- Astro: https://docs.astro.build/llms.txt
- Next.js: https://nextjs.org/llms.txt
- Remix: https://remix.run/llms.txt
- SvelteKit: https://kit.svelte.dev/llms.txt

## Key Principles

1. **Search for llms.txt first** — Most efficient path to AI-friendly documentation
2. **Use parallel agents aggressively** — Faster results, better coverage
3. **Verify official sources** — Confirm documentation is from official domains
4. **Report methodology** — Tell user which approach was used
5. **Handle versions explicitly** — Don't assume latest

## Reference Guides

**Workflows:**
- [WORKFLOWS.md](./WORKFLOWS.md) — Detailed workflow examples and strategies

**Tool usage:**
- [Tool Selection](./references/tool-selection/tools-reference.md) — Tools and when to use them
- [Decision Trees](./references/tool-selection/decision-tree.md) — Tool and agent count selection

**Sources:**
- [llms.txt & Registries](./references/documentation-sources/llms-txt-and-registries.md) — Known llms.txt URLs and package registries
- [Hosting & Search Patterns](./references/documentation-sources/hosting-and-search-patterns.md) — Hosting platforms and search strategies

**Error handling:**
- [llms.txt & Repository Errors](./references/error-handling/llms-txt-and-repository.md) — Resolution for common failures
- [Conflicts & Rate Limits](./references/error-handling/conflicts-and-rate-limits.md) — Conflict resolution and rate limiting

**Best practices:**
- [Discovery & Sources](./references/best-practices/discovery-and-sources.md) — llms.txt priority, version handling, source verification
- [Parallel Agents](./references/best-practices/parallel-agents.md) — Agent parallelism and aggregation
- [Methodology & Caching](./references/best-practices/methodology-and-caching.md) — Reporting, time management, caching

**Performance:**
- [Core Principles](./references/performance/core-principles.md) — Parallelism, batching, early termination patterns
- [Optimization & Benchmarks](./references/performance/optimization-and-benchmarks.md) — Techniques, benchmarks, common issues

**Limitations:**
- [Access Constraints](./references/limitations/access-constraints.md) — Auth, rate limits, real-time, interactive, video
- [Difficult Scenarios](./references/limitations/difficult-scenarios.md) — Large repos, PDFs, non-English, scattered, legacy
- [Success Criteria](./references/limitations/success-criteria.md) — Quality metrics and performance targets
