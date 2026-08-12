# Limitations: Success Criteria & Quality Metrics

Measuring effectiveness of documentation discovery.

## Success Criteria

### 1. Finds Relevant Information

Quality levels:

**Excellent (100%):** All requested topics covered, examples for each concept, official source, no gaps.

**Good (80-99%):** Most topics covered, information mostly complete, minor gaps noted.

**Acceptable (60-79%):** Core topics covered, mix of official/community sources, some gaps.

**Poor (less than 60%):** Partial coverage, few examples, significant gaps.

### 2. Uses Most Efficient Method

**Optimal:**
- Found llms.txt immediately
- Parallel agents for all URLs
- Completed in less than 2 minutes

**Poor:**
- Didn't try llms.txt first
- Mostly sequential processing
- Took more than 10 minutes

### 3. Completes in Reasonable Time

| Scenario | Excellent | Good | Acceptable | Poor |
|----------|-----------|------|------------|------|
| Simple (1-5 URLs) | less than 1 min | 1-2 min | 2-5 min | more than 5 min |
| Medium (6-15 URLs) | less than 2 min | 2-4 min | 4-7 min | more than 7 min |
| Complex (16+ URLs) | less than 3 min | 3-6 min | 6-10 min | more than 10 min |
| Repository | less than 3 min | 3-6 min | 6-10 min | more than 10 min |
| Research | less than 5 min | 5-8 min | 8-12 min | more than 12 min |

### 4. Provides Clear Source Attribution

Measured by:
- [ ] Lists all sources used
- [ ] Notes method employed
- [ ] Includes URLs/references
- [ ] Identifies official vs community

### 5. Identifies Version/Date

```markdown
## Version Information

**Documentation version**: v3.2.1
**Last updated**: 2025-10-20
**Retrieved**: 2025-10-26
**User requested**: v3.x - Match

Note: This is the latest stable version as of retrieval date.
```

### 6. Notes Limitations/Gaps

```markdown
## Limitations

**Incomplete documentation**:
- Advanced features section (stub page)
- Migration guide (404 error)

**Workarounds**:
- Advanced features: See examples in repository
- Migration: Check CHANGELOG.md for breaking changes
```

## Quality Checklist

### Before Presenting Report

**Content quality:**
- [ ] Information is accurate
- [ ] Sources are official (or noted as unofficial)
- [ ] Version matches request
- [ ] Examples are clear

**Completeness:**
- [ ] All key topics covered
- [ ] Installation instructions present
- [ ] Usage examples included
- [ ] Configuration documented

**Attribution:**
- [ ] Sources listed
- [ ] Method documented
- [ ] Version identified
- [ ] Date noted
- [ ] Limitations disclosed

## Performance Metrics

### Time-to-Value

```
First useful info: less than 30 seconds
Core coverage: less than 2 minutes
Complete report: less than 5 minutes
```

### Coverage Completeness

**Targets:**
```
Excellent: 90-100%
Good: 75-89%
Acceptable: 60-74%
Poor: less than 60%
```

### Source Quality Scoring

```
Official docs: 100 points
Official repository: 80 points
Package registry: 60 points
Recent community (verified): 40 points
Old community (unverified): 20 points
```

**Target:** Average more than 70 points

### User Satisfaction Indicators

**Positive signals:**
- User proceeds immediately with info
- No follow-up questions needed

**Negative signals:**
- User asks same question differently
- User requests more details
- User says "incomplete" or "not what I needed"
