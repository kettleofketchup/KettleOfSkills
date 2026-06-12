# Copyparty Upload and Media Features

## Upload Methods

- **up2k** (drag-drop): resumable, chunked, checksummed, parallel, no size limit
- **bup** (basic): works in IE6, simple multipart
- **PUT/POST**: curl-friendly, programmatic

## Upload Volflags

```yaml
flags:
  sz: 1k-3m        # filesize range (b, k, m, g suffixes)
  df: 4g            # minimum free disk space
  vmaxb: 1g         # max total volume size
  nosub             # no subdirectory uploads
  rotn: 1000,2      # rotate uploads into subfolders
  rotf: %Y/%m/%d    # date-based subfolder
  lifetime: 300     # self-destruct after 5 minutes
  maxn: 250,3600    # rate limit: 250 files per hour per IP
  maxb: 1g,300      # rate limit: 1 GiB per 5 min per IP
  rand              # force randomized filenames
  gz                # allow gzip compression
  pk                # force compression on all uploads
```

## Upload Features

**Unpost (Upload Undo):** Delete accidental uploads within `--unpost` seconds (default 12 hours). Requires `-e2d`.

**Race the Beam:** Download files while they're still uploading. Requires up2k uploader.

**Self-Destruct:** Enable per-volume with `lifetime` volflag.

## Thumbnails

```yaml
[global]
  no-thumb          # disable ALL thumbnails
  no-vthumb         # disable video thumbnails only
  no-athumb         # disable audio spectrograms
  th-size: 320x256  # thumbnail resolution
  th-mt: 4          # CPU cores for thumbnail generation
  th-crop: y        # crop to 4:3
  th-dec: vips,pil,raw,ff  # decoder preference order
  th-covers: folder.png,cover.png,cover.jpg
```

Per-volume:
```yaml
flags:
  dthumb          # disable all
  dvthumb         # disable video only
  dathumb         # disable audio only
  ext-th: exe=/ico/exe.png  # custom thumbnail for file type
```

- pyvips is 3x faster than Pillow; Pillow is 3x faster than FFmpeg
- Pre-generate thumbnails with `th-pregen` or `?tar&j`/`?tar&w`

## Media Player

Natively playable: `aac|flac|m4a|mp3|ogg|opus|wav`

```yaml
[global]
  q-opus: 128      # opus bitrate (default)
  q-mp3: q2        # mp3 quality (q0=best, q9=smallest, or 192k CBR)
  no-acode          # disable all audio transcoding
  ac-maxage: 86400  # delete cached transcodes after 24h
```

Features: OS media controls, seekbar waveform, near-gapless playback, EQ + compressor, M3U8 playlists.

## Event Hooks

```yaml
[global]
  xau: /usr/bin/notify-send,--    # after upload
  xbu: /path/to/validate.py       # before upload
  xar: /path/to/on-rename.sh      # after rename
  xad: /path/to/on-delete.sh      # after delete
  xau: zmq:pub:tcp://*:5556       # ZeroMQ hook
  xau: t3,j,zmq:req:tcp://localhost:5555
```

Hook effects (with `c1` flag): `reloc` (redirect upload), `idx` (inform about new files), `del` (delete by vpath).

Run hooks inside copyparty process with `I` flag (~140x faster, but can crash).

## File Parser Plugins (mtp)

```yaml
flags:
  mtp: .bpm=~/bin/audio-bpm.py              # assign .bpm tag
  mtp: key=f,t5,~/bin/audio-key.py          # force/overwrite, 5s timeout
  mtp: ext=an,~/bin/file-ext.py             # non-audio files only
```

Flags: `f`=force, `t5`=5sec timeout, `ay`=audio-only (default), `an`=non-audio, `ad`=all

## Shares (Temporary Links)

```yaml
[global]
  shr: /shares           # enable at this URL prefix
  shr-adm: admin1        # users who can manage all shares
```

Share options: password-protection, expiration, upload permission.

## Misc Features

**Markdown Editor:** Two editors (basic + fancy/EasyMDE). Document history in `.hist`.

**RSS/OPDS:**
```yaml
[global]
  rss              # enable RSS
  opds             # enable OPDS (e-readers)
```

**OpenGraph/Discord:**
```yaml
[global]
  og                    # enable OpenGraph (disables hotlinking)
  og-ua: '(Discord|Twitter|Slack)bot'  # selective by user-agent
```

**Themes:** 6 built-in themes (0-5), each with dark/light variant. Custom CSS via `--css-browser`.

**File Manager:** Cut/paste across tabs (ctrl-x/c/v), batch rename (F2), download selection (Y).

**Version Checker:**
```yaml
[global]
  vc-url: https://api.copyparty.eu/advisories
  vc-age: 3       # check every 3 hours
  vc-exit          # emergency exit if vulnerable
```
