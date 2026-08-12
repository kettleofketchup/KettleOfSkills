# Workspaces, Repos & Backends

How a repository gets attached to a self-hosted agent-server. Verified against **agent-canvas frontend +
agent-server 1.40.1**.

## The three concepts are not interchangeable

| Concept | What it is | Where it lives |
|---------|-----------|----------------|
| **Backend** | One agent-server instance the UI connects to | Browser-side list; `Manage backends` dialog |
| **Workspace** | A named *directory on the agent-server* | `<persistence_dir>/workspaces.json` |
| **Repository** | A git provider integration (GitHub/GitLab/…) | **Cloud / enterprise only** |

The common mistake is reaching for "backends" to get per-repo agents. A backend is a **machine**, not a project.

## Backends

`BACKEND$ADD_SUBTITLE`: *"Connect this app to another agent server. Once added, you can switch between
backends from the menu above."*

Fields, and that is the whole schema:

| Field | Meaning |
|-------|---------|
| Host Name | friendly label |
| Host | URL of the agent server |
| API Key | `X-Session-API-Key` (local/remote) or `Authorization: Bearer` (cloud) |
| Type | `local` / `remote` / `cloud` |

There is no repo field. Add a backend only when a second agent-server actually exists. One agent-canvas
release per repo *is* a legitimate architecture — separate PVC, separate LLM budget, separate blast radius —
but it multiplies the whole deployment, so reach for it only when you want that isolation.

### Running a backend to point it at

A backend does not need the full Canvas deployment — it needs a backend-only agent-server:

```bash
export LOCAL_BACKEND_API_KEY="<high-entropy secret>"   # REQUIRED by --public
agent-canvas --backend-only --public                   # listens on :8000
```

or as a container:

```bash
docker run -p 8000:8000 ghcr.io/openhands/agent-server:<tag>-python
```

`LOCAL_BACKEND_API_KEY` is exactly what goes in the API Key field above, and it travels as
`X-Session-API-Key`. **That key is the entire security boundary** — the agent-server accepts any request
carrying it, and there is no user auth behind it. Upstream's own guidance is to keep 8000 firewalled and reach
it through an SSH tunnel, ngrok, or a TLS reverse proxy. In-cluster, a NetworkPolicy restricting who may reach
:8000 is the equivalent, and it is not optional: anyone who can dial the port and guess the key drives an
agent that executes arbitrary code.

### What switching a backend actually switches

Settings, LLM configuration, MCP servers and automations all live **on the backend**, not in the browser. So
backends are environments to provision, not contexts to flip between — expect to configure each one. Whether
an existing conversation can be reassigned to a different backend is undocumented; assume a conversation stays
on the backend that created it unless you have verified otherwise.

### Per-backend isolation is the OSS answer to "agents must not see each other"

Conversations sharing one backend share its filesystem, processes and any Docker daemon it can reach. Separate
backends share nothing. So the shape that buys real isolation is *N* agent-servers — one per user, per repo,
or per long-running task — each a separate pod/VM/workspace, all registered in `Manage backends`. This is
coarser than Enterprise's automatic per-run sandboxes, but it is real and it costs no license.

## Workspaces are the repo linkage

From `openhands/agent_server/workspaces_router.py`:

> *"Workspaces are local directories the GUI surfaces in its workspace picker. They are persisted on the
> agent-server (file-backed JSON) rather than in each browser's localStorage so that every client connected to
> the same agent-server sees the same list."*

```
GET    /api/workspaces           → {"workspaces":[…], "workspaceParents":[…]}
POST   /api/workspaces           → {"workspaces":[WorkspaceItem, …]}
DELETE /api/workspaces?path=…
POST   /api/workspaces/parents   → {"parents":[WorkspaceParentItem, …]}
DELETE /api/workspaces/parents?path=…
```

`WorkspaceItem = {id, name, path, parentPath?}` — `path` is a directory **on the agent-server**.
`WorkspaceParentItem = {id, name, path}` groups them into a folder; children under a registered parent are
discovered automatically, so later clones appear without re-adding.

Persisted to `<persistence_dir>/workspaces.json` — i.e. `$OH_PERSISTENCE_DIR/workspaces.json`, default
`~/.openhands/workspaces.json`. On K8s that must be on the PVC or the list resets every restart.

Once registered, the conversation panel groups threads by them (`CONVERSATION_PANEL$BY_WORKSPACE`).

## There is no "add a git repo" in a self-hosted UI

Git provider integration is **not an agent-server feature**. In 1.40.1:

- The settings nav is a fixed seven: `agents`, `llm`, `condenser`, `agent-context`, `verification`, `app`,
  `secrets`. No Git tab, no Integrations tab.
- The "Integrations" and "Cloud settings" nav links are hard-gated `kind !== 'cloud' ? null : …`. On a
  **local** backend they render as nothing.
- The agent-server exposes **zero** provider endpoints. Its only git routes — `/api/git/changes`,
  `/api/git/commits`, `/api/git/diff` — operate on whatever repo is already in the working directory.

So the repo must be cloned onto the agent-server first, by you or by the agent.

### The actual flow

1. **Clone onto the agent-server**, under the persisted workspace dir. Asking the agent to run the clone is
   usually easiest — it already has the container's SSH key and egress:
   ```
   git clone <url> /home/openhands/workspace/repos/<name>
   ```
2. **Home → Workspaces → `+ Add Workspace`.** This opens a *server-side* folder browser
   (`folder-browser-modal`) — it lists the agent-server's filesystem, not the browser host's. No
   `showDirectoryPicker`/`webkitdirectory` is involved.
3. **"Add this directory"** for one repo, or sit on the parent and **"Add all subdirectories"** to register
   every repo under it at once (that writes a workspace *parent*).

The folder browser is backed by:

```
GET /api/file/home           → {"home":…, "favorites":[…], "locations":[…]}
GET /api/file/search_subdirs?path=…  → {"items":[{name,path}], "next_page_id":…}
```

`HOME$HOST_HOME_NOT_MOUNTED_HINT` — *"The agent server cannot access this directory."* — is the
Docker case where the host home was never bind-mounted, not a permissions bug in your setup.

Per-conversation scratch dirs live at `workspace/project/<conversation_id>`. Don't register those as
workspaces.

## Per-repo agent behavior

This is what actually makes an agent "know" a project — it lives **in the repo**, not in any backend or
workspace setting:

- `.openhands/setup.sh` — runs at every conversation start
- `.openhands/microagents/repo.md` — how to build, run, test
- `.openhands/` skills — gated by the agent's `load_project_skills`

→ `mcp-skills-hooks.md`

## Trap: locale strings are not a feature list

`locales/en/openhands.json` is shared with the classic OpenHands GUI, so it contains keys for features this
frontend never renders — `FORGEJO$*`, `HOME$REPOSITORIES_TAB`, `HOME$ADD_GITHUB_REPOS`, the whole
`GITHUB$`/`GITLAB$`/`BITBUCKET$` provider vocabulary. Those appear **only** in the locale-key constants module
(`utils-*.js`); no component imports them.

Before concluding a feature exists, check that a real component references the key:

```bash
grep -rl 'FORGEJO' frontend/assets      # → only utils-*.js  ⇒ dead code
grep -rl 'ADD_WORKSPACES' frontend/assets  # → home/onboarding/root-layout  ⇒ live
```

And check the nav gating — several links exist in the bundle but return `null` unless `backend.kind` is
`cloud`.
