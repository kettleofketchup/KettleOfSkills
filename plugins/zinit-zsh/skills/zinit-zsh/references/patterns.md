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

## External Tool Integration

### Yazi file manager with plugins

```zsh
# Main binary
zinit ice from"gh-r" as"program" \
    sbin'yazi -> yazi' \
    sbin'ya -> ya'
zinit light sxyazi/yazi

# Plugin repo linked to config
zinit ice \
    atclone"mkdir -p ~/.config/yazi/plugins && ln -sfn \$PWD ~/.config/yazi/plugins/starship.yazi" \
    atpull"%atclone" \
    as"null"
zinit light Rolv-Apneseth/starship.yazi
```

### TPM (tmux plugin manager)

```zsh
zinit ice depth=1 id-as"tpm" lucid \
    atclone"mkdir -p ~/.tmux/plugins && ln -sfn \$PWD ~/.tmux/plugins/tpm" \
    atpull'%atclone'
zinit load tmux-plugins/tpm
```

## Prompt/Theme

### Starship with completions

```zsh
zinit ice as"command" from"gh-r" \
    atclone"./starship init zsh > init.zsh; ./starship completions zsh > _starship" \
    atpull"%atclone" src"init.zsh"
zinit load starship/starship
```

## Local Snippets

```zsh
# Load local zsh files as zinit snippets
[[ -f ~/.config/zsh/aliases.zsh ]] && zinit snippet ~/.config/zsh/aliases.zsh
[[ -f ~/.config/zsh/exports.zsh ]] && zinit snippet ~/.config/zsh/exports.zsh
```

## Syntax Highlighting (load late)

```zsh
zinit ice wait lucid atinit"zicompinit; zicdreplay"
zinit light zdharma-continuum/fast-syntax-highlighting
```
