# Flagship Targeting Rules & Safe Deletion

Split out of `patterns.md`; see it for the preceding sections.

## Targeting Rule Patterns

### Enterprise-Only Access

```json
{
  "priority": 1,
  "conditions": [
    { "attribute": "plan", "operator": "equals", "value": "enterprise" }
  ],
  "serve_variation": "on"
}
```

### Country-Based Targeting with Logical AND/OR

Target enterprise users in the US or Canada:

```json
{
  "priority": 1,
  "conditions": [
    {
      "logical_operator": "AND",
      "clauses": [
        { "attribute": "plan", "operator": "equals", "value": "enterprise" },
        {
          "logical_operator": "OR",
          "clauses": [
            { "attribute": "country", "operator": "equals", "value": "US" },
            { "attribute": "country", "operator": "equals", "value": "CA" }
          ]
        }
      ]
    }
  ],
  "serve_variation": "on"
}
```

### Percentage Rollout

Gradually roll out to 10% of users:

```json
{
  "priority": 1,
  "conditions": [
    { "attribute": "targetingKey", "operator": "not_equals", "value": "" }
  ],
  "serve_variation": "on",
  "rollout": {
    "percentage": 10,
    "attribute": "targetingKey"
  }
}
```

### A/B/n (Multi-Variant) Testing

To split traffic across N variants, create one rule per variant with **cumulative** rollout percentages. Flagship evaluates rules in priority order. If a rule's conditions match but the user misses that rule's rollout percentage, evaluation continues to the next rule. Use the same stable rollout attribute on every rule so each user is compared against the same bucket as the thresholds increase.

The example uses `conditions: []` because the rules are intended to match every context. For sticky user assignment, callers must still pass the configured bucketing attribute (`targetingKey` here); otherwise Flagship uses a random bucket per request.

For example, to split traffic 30% / 40% / 30% across variants A, B, and C:

| Variant | Share | Cumulative threshold |
|---------|-------|----------------------|
| A       | 30%   | 30                   |
| B       | 40%   | 70                   |
| C       | 30%   | 100                  |

```json
"rules": [
  {
    "priority": 1,
    "conditions": [],
    "serve_variation": "variant-a",
    "rollout": { "percentage": 30, "attribute": "targetingKey" }
  },
  {
    "priority": 2,
    "conditions": [],
    "serve_variation": "variant-b",
    "rollout": { "percentage": 70, "attribute": "targetingKey" }
  },
  {
    "priority": 3,
    "conditions": [],
    "serve_variation": "variant-c",
    "rollout": { "percentage": 100, "attribute": "targetingKey" }
  }
]
```

Key points:
- Rules are evaluated lowest-priority-number first. A user who falls into rule 1's 0-30% bucket gets `variant-a` and is not evaluated further.
- Rule 2's 70% threshold covers the next 40% of users (31-70%).
- Rule 3's 100% threshold catches the remaining 30% (71-100%).
- Always set the last rule to `100` so every context with the bucketing attribute is assigned a variant.
- For sticky A/B/n assignment, pass a stable `targetingKey` or configured bucketing attribute. Without it, rollout assignment is random per request, which can be useful for request-level sampling but is usually wrong for user experiments.
- A percentage rollout match reports reason `SPLIT` in evaluation details.

### Progressive Rollout Workflow

1. Create flag with 5% rollout, enable it
2. Monitor metrics
3. Increase to 25% → 50% → 100% by updating the `rollout.percentage`
4. Once at 100%, remove the rule and set `default_variation` to the winning variation
5. Eventually remove the flag and the code branch

---

## Safe Deletion Workflow

1. **Disable** the flag first (`enabled: false`) — confirms nothing depends on it being active
2. **Monitor** for unexpected behavior
3. **Remove** flag evaluation code from your application
4. **Deploy** the code change
5. **Delete** the flag via API
