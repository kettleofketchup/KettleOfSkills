#!/usr/bin/env python3
"""Generate a single JSON line for a marketplace plugin entry."""
import json
import sys

entry = {
    "name": sys.argv[1],
    "description": sys.argv[2],
    "source": "./plugins/" + sys.argv[1],
}
# Optional type hint for merge-marketplace to distinguish individual vs group
if len(sys.argv) > 3:
    entry["_type"] = sys.argv[3]
print(json.dumps(entry))
