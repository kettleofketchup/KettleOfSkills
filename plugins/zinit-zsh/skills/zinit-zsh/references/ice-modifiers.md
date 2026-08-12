# Zinit Ice Modifiers Reference

Complete reference for zinit ice modifiers used in this dotfiles repo.

## Source Selection

| Ice | Description | Example |
|-----|-------------|---------|
| `from'gh-r'` | GitHub releases | `from'gh-r'` |
| `from'gitlab'` | GitLab repo | `from'gitlab'` |
| `ver'tag'` | Specific version/tag | `ver'nightly'`, `ver'v1.2.3'` |
| `bpick'pattern'` | Binary asset pattern (see below) | `bpick'*.tar.gz'` |

### bpick and OS/Arch Auto-Detection

Zinit's `from'gh-r'` automatically detects OS and architecture from release asset names. `bpick` does **not** disable this — it filters first, then auto-detection runs on the filtered results:

1. `bpick` glob narrows the asset list (e.g., only `.tar.gz` files)
2. OS/arch detection filters those results (matches `linux`/`darwin`, `x64`/`arm64`, etc.)

This means `bpick'*.tar.gz'` is cross-platform safe — it excludes raw binaries or other formats while letting zinit pick the correct OS/arch tarball.

**When to use bpick:**
- Repo publishes both raw binaries and tarballs, and zinit grabs the wrong one (raw binary it can't extract)
- Repo has multiple variants (e.g., `musl` vs `gnu`) — use `bpick'*musl*'` to prefer one
- Multiple sub-projects in one repo — use `bpick'kubectx_*'` to pick the right asset

**Do NOT hardcode OS/arch in bpick** (e.g., `bpick'*linux*amd64*'`) — this breaks cross-platform. Use format/variant filters instead and let auto-detection handle the rest.

**Special case:** `bpick'src'` downloads the auto-generated source tarball and bypasses all detection.

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
