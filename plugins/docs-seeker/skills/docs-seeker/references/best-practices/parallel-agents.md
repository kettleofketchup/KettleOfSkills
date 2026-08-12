# Best Practices: Parallel Agents

## 2. Use Parallel Agents Aggressively

### Why

- **Speed**: N tasks in time of 1 (vs N × time)
- **Efficiency**: Better resource utilization
- **Coverage**: Comprehensive results faster
- **Scalability**: Handles large documentation sets

### Guidelines

**Always use parallel for 3+ URLs:**
```
3 URLs → 1 Explorer agent (acceptable)
4-10 URLs → 3-5 Explorer agents (optimal)
11+ URLs → 5-7 agents in phases (best)
```

**Launch all agents in single message:**
```
Good:
[Send one message with 5 Task tool calls]

Bad:
[Send message with Task call]
[Wait for result]
[Send another message with Task call]
[Wait for result]
...
```

### Distribution Strategy

**Even distribution:**
```
10 URLs, 5 agents:
Agent 1: URLs 1-2
Agent 2: URLs 3-4
Agent 3: URLs 5-6
Agent 4: URLs 7-8
Agent 5: URLs 9-10
```

**Topic-based distribution:**
```
10 URLs, 3 agents:
Agent 1: Installation & Setup (URLs 1-3)
Agent 2: Core Concepts & API (URLs 4-7)
Agent 3: Examples & Guides (URLs 8-10)
```

### When Not to Parallelize

- Single URL (use WebFetch)
- 2 URLs (single agent is fine)
- Dependencies between tasks (sequential required)
- Limited documentation (1-2 pages)

## 6. Aggregate Intelligently

### Bad Aggregation (Don't Do This)

```markdown
## Results

Agent 1 found:
[dump of agent 1 output]

Agent 2 found:
[dump of agent 2 output]
```

Problems: Redundant information, no synthesis, hard to scan, lacks narrative.

### Good Aggregation (Do This)

```markdown
## Installation

Three installation methods available:

1. **npm (recommended)**: `npm install library-name`
2. **CDN**: `<script src="..."></script>`
3. **Manual**: Download and include in project

## Core Concepts

The library is built around three main concepts:
1. **Components**, 2. **State**, 3. **Effects**
```

### Synthesis Techniques

**Deduplication:**
```
Agent 1: "Install with npm install foo"
Agent 2: "You can install using npm: npm install foo"
→ Synthesized: "Install: `npm install foo`"
```

**Organization:**
```
Agents returned mixed information:
- Installation steps, Configuration, Usage, more

→ Reorganize:
1. Installation (requirements + steps)
2. Configuration
3. Usage (all examples together)
```

## Quick Reference Checklist

### Before Starting
- [ ] Identify library name clearly
- [ ] Confirm version (default: latest)
- [ ] Check if cached data available
- [ ] Plan method (llms.txt → repo → research)

### During Exploration
- [ ] Use parallel agents for 3+ URLs
- [ ] Launch all agents in single message
- [ ] Distribute workload evenly
- [ ] Monitor for errors/timeouts

### Before Presenting
- [ ] Synthesize by topic (not by agent)
- [ ] Deduplicate repeated information
- [ ] Verify version is correct
- [ ] Include source attribution
- [ ] Note any limitations
