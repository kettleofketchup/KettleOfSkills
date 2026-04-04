#!/usr/bin/env python3
"""Generate a single JSON line for a marketplace plugin entry."""
import json
import sys

entry = {
    "name": sys.argv[1],
    "description": sys.argv[2],
    "source": "./plugins/" + sys.argv[1],
}
print(json.dumps(entry))
