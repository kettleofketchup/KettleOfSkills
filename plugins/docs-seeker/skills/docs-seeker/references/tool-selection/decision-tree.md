# Tool Selection: Decision Tree

## Tool Selection Decision Tree

```
Need documentation?
  ↓
WebSearch for llms.txt
  ↓
llms.txt found?
  YES → Process llms.txt URLs (go to URL count check)
  NO → Continue
  ↓
Single URL?
  YES → WebFetch
  NO → Continue
  ↓
1-3 URLs?
  YES → Single Explorer agent
  NO → Continue
  ↓
4+ URLs?
  YES → Multiple Explorer agents (3-7)
  NO → Continue
  ↓
Need repository analysis?
  YES → Repomix (if available)
  NO → Continue
  ↓
No structured docs?
  YES → Researcher agents
```

## Agent Count Decision Tree

```
URL Count less than 3
  ↓
Single Explorer
  ↓
URL Count 4-10
  ↓
3-5 Explorers
  ↓
URL Count 11-20
  ↓
5-7 Explorers (or two phases)
  ↓
URL Count more than 20
  ↓
Two-phase approach:
  Phase 1: 5 agents (critical)
  Phase 2: 5 agents (important)
```

## Optimization Decision Tree

```
Need documentation?
  ↓
Check cache
  ↓
HIT → Use cached (0s)
MISS → Continue
  ↓
llms.txt available?
  ↓
YES → Parallel agents (30-60s)
NO → Continue
  ↓
Repository available?
  ↓
YES → Repomix (2-5min)
NO → Research (3-7min)
  ↓
After Phase 1:
80%+ coverage?
  ↓
YES → Deliver now (save time)
NO → Continue to Phase 2
```

## Choosing Documentation Strategy

```
Start
  ↓
Does llms.txt exist?
  ↓
YES → How many URLs?
  ↓
  1-3 URLs → Single WebFetch/Explorer
  4+ URLs → Parallel Explorers
  ↓
NO → Is there GitHub repo?
  ↓
  YES → Is Repomix feasible?
    ↓
    YES → Use Repomix
    NO → Manual exploration with Explorers
  ↓
  NO → Deploy Researcher agents
```

## When to Use Each Fallback

| Situation | Primary Tool | Fallback |
|-----------|-------------|---------|
| llms.txt found | Explorer agents | - |
| No llms.txt | Repomix (if repo exists) | Researcher agents |
| No public repo | Researcher agents | Manual WebFetch |
| Large repo (more than 1GB) | Explorer agents on /docs | Researcher agents |
| Private/auth required | Researcher agents | Public info only |
| Rate limited | Alternative sources | Cached versions |
| Timeout | Alternative endpoints | Archive.org |
