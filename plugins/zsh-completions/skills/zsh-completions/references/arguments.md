# _arguments Reference

The primary function for option and argument completion.

## Basic Syntax

```zsh
_arguments [options] specs...
```

## Option Specs

Format: `optspec[description]:message:action`

### Simple flags

```zsh
'-v[Verbose output]'                    # -v with description
'--help[Show help message]'             # long option
'-f[Force]' '--force[Force]'            # both forms
'(-v --verbose)'{-v,--verbose}'[Verbose]'  # mutually exclusive group
```

### Flags with arguments

```zsh
'-o[Output file]:filename:_files'       # -o FILE
'--config=[Config path]:file:_files'    # --config=FILE (= means attached)
'-n+[Count]:number:'                    # + means argument directly follows
'*-I[Include dir]:directory:_files -/'  # repeatable (* prefix)
```

### Argument actions

| Action | Purpose |
|--------|---------|
| `_files` | File completion |
| `_files -/` | Directories only |
| `_directories` | Same as _files -/ |
| `_users` | System users |
| `_hosts` | Hostnames |
| `_urls` | URL completion |
| `(val1 val2)` | Static list |
| `->state` | Set $state for case handling |
| `_default` | Default completion |

## Positional Arguments

Format: `n:message:action` or `*:message:action`

```zsh
'1:command:(start stop restart)'        # First positional
'2:target:_hosts'                       # Second positional
'*:files:_files'                        # All remaining
'*::files:_files'                       # Remaining (ignore options after)
```

## Options Flags

```zsh
_arguments -s    # Allow single-letter option stacking (-abc = -a -b -c)
_arguments -S    # Respect -- to stop option parsing
_arguments -C    # Enable state-based completion (for subcommands)
_arguments -A    # Complete all options even after first positional
```

## State-Based Completion

For complex commands with subcommands:

```zsh
_arguments -C \
    '-h[Help]' \
    '1:command:->cmd' \
    '*::args:->args' && return

case $state in
    cmd)
        local commands=(
            'add:Add new item'
            'remove:Remove item'
            'list:List all items'
        )
        _describe 'command' commands
        ;;
    args)
        case $words[1] in
            add) _mycommand_add ;;
            remove) _mycommand_remove ;;
            list) _mycommand_list ;;
        esac
        ;;
esac
```

## _values Function

For comma-separated or space-separated value lists:

```zsh
# Comma-separated (default)
_values 'features' \
    'debug[Enable debugging]' \
    'verbose[Verbose output]' \
    'color[Colored output]'

# With custom separator
_values -s ' ' 'options' opt1 opt2 opt3
```

## Mutually Exclusive Options

```zsh
# Group exclusion
'(-a -b)'-a'[Option A]'
'(-a -b)'-b'[Option B]'

# With itself (non-repeatable)
'(-f)'-f'[Force (once only)]'
```

## Real Example: kubectl-style

```zsh
_kubectl() {
    local -a commands
    commands=(
        'get:Display resources'
        'create:Create resource'
        'delete:Delete resources'
        'apply:Apply configuration'
    )

    _arguments -C \
        '(-n --namespace)'{-n,--namespace}'[Namespace]:namespace:_kubectl_namespaces' \
        '--context[Cluster context]:context:_kubectl_contexts' \
        '-o[Output format]:format:(json yaml wide name)' \
        '1:command:->cmd' \
        '*::args:->args'

    case $state in
        cmd) _describe 'command' commands ;;
        args)
            case $words[1] in
                get) _kubectl_get ;;
                # ...
            esac
            ;;
    esac
}
```
