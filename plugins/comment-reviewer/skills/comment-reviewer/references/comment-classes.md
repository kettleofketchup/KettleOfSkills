# Comment classes — rules and worked examples

Judged in this order, after both never-touch tiers: **A → B → C**. Within a class, a
report-only valve always wins over a fix.

## Class A — spec and plan leakage

Comments that only make sense to a reader holding the plan, ticket, or review thread.

| Found | Action |
|---|---|
| `// As per step 3 of the plan, retry twice` | drop the provenance, keep the fact: `// Retry twice: upstream 502s on cold start` |
| `# New implementation (was using requests before)` | delete |
| `// TODO from the spec: handle the empty case` | if handled **with confirmed evidence in the same function**, delete; else `// TODO:` retaining the text |
| `// Changed this to fix the bug Mark found` | **report, do not delete** — the reason is recoverable from neither the comment nor the code |
| `// This satisfies requirement 4.2` | **report** — never delete an ID-shaped traceability comment |

### Tell-tales are candidates, not verdicts

*plan, spec, step N, phase, requirement, ticket, as requested, as discussed, per the design
doc, previously, now we, I changed* — each one requires a **second test**: is the referenced
artifact a development-process artifact, or the code's subject matter?

**Non-triggers, spelled out:**

- RFC, standard, and protocol references (`// per RFC 7231, PATCH is not idempotent`).
- Algorithm-step and phase numbering where the ordering *is* the content
  (`# Step 1: CRDs for target version`, present in this repository).
- Concurrency-state descriptions (`// Phase 2: draining in-flight requests`).

When a tell-tale word appears but the second test fails, leave the comment alone — it is not
Class A.

### The two report-only valves

1. **Unrecoverable reason.** When a comment references a fix, bug, incident, or abandoned
   approach and the reason is not recoverable from surrounding code, report it — never delete
   it and never guess a replacement. "History belongs in git" is false under squash-merge, so
   it is not a justification for deleting on its own.
2. **ID-shaped traceability.** A comment naming a requirement, ticket, or issue ID
   (`// satisfies requirement 4.2`, `// closes JIRA-991`) is reported, never deleted, and
   **never invent an issue, ticket, or PR reference** — carry over only an identifier already
   present in the comment or supplied by the user.

## Class B — comment does not match the code's purpose

- **Drifted** — describes behaviour the code no longer has. Rewrite to match, or delete when
  the code is now self-evident.
- **Over-specific** — describes one caller's use of a general function. Generalize *only* to
  what is verifiable from the body and signature. **Never widen a stated guarantee.** Prefer
  dropping the caller name over asserting a new contract.

  Example: `// used by the login form` above a general-purpose validator. Turning it into
  "validates any email address" is a confidently wrong comment that invites new callers to
  rely on behaviour the code may not have — worse than the stale comment it replaced. If
  generalizing requires a claim the code does not support, **report instead of rewriting**. A
  `// used by` pointing at a non-obvious consumer is retained as-is where no other
  cross-reference to that caller exists.
- **Restates the code** — `// increment counter` above `counter += 1`. Delete, or replace with
  the rationale when one exists.

The governing bias in every Class B fix: comments say **why**, not **what**.

## Class C — verbosity, judged by a no-loss test

Condensing is measured by density, never by length.

1. **Enumerate every load-bearing fact** in the original comment: a constraint, unit, range,
   rationale, invariant, caveat, or ownership rule.
2. Point to where each fact lands in the candidate replacement.
3. **Emit that enumeration in the returned summary for every Class C rewrite** — the test
   leaves an auditable artifact instead of being self-refereed.

Rules that follow from the test:

- If condensing would drop a load-bearing fact, the fact stays and only surrounding words are
  cut.
- **If no version is both shorter and at least as informative, the comment is left alone and
  reported.** Do not ship a rewrite just because one was attempted.
- **Shorter but vaguer is a regression, not a fix.**
- No rewrite may drop a numeric literal, unit, or identifier present in the original.
- **"Shorter" is measured in clauses, not characters** — raw length is not comparable across
  scripts (a CJK sentence is short in characters and dense in clauses).

### Parameter documentation

Parameter docs that only repeat the signature go — **but only where the language's signature
actually carries the type.** All JSDoc `@param` tag blocks in `.js`/`.jsx` are off-limits,
because there the tags are the only type information available; the same tag block in a typed
language (TypeScript, Java, Go) is a restatement and may be condensed under the no-loss test
like any other Class C candidate.

See `never-touch.md` for what never reaches this classification at all, and
`rewrite-guidelines.md` for how the actual rewrite text is produced.
