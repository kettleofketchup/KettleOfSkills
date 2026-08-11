# Coder CLI & Day-2 Operations

## Setup

```bash
curl -fsSL https://coder.com/install.sh | sh
coder login https://coder.example.com
coder whoami
```

Non-interactive (CI):

```bash
export CODER_URL=https://coder.example.com
export CODER_SESSION_TOKEN=$(cat token)
coder tokens create --lifetime 720h --name ci
```

## Workspaces

```bash
coder create --template kubernetes my-ws        # create
coder create --template kubernetes my-ws \
  --parameter cpu=8 --parameter memory=16 -y    # non-interactive
coder list                                      # your workspaces
coder list --all                                # all (admin)
coder start|stop|restart my-ws
coder delete my-ws --orphan                     # skip terraform destroy (last resort)
coder ssh my-ws
coder port-forward my-ws --tcp 8080:8080
coder open vscode my-ws
coder update my-ws                              # rebuild on latest template version
coder show my-ws                                # resources + agent status
```

`--orphan` removes the workspace record without destroying infrastructure. It leaks real resources — use only
when Terraform destroy is permanently broken, then clean up by hand.

## Templates

```bash
coder templates init                            # scaffold
coder templates list
coder templates push k8s -d ./templates/k8s --yes
coder templates push k8s --activate=false       # stage a version
coder templates versions list k8s
coder templates versions archive k8s <version>
coder templates pull k8s ./out
coder templates delete k8s
```

Safe promotion: push with `--activate=false`, update one workspace to the new version, verify, then activate.

## Users, Groups, Roles

```bash
coder users list
coder users create --email a@example.com --username alice
coder users edit-roles alice --roles template-admin
coder users suspend alice
coder groups create devops -O default
coder groups edit devops --add-users alice,bob
coder organization roles show --org default
```

## Provisioners

```bash
coder provisioner list
coder provisioner jobs list
coder provisioner jobs cancel <id>
coder provisioner keys create k8s --org default
```

## Diagnostics

```bash
coder ping my-ws           # p2p vs relay, latency
coder speedtest my-ws
coder netcheck             # local connectivity report
coder stat                 # inside a workspace: cpu/mem/disk
coder support bundle my-ws # full diagnostic archive for a ticket
```

## Debugging a Failed Build

1. `coder show <ws>` — which stage failed.
2. Dashboard → workspace → **Build log** — full `terraform apply` output.
3. `coder provisioner jobs list` — is the job even claimed? An unclaimed job means a tag mismatch, not a
   Terraform error.
4. `kubectl get events -n coder-workspaces --sort-by=.lastTimestamp` — image pull, quota, scheduling failures.
5. `kubectl logs -n coder deploy/coder` — control plane errors.

### coder-logstream-kube

Install this on any Kubernetes deployment. It streams pod events into the workspace build log, so users see
"ImagePullBackOff" or "exceeded quota" in the dashboard instead of a build that hangs with no explanation.

```bash
helm repo add coder-logstream-kube https://helm.coder.com/logstream-kube
helm install coder-logstream-kube coder-logstream-kube/coder-logstream-kube \
  --namespace coder \
  --set url=https://coder.example.com
```

Surfaces pending-pod causes, image and resource-quota failures, OOMKills, and evictions. Install it in the
namespace where workspace pods run if that differs from the `coderd` namespace.

## Debugging an Agent That Never Connects

The build succeeded but the agent shows "connecting" forever. In order:

```bash
kubectl get pods -n coder-workspaces
kubectl logs -n coder-workspaces <workspace-pod>       # look for the init script running
kubectl exec -n coder-workspaces <pod> -- env | grep CODER_AGENT_TOKEN
kubectl exec -n coder-workspaces <pod> -- curl -sv $CODER_URL/api/v2/buildinfo
```

Ranked causes: missing `CODER_AGENT_TOKEN`; `init_script` not used as the container command;
`CODER_ACCESS_URL` unreachable from the pod network; egress NetworkPolicy blocking the control plane;
container image lacking `curl`/`bash` needed by the init script.

## Server Logs

```bash
kubectl logs -n coder deploy/coder -f
kubectl logs -n coder deploy/coder | grep -i "oidc claims"      # with CODER_LOG_FILTER set
```

```yaml
coder:
  env:
    - name: CODER_VERBOSE
      value: "true"
    - name: CODER_LOG_JSON
      value: "/dev/stderr"
```

## Backup & Restore

State lives entirely in PostgreSQL plus workspace PVCs.

```bash
pg_dump -Fc "$CODER_PG_CONNECTION_URL" > coder-$(date +%F).dump
```

Restoring the database without the matching PVCs gives you workspace records pointing at volumes that no
longer exist — back up both, or accept that restore means rebuilding workspaces.

## Audit Log (Premium)

```bash
coder audit list --limit 50
```

Covers user, template, workspace, and organization mutations. Ship it off-box if you need retention beyond the
database.
