# Zinit Ice Modifiers Reference

Complete reference for zinit ice modifiers used in this dotfiles repo.

## Source Selection

| Ice | Description | Example |
|-----|-------------|---------|
| `from'gh-r'` | GitHub releases | `from'gh-r'` |
| `from'gitlab'` | GitLab repo | `from'gitlab'` |
| `ver'tag'` | Specific version/tag | `ver'nightly'`, `ver'v1.2.3'` |
| `bpick'pattern'` | Binary asset pattern | `bpick'*linux*amd64*'` |

## Binary Management (sbin)

```zsh
# Basic - binary name matches repo
sbin'tool'

# Rename binary
sbin'downloaded-name -> desired-name'

# Glob pattern for nested binaries
sbin'**/binary-name -> name'

# Multiple binaries
sbin'bin1' sbin'bin2'

# Exclamation - extract then symlink
sbin'!archive-* -> tool'
```

## Loading Control

| Ice | Description | Example |
|-----|-------------|---------|
| `wait` | Turbo mode, load after prompt | `wait` |
| `wait"N"` | Load after N seconds | `wait"2"` |
| `lucid` | Silence "Loaded..." message | `lucid` |
| `light-mode` | Minimal tracking | `light-mode` |
| `nocompile` | Skip .zwc compilation | `nocompile` |

## Hooks

| Ice | When | Use |
|-----|------|-----|
| `atclone"cmd"` | After clone | Generate completions, setup |
| `atpull"cmd"` | After update | Re-run setup |
| `atpull'%atclone'` | Update | Run same as atclone |
| `atinit"cmd"` | Before load | Set vars |
| `atload"cmd"` | After load | Configure plugin |

## Plugin Type

| Ice | Purpose |
|-----|---------|
| `as'program'` | Don't source, just add to PATH |
| `as'null'` | Don't source, don't add to PATH (use with sbin) |
| `as'completion'` | Register as completion |
| `as'snippet'` | Load as snippet not plugin |

## Build from Source

```zsh
# Configure + make
configure'--prefix=$PWD --quiet'
make'install'

# CMake
cmake'.'
make'install'

# Just make
make'PREFIX=$ZPFX install'
```

## Completions

```zsh
# Generate on clone
atclone'./tool completion zsh > _tool'
atpull'%atclone'
as'completion'

# Pick completion file
pick'_completion-file'

# Load completion directly
as'completion' mv'pattern -> _name'
```

## OMZ Shortcuts

| Prefix | Expands to |
|--------|------------|
| `OMZP::name` | oh-my-zsh/plugins/name |
| `OMZL::file` | oh-my-zsh/lib/file |
| `OMZ::path` | oh-my-zsh/path |

## id-as

Override plugin ID (useful for snippets):

```zsh
zinit ice id-as"custom-id"
zinit snippet file.zsh
```

## Linking Patterns

```zsh
# Symlink to config dir
atclone"mkdir -p ~/.config/app && ln -sfn \$PWD ~/.config/app/plugins"

# Use {dir} placeholder
atclone"ln -sfn {dir} ~/.config/app/data"
```
