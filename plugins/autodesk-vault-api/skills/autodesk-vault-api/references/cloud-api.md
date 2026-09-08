# Vault Data API (REST) and Vault Gateway

The modern REST surface, introduced with **Vault 2025.2** and documented on Autodesk Platform
Services. Language-agnostic, JSON, no SDK install. Use it for integrations, web apps, scripts,
and anything that cannot host .NET Framework. Subject to the APS Terms of Service.

## Base URLs

```
Direct server:   http://{server}/AutodeskDM/Services/api/vault/v2/
Vault Gateway:   https://{gateway}.vg.autodesk.com/AutodeskDM/Services/api/vault/v2/
```

Both hosts serve the identical API surface. The gateway is a cloud relay: the Vault server
makes an **outbound** HTTPS connection to it, so no inbound firewall ports, VPN, or public IP
are needed. Vault data is not stored in the gateway, only passed through. Gateway service
locations are the continental US, Europe (Ireland), and Australia; gateways are a logical
construct on shared infrastructure, not single-tenant. Administrators create and manage
gateways in the **ADMS Console**.

## Authentication

Two token types, with different reach:

| Token | Header | Works against |
|-------|--------|---------------|
| Vault token | `Authorization: Bearer V:{uuid}` | Direct server only |
| APS 3-legged (Autodesk ID) | `Authorization: Bearer {jwt}` | Direct server **and** gateway |

Vault tokens come from a session:

```bash
# POST a session, then reuse the returned accessToken
curl -X POST "http://{server}/AutodeskDM/Services/api/vault/v2/sessions" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"vault":"Vault","userName":"Administrator","password":""}'
```

The session response carries `id`, `accessToken` (`V:{uuid}`), create date, vault info, user
info, and a self URL at `/sessions/{session-id}`. Feed `accessToken` straight into
`Authorization` on later calls.

For APS tokens: register an app at `https://aps.autodesk.com/myapps/`, choose the
**Desktop, Mobile, Single-Page App** type, copy the Client ID, then run OAuth 2.0
**Authorization Code Grant with PKCE**. There is no client secret for this app type, so PKCE
is mandatory — a 2-legged client-credentials token will not authenticate a Vault user.

```bash
curl -X GET "https://{gateway}.vg.autodesk.com/AutodeskDM/Services/api/vault/v2/users/9" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIs..."
```

## Discover the real endpoint set

The API evolves per Vault release, so read the spec off the live server rather than trusting
any static list:

```bash
curl -s "http://{server}/AutodeskDM/Services/api/vault/v2/openapi-spec.yml" -o vault-openapi.yml
```

Load it into `https://editor.swagger.io/` or parse it directly. The spec documents endpoints,
request/response schemas, and auth requirements for exactly the deployed version. Known
caveat: the spec path frequently **404s through a Gateway URL** — fetch it from the direct
server address.

## Endpoint families

`server-info` is the only unauthenticated endpoint — use it to confirm reachability and read
the product version before anything else.

| Purpose | Path (after the `.../vault/v2/` base) |
|---------|----------------------------------------|
| Server product name + version, no auth | `GET server-info` |
| Create / inspect a session | `POST sessions`, `GET sessions/{id}` |
| Vault list | `GET vaults` |
| Folder contents (files + subfolders, paged) | `GET vaults/{vaultId}/folders/{id}/contents` |
| File version history | `GET vaults/{vaultId}/files/{id}/versions` |
| Basic search | `GET vaults/{vaultId}/search-results?q={query}` |
| Item | `GET vaults/{vaultId}/items/{id}` |
| Item BOM / child items | `GET vaults/{vaultId}/item-versions/{id}/bill-of-materials` |
| **Download file bytes** | `GET` file-version content (`getfileversioncontent`) |
| **Download thumbnail** | `GET` file-version thumbnail (`getfileversionthumbnailbyid`) |
| User by id | `GET users/{id}` |

Binary **download is supported** — file version content and thumbnails both have GET
endpoints. Change orders and their attachments, comments, links, and advanced search are
covered too. Upload and check-in are not; see the capability table below.

File entries return `name`, `id`, `state`, `revision`, `category`, `size`, checkout status and
`parentFolderId`. Item payloads use an `entityType` discriminator (`"Item"`, `"ItemVersion"`)
rather than the legacy short codes, alongside `state`, `stateColor`, `category`, `revision`.
BOM responses nest `itemVersions`, `itemBomLinks`, `occurrences`, and `bomComponents`.

Search results include an `indexingStatus` in the pagination block. A search that returns
fewer hits than expected usually means the server index is still building, not that the data
is missing — check that field before debugging the query.

## Capability and version gates

The API is **primarily read-focused**. Confirm the target server version before promising a
write path:

| Capability | Availability |
|------------|--------------|
| Read: search, files, folders, items, BOM, properties, users, change orders, links | 2025.2+ |
| Read: file content and thumbnail downloads | 2025.2+ |
| Write: job creation/management | 2025.2+ |
| Write: lifecycle state updates; external sync tasks | **Vault 2027.1 and newer** |
| Write: file upload, check-in/check-out, property writes, custom entities | **not available — use the SDK/SOAP** |
| Endpoints marked *Beta* in the docs | pre-GA, may change |

Autodesk's marketing copy says the API can "create, update, and delete" and lists "file
operations", while the same overview's limitations section describes it as *read-first with
targeted writes*. The second statement is the accurate one: the documented write surface is
lifecycle states, external sync tasks, and jobs. Treat the live `openapi-spec.yml` as the only
authority for a given server, and never promise a write path from the docs alone.

Anything not explicitly marked Beta is GA. If a write operation is unavailable on the target
version, fall back to the .NET SDK or its SOAP endpoints — see `dotnet-api.md`.

## CORS for browser callers

Browser clients hitting the API cross-origin need IIS configured on the Vault server. Edit
`web.config`, find `<server>` under `<connectivity.web>`, and add:

```xml
<server ...>
  <restapi>
    <cors enabled="true" origins="http://servera,https://serverb" />
  </restapi>
</server>
```

`origins` takes a comma-separated allowlist. Without this, preflight fails and the browser
reports a generic network error rather than an HTTP status.

## Choosing REST over .NET

Pick the Vault Data API when the client is non-Windows, containerised, browser-based, or
remote via Gateway. Pick the .NET SDK when the task needs writes the REST API lacks (check-in,
file upload, property writes, custom entities), Job Processor handlers, or Vault client UI
extensions. The two authenticate independently — an APS token does not carry into the SDK
except through `AutodeskAuthCredentials`.
