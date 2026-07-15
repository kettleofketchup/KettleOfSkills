# Docker-in-Docker: bind mounts, build context, and rootless

How files get into images vs. containers, why bind-mounting a checkout fails on
rootless dind, and the CI patterns that actually work.

## The mental model: three filesystems, two delivery mechanisms

In a dind-based CI runner there are **three separate filesystems**:

1. **The runner / client container** — holds the checkout the CI system placed there.
2. **The dind daemon container** — a *separate* container (often rootless, uid 1000) that
   shares only the API socket (`DOCKER_HOST=unix:///run/dind/docker.sock`) and its own data
   dir (`/var/lib/docker`). It does **not** see the runner's workspace.
3. **Each job / build container** the daemon launches — siblings of the job, children of the daemon.

Two mechanisms move host files, and they are **not interchangeable**:

| | Build-time `COPY`/`ADD` | Run-time bind mount |
|---|---|---|
| When | During `docker build` | At `docker run` / compose up |
| Reads from | The **build context** (shipped to the builder over the API) | A path on the **daemon host's** filesystem |
| Result | Baked into an immutable image layer | Live, bidirectional overlay on a running container |
| Honors `.dockerignore`? | **Yes** — context is filtered before it's sent | **No** — never consults it |
| Path resolved on | The builder (travels over the socket) | The **daemon**, not the client |

> "Mount a folder into an image" is a category error. Mounts attach to *containers*; copies
> build *images*. — see [build context](https://docs.docker.com/build/concepts/context/) and
> [bind mounts](https://docs.docker.com/engine/storage/bind-mounts/).

## Why bind-mounting a checkout fails on rootless dind

**Key rule (verbatim):** *"Bind mounts are created to the Docker daemon host, not the client.
If you're using a remote Docker daemon, you can't create a bind mount to access files on the
client machine in a container."* — [docs](https://docs.docker.com/engine/storage/bind-mounts/)

A dind daemon reached over a socket **is** effectively a remote daemon w.r.t. your files.
Failure chain for `volumes: ["..:/workspace"]`:

1. **Visibility (root cause):** the checkout lives only in the *runner* container. The dind
   daemon resolves `/workspace/...` on *its own* filesystem, where it does not exist.
2. **Auto-create:** with `--volume` / compose short-syntax, Docker auto-creates a missing
   source dir on the daemon host. So the daemon runs `mkdir /workspace`.
3. **Permission (symptom):** rootless daemon (uid 1000) can't write to `/`, so →
   `mkdir /workspace: permission denied`.

Two independent facts: **`--mount` errors instead of auto-creating** (only `-v`/compose
auto-create), and rootful daemons *can* mkdir at `/` — which is why a rootful runner "works."
But even a successful mkdir yields an **empty** directory, not your checkout.
**Fixing permissions never fixes visibility.**

## Decision list: `mkdir <path>: permission denied` on a dind bind mount

1. **The source path lives only in the runner/client**, not on the daemon. Do **not**
   `chmod`/`chown` — the path doesn't exist on the daemon at all.
2. **Prefer:** bake the files into the image (`COPY`) or use a **named volume** — both remove
   the host-path dependency.
3. **If you must keep a host path:** mount the *same* directory into both the runner and the
   dind container at the *identical absolute path*, correct rootless uid/gid, and allow it in
   the runner's `valid_volumes` glob. Fragile — any drift silently reverts to the mkdir failure.
4. **Rootful "works"** only because the daemon shares the filesystem — it hides the design
   flaw, it doesn't fix it.

## CI solutions playbook

### Option 1 — Bake into a hermetic image (best default)
`COPY . /app/repo` and run tests inside the image. No bind mount → daemon-topology-agnostic;
identical on rootless dind and rootful runners. Reproducible and cache-friendly. Con: rebuild
on source change (mitigate with layer ordering / cache mounts) **and the `.dockerignore`
gotcha below.**

#### ⚠ The `.dockerignore`-strips-tests gotcha
`.dockerignore` filters the context *before* it reaches the builder — matching files *"are
removed from the build context before it's sent to the builder."* A pattern like `**/tests/`
removes every test package, so `COPY . /app/repo` yields an image missing `yourpkg.users.tests`
→ `ModuleNotFoundError`. A **bind mount never hit this** (it ignores `.dockerignore`), which is
exactly why switching bind → COPY *surfaces* the bug.

**Fix** (last matching line wins):
```dockerignore
**/tests/
!**/src/**/tests/**   # re-include contents; target /** not just the dir entry
```
Or use a Dockerfile-specific ignore file — `test.Dockerfile.dockerignore` takes precedence over
the root `.dockerignore`, so the prod image keeps stripping tests while the test image keeps them.

### Option 2 — Named volumes
Daemon-managed, stored under the daemon's own data root (`~/.local/share/docker/volumes` when
rootless) — no host path for the rootless daemon to `mkdir` at `/`. **Caveat:** a named volume
starts *empty* — it does not deliver your repo (git-clone in an init step or bake instead).

### Option 3 — Native `services:` (often cleanest)
Drop the nested `docker compose`. Use the Actions workflow's `services:` block for
Postgres/Redis/etc. and run the test command directly in the job container, which already has
the checkout via the standard checkout step. Removes the whole dind path/permission surface and
any `.dockerignore` interaction. (Works in Forgejo/Gitea Actions; mirrors GitHub Actions.)

### Option 4 — DooD (Docker-out-of-Docker)
Mount the **host** docker socket into the runner instead of a separate dind; bind mounts then
resolve against the host filesystem. Acceptable **only** when runner and host share the
referenced filesystem **and** you accept jobs gain control of the host daemon —
**host-root-equivalent**. Unacceptable on shared/multi-tenant clusters. (K8s nodes often run
containerd, so there may be no host dockerd to mount.)

### Option 5 — Rootful / privileged dind
Makes the bind-mount job "just work" (root daemon can create paths at `/`). Cost: `--privileged`
is required for *any* dind, and rootful additionally runs the daemon as **real root** — you give
up the isolation rootless was chosen for. Trade only where the threat model permits.

### Version pinning — the 29.x CDI note
Pin the dind image to an explicit tag (e.g. `docker:28.3-dind-rootless`), never `docker:dind`
/ `docker:latest`. Docker **29.2.0** started handling `--gpus` via CDI (moby/moby#50228);
**29.3.0** extended CDI and changed rootless CDI spec paths (#51624). On a GPU-less node with no
CDI specs, the discovery path can fatally return HTTP 500 `failed to discover GPU vendor from
CDI: no known GPU vendor found`, hanging buildx/container start. The 28.x line is unaffected.
**Mitigation:** pin dind to 28.x; validate buildx + a container start on a GPU-less node before
promoting any dind bump. See [Docker 29 release notes](https://docs.docker.com/engine/release-notes/29/).

## Rootless dind: can / cannot

| Rootless dind (dockerd as uid 1000 in a user namespace) | |
|---|---|
| **Named volumes** (daemon-managed, under `~/.local/share/docker/volumes`) | ✅ works |
| **Bind to a path the rootless user owns on the daemon host** | ✅ works |
| **Create/own a bind source at a privileged location** (e.g. `/workspace` at `/`) | ❌ `mkdir … permission denied` |
| **Bind a path that exists only in another container's namespace** (nested-workspace case) | ❌ not visible to the daemon |
| **`COPY` from build context** (subject to `.dockerignore`) | ✅ works (topology-agnostic) |

**Why accept the pain:** rootless maps container "root" to an unprivileged host uid, so a daemon
compromise or breakout is confined to one unprivileged account instead of node root. The right
fixes (bake source, shared/named volume, scoped socket perms, version pin) preserve rootless
rather than reverting to rootful.

**References:** [build context](https://docs.docker.com/build/concepts/context/) ·
[bind mounts](https://docs.docker.com/engine/storage/bind-mounts/) ·
[volumes](https://docs.docker.com/engine/storage/volumes/) ·
[rootless mode](https://docs.docker.com/engine/security/rootless/) ·
[docker/dind image](https://hub.docker.com/_/docker) ·
[Docker 29 release notes](https://docs.docker.com/engine/release-notes/29/)
