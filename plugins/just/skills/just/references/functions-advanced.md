# Just Advanced Functions

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

See `functions.md` for system, path, string, and environment functions.
