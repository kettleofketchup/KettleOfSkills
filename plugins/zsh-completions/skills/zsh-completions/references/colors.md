# ZSH Completion Colors

Style completions with colors and formatting.

## zstyle Basics

Format: `zstyle 'context' style value`

Common contexts:
- `:completion:*` - all completions
- `:completion:*:descriptions` - description text
- `:completion:*:commands` - command completions
- `:completion:*:*:*:*:processes` - process completions

## Description Formatting

```zsh
# Colored section headers
zstyle ':completion:*:descriptions' format '%F{green}-- %d --%f'
zstyle ':completion:*:corrections' format '%F{yellow}-- %d (errors: %e) --%f'
zstyle ':completion:*:warnings' format '%F{red}-- no matches --%f'
zstyle ':completion:*:messages' format '%F{purple}-- %d --%f'

# Bold descriptions
zstyle ':completion:*:descriptions' format '%B%F{cyan}-- %d --%f%b'
```

## Color Codes

| Code | Meaning |
|------|---------|
| `%F{color}` | Start foreground color |
| `%f` | Reset foreground |
| `%K{color}` | Start background color |
| `%k` | Reset background |
| `%B` / `%b` | Bold on/off |
| `%U` / `%u` | Underline on/off |

Named colors: black, red, green, yellow, blue, magenta, cyan, white

256-color: `%F{123}` or `%F{#ff5500}`

## list-colors Style

Color completions based on type:

```zsh
# Use LS_COLORS for files
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}

# Custom colors for specific completions
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
```

### list-colors Format

`pattern=color` or `=pattern=color` for extended patterns

```zsh
# Color executables green, directories blue
zstyle ':completion:*' list-colors \
    'di=34' \
    'ex=32' \
    'ln=36'

# Color by file extension
zstyle ':completion:*' list-colors \
    '*.py=33' \
    '*.sh=32' \
    '*.md=35'
```

### ANSI Color Codes

| Code | Color |
|------|-------|
| 30/40 | Black |
| 31/41 | Red |
| 32/42 | Green |
| 33/43 | Yellow |
| 34/44 | Blue |
| 35/45 | Magenta |
| 36/46 | Cyan |
| 37/47 | White |
| 01 | Bold |
| 04 | Underline |

Combine: `01;32` = bold green

## Group Formatting

```zsh
# Separate groups visually
zstyle ':completion:*' group-name ''
zstyle ':completion:*:descriptions' format '%F{yellow}-- %d --%f'

# Specific group styling
zstyle ':completion:*:*:-command-:*:commands' group-name commands
zstyle ':completion:*:*:-command-:*:builtins' group-name builtins
```

## Menu Selection Colors

```zsh
# Highlight current selection
zstyle ':completion:*' menu select
zstyle ':completion:*:default' list-colors ${(s.:.)LS_COLORS}

# Selection highlight (requires menu select)
zstyle ':completion:*' select-prompt '%SScrolling: %p%s'
```

## Per-Command Styling

```zsh
# Color kill process list
zstyle ':completion:*:*:kill:*:processes' list-colors \
    '=(#b) #([0-9]#)*=0=01;31'

# Color git branches
zstyle ':completion:*:*:git:*:heads' list-colors '=*=34'
```

## Complete zstyle Setup

```zsh
# In ~/.config/zsh/completions.zsh or similar

# Enable menu selection
zstyle ':completion:*' menu select

# Use LS_COLORS
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}

# Group completions
zstyle ':completion:*' group-name ''

# Format descriptions
zstyle ':completion:*:descriptions' format '%F{green}-- %d --%f'
zstyle ':completion:*:corrections' format '%F{yellow}!- %d (errors: %e) -!%f'
zstyle ':completion:*:warnings' format '%F{red}-- no matches found --%f'

# Case-insensitive matching
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# Partial completion suggestions
zstyle ':completion:*' list-suffixes
zstyle ':completion:*' expand prefix suffix
```

## fzf-tab Integration

When using fzf-tab, colors are handled differently:

```zsh
# fzf-tab uses FZF_DEFAULT_OPTS for colors
zstyle ':fzf-tab:*' fzf-flags --color=fg:white,hl:blue,bg+:black

# Preview window styling
zstyle ':fzf-tab:complete:*' fzf-preview 'less ${(Q)realpath}'
```
