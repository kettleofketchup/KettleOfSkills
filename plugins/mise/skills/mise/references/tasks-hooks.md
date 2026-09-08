# Mise Tasks & Hooks

## TOML Task Definitions

```toml
[tasks]
dev = "npm run dev"
test = "npm test"
build = "cargo build --release"

# multi-command
[tasks.setup]
run = ["npm install", "npm run build", "npm run migrate"]

# with metadata
[tasks.deploy]
description = "Deploy to production"
run = "kubectl apply -f k8s/"
depends = ["build", "test"]
```

## Task Dependencies

```toml
[tasks.test]
depends = ["build"]
run = "cargo test"

# pass env to dependency
[tasks.e2e]
depends = [{ task = "setup", env = { NODE_ENV = "test" } }]
run = "playwright test"

# post-completion tasks
[tasks.build]
run = "cargo build"
depends_post = ["notify"]

# wait without adding to run list
[tasks.deploy]
wait_for = ["build"]
run = "kubectl apply -f k8s/"
```

## Task Arguments (usage spec)

```toml
[tasks.greet]
usage = '''
arg "<name>" help="Person to greet"
flag "-l --loud" help="Shout the greeting"
flag "-g --greeting <msg>" default="Hello" help="Greeting to use"
'''
run = 'echo "${usage_greeting} ${usage_name}"'
```

## Task Environment, Tools & Caching

```toml
[tasks.lint]
env.ESLINT_USE_FLAT_CONFIG = "true"
tools.node = "22"              # task-specific tool version
dir = "{{cwd}}"                # run from current dir (default: config root)

[tasks.build]
run = "cargo build --release"
sources = ["Cargo.toml", "src/**/*.rs"]  # skip if unchanged
outputs = ["target/release/myapp"]       # or { auto = true }
```

## Task Modifiers

```toml
[tasks.dangerous]
confirm = "Are you sure?"   # prompt before running
quiet = true                # suppress mise output
raw = true                  # connect stdin/stdout directly
hide = true                 # hide from listings
alias = "d"                 # short alias
```

Output modes (`mise settings set task.output <mode>`):
`prefix` | `interleave` | `keep-order` | `replacing` | `quiet` | `silent`

## File-Based Tasks

Executable files in `mise-tasks/` with `#MISE` metadata comments:
`#MISE description="..."`, `#MISE depends=[...]`, `#MISE sources=[...]`

## Shared Variables & Task Config

```toml
[vars]
e2e_args = "--headless --reporter=html"

[tasks.test-e2e]
run = "playwright test {{vars.e2e_args}}"

[task_config]
dir = "{{cwd}}"              # default working directory
includes = ["tasks/"]         # custom task directories
redactions = ["SECRET_KEY"]   # hide values from output
```

---

## Hooks

Require `mise activate` in shell (except pre/postinstall).

```toml
[hooks]
cd = "echo 'changed to {{env.PWD}}'"
enter = "echo 'entered project'"
leave = "echo 'left project'"

# run a task on enter
[hooks]
enter = { task = "setup" }

# multiple hooks
[hooks]
enter = ["echo 'welcome'", { task = "setup" }]
```

### Hook Types

| Hook | Trigger | Use case |
|------|---------|----------|
| `cd` | Every directory change | Status updates |
| `enter` | First time entering project | One-time setup |
| `leave` | Leaving project directory | Cleanup |
| `preinstall` | Before tool install | Validation |
| `postinstall` | After tool install | Post-setup |

### Watch Files & Tool Postinstall

```toml
[[hooks]]
watch_files = ["src/**/*.rs"]
run = "cargo check"

[tools]
node = { version = "22", postinstall = "corepack enable" }
```

Hook env vars: `MISE_ORIGINAL_CWD`, `MISE_PROJECT_ROOT`, `MISE_PREVIOUS_DIR` (cd only), `MISE_INSTALLED_TOOLS` (postinstall, JSON array)
Tool postinstall env vars: `MISE_TOOL_NAME`, `MISE_TOOL_VERSION`, `MISE_TOOL_INSTALL_PATH`
