# fzf-tab Integration

Enhance completions with fzf fuzzy finding, grouping, and previews.

## Installation

```zsh
# With zinit (load early, before compinit)
zinit light Aloxaf/fzf-tab
```

## Group Configuration

Groups organize completions by type (commands, files, options).

```zsh
# Show group headers
zstyle ':fzf-tab:*' show-group full        # Always show group name
zstyle ':fzf-tab:*' show-group brief       # Show only when multiple groups
zstyle ':fzf-tab:*' single-group full      # Show even for single group

# Switch between groups with < and >
zstyle ':fzf-tab:*' switch-group '<' '>'
```

## Completion Grouping in Scripts

Tag completions to create groups:

```zsh
_mycommand() {
    local -a commands options

    commands=(
        'start:Start the service'
        'stop:Stop the service'
    )
    options=(
        '--verbose:Enable verbose output'
        '--config:Config file path'
    )

    # Tags create separate groups in fzf-tab
    _describe -t commands 'command' commands
    _describe -t options 'option' options
}
```

With `_alternative`:

```zsh
_alternative \
    'commands:command:_mycommand_commands' \
    'files:file:_files' \
    'options:option:_mycommand_options'
```

## Preview Configuration

### Preview Variables

| Variable | Description |
|----------|-------------|
| `$realpath` | Full path to file (resolved) |
| `$word` | Current completion word |
| `$group` | Current group name |
| `$desc` | Description text |

### Command-Specific Previews

```zsh
# File browsing commands
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'lsd --tree --depth 1 $realpath'
zstyle ':fzf-tab:complete:ls:*' fzf-preview 'lsd --tree --depth 1 $realpath'
zstyle ':fzf-tab:complete:cat:*' fzf-preview 'bat --color=always $realpath'

# Use a preview script for multiple types
zstyle ':fzf-tab:complete:*:*' fzf-preview 'fzf.zsh $realpath'
```

### Preview Script Pattern (fzf.zsh)

Universal preview script that handles different file types:

```zsh
#!/usr/bin/env zsh
# ~/bin/fzf.zsh - Universal preview for fzf-tab

[[ $# -ne 1 ]] && { echo "usage: $0 FILENAME"; exit 1; }

file=${1/#\~\//$HOME/}
type=$(file --dereference --mime -- "$file")

# Directory: show tree
if [[ $type =~ directory ]]; then
    lsd --tree --depth 1 --group-directories-first --color=always --icon=always "$file"
    exit
fi

# Binary: show file info
if [[ $type =~ binary ]]; then
    file "$file"
    exit
fi

# Image: use kitty/chafa
if [[ $type =~ image ]]; then
    if [[ $KITTY_WINDOW_ID ]]; then
        kitty icat --clear --transfer-mode=memory --place="${FZF_PREVIEW_COLUMNS}x${FZF_PREVIEW_LINES}@0x0" "$file"
    elif command -v chafa &>/dev/null; then
        chafa -s "${FZF_PREVIEW_COLUMNS}x${FZF_PREVIEW_LINES}" "$file"
    fi
    exit
fi

# Text: use bat
bat --style="grid,header,numbers" --color=always --pager=never --line-range 0:30 "$file"
```

## Popup Configuration

```zsh
# Use tmux popup
zstyle ':fzf-tab:*' fzf-command ftb-tmux-popup
zstyle ':fzf-tab:*' popup-min-size 80 20

# Pass fzf options
zstyle ':fzf-tab:*' fzf-flags --height=50%
zstyle ':fzf-tab:*' use-fzf-default-opts yes
```

See `references/fzf-tab-advanced.md` for custom command previews and context extraction.
