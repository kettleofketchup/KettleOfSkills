# Advanced Completion Patterns

## Current Word Analysis

```zsh
_mycommand() {
    local curword=$words[CURRENT]

    # Special handling if current word contains =
    if [[ $curword == *=* ]]; then
        local key=${curword%%=*}
        local val=${curword#*=}
        # complete value based on key
        case $key in
            --format) compadd json yaml text ;;
            --output) _files ;;
        esac
        return
    fi

    _arguments \
        '--format=[Output format]:format:(json yaml text)' \
        '--output=[Output file]:file:_files'
}
```

## Completing After =

```zsh
# --config=FILE style
'--config=[Config file]:file:_files'

# Multiple values after =
'--features=[Enable features]:feature:_values -s , feature debug trace log'
```

## File Type Filtering

```zsh
'*:python file:_files -g "*.py"'           # Python files
'*:config:_files -g "*.{json,yaml,toml}"'  # Config files
'1:directory:_files -/'                     # Directories only
'*:script:_files -g "*.(sh|bash|zsh)"'     # Shell scripts
```

## Optional Arguments

```zsh
# --format with optional argument
'--format=-[Output format]::format:(json yaml text)'
#        ^^ double colon = optional
```

## Repeatable Options

```zsh
# Can specify -I multiple times
'*-I[Include directory]:directory:_directories'

# Or with long form
'*'{-I,--include}'[Include directory]:directory:_directories'
```

## Dynamic State Routing

```zsh
_complex_tool() {
    local state ret=1

    _arguments -C \
        '--global[Apply globally]' \
        '1:mode:->mode' \
        '*::args:->args' && return

    case $state in
        mode)
            local -a modes=('read:Read data' 'write:Write data' 'exec:Execute')
            _describe 'mode' modes && ret=0
            ;;
        args)
            case $words[1] in
                read)  _files && ret=0 ;;
                write) _files && ret=0 ;;
                exec)  _command && ret=0 ;;
            esac
            ;;
    esac

    return ret
}
```

## Completion with Caching

```zsh
_mycli_cached_complete() {
    local cache="/tmp/.zsh_mycli_cache"
    local max_age=30  # seconds

    if [[ ! -f $cache ]] || \
       [[ $(( $(date +%s) - $(stat -c %Y $cache 2>/dev/null || echo 0) )) -gt $max_age ]]; then
        mycli list --format=name:desc 2>/dev/null > $cache
    fi

    local -a items
    items=(${(f)"$(<$cache)"})
    _describe 'item' items
}
```
