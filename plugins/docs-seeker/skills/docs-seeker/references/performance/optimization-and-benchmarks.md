# Performance: Optimization Techniques & Benchmarks

## Optimization Techniques

### Technique 1: Workload Balancing

**Problem:** Uneven distribution causes bottlenecks.
```
Bad: Agent 1: 1 URL → 5s, Agent 2: 10 URLs → 50s. Total: 50s bottleneck.

Good: 4 agents, 3 URLs each (~15s each). Total: ~15s (balanced).
```

### Technique 2: Request Coalescing

**Problem:** Redundant requests slow things down.
```
Bad: Agent 1, 2, 3 all fetch README.md → 2 redundant fetches.

Good: Pre-processing: Identify unique URLs. Agent 1 fetches README once.
```

### Technique 3: Timeout Tuning

```
Known fast sites (official docs): 30s timeout
Unknown sites: 60s timeout
Large repos: 120s timeout
If timeout hit: Immediately try alternative
```

### Technique 4: Selective Fetching

```
User need: "How to get started"
Fetch only: Installation, basic usage, examples
Skip: Advanced topics, internals, contribution
Speedup: 50% less fetching
```

## Performance Benchmarks

### Target Times

| Scenario | Target Time | Acceptable | Too Slow |
|----------|-------------|------------|----------|
| Single URL | less than 10s | 10-20s | more than 20s |
| llms.txt (5 URLs) | less than 30s | 30-60s | more than 60s |
| llms.txt (15 URLs) | less than 60s | 60-120s | more than 120s |
| Repository analysis | less than 2min | 2-5min | more than 5min |
| Research fallback | less than 3min | 3-7min | more than 7min |

### Real-World Examples

| Scenario | Timeline | Total |
|----------|----------|-------|
| Fast (Next.js + llms.txt) | Find llms.txt 5s, fetch 10s, 4 agents 45s, report 55s | ~55s |
| Medium (repo, no llms.txt) | No llms.txt 15s, clone 30s, Repomix 2m, report ready | ~2m 45s |
| Slow (scattered docs) | No llms.txt/repo, 4 researchers 5m, aggregate 1m | ~6m 30s |

## Common Performance Issues

| Issue | Problem | Solution |
|-------|---------|---------|
| Too many agents | 15 agents → overhead bottleneck | Max 7 per batch, use phases |
| Blocking operations | Agents wait on each other | Launch independently, aggregate after |
| Redundant fetching | Same page fetched twice | Cache content, check cache first |
| Late bailout | 90% found at 1min, 4 more min for 10% | Stop at 80%+ coverage, offer more |

## Performance Monitoring

### Key Metrics

```
- llms.txt discovery: Target less than 30s
- Repository clone: Target less than 60s
- Repomix processing: Target less than 2min
- Agent exploration: Target less than 60s
- Total time: Target less than 3min for typical case
```

### Performance Report Template

```markdown
## Performance Summary

**Total time**: 1m 25s
**Method**: llms.txt + parallel exploration

**Breakdown**:
- Discovery: 15s (llms.txt search & fetch)
- Exploration: 50s (4 agents, 12 URLs)
- Aggregation: 20s (synthesis & formatting)

**Efficiency**: 8.5x faster than sequential
```

## Quick Optimization Checklist

### Before Starting
- [ ] Check if content already cached
- [ ] Identify fastest method for this case
- [ ] Plan for parallel execution
- [ ] Set appropriate timeouts

### During Execution
- [ ] Launch agents in parallel (not sequential)
- [ ] Use single message for multiple agents
- [ ] Monitor for bottlenecks
- [ ] Be ready to terminate early

### After First Phase
- [ ] Assess coverage achieved
- [ ] Determine if user needs met
- [ ] Decide: continue or deliver now
- [ ] Cache results for potential reuse
