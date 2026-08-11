# Scheduling, Lifecycle & Quotas

The two mechanisms that stop a self-hosted deployment from quietly running idle workspaces forever.

## Autostop / Autostart

Set per template (Template → Settings → Schedule), with user overrides if permitted.

| Setting | Meaning |
|---------|---------|
| **Default autostop** | Hours of inactivity before the workspace stops |
| **Activity bump** | Extends the deadline when activity is detected (default 1h) |
| **Autostart** | Whether users may schedule automatic starts |
| **Allow user custom schedule** | Lets users override the template default |

Activity means an active VS Code, JetBrains, terminal, or SSH session. A workspace with an idle SSH session
left open still counts as active — this is the usual reason autostop appears not to fire.

```bash
coder templates edit my-template \
  --default-ttl 8h \
  --allow-user-autostop=true \
  --allow-user-autostart=true \
  --dormancy-threshold 168h \
  --failure-ttl 24h
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--default-ttl` | — | Time before shutdown for workspaces from this template |
| `--allow-user-autostop` | `true` | Users may set their own autostop TTL (disabling requires Premium) |
| `--allow-user-autostart` | `true` | Users may configure autostart (disabling requires Premium) |
| `--require-active-version` | `false` | Force builds onto the active version (template admins exempt) |
| `--dormancy-threshold` | `0h` | Inactivity before dormant; `0h` disables |
| `--failure-ttl` | `0h` | Time after a failed start before cleanup |

Users manage their own schedules with:

```bash
coder schedule show <workspace>
coder schedule start <workspace>    # edit the start schedule
coder schedule stop <workspace>     # edit the stop schedule
coder schedule extend <workspace>   # push back the deadline of a running workspace
```

`stop` edits the recurring schedule; `extend` is what buys more time on a workspace that's about to autostop.
Run each with `--help` for its argument format.

## Quiet Hours

Deployment-wide window in which forced restarts happen:

```
CODER_QUIET_HOURS_DEFAULT_SCHEDULE="CRON_TZ=Europe/London 0 3 * * *"
CODER_ALLOW_CUSTOM_QUIET_HOURS=true
```

Set `CODER_ALLOW_CUSTOM_QUIET_HOURS=false` to pin everyone to the default.

## Autostop Requirement (Premium)

Mandatory periodic restart so long-lived workspaces pick up template updates and don't run indefinitely
because a connection was left open.

- **Days**: daily, Saturday, or Sunday
- **Weeks**: every 1–16 weeks, synchronized across the template's workspaces
- Restarts occur inside each user's quiet hours

## Dormancy & Cleanup (Premium)

| Setting | Effect |
|---------|--------|
| **Dormancy threshold** | Inactivity before a workspace becomes dormant (stopped, needs manual reactivation) |
| **Dormancy auto-deletion** | How long a dormant workspace survives before deletion |
| **Failure cleanup** | How long a failed workspace waits before being stopped |

Auto-deletion destroys the PVC too. Announce it before enabling, and confirm users keep work in git rather
than only in `/home/coder`.

## Quotas

Credit budgets that cap concurrent resource consumption per user.

### Declaring Cost in a Template

```hcl
resource "coder_metadata" "workspace" {
  resource_id = kubernetes_deployment_v1.main[0].id
  daily_cost  = 20
}

resource "coder_metadata" "home" {
  resource_id = kubernetes_persistent_volume_claim_v1.home.id
  daily_cost  = 10
}
```

Resources without `daily_cost` are free. Put the cost on the compute resource (which is gated by
`start_count`) and a smaller cost on the PVC, so a stopped workspace consumes 10 rather than 30. That
difference is what actually incentivizes users to stop workspaces.

### Budgets

Allowances are set per group; **a user's budget is the sum of all their groups' allowances**. Default group
allowance is 0. A user in Frontend (10) and Backend (20) has 30 credits.

Because the Everyone group also carries an allowance, setting it deployment-wide gives a baseline that group
membership adds to.

### Enforcement

Quotas are enforced at workspace **start**, not at creation. Exceeding the budget fails the build rather than
blocking the form — users see a failed start with a quota message, not a rejected create. Expect that as a
support question the first time you enable quotas.

## Template Update Policy

```bash
coder templates edit my-template --require-active-version
```

Forces workspaces onto the current template version at next start, rather than letting them pin an old one.
Pair it with an autostop requirement so the update actually lands.

## Cost Controls Summary

| Lever | Stops |
|-------|-------|
| Autostop + activity bump | Idle running compute |
| Dormancy + auto-deletion | Abandoned workspaces |
| Quotas | Over-provisioning by any one user |
| Prebuild `scheduling` | Warm pools running overnight (→ `presets-prebuilds.md`) |
| `coder_parameter` `validation.max` | Oversized individual workspaces (→ `parameters.md`) |
