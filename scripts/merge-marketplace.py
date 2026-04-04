#!/usr/bin/env python3
"""Assemble marketplace.json from JSON-lines entries file."""
import json
import sys

entries_file = sys.argv[1]
group_names = set(sys.argv[2].split(","))

entries = []
with open(entries_file) as f:
    for line in f:
        line = line.strip()
        if line:
            entries.append(json.loads(line))

# Sort: individual plugins first (alphabetically), then groups (alphabetically)
individuals = sorted(
    [e for e in entries if e["name"] not in group_names],
    key=lambda x: x["name"],
)
group_entries = sorted(
    [e for e in entries if e["name"] in group_names],
    key=lambda x: x["name"],
)

marketplace = {
    "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
    "name": "kettleofskills",
    "description": "Curated skill packs for Claude Code \u2014 individual skills and grouped bundles",
    "owner": {"name": "kettleofketchup"},
    "plugins": individuals + group_entries,
}

print(json.dumps(marketplace, indent=2, ensure_ascii=False))
