---
name: autodesk-vault-api
description: "Autodesk Vault APIs. Use for the Vault .NET SDK (WebServiceManager, VDF), Vault Data API REST endpoints, Gateway and APS auth, property definitions, categories, lifecycles, or BOM metadata."
---

# Autodesk Vault API

Vault exposes two independent API surfaces over the same data model: a complete but
Windows-bound **.NET SDK**, and a newer, read-focused **Vault Data API** (REST, on Autodesk
Platform Services). Choosing the wrong one wastes the most time, so the workflow below picks
it from live server facts rather than assumption.

## Dynamic workflow

Run these phases in order. Each phase's outcome selects the next — do not skip to writing code.

### Phase 1 — Probe the server, do not guess

The API surface is gated on the deployed Vault version, and endpoints move between releases.
Ask the server what it supports:

```bash
python3 scripts/vault_probe.py --server http://vault.example.com
python3 scripts/vault_probe.py --server https://abc123.vg.autodesk.com --json
```

This reports the product version (via the unauthenticated `server-info` endpoint), which
capabilities that version gates on, and the endpoint families the live `openapi-spec.yml`
declares. Stdlib only, no install. If the server is unreachable, ask the user for the version
and edition (Basic / Workgroup / Professional) before continuing — both change what is possible.

### Phase 2 — Route to a surface

| Situation | Surface | Reference |
|-----------|---------|-----------|
| Non-Windows, container, browser, or CI client | Vault Data API | [cloud-api.md](references/cloud-api.md) |
| Remote client with no VPN into the Vault network | Vault Data API via Gateway | [cloud-api.md](references/cloud-api.md) |
| Read files, folders, items, BOM, search, users | Vault Data API | [cloud-api.md](references/cloud-api.md) |
| Check-in, file upload, property writes, custom entities | .NET SDK | [dotnet-api.md](references/dotnet-api.md) |
| Job Processor handlers, Vault client UI extensions | .NET SDK | [dotnet-api.md](references/dotnet-api.md) |
| Lifecycle state changes on a server below 2027.1 | .NET SDK | [dotnet-api.md](references/dotnet-api.md) |
| Server below 2025.2 | .NET SDK (REST API does not exist) | [dotnet-api.md](references/dotnet-api.md) |

Splitting a task across both surfaces is normal — read over REST, write over the SDK. They
authenticate independently; an APS token does not carry into the SDK except through
`AutodeskAuthCredentials`.

### Phase 3 — Authenticate

- **.NET SDK** — `UserPasswordCredentials` or `WinAuthCredentials` into `WebServiceManager`,
  or `VDF.Vault.Library.ConnectionManager.LogIn`. Always `LogOut` in a `finally`: Vault seats
  are licence-bound and leaked sessions exhaust them.
- **REST, direct server** — `POST sessions`, then send the returned `accessToken` as
  `Authorization: Bearer V:{uuid}`.
- **REST, via Gateway** — Vault tokens do not work. Register an APS app of type
  *Desktop, Mobile, Single-Page App* and mint a 3-legged token with Authorization Code Grant
  + PKCE. There is no client secret, so 2-legged client-credentials will not authenticate a user.

### Phase 4 — Resolve metadata before querying

Most Vault bugs are metadata bugs, not API bugs. Before writing a query, establish:

1. The **entity class** of the target (`FILE`, `FLDR`, `ITEM`, `CO`, `CUSTENT` in .NET;
   an `entityType` string in REST).
2. The **property definition IDs**, resolved at runtime by `SysName` or `DispName`.
   **Never hardcode a `PropDefId`** — IDs differ per Vault, and a hardcoded one is the usual
   cause of a search returning nothing for a file that plainly exists.
3. The object's **category**, which decides which UDPs, lifecycle, and revision scheme apply.
4. Whether the requirement means latest **version** (every check-in) or latest **revision**
   (a milestone, usually at a released state). Filter on state, not version number.

Full model in [vault-metadata.md](references/vault-metadata.md).

### Phase 5 — Execute, then verify against the client

Write the call using the reference for the chosen surface. Then check the result against what
the Vault client UI shows for the same object. Vault fails quietly in several places:

- `AcquireFiles` reports per-file failures in `FileResults[].Exception`, not by throwing.
- `FindFilesBySearchConditions` pages — loop on the bookmark until `TotalHits`, and break on
  an empty page or the loop never ends.
- REST search results carry an `indexingStatus`; too few hits often means the index is still
  building, not that the query is wrong.
- A failed lifecycle transition is usually unmet criteria or permissions — read the returned
  restrictions rather than retrying.

## Edition and version gates

| Capability | Requires |
|------------|----------|
| Web Service API (files, folders, properties) | Any edition |
| Items, BOM, change orders, custom entities | Vault **Professional** |
| Vault Client API, Job Processor API | Workgroup or Professional |
| Vault Data API (REST) | Vault **2025.2**+ |
| REST lifecycle definition/state **updates** | Vault **2027.1**+ |

Calling a Professional-only service against Basic throws rather than returning empty.

## Traps worth stating up front

- The .NET SDK targets **.NET Framework 4.8** and needs `Copy Local = True` on every
  reference — assemblies are not preloaded into the host process.
- SDK version must match server version; a 2025 SDK will not talk to a 2024 server.
- A UDP with no entity-class association is invisible everywhere, API included.
- Job handler and client extensions fail to load silently without a `*.vcet.config` beside the
  DLL, exactly one public `IJobHandler`, and a matching `ApiVersionAttribute`.
- `openapi-spec.yml` commonly 404s through a Gateway URL — fetch it from the direct server.
- Browser callers need CORS enabled in the Vault server's IIS `web.config`; without it the
  browser reports a generic network error instead of an HTTP status.

## References

- [references/dotnet-api.md](references/dotnet-api.md) — SDK setup, `WebServiceManager`
  services, VDF, search and acquire patterns, job handlers, client extensions
- [references/cloud-api.md](references/cloud-api.md) — Vault Data API base URLs, token types,
  endpoint families, spec discovery, Gateway, CORS
- [references/vault-metadata.md](references/vault-metadata.md) — entity classes, system
  properties vs UDPs, categories, lifecycles, versions vs revisions, items and BOMs
- `scripts/vault_probe.py` — live capability probe used in Phase 1
