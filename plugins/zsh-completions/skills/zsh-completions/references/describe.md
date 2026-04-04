# _describe Reference

Display completion candidates with descriptions.

## Basic Syntax

```zsh
_describe [-t tag] 'description' array [options]
```

## Array Format

```zsh
local -a items
items=(
    'name1:description for name1'
    'name2:description for name2'
    'name3'                          # no description
)
_describe 'item type' items
```

## Common Options

```zsh
_describe -t tag 'desc' array    # Tag for grouping
_describe 'desc' array -qS '='   # Add = suffix, quote special chars
_describe 'desc' array -- array2 # Multiple arrays
```

## Dynamic Completion from Commands

### Simple list

```zsh
_mycommand_targets() {
    local -a targets
    targets=(${(f)"$(mycommand list 2>/dev/null)"})
    _describe 'target' targets
}
```

### With descriptions (tab-separated)

```zsh
_docker_containers() {
    local -a containers
    # docker ps outputs: ID NAME STATUS
    containers=(${(f)"$(docker ps --format '{{.Names}}:{{.Status}}')"})
    _describe 'container' containers
}
```

### From JSON with jq

```zsh
_gh_repos() {
    local -a repos
    repos=($(gh repo list --json nameWithOwner,description -q \
        '.[] | "\(.nameWithOwner):\(.description // "No description")"'))
    _describe 'repository' repos
}
```

### Caching expensive lookups

```zsh
_kubectl_pods() {
    local cache_file="/tmp/.zsh_kubectl_pods_$$"

    if [[ ! -f $cache_file ]] || [[ $(stat -c %Y $cache_file) -lt $(($(date +%s) - 30)) ]]; then
        kubectl get pods -o name 2>/dev/null | sed 's|pod/||' > $cache_file
    fi

    local -a pods
    pods=(${(f)"$(<$cache_file)"})
    _describe 'pod' pods
}
```

## Escaping Colons in Names

Names containing `:` must escape them:

```zsh
# If names can contain colons (like just recipes with modules)
local -a items
while IFS=$'\t' read -r name desc; do
    local escaped="${name//:/\\:}"  # foo:bar → foo\:bar
    if [[ -n "$desc" ]]; then
        items+=("${escaped}:${desc}")
    else
        items+=("${escaped}")
    fi
done <<< "$(get_items_with_tabs)"
_describe 'item' items
```

## Multiple Sources with Tags

```zsh
_mycommand_complete() {
    local -a commands files

    commands=(
        'init:Initialize project'
        'build:Build project'
    )

    files=(${(f)"$(ls *.conf 2>/dev/null)"})

    _describe -t commands 'command' commands
    _describe -t files 'config file' files
}
```

## Combining with _alternative

```zsh
_alternative \
    'commands:command:_mycommand_commands' \
    'files:file:_files -g "*.txt"' \
    'users:user:_users'
```

## Return Values

```zsh
_describe 'item' items && ret=0  # Track if completions found

# Full pattern
local ret=1
_describe 'item' items && ret=0
return ret
```

## Real Example: git branches with tracking info

```zsh
_git_branches() {
    local -a branches
    local line

    while IFS= read -r line; do
        local name="${line%% *}"
        local info="${line#* }"
        branches+=("${name}:${info}")
    done < <(git branch -vv 2>/dev/null | sed 's/^[* ] //')

    _describe 'branch' branches
}
```
