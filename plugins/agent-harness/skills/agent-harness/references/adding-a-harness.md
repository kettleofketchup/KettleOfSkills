# Adding a Harness

Supporting a new tool is one function plus two registry entries in
`scripts/sync_harnesses.py`. Nothing else changes.

## 1. Find out what it actually reads

Do not trust a blog post. Establish, for the tool in question:

- which directory it scans for project-level instructions
- what frontmatter it requires (`name`? `triggers`? a glob?)
- whether it reads root `AGENTS.md` already, which may make an emitter unnecessary
- whether it follows symlinks, which decides if the `.agents/skills` link is enough

The cheapest reliable method is a probe: create a throwaway repo with a uniquely named
skill in each candidate directory, then ask the tool to render or list what it can see.
Codex exposes `codex debug prompt-input`, which prints the real prompt with no API call.
If a tool has no such command, ask it in a session what skills it can see and grep the
answer for the probe names.

Record the result in `harness-matrix.md` and mark it verified or documented. An
unverified guess in that table is worse than a blank row.

## 2. Write the emitter

Add a function taking the artifact dict and returning
`{repo-relative Path: file content}`:

```python
def emit_newtool(arts: dict[str, list[Artifact]]) -> dict[Path, str]:
    out = {}
    for art in arts["skill"]:
        out[Path(".newtool/rules") / f"{art.name}.md"] = f"""---
description: {art.description}
---

<!-- {MARKER} -->

Canonical source: `{art.path}` — read it before acting. This is a pointer only.
Repo-wide conventions are in `AGENTS.md`.
"""
    return out
```

Three rules the existing emitters follow:

- **Point, never copy.** Emit the description and the canonical path. Never inline a
  skill body — a copy is exactly the drift this skill prevents. A test enforces this.
- **Include the marker.** Only files containing `MARKER` are eligible for pruning, so a
  file without it will be orphaned forever, and a hand-written file with it will be
  deleted.
- **No repo conventions.** They live in `AGENTS.md`.

Use `art.applies_to` for glob-scoped tools and `art.triggers` for keyword-matched ones.
Both come from the skill's own frontmatter with sensible fallbacks.

## 3. Register it

```python
EMITTERS = {..., "newtool": emit_newtool}
OWNED = {..., "newtool": [Path(".newtool/rules")]}
```

`OWNED` lists the paths the emitter controls. They are scanned for orphaned generated
files, so listing too little leaves stale files behind, and listing a directory shared
with hand-written content risks deleting it. When a tool writes into a shared directory
such as `.github/`, list the specific subdirectory and files, never the parent.

## 4. Test it

Add a case to `scripts/tests/test_sync_harnesses.py` asserting the file lands with the
right frontmatter. The generic tests — idempotence, staleness, pruning, pointer-only —
cover every registered emitter automatically, so a new harness inherits them once it is
in `EMITTERS`.

Run the suite:

```bash
python3 -m pytest scripts/tests -q
```

## 5. Adopt it per repo

Emitters are opt-in. Existing repos are unaffected until someone runs
`sync_harnesses.py --harness ...,newtool`, which rewrites `.agents/harnesses.json`.
Dropping a harness from that list prunes its generated files on the next sync.
