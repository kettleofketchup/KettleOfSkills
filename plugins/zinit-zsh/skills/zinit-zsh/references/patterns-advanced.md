# Zinit Advanced Patterns

Advanced integration patterns (external tools, prompts, local snippets).

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
