---
description: Shell completions, kube-ps1 prompt integration, fzf configuration, and zinit plugin setup for kubectx/kubens
last_updated: 2026-03-18
---

# kubectx/kubens Shell Integration

## Zsh Completions

### Manual Install

```bash
# Download completion files to fpath directory
mkdir -p ~/.config/zsh/completions
curl -Lo ~/.config/zsh/completions/_kubectx \
  https://raw.githubusercontent.com/ahmetb/kubectx/master/completion/_kubectx.zsh
curl -Lo ~/.config/zsh/completions/_kubens \
  https://raw.githubusercontent.com/ahmetb/kubectx/master/completion/_kubens.zsh
```

Ensure `~/.config/zsh/completions` is in `$fpath` before `compinit`.

### Zinit Install (Binary + Completions)

```zsh
# Install kubectx and kubens binaries from GitHub releases with completions
zinit from"gh-r" as"program" pick"kubectx" for ahmetb/kubectx
zinit from"gh-r" as"program" pick"kubens" for ahmetb/kubectx

# Or with completions bundled
zinit ice from"gh-r" as"program" pick"kubectx" \
  atclone"curl -fsSLo _kubectx https://raw.githubusercontent.com/ahmetb/kubectx/master/completion/_kubectx.zsh" \
  atpull"%atclone"
zinit light ahmetb/kubectx
```

### Bash Completions

```bash
# Source completion scripts
source <(kubectl completion bash)
# kubectx/kubens bash completions (if installed via package manager, auto-loaded)
```

## kube-ps1 - Shell Prompt Integration

Displays current context and namespace in shell prompt.

### Installation

```bash
brew install kube-ps1
# Or via zinit
zinit light jonmosco/kube-ps1
```

### Zsh Configuration

```zsh
# In .zshrc
source "/opt/homebrew/opt/kube-ps1/share/kube-ps1.sh"  # or zinit loads it
PROMPT='$(kube_ps1) '$PROMPT
# Or for right prompt
RPROMPT='$(kube_ps1)'
```

### Customization

```zsh
KUBE_PS1_SYMBOL_ENABLE=true        # Show ⎈ symbol (default: true)
KUBE_PS1_SYMBOL_DEFAULT="⎈"        # Custom symbol
KUBE_PS1_CTX_COLOR="cyan"          # Context color
KUBE_PS1_NS_COLOR="blue"           # Namespace color
KUBE_PS1_SEPARATOR="/"             # Between context and namespace
KUBE_PS1_PREFIX="("                # Before kube info
KUBE_PS1_SUFFIX=")"                # After kube info
KUBE_PS1_DIVIDER=":"               # Between symbol and context
KUBE_PS1_ENABLED=true              # Toggle on/off
```

### Toggle On/Off

```bash
kubeoff          # Disable kube-ps1
kubeon           # Enable kube-ps1
kubeoff -g       # Disable globally (persists across shells)
```

## fzf Configuration

kubectx/kubens auto-detect fzf. Customize with environment variables:

```bash
# Custom fzf options for kubectx/kubens
export FZF_DEFAULT_OPTS="--height=10 --layout=reverse --border"

# Disable fzf integration (force list mode)
export KUBECTX_IGNORE_FZF=1
```

When fzf is available:
- `kubectx` opens fuzzy context picker
- `kubens` opens fuzzy namespace picker
- Type to filter, Enter to select, Esc to cancel

## fzf-tab Previews

For fzf-tab zsh plugin, add preview commands:

```zsh
# Preview context details when tab-completing kubectx
zstyle ':fzf-tab:complete:kubectx:*' fzf-preview \
  'kubectl config get-contexts ${word} 2>/dev/null'

# Preview namespace resources when tab-completing kubens
zstyle ':fzf-tab:complete:kubens:*' fzf-preview \
  'kubectl get pods -n ${word} --no-headers 2>/dev/null | head -20'
```

## Aliases

Common shell aliases for faster workflow:

```zsh
alias kctx="kubectx"
alias kns="kubens"
# Or even shorter
alias kx="kubectx"
alias kn="kubens"
```

## Troubleshooting

- **"error: no context exists"**: kubeconfig has no contexts; check `$KUBECONFIG` or `~/.kube/config`
- **fzf not triggering**: Ensure fzf binary is in `$PATH`; check `which fzf`
- **Completions not working**: Verify fpath contains completion dir, run `compinit` after adding
- **Wrong kubeconfig modified**: With multi-file `$KUBECONFIG`, changes go to file containing the context
- **Previous context (`-`) not working**: `~/.kube/kubectx` may be missing or corrupted; delete to reset
