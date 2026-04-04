# Zinit Troubleshooting

Common issues and debugging techniques.

## Load Order Issues

### Completions not working

1. Ensure `compinit` runs after plugins load:
```zsh
# At end of .zshrc
autoload -U compinit; compinit
```

2. For turbo-loaded completions, use atinit:
```zsh
zinit ice wait lucid atinit"zicompinit; zicdreplay"
zinit light zdharma-continuum/fast-syntax-highlighting
```

3. Check completion is registered:
```zsh
echo $_comps[command-name]
```

### Plugin loads too early

Increase wait time:
```zsh
wait"0"  # After prompt
wait"1"  # 1 second after
wait"2"  # 2 seconds after
```

### Plugin loads but doesn't work

Check if sourcing is needed:
```zsh
# as"null" = don't source (for binaries)
# as"program" = add to PATH, don't source
# Remove these if plugin needs sourcing
```

## Binary Issues

### Binary not found after install

1. Check $ZPFX/bin in PATH:
```zsh
echo $ZPFX  # Usually ~/.local/share/zinit/polaris
ls $ZPFX/bin/
```

2. Verify sbin pattern matches:
```zsh
# Check what was downloaded
ls ~/.local/share/zinit/plugins/owner---repo/
```

3. Use glob for nested:
```zsh
sbin'**/binary -> name'
```

### Wrong binary version

Force specific release:
```zsh
ver'v1.2.3'          # Exact tag
ver'nightly'         # Nightly
bpick'*linux*amd64*' # Specific asset
```

## Debug Commands

```zsh
# List loaded plugins
zinit list

# Show plugin info
zinit report plugin-name

# Recompile plugins
zinit compile --all

# Update all
zinit update --all

# Clear plugin
zinit delete plugin-name

# Self-update zinit
zinit self-update

# Check times
zinit times
```

## Completion Generation

### atclone not running

```zsh
# Force re-clone
zinit delete owner/repo
zinit load owner/repo
```

### Completion file in wrong place

Check completion output location:
```zsh
# Should output to plugin dir
atclone'./tool completion zsh > _tool'

# Or to fpath
atclone'./tool completion zsh > $ZPFX/share/zsh/site-functions/_tool'
```

## Path Escaping

### $PWD in atclone

Use backslash to escape:
```zsh
atclone"ln -sfn \$PWD ~/.config/app"
```

### {dir} placeholder

Zinit provides {dir} for plugin directory:
```zsh
atclone"ln -sfn {dir} ~/.config/app/plugins"
```

## Stow Considerations

This repo uses GNU Stow. After modifying zsh config:

```bash
# In dotfiles repo root
stow .
# Or re-stow
stow -R .
```

Files in repo symlink to $HOME, so edits in either location work.

## Common Mistakes

| Issue | Fix |
|-------|-----|
| `sbin` without binary name | Add explicit: `sbin'binary'` |
| Missing `as'null'` for binaries | Add if plugin shouldn't be sourced |
| `atpull` without `%atclone` | Use `atpull'%atclone'` to rerun |
| Completion not found | Check file naming: `_command` |
| Quote type mismatch | Use consistent `'` or `"` |
