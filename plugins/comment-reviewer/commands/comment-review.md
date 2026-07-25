---
description: Review this branch's comments and write the gate receipt
---

Dispatch the `comment-reviewer` agent against the current branch.

If the user supplied an argument, pass it as the explicit base ref: `$ARGUMENTS`

Report the agent's summary — per-class counts and any report-only findings — then tell the user
they can retry `pr create`.
