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
justfile()              # Path to ROOT justfile (entry point)
justfile_directory()    # Parent dir of ROOT justfile
source_file()           # Path to CURRENT .just file being evaluated
source_directory()      # Parent dir of CURRENT .just file
invocation_directory()  # Dir where `just` command was run
just_executable()       # Path to just binary
just_pid()              # Process ID
home_directory()        # User home (~)
```

### Critical: source_directory() vs justfile_directory()

When writing **imported or module files**, use `source_directory()` for paths relative to that file:

```
project/
├── justfile              # Root - imports automation/just/ansible.just
└── automation/
    ├── just/
    │   └── ansible.just  # Module file
    └── ansible/
        └── playbooks/
```

```just
# automation/just/ansible.just

# WRONG - points to project/, not automation/
wrong_root := justfile_directory()

# CORRECT - points to automation/just/, can navigate to automation/
automation_root := source_directory() / ".."

[working-directory(automation_root)]
deploy:
    ansible-playbook ansible/playbooks/deploy.yml
```

| Function | In root justfile | In imported/module file |
|----------|------------------|-------------------------|
| `justfile_directory()` | Root dir | Root dir (unchanged) |
| `source_directory()` | Root dir | Module file's dir |

**Rule:** In modules/imports, always use `source_directory()` for relative paths.

## String Manipulation

```just
# Trim
trim(s)                 # Both ends
trim_start(s)           # Leading whitespace
trim_end(s)             # Trailing whitespace
trim_start_match(s, m)  # Remove prefix once
trim_end_match(s, m)    # Remove suffix once

# Transform
replace(s, from, to)    # Replace all occurrences
replace_regex(s, re, r) # Regex replace
quote(s)                # Shell-safe quoting
encode_uri_component(s) # URL encode

# Whitespace-separated operations
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

## Shell Execution

```just
shell("command", args...) # Run command, return stdout
```

## Random & Hashing

```just
uuid()                  # Random UUID v4
choose(n, alphabet)     # Random string from chars
sha256(s)               # SHA-256 hash
sha256_file(p)          # SHA-256 of file
blake3(s)               # BLAKE3 hash
blake3_file(p)          # BLAKE3 of file
```

## Datetime

```just
datetime(format)        # Local time (strftime)
datetime_utc(format)    # UTC time
```

## Misc

```just
error(msg)              # Abort with message
is_dependency()         # "true" if running as dep
semver_matches(v, req)  # Check version match
```

## Usage Example

```just
version := `git describe --tags`
build_dir := join(justfile_directory(), "build")
timestamp := datetime("%Y%m%d-%H%M%S")

build:
    echo "Building {{version}} at {{timestamp}}"
    mkdir -p {{build_dir}}
```
