# fzf-tab Advanced Previews

Custom command previews and context extraction for fzf-tab.

## Custom Previews for Commands

```zsh
# systemctl: show service status
zstyle ':fzf-tab:complete:systemctl-*:*' fzf-preview \
    'SYSTEMD_COLORS=1 systemctl status $word'

# kill: show process info
zstyle ':fzf-tab:complete:kill:argument-rest' fzf-preview \
    'ps --pid=$word -o cmd,pid,%cpu,%mem --no-headers'

# git checkout: show branch info
zstyle ':fzf-tab:complete:git-checkout:*' fzf-preview \
    'git log --oneline --graph -10 $word'

# docker: show container/image info
zstyle ':fzf-tab:complete:docker-run:*' fzf-preview \
    'docker images $word --format "{{.Repository}}:{{.Tag}} {{.Size}}"'
```

## Targeting Specific Contexts

```zsh
# Target argument-rest (not options)
zstyle ':fzf-tab:complete:mycli:argument-rest' fzf-preview 'mycli info $word'
# Target specific option values
zstyle ':fzf-tab:complete:mycli:option-config-1' fzf-preview 'cat $word'
```

## Advanced: Extract Context

For complex previews needing completion context:

```zsh
local extract="
in=\${\${\"\$(<{f})\"%\$'\\0'*}#*\$'\\0'}
local -A ctxt=(\"\${(@ps:\\2:)CTXT}\")
"

zstyle ':fzf-tab:complete:kill:*' extra-opts \
    --preview=$extract'ps --pid=$in[(w)1] -o cmd --no-headers -w -w' \
    --preview-window=down:3:wrap
```

## Subcommand Completion with Groups

```zsh
_mycli() {
    local -a main_cmds=('start:Start app' 'stop:Stop app' 'config:Manage config')
    local -a config_cmds=('get:Get value' 'set:Set value')

    case $words[2] in
        config) _describe -t config-commands 'config command' config_cmds ;;
        *)      _describe -t main-commands 'command' main_cmds ;;
    esac
}
```

## Color Configuration for fzf-tab

```zsh
# fzf-tab uses FZF_DEFAULT_OPTS for colors
zstyle ':fzf-tab:*' fzf-flags --color=fg:white,hl:blue,bg+:black

# Preview window styling
zstyle ':fzf-tab:complete:*' fzf-preview 'less ${(Q)realpath}'
```
