# Completion Patterns

Common patterns for complex completion scenarios.

## Subcommand Trees

### Two-level (command + subcommand)

```zsh
#compdef mycli

_mycli() {
    local -a commands
    commands=(
        'init:Initialize new project'
        'build:Build the project'
        'deploy:Deploy to production'
        'config:Manage configuration'
    )

    _arguments -C \
        '(-h --help)'{-h,--help}'[Show help]' \
        '(-v --verbose)'{-v,--verbose}'[Verbose output]' \
        '1:command:->cmd' \
        '*::args:->args'

    case $state in
        cmd)
            _describe 'command' commands
            ;;
        args)
            case $words[1] in
                init) _mycli_init ;;
                build) _mycli_build ;;
                deploy) _mycli_deploy ;;
                config) _mycli_config ;;
            esac
            ;;
    esac
}

_mycli_init() {
    _arguments \
        '--template[Project template]:template:(basic advanced)' \
        '1:name:_default'
}

_mycli_build() {
    _arguments \
        '--target[Build target]:target:(dev prod)' \
        '--clean[Clean before build]'
}

# etc.
```

### Three-level (kubectl/docker style)

```zsh
_mycli_config() {
    local -a subcommands
    subcommands=(
        'get:Get config value'
        'set:Set config value'
        'list:List all config'
    )

    _arguments -C \
        '1:subcommand:->subcmd' \
        '*::args:->subargs'

    case $state in
        subcmd) _describe 'config command' subcommands ;;
        subargs)
            case $words[1] in
                get) _mycli_config_get ;;
                set) _mycli_config_set ;;
                list) : ;;  # no args
            esac
            ;;
    esac
}
```

## _alternative for Multiple Types

```zsh
_mycommand() {
    _alternative \
        'commands:command:_mycommand_commands' \
        'files:file:_files -g "*.conf"' \
        'recent:recent item:_mycommand_recent'
}

_mycommand_commands() {
    local -a commands=(start stop restart status)
    _describe 'command' commands
}

_mycommand_recent() {
    local -a recent
    recent=(${(f)"$(mycommand history 2>/dev/null)"})
    _describe 'recent' recent
}
```

## Context-Aware Completions

```zsh
_git_checkout() {
    # After -b, complete nothing (new branch name)
    # Otherwise, complete branches and files

    if (( CURRENT > 2 )) && [[ $words[2] == -b ]]; then
        _message 'new branch name'
        return
    fi

    _alternative \
        'branches:branch:_git_branches' \
        'files:file:_files'
}
```

## Repeatable Options

```zsh
# Can specify -I multiple times
'*-I[Include directory]:directory:_directories'

# Or with long form
'*'{-I,--include}'[Include directory]:directory:_directories'
```

## Optional Arguments

```zsh
# --format with optional argument
'--format=-[Output format]::format:(json yaml text)'
#        ^^ double colon = optional
```

## Mutually Exclusive Groups

```zsh
# Only one of -a, -b, or -c
'(-a -b -c)'-a'[Option A]'
'(-a -b -c)'-b'[Option B]'
'(-a -b -c)'-c'[Option C]'

# -q silences -v
'(-q --quiet -v --verbose)'{-q,--quiet}'[Quiet mode]'
'(-q --quiet -v --verbose)'{-v,--verbose}'[Verbose mode]'
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

## Current Word Analysis

```zsh
_mycommand() {
    local curword=$words[CURRENT]

    # Special handling if current word contains =
    if [[ $curword == *=* ]]; then
        local key=${curword%%=*}
        local val=${curword#*=}
        # complete value based on key
    fi
}
```

## Error Handling

```zsh
_safe_complete() {
    local -a items
    items=(${(f)"$(mycommand list 2>/dev/null)"}) || { _message 'unavailable'; return 1 }
    (( ${#items} )) || { _message 'no items'; return 1 }
    _describe 'item' items
}
```
