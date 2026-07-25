# Rewrite guidelines

How the text of a permitted rewrite gets produced, once `never-touch.md` has cleared a span
and `comment-classes.md` has picked a class and an action.

## Generalize without over-claiming

Class B's over-specific case is the one most likely to produce a confidently wrong comment.
When lifting a comment from one caller's use to the general case:

- Generalize only to what is **verifiable from the function body and signature in front of
  you** — not from what the function is *probably* also used for elsewhere.
- **Never widen a stated guarantee.** If the original says "retries once on timeout" and the
  code actually retries on any `IOError`, fix the guarantee to match the code — do not also
  invent a new guarantee the code doesn't demonstrably provide.
- When generalizing would require a claim the code does not support, stop and report instead
  of writing a plausible-sounding rewrite. A wrong comment that reads as authoritative is
  worse than a stale one that reads as suspect: `// validates any email address` invites a new
  caller to rely on behaviour that may not exist, where `// used by the login form` at least
  signals "check before reusing."
- Prefer dropping the caller's name (`// used by the login form` → `// validates RFC 5322
  addresses`) over asserting a contract beyond what's shown. If even that can't be verified
  from the code, leave the caller name in.

## Rephrase to *why*, not *what*

The code already says *what* it does; a comment repeating that is Class C's "restates the
code" case waiting to happen. When a comment survives judgment and needs rewording:

- Ask what a future reader would need that the code alone doesn't supply: a non-obvious
  invariant, a constraint from outside this function, a tradeoff, a reason a simpler approach
  wasn't used.
- If nothing survives that question, the comment restates the code — delete it, don't reword
  it into a slightly different restatement.
- If a rationale exists, put the rationale in the rewrite and let the code speak for the
  mechanics: `// increment counter` above `counter += 1` becomes nothing (delete) unless there
  is a reason the increment happens *here specifically*, in which case that reason is the
  entire rewrite.

## Condense under the no-loss test

This is Class C's test (full mechanics in `comment-classes.md`); the guideline here is how to
apply it while writing, not just how to check afterward:

- Draft the enumeration of load-bearing facts **before** drafting the shorter text, not after
  — writing the short version first and then checking it tends to rationalize losses instead
  of catching them.
- Cut connective prose and repeated context first; cut a fact only as a last resort, and if a
  fact must go, the comment is not a no-loss candidate — leave it alone and report it instead
  of shipping a partial cut.
- A rewrite that is shorter but forces the reader to go read the code to recover a fact that
  used to be stated outright is not a win. Measure "informative enough" by whether the reader
  still needs zero extra lookups, not by whether the words feel adequate.

## Stay in the original natural language

**Every rewrite is written in the same natural language as the comment it replaces. Nothing is
ever translated.** For a comment mixing languages, the language of the prose wins over any
embedded natural-language snippet. If the agent cannot confidently write fluent, natural
prose in that language, it reports the span instead of writing a rewrite — a mediocre
translation is a worse outcome than leaving the original in place, because it reads as
authoritative in a language the agent doesn't actually command.

This rule has no exception for the class of the finding: it applies identically to Class A
drops, Class B rewrites, and Class C condensing.
