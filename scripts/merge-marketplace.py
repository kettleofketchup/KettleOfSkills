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

# Use _type hint if present, otherwise fall back to name-based detection
individuals = sorted(
    [e for e in entries if e.get("_type", "group" if e["name"] in group_names else "individual") == "individual"],
    key=lambda x: x["name"],
)
group_entries = sorted(
    [e for e in entries if e.get("_type", "group" if e["name"] in group_names else "individual") == "group"],
    key=lambda x: x["name"],
)

# Strip internal _type field from output
for e in individuals + group_entries:
    e.pop("_type", None)

marketplace = {
    "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
    "name": "kettleofskills",
    "description": "Curated skill packs for Claude Code \u2014 individual skills and grouped bundles",
    "owner": {"name": "kettleofketchup"},
    "plugins": individuals + group_entries,
}

print(json.dumps(marketplace, indent=2, ensure_ascii=False))
