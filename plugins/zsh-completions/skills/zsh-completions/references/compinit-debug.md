# compinit Debugging and Troubleshooting

## Debug Completions

### Check registered completers

```zsh
# What handles 'git'?
print $_comps[git]

# List all registered
print -l ${(k)_comps}
```

### Trace completion

```zsh
# Enable debug output
zstyle ':completion:*' verbose yes

# Or full trace
setopt XTRACE
mycommand <TAB>
unsetopt XTRACE
```

### Test completion function directly

```zsh
# Call completion function
_mycommand

# With compstate
print -r -- $compstate[nmatches]
```

## Common Issues

### "command not found: compdef"

compdef called before compinit:

```zsh
# Fix: ensure compinit runs first, or use zinit's zicdreplay
zinit ice atinit"zicompinit; zicdreplay"
```

### Completions not loading

```zsh
# Check fpath includes your dir
print -l $fpath | grep completions

# Check file permissions
ls -la ~/.config/zsh/completions/

# Ensure #compdef header exists
head -1 ~/.config/zsh/completions/_mycommand
```

### Slow completions

```zsh
# Profile completion
time (print -l ${(k)_comps} > /dev/null)

# Cache expensive lookups
_expensive_complete() {
    local cache=/tmp/.zsh_cache_$$
    if [[ ! -f $cache ]] || [[ -z "$(find $cache -mmin -5)" ]]; then
        expensive_command > $cache
    fi
    _describe 'item' ${(f)"$(<$cache)"}
}
```

### Stale cache

```zsh
# Force full rebuild
rm -f ~/.zcompdump
exec zsh
```

### Permission issues

```zsh
# Completions must not be world-writable
chmod go-w ~/.config/zsh/completions/_mycommand

# Or run with insecure flag (not recommended)
compinit -u
```
