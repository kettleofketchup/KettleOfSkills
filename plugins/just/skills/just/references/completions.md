# Just Shell Completions

## Detection

Check if completions exist:

```bash
# For zsh
type _just &>/dev/null

# For bash
type _just &>/dev/null || complete -p just &>/dev/null
```

## Setup

Create completions directory (respects XDG):

```bash
JUST_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/just"
mkdir -p "$JUST_CONFIG_DIR"
```

Generate completions file:

```bash
# For zsh
just --completions zsh > "$JUST_CONFIG_DIR/completions.zsh"

# For bash
just --completions bash > "$JUST_CONFIG_DIR/completions.bash"
```

## Add to Shell RC

For **zsh** (`~/.zshrc`):

```bash
# just completions
if command -v just &>/dev/null; then
    [[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/just/completions.zsh" ]] && \
        source "${XDG_CONFIG_HOME:-$HOME/.config}/just/completions.zsh"
fi
```

For **bash** (`~/.bashrc`):

```bash
# just completions
if command -v just &>/dev/null; then
    [[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/just/completions.bash" ]] && \
        source "${XDG_CONFIG_HOME:-$HOME/.config}/just/completions.bash"
fi
```

## Verification

```bash
source ~/.zshrc  # or ~/.bashrc
type _just  # should show completion function
```

## fzf-tab Integration

For rich group-aware previews, see `groups.md`.
