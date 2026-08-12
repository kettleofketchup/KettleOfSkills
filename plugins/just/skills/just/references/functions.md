# Just Built-in Functions

## System Info

```just
arch()        # CPU: "x86_64", "aarch64"
os()          # OS: "linux", "macos", "windows"
os_family()   # "unix" or "windows"
num_cpus()    # Logical CPU count
```

## Environment

```just
env("KEY")              # Get env var (error if missing)
env("KEY", "default")   # Get with fallback
```

## Paths & Executables

```just
require("cmd")          # Find in PATH or error
which("cmd")            # Find in PATH or empty string
```

## Justfile Locations

```just
justfile()              # Path to ROOT justfile
justfile_directory()    # Parent dir of ROOT justfile
source_file()           # Path to CURRENT .just file
source_directory()      # Parent dir of CURRENT .just file
invocation_directory()  # Dir where `just` was run
just_executable()       # Path to just binary
just_pid()              # Process ID
home_directory()        # User home (~)
```

### Critical: source_directory() vs justfile_directory()

In modules/imports, use `source_directory()` for paths relative to that file:

```just
# automation/just/ansible.just
automation_root := source_directory() / ".."

[working-directory(automation_root)]
deploy:
    ansible-playbook ansible/playbooks/deploy.yml
```

| Function | In root justfile | In module file |
|----------|------------------|----------------|
| `justfile_directory()` | Root dir | Root dir (unchanged) |
| `source_directory()` | Root dir | Module file's dir |

**Rule:** In modules/imports, always use `source_directory()` for relative paths.

## String Manipulation

```just
trim(s)                 # Both ends
trim_start(s)           # Leading whitespace
trim_end(s)             # Trailing whitespace
trim_start_match(s, m)  # Remove prefix once
trim_end_match(s, m)    # Remove suffix once
replace(s, from, to)    # Replace all occurrences
replace_regex(s, re, r) # Regex replace
quote(s)                # Shell-safe quoting
encode_uri_component(s) # URL encode
append(suffix, s)       # Append to each word
prepend(prefix, s)      # Prepend to each word
```

## Case Conversion

```just
uppercase(s)            # HELLO
lowercase(s)            # hello
capitalize(s)           # Hello
titlecase(s)            # Hello World
snakecase(s)            # hello_world
shoutysnakecase(s)      # HELLO_WORLD
kebabcase(s)            # hello-world
shoutykebabcase(s)      # HELLO-WORLD
lowercamelcase(s)       # helloWorld
uppercamelcase(s)       # HelloWorld
```

## Path Operations

```just
# May fail
absolute_path(p)        # Resolve to absolute
canonicalize(p)         # Resolve symlinks
extension(p)            # File extension
file_name(p)            # Filename only
file_stem(p)            # Name without extension
parent_directory(p)     # Parent dir
without_extension(p)    # Remove extension

# Always succeed
clean(p)                # Normalize path
join(a, b, ...)         # Join path parts
```

## Filesystem

```just
path_exists(p)          # Check if exists
read(p)                 # Read file contents
```

See `functions-advanced.md` for shell execution, hashing, datetime, and misc functions.
