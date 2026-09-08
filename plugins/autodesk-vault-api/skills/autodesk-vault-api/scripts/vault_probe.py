#!/usr/bin/env python3
"""Probe a live Autodesk Vault server and report what its API actually supports.

The Vault Data API surface changes per release, so never assume an endpoint exists --
ask the server. This hits the unauthenticated `server-info` endpoint for the product
version, then pulls the OpenAPI spec and lists the endpoint families it declares.

Usage:
    python3 vault_probe.py --server http://vault.example.com
    python3 vault_probe.py --server https://abc123.vg.autodesk.com --json
    VAULT_SERVER_URL=http://vault.local python3 vault_probe.py

Stdlib only -- no install step, runs anywhere python3 does.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

API_SUFFIX = "/AutodeskDM/Services/api/vault/v2"
TIMEOUT = 20

# Capabilities gated on server version; see references/cloud-api.md.
VERSION_GATES = [
    (2025.2, "Vault Data API (read: files, folders, items, BOM, search, users)"),
    (2027.1, "Lifecycle definition/state read and update over REST"),
]


def normalize_base(server: str) -> str:
    """Turn any user-supplied server string into the v2 API base URL."""
    server = server.strip().rstrip("/")
    if not server:
        raise ValueError("server URL is empty")
    if not re.match(r"^https?://", server):
        server = "https://" + server if ".vg.autodesk.com" in server else "http://" + server
    if API_SUFFIX.lower() in server.lower():
        idx = server.lower().index(API_SUFFIX.lower())
        return server[: idx + len(API_SUFFIX)]
    return server + API_SUFFIX


def is_gateway(base: str) -> bool:
    return ".vg.autodesk.com" in base.lower()


def parse_openapi_paths(spec_text: str) -> list[str]:
    """Extract path templates from an OpenAPI YAML document.

    Deliberately line-based so the script stays dependency-free: inside the top-level
    `paths:` block, every two-space-indented key starting with `/` is a route.
    """
    paths: list[str] = []
    in_paths = False
    for raw in spec_text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if re.match(r"^paths:\s*$", line):
            in_paths = True
            continue
        if in_paths:
            if re.match(r"^\S", line):  # next top-level key ends the block
                break
            m = re.match(r"^\s{1,4}(/\S*?):\s*$", line)
            if m:
                paths.append(m.group(1))
    return paths


def group_endpoints(paths: list[str]) -> dict[str, list[str]]:
    """Bucket routes by their first meaningful segment (the endpoint family)."""
    groups: dict[str, list[str]] = {}
    for p in paths:
        segments = [s for s in p.split("/") if s and not s.startswith("{")]
        family = segments[0] if segments else "/"
        # `vaults/{id}/files` is more usefully filed under `files` than `vaults`.
        if family == "vaults" and len(segments) > 1:
            family = segments[1]
        groups.setdefault(family, []).append(p)
    return {k: sorted(v) for k, v in sorted(groups.items())}


def version_capabilities(version: str | None) -> list[tuple[str, bool | None]]:
    """Map a reported server version onto the known capability gates."""
    numeric = None
    if version:
        m = re.search(r"(\d{4})(?:\.(\d+))?", version)
        if m:
            numeric = float(f"{m.group(1)}.{m.group(2) or 0}")
    return [(label, None if numeric is None else numeric >= gate) for gate, label in VERSION_GATES]


def _get(url: str, accept: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001 - surfaced to the caller as a report line
        return 0, str(e)


def probe(server: str) -> dict:
    base = normalize_base(server)
    report: dict = {"base_url": base, "gateway": is_gateway(base)}

    status, body = _get(f"{base}/server-info", "application/json")
    report["server_info_status"] = status
    if status == 200:
        try:
            report["server_info"] = json.loads(body)
        except json.JSONDecodeError:
            report["server_info"] = {"raw": body[:400]}
    else:
        report["server_info_error"] = body[:400]

    info = report.get("server_info") or {}
    version = next(
        (str(info[k]) for k in ("version", "productVersion", "Version") if k in info), None
    )
    report["version"] = version
    report["capabilities"] = [
        {"capability": label, "available": ok} for label, ok in version_capabilities(version)
    ]

    status, body = _get(f"{base}/openapi-spec.yml", "application/yaml")
    report["openapi_status"] = status
    if status == 200:
        report["endpoints"] = group_endpoints(parse_openapi_paths(body))
    elif report["gateway"]:
        report["openapi_note"] = (
            "openapi-spec.yml commonly 404s through a Gateway URL -- "
            "fetch it from the direct server address instead."
        )
    return report


def render(report: dict) -> str:
    out = [f"Vault API base: {report['base_url']}"]
    out.append(f"Host type:      {'Vault Gateway' if report['gateway'] else 'direct server'}")
    if report.get("server_info"):
        out.append(f"server-info:    {json.dumps(report['server_info'])[:200]}")
    else:
        out.append(
            f"server-info:    UNREACHABLE (status {report['server_info_status']}) "
            f"{report.get('server_info_error', '')[:120]}"
        )
    out.append("")
    out.append("Capabilities (by reported version):")
    for c in report["capabilities"]:
        mark = {True: "yes", False: "no", None: "unknown"}[c["available"]]
        out.append(f"  [{mark:>7}] {c['capability']}")
    out.append("")
    if report.get("endpoints"):
        out.append("Endpoint families declared by openapi-spec.yml:")
        for family, routes in report["endpoints"].items():
            out.append(f"  {family} ({len(routes)})")
            for r in routes[:6]:
                out.append(f"      {r}")
            if len(routes) > 6:
                out.append(f"      ... {len(routes) - 6} more")
    else:
        out.append(f"OpenAPI spec:   not retrieved (status {report.get('openapi_status')})")
        if report.get("openapi_note"):
            out.append(f"  note: {report['openapi_note']}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--server",
        default=os.environ.get("VAULT_SERVER_URL"),
        help="Vault server or Gateway URL (or set VAULT_SERVER_URL)",
    )
    parser.add_argument("--json", action="store_true", help="emit the raw report as JSON")
    args = parser.parse_args(argv)

    if not args.server:
        parser.error("no server given: pass --server or set VAULT_SERVER_URL")

    report = probe(args.server)
    print(json.dumps(report, indent=2) if args.json else render(report))
    return 0 if report.get("server_info_status") == 200 else 1


if __name__ == "__main__":
    sys.exit(main())
