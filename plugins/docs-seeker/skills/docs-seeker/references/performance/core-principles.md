# Performance: Core Principles & Patterns

## Core Principles

### 1. Minimize Sequential Operations

**The Problem:** Sequential operations add up linearly.
```
Fetch URL 1: 5s + Fetch URL 2: 5s + Fetch URL 3: 5s = 15 seconds
```

**The Solution:** Parallel operations complete in max time of slowest.
```
Launch 3 agents simultaneously → All complete in: ~5 seconds
```

### 2. Batch Related Operations

**Grouping Strategies:**

**By topic:**
```
Agent 1: All authentication-related docs
Agent 2: All database-related docs
Agent 3: All API-related docs
```

**By priority:**
```
Phase 1 (critical): Getting started, installation, core concepts
Phase 2 (important): Guides, API reference, configuration
Phase 3 (optional): Advanced topics, optimization
```

### 3. Smart Caching

**What to cache:** Repomix output, llms.txt content, repository structure, documentation URLs.

**When to refresh:** User requests specific version, documentation updated, user explicitly requests fresh data.

### 4. Early Termination

**When to stop:**
```
After Phase 1 (critical docs):
- Review what was found
- Check against user request
- If 80%+ covered → deliver now
- Offer to fetch more if needed
```

## Performance Patterns

### Pattern 1: Parallel Exploration

**Scenario:** llms.txt contains 10 URLs

**Slow approach (sequential):** 10 URLs × 5 seconds = 50 seconds

**Fast approach (parallel):**
```
Step 1: Launch 5 Explorer agents simultaneously
  Agent 1: URLs 1-2
  Agent 2: URLs 3-4
  Agent 3: URLs 5-6
  Agent 4: URLs 7-8
  Agent 5: URLs 9-10

Step 2: Wait for all (~5-10s)
Step 3: Aggregate results
```

**Speedup:** 5-10x faster

### Pattern 2: Lazy Loading

**Scenario:** Documentation has 30+ pages

**Slow approach:** Fetch all 30 pages upfront (30 URLs × 5s ÷ 5 agents = 30 seconds, but user only needs 5).

**Fast approach:**
```
Phase 1: Fetch critical 10 pages
Review: Does this cover user's needs?
If yes: Stop here (saved 20 seconds)
If no: Fetch additional as needed
```

**Speedup:** Up to 3x faster for typical use cases

### Pattern 3: Smart Fallbacks

**Slow approach:** Try each llms.txt domain with 30s timeout each → ~5 minutes.

**Fast approach:**
```
Try: docs.library.com/llms.txt (15s)
Try: library.dev/llms.txt (15s)
Not found → Immediately try repository (30s)
```

**Speedup:** 5x faster

### Pattern 4: Incremental Results

**Slow approach:** Wait 5 minutes until full report ready.

**Fast approach:**
```
Phase 1: Fetch critical docs (30s) → Present initial findings
Phase 2: Fetch important docs (60s) → Update findings
Phase 3: Fetch supplementary (90s) → Complete report
```

**Benefit:** User gets value at 30 seconds, can stop early if satisfied.
