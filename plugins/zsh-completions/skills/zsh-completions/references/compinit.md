# compinit Internals

Understanding the zsh completion system initialization.

## Core Concepts

### fpath

Function search path for autoloaded functions (including completions):

```zsh
# View current fpath
print -l $fpath

# Add custom completions directory (BEFORE compinit)
fpath=(~/.config/zsh/completions $fpath)
```

### compinit

Initializes the completion system:

```zsh
autoload -Uz compinit && compinit
```

What it does:
1. Sources completion functions from fpath
2. Creates `~/.zcompdump` cache file
3. Sets up `_comps` associative array (command → completer mapping)

### compdef

Registers completion function for commands:

```zsh
compdef _mycommand mycommand        # _mycommand handles 'mycommand'
compdef _mycommand mycommand mycmd  # Also alias 'mycmd'
compdef _gnu_generic mytool         # Use generic GNU-style completion
```

## Completion File Structure

Standard `_commandname` file:

```zsh
#compdef commandname

# Optional: register aliases
compdef _commandname commandname
compdef _commandname cmd-alias

_commandname() {
    # completion logic
}

_commandname "$@"
```

## Load Order Matters

```zsh
# CORRECT ORDER:
fpath=(~/.config/zsh/completions $fpath)  # 1. Set fpath first
autoload -Uz compinit && compinit         # 2. Then initialize

# WRONG - completions won't be found:
autoload -Uz compinit && compinit
fpath=(~/.config/zsh/completions $fpath)  # Too late!
```

## zcompdump Cache

compinit creates `~/.zcompdump` for faster startup:

```zsh
# Force rebuild
rm ~/.zcompdump && compinit

# Rebuild only if older than 1 day (startup optimization)
autoload -Uz compinit
if [[ -n ${ZDOTDIR}/.zcompdump(#qN.mh+24) ]]; then
    compinit
else
    compinit -C  # Skip security check for speed
fi
```

## Zinit Integration

Zinit manages compinit timing:

```zsh
# Let zinit handle compinit (recommended)
zinit ice wait lucid atinit"zicompinit; zicdreplay"
zinit light zdharma-continuum/fast-syntax-highlighting

# zicompinit - zinit's compinit wrapper
# zicdreplay - replay any compdef calls made before compinit
```

### as'completion' Ice

Tells zinit to register as completion:

```zsh
zinit ice as'completion'
zinit snippet https://example.com/_mycommand

# Or with gh-r binary
zinit for \
    from'gh-r' \
    sbin'mycli' \
    atclone'./mycli completion zsh > _mycli' \
    atpull'%atclone' \
    as'completion' \
  @owner/mycli
```

See `references/compinit-debug.md` for debugging and troubleshooting.
