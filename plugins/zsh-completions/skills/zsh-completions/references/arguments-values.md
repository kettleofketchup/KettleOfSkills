# _values Function

For comma-separated or space-separated value lists.

## Basic Syntax

```zsh
_values [-s sep] 'description' spec...
```

## Examples

```zsh
# Comma-separated (default)
_values 'features' \
    'debug[Enable debugging]' \
    'verbose[Verbose output]' \
    'color[Colored output]'

# With custom separator
_values -s ' ' 'options' opt1 opt2 opt3
```

## In _arguments

```zsh
# Multiple values after =
'--features=[Enable features]:feature:_values -s , feature debug trace log'
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
