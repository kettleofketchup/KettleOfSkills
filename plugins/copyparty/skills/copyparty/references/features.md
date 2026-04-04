# Copyparty Features Reference

## File Indexing and Search

### Enabling Indexing

```yaml
[global]
  e2d            # enable upload database
  e2ds           # + scan writable folders on startup
  e2dsa          # + scan ALL folders on startup (recommended)
  e2t            # enable media tag indexing on upload
  e2ts           # + scan for tags on startup
  e2tsr          # + full reindex of all tags
  e2v            # verify file integrity (compare hashes)
  e2vu           # on mismatch: update db with new hash
  e2vp           # on mismatch: panic and quit
```

### Search Syntax

Space-separated terms are AND'ed. Prefix with `-` to negate:
- Path: `shibayan -bossa` -- folders contain "shibayan" but not "bossa"
- Name: `demetori styx`

Raw query field supports complex queries:
```
( tags like *nhato* or tags like *taishi* ) and ( not tags like *nhato* or not tags like *taishi* )
```

Search by wark (file checksum): `w = kFpDiztbZc8Z1Lzi`

### File Search (Drag-Drop)

Drag files into browser and drop on "Search" zone. Files are hashed client-side and checked against server.

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
```

### Database Location

```yaml
[global]
  hist: ~/.cache/copyparty    # global db/thumbs location
  dbpath: /fast-ssd/cpp-db/   # override just the database location

[/pics]
  /mnt/nas/pics
  flags:
    hist: -                    # restore default (.hist in volume)
    hist: /mnt/ssd/cache/pics/ # absolute path
    landmark: me.jpg           # file must exist for db to work
    landmark: info/a.txt^=ok   # file must start with "ok"
```

## File Deduplication

```yaml
[global]
  dedup           # symlink-based (default)
  hardlink        # prefer hardlinks, fallback to symlinks
  hardlink-only   # hardlinks only, no symlinks
  reflink         # CoW/reflinks (btrfs, maybe xfs; Linux 5.3+, Python 3.14+)
  safe-dedup: 50  # verify file contents (1=size-only, 50=full verify)
  xlink           # cross-volume deduplication (probably buggy)
  no-dupe         # reject duplicate uploads
  no-clone        # disable dupe detection entirely (for expensive storage like S3)
```

**Warning:** Enable `-e2dsa` with dedup. Without indexing, rename/delete of deduped files is unsafe.

Advantages of each method:
- **Symlinks (default):** individual timestamps, obvious to other software
- **Hardlinks:** compatible with other file managers, move/rename safe
- **Reflinks:** entirely safe, either copy can be edited/deleted independently

## Upload Features

### Uploaders

- **up2k** (drag-drop): resumable, chunked, checksummed, parallel, no size limit
- **bup** (basic): works in IE6, simple multipart, theoretically faster for huge files on slow connections
- **PUT/POST**: curl-friendly, programmatic

### Upload Rules (Volflags)

```yaml
flags:
  sz: 1k-3m        # filesize range (b, k, m, g suffixes)
  df: 4g            # minimum free disk space
  vmaxb: 1g         # max total volume size
  vmaxn: 4k         # max files in volume
  nosub             # no subdirectory uploads
  rotn: 1000,2      # rotate uploads into subfolders (1000 files, 2 levels)
  rotf: %Y/%m/%d    # date-based subfolder structure
  rotf_tz: Europe/Oslo  # timezone for rotf (default UTC)
  lifetime: 300     # self-destruct after 5 minutes
  maxn: 250,3600    # rate limit: 250 files per hour per IP
  maxb: 1g,300      # rate limit: 1 GiB per 5 min per IP
  rand              # force randomized filenames
  nrand: 9          # random filename length
  magic             # detect filetype for nameless uploads
```

### Unpost (Upload Undo)

Delete accidental uploads within `--unpost` seconds (default 12 hours). Requires `-e2d`.

```yaml
[global]
  e2d
  unpost: 43200    # 12 hours (default)
```

### Self-Destruct

Enable per-volume with `lifetime` volflag. Clients can set shorter lifetimes via up2k UI or `life` upload modifier.

### Race the Beam

Download files while they're still uploading. Requires up2k uploader.

### Compress Uploads

```yaml
flags:
  gz             # allow gzip compression
  xz             # allow lzma compression
  pk             # force compression on all uploads
  pk: xz,0       # force xz level 0
  pk: gz,9       # force gzip level 9
```

## Thumbnails

### Configuration

```yaml
[global]
  no-thumb          # disable ALL thumbnails
  no-vthumb         # disable video thumbnails only
  no-athumb         # disable audio spectrograms
  th-size: 320x256  # thumbnail resolution
  th-mt: 4          # CPU cores for thumbnail generation
  th-convt: 60      # conversion timeout (seconds)
  th-crop: y        # crop to 4:3 (y/n/fy/fn)
  th-x3: n          # 3x resolution (y/n/fy/fn)
  th-dec: vips,pil,raw,ff  # decoder preference order
  th-covers: folder.png,folder.jpg,cover.png,cover.jpg
  th-maxage: 604800 # max cache age (1 week default)
  th-clean: 43200   # cleanup interval (12 hours default)
```

Per-volume:
```yaml
flags:
  dthumb          # disable all
  dvthumb         # disable video only
  dathumb         # disable audio only
  dithumb         # disable image only
  ext-th: exe=/ico/exe.png  # custom thumbnail for file type
```

### Thumbnail Performance

- pyvips is 3x faster than Pillow
- Pillow is 3x faster than FFmpeg
- Thumbnails generated on-demand by default, then cached
- Pre-generate with `th-pregen` or `?tar&j`/`?tar&w`

## Media Player

Plays almost every audio format (with FFmpeg for on-demand transcoding).

Natively playable: `aac|flac|m4a|mp3|ogg|opus|wav`

### Transcoding Options

```yaml
[global]
  q-opus: 128      # opus bitrate (default)
  q-mp3: q2        # mp3 quality (q0=best, q9=smallest, or 192k for CBR)
  allow-wav         # allow lossless wav transcoding
  allow-flac        # allow lossless flac transcoding
  no-caf            # disable caf-opus (iOS v12-v17)
  no-owa            # disable webm-opus (iOS v18+)
  no-acode          # disable all audio transcoding
  ac-maxage: 86400  # delete cached transcodes after 24h
```

### Audio Features

- OS media controls integration (lockscreen playback)
- Seekbar waveform display
- Near-gapless playback (enable EQ for best results)
- Audio equalizer + dynamic range compressor
- Video-as-audio playback (saves bandwidth)
- M3U8 playlist support

## Markdown Viewer/Editor

- Two editors available (basic + fancy/EasyMDE)
- Inline thumbnails: add `<!-- th -->` then `!th[l](image.jpg)` (l=left, r=right)
- Markdown variables: `{{self.ip}}`, `{{srv.htime}}` for dynamic content
- Document history stored in `.hist` subdirectory

## RSS and OPDS Feeds

```yaml
[global]
  rss              # enable RSS
  opds             # enable OPDS (e-readers)
  rss-nf: 250      # default results count
  rss-sort: m      # sort: m=mtime, u=upload-time, n=filename, s=size
```

RSS URL params: `?rss&recursive&fext=mp3,opus&nf=30&sort=m&title=My%20Feed`

## Event Hooks

Trigger programs on uploads, renames, deletes. See `--help-hooks`.

```yaml
[global]
  # After upload: run script
  xau: /usr/bin/notify-send,--

  # Before upload: validate
  xbu: /path/to/validate.py

  # After rename
  xar: /path/to/on-rename.sh

  # After delete
  xad: /path/to/on-delete.sh

  # ZeroMQ hooks
  xau: zmq:pub:tcp://*:5556
  xau: t3,j,zmq:req:tcp://localhost:5555
```

### Hook Effects (with `c1` flag)

- `reloc`: redirect uploads to different location
- `idx`: inform copyparty about new files to index
- `del`: delete files by vpath

### Hook Import (`I` flag)

Run hooks inside copyparty process (~140x faster, but can crash things).

## File Parser Plugins (mtp)

Custom metadata extraction:

```yaml
flags:
  mtp: .bpm=~/bin/audio-bpm.py              # assign .bpm tag
  mtp: key=f,t5,~/bin/audio-key.py          # force/overwrite, 5s timeout
  mtp: ext=an,~/bin/file-ext.py             # non-audio files only
  mtp: arch,built=an,eexe,edll,~/bin/exe.py # only .exe/.dll
```

Flags: `f`=force, `t5`=5sec timeout, `ay`=audio-only(default), `an`=non-audio, `ad`=all, `p1`=priority, `c0`=no-capture

## Shares (Temporary Links)

```yaml
[global]
  shr: /shares        # enable at this URL prefix
  shr-db: /path/to/shares.db
  shr-adm: admin1,admin2  # users who can manage all shares
  shr-rt: 1440        # expired shares visible for 24h (default)
```

Share options: password-protection, expiration, upload permission.

Volflag `shr-who`: `no`=nobody, `a`=admins, `auth`=logged-in users.

## File Manager

- Cut/paste across browser tabs (ctrl-x/c/v)
- Batch rename with regex, tags, counters (F2)
- Delete (ctrl-K)
- Download selection (Y)

## Zip Downloads

| Format | URL Param | Notes |
|--------|-----------|-------|
| tar | `?tar` | GNU tar, works with `curl \| tar -xv` |
| pax | `?tar=pax` | PAX format, futureproof |
| tgz | `?tar=gz` | Gzip compressed |
| txz | `?tar=xz` | XZ compressed |
| zip | `?zip` | Universal |
| zip_dos | `?zip=dos` | CP437, fixes Win7 filenames |
| zip_crc | `?zip=crc` | For ancient software |

## Performance Tuning

```yaml
[global]
  q                   # disable stdout logging
  lo: /var/log/cpp/%Y-%m-%d.txt  # log to file instead
  hist: /fast-ssd/    # put db/thumbs on SSD
  dedup               # avoid writes for duplicate uploads
  safe-dedup: 1       # skip content verification (faster)
  no-dirsz            # faster directory listings (~30%)
  no-hash: .          # skip content hashing for network disks
  j: 0                # multiprocessing (usually NOT recommended)
  iobuf: 4194304      # larger I/O buffer for network storage
  s-rd-sz: 4194304    # larger read size
  s-wr-sz: 4194304    # larger write size
  casechk: n          # faster on Windows/macOS (case-insensitive FS)
```

Client-side: Chrome is faster than Firefox for hashing. `[wasm]` in settings for NVMe uploads.

## Logging

```yaml
[global]
  q                              # quiet (disable stdout)
  lo: /var/log/cpp/%Y-%m-%d.txt  # logfile with daily rotation
  flo: 2                         # no colors in logfile
  no-ansi                        # no colors anywhere
  log-date: %Y-%m-%d             # show dates on stdout
  log-utc                        # use UTC timestamps
```

## Version Checker

```yaml
[global]
  vc-url: https://api.copyparty.eu/advisories
  vc-age: 3       # check every 3 hours
  vc-exit          # emergency exit if vulnerable
```

## OpenGraph / Discord Embeds

```yaml
[global]
  og                    # enable OpenGraph (disables hotlinking)
  og-ua: '(Discord|Twitter|Slack)bot'  # selective by user-agent
```

Note: `?raw` appended to URL bypasses OpenGraph.

## GDPR Compliance

```yaml
[global]
  forget-ip: 43200   # forget uploader IPs after 30 days
  # Also: configure log rotation with -lo
```

## Themes

6 built-in themes (0-5, each with dark/light variant). Change default with `--theme 2`.

Custom CSS via `--css-browser`. Add themes by increasing `--themes` count.

## Special Files

- `.prologue.html` / `.epilogue.html` - rendered before/after directory listings
- `PREADME.md` / `preadme.md` - shown above directory listings
- `README.md` / `readme.md` - shown after directory listings
- `descript.ion` / `DESCRIPT.ION` - file descriptions in listings
- `.hidden` - cosmetically hide files (with `dothidden` volflag)
