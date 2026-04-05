#!/usr/bin/env python3
"""Extract description from SKILL.md YAML frontmatter, handling multiline values."""
import sys

skill_md = sys.argv[1]

fm_lines = []
in_fm = False
for line in open(skill_md):
    line = line.rstrip("\n")
    if line == "---":
        if in_fm:
            break
        in_fm = True
        continue
    if in_fm:
        fm_lines.append(line)

# Parse description from frontmatter lines
desc = ""
in_desc = False
for line in fm_lines:
    if line.startswith("description:"):
        val = line.split(":", 1)[1].strip()
        if val in (">-", ">", "|", "|-"):
            in_desc = True
            continue
        desc = val
        break
    elif in_desc:
        if line and line[0] in (" ", "\t"):
            desc += (" " if desc else "") + line.strip()
        else:
            break

# Strip surrounding quotes
for q in ('"', "'"):
    if desc.startswith(q) and desc.endswith(q):
        desc = desc[1:-1]
        break

print(desc)
