# Copyparty Volflags Reference

Volflags are per-volume configuration flags. Set via CLI `:c,flagname=value` or config `flags:` section.

Full list: `--help-flags` or https://copyparty.eu/cli/#flags-help-page

## Indexing

```yaml
flags:
  e2d            # enable uploads database
  e2ds           # scan writable folders on startup
  e2dsa          # scan ALL folders (recommended)
  e2ts           # scan for media tags on startup
  d2d            # disable all indexing for this volume
  d2t            # disable media tag parsing (safety for untrusted uploads)
  scan: 60       # rescan every 60 seconds
  re-maxage: 3600  # global: rescan all volumes every hour
  hist: /path    # override .hist location
  dbpath: /path  # override database location
  nohash: \.iso$ # skip hashing matching files
  noidx: \.log$  # skip indexing matching files
```

## Dedup

```yaml
flags:
  dedup          # symlink-based deduplication
  hardlinkonly   # use hardlinks instead of symlinks
  reflink        # use CoW/reflinks (btrfs; Python 3.14+)
  nodupe         # reject duplicate uploads
```

## Upload Rules

```yaml
flags:
  sz: 1k-3m      # allowed filesize range (b, k, m, g suffixes)
  df: 4g         # minimum free disk space
  vmaxb: 1g      # max volume size
  vmaxn: 4k      # max files in volume
  nosub          # no subdirectory uploads
  rotn: 1000,2   # rotate into subfolders (1000 files, 2 levels)
  rotf: %Y/%m/%d # date-based subdirectory structure
  rotf_tz: Europe/Oslo  # timezone for rotf (default UTC)
  lifetime: 300  # self-destruct uploads after 5 min
  maxn: 250,3600 # rate limit: 250 files per hour per IP
  maxb: 1g,300   # rate limit: 1 GiB per 5 min per IP
  rand           # force randomized filenames
  nrand: 9       # random filename length
  gz             # allow gzip compression
  xz             # allow lzma compression
  pk             # force compression on all uploads
```

## Display and Thumbnails

```yaml
flags:
  dthumb         # disable all thumbnails
  dvthumb        # disable video thumbnails only
  dathumb        # disable audio spectrograms only
  dithumb        # disable image thumbnails only
  grid           # default to grid view
  sort: href     # default sort column
  norobots       # tell search engines to go away
  nohtml         # prevent XSS by returning HTML as plaintext
  og             # enable OpenGraph/Discord embeds
  rss            # enable RSS feeds
  opds           # enable OPDS feeds (e-readers)
```

## Filesystem and Access

```yaml
flags:
  fk: 4          # 4-character filekeys
  dk             # enable dirkeys
  dks            # dirkeys work in subfolders too
  dots           # show dotfiles to everyone
  xvol           # don't follow symlinks leaving volume
  xdev           # stay within volume filesystem
  daw            # WebDAV: allow overwrite via PUT
  chmod_f: 644   # file permissions
  chmod_d: 755   # directory permissions
  uid: 1000      # chown user
  gid: 573       # chown group
```

## Custom Tag Parsers

```yaml
flags:
  mte: title,artist  # tags to index and display
  mth: album         # tags to hide but still index
  mtp: .bpm=f,t30,/mtag/audio-bpm.py  # custom tag parser script
  # Flags: f=force, t5=5sec timeout, ay=audio-only, an=non-audio, ad=all
```
