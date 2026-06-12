# Copyparty Features: Indexing, Search, and Dedup

## Enabling Indexing

```yaml
[global]
  e2d            # enable upload database
  e2ds           # + scan writable folders on startup
  e2dsa          # + scan ALL folders (recommended)
  e2t            # enable media tag indexing on upload
  e2ts           # + scan for tags on startup
  e2tsr          # + full reindex of all tags
  e2v            # verify file integrity (compare hashes)
  e2vu           # on mismatch: update db with new hash
  e2vp           # on mismatch: panic and quit
```

## Search Syntax

Space-separated terms are AND'ed. Prefix with `-` to negate:
- Path: `shibayan -bossa` -- folders contain "shibayan" but not "bossa"

Raw query supports complex expressions:
```
( tags like *nhato* or tags like *taishi* ) and ( not tags like *nhato* or not tags like *taishi* )
```

Search by wark (file checksum): `w = kFpDiztbZc8Z1Lzi`

Drag files into browser and drop on "Search" zone — hashed client-side, checked against server.

### Exclude Patterns

```yaml
[global]
  no-hash: \.iso$     # skip hashing, still index by name/size/date
  no-idx: \.log$      # skip indexing entirely
  srch-excl: password  # exclude from search results

[/games]
  /mnt/nas/games
  flags:
    noidx: \.iso$
    nohash: \.bak$
    srch_excl: password|logs/[0-9]
```

### Periodic Rescan

```yaml
[global]
  re-maxage: 3600     # rescan all volumes every hour

[/pics]
  /mnt/nas/pics
  flags:
    scan: 900          # rescan this volume every 15 min
    landmark: me.jpg   # file must exist for db to work
```

### Database Location

```yaml
[global]
  hist: ~/.cache/copyparty    # global db/thumbs location
  dbpath: /fast-ssd/cpp-db/   # override just the database location
```

## File Deduplication

```yaml
[global]
  dedup           # symlink-based (default)
  hardlink        # prefer hardlinks, fallback to symlinks
  hardlink-only   # hardlinks only, no symlinks
  reflink         # CoW/reflinks (btrfs, maybe xfs; Linux 5.3+, Python 3.14+)
  safe-dedup: 50  # verify file contents (1=size-only, 50=full verify)
  xlink           # cross-volume deduplication (possibly buggy)
  no-dupe         # reject duplicate uploads
  no-clone        # disable dupe detection (for expensive storage like S3)
```

**Warning:** Enable `-e2dsa` with dedup. Without indexing, rename/delete of deduped files is unsafe.

- **Symlinks (default):** individual timestamps, obvious to other software
- **Hardlinks:** compatible with other file managers, move/rename safe
- **Reflinks:** entirely safe, either copy can be edited/deleted independently

## Zip Downloads

| Format | URL Param | Notes |
|--------|-----------|-------|
| tar | `?tar` | GNU tar, works with `curl \| tar -xv` |
| pax | `?tar=pax` | PAX format, futureproof |
| tgz | `?tar=gz` | Gzip compressed |
| txz | `?tar=xz` | XZ compressed |
| zip | `?zip` | Universal |
| zip_dos | `?zip=dos` | CP437, fixes Win7 filenames |

## Performance Tuning

```yaml
[global]
  q                   # disable stdout logging
  lo: /var/log/cpp/%Y-%m-%d.txt  # log to file
  hist: /fast-ssd/    # put db/thumbs on SSD
  dedup               # avoid writes for duplicate uploads
  no-dirsz            # faster directory listings (~30%)
  no-hash: .          # skip content hashing for network disks
  j: 0                # multiprocessing (usually NOT recommended)
  iobuf: 4194304      # larger I/O buffer for network storage
  casechk: n          # faster on Windows/macOS (case-insensitive FS)
```

## Special Files

- `.prologue.html` / `.epilogue.html` - rendered before/after directory listings
- `PREADME.md` / `preadme.md` - shown above directory listings
- `README.md` / `readme.md` - shown after directory listings
- `descript.ion` / `DESCRIPT.ION` - file descriptions in listings
- `.hidden` - cosmetically hide files (with `dothidden` volflag)
