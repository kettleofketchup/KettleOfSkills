# Common Zinit Patterns

Patterns extracted from this dotfiles repo for reference.

## GitHub Release Binaries

### Simple binary

```zsh
zinit as"null" wait lucid from"gh-r" for \
    sbin"fd"      @sharkdp/fd \
    sbin"fzf"     junegunn/fzf
```

### Binary with completion generation

```zsh
zinit for \
    from'gh-r' \
    sbin'gh' \
    atclone'./**/gh completion -s zsh > _gh' atpull'%atclone' as'completion' \
  cli/cli
```

### Nested binary (archive structure)

```zsh
zi for \
    from'gh-r' \
    sbin'**/nvim -> nvim' \
    ver'nightly' \
  neovim/neovim
```

### Prefer tarball over raw binary (cross-platform)

Some repos publish both raw binaries and tarballs. Zinit may grab the raw binary
and fail to extract it. Use `bpick'*.tar.gz'` to force tarballs — zinit still
auto-detects OS/arch from the filtered list:

```zsh
zi for \
    from'gh-r' \
    bpick'*.tar.gz' \
    sbin'mise/bin/mise -> mise' \
    atclone'mise/bin/mise completion zsh > _mise' atpull'%atclone' as'completion' \
    atload'eval "$(mise activate zsh)"' \
  @jdx/mise
```

### Multiple binaries from one release

```zsh
zi for \
    from'gh-r' \
    sbin'**/cmake -> cmake' \
    sbin'**/ctest -> ctest' \
    sbin'**/cpack -> cpack' \
  @Kitware/CMake
```

## Build from Source

### Configure + make

```zsh
zinit for \
    as'null' \
    configure'--prefix=$PWD' \
    make'PREFIX=$ZPFX install' \
    sbin \
  @eradman/entr
```

### CMake project

```zsh
zinit for \
    as'null' \
    cmake'.' \
    make'install' \
    sbin \
  @posva/catimg
```

### Stow (special build)

```zsh
zinit build for @aspiers/stow
```

## Oh-My-Zsh Plugins

### Basic plugins

```zsh
zinit wait lucid for \
    OMZP::git \
    OMZP::fzf \
    OMZP::npm
```

### Completions from OMZ

```zsh
zinit wait lucid for \
  as"completion" \
    OMZP::docker/completions/_docker \
    OMZP::docker-compose/_docker-compose
```

### OMZ libraries

```zsh
zinit wait lucid for \
    OMZ::lib/clipboard.zsh
```

## Turbo Loading Order

```zsh
# Load immediately for interactive features
zinit light Aloxaf/fzf-tab

# wait"1" - secondary plugins
zinit wait"1" lucid for \
    OMZP::git \
    zsh-users/zsh-completions

# wait"2" - cosmetic/optional
zinit wait"2" lucid for \
    zsh-users/zsh-autosuggestions \
    hlissner/zsh-autopair
```

See `references/patterns-advanced.md` for external tool integration, prompt/theme, and syntax highlighting patterns.
