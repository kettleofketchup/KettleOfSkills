# Copyparty HTTP API

Full API reference. Methods: `GET`, `POST`, `PUT`, `jPOST` (JSON POST), `mPOST` (multipart POST), `uPOST` (URL-encoded POST).

## Authentication

Clients authenticate via (first non-blank wins):
1. URL param `&pw=password` (disable with `--pw-urlp=A`)
2. Header `PW: password` (disable with `--pw-hdr=A`)
3. Basic auth (disable with `--no-bauth`)
4. Cookie `cppwd=password` (HTTP) or `cppws=password` (HTTPS)

With `--usernames`: format is `user:password` everywhere.

## Read Endpoints

### File/Directory Listing

| Method | Params | Result |
|--------|--------|--------|
| GET | `?ls` | List files/folders as JSON |
| GET | `?ls&dots` | List including dotfiles |
| GET | `?ls=t` | List as plaintext |
| GET | `?ls=v` | List with terminal colors |
| GET | `?b` | Simplified HTML listing |
| GET | `?tree=.` | One level of subdirectories |
| GET | `?tree` | Subdirectories for each level to URL |
| GET | `?opds` | OPDS feed (e-readers) |

### File Download

| Method | Params | Result |
|--------|--------|--------|
| GET | `?dl` | Force download (not in-browser) |
| GET | `?txt` | Get as plaintext |
| GET | `?txt=iso-8859-1` | Plaintext with charset |
| GET | `?mime=foo` | Return with specific mimetype |
| GET | `?v` | Render markdown / open in mediaplayer |
| GET | `?lt` | Use symlink timestamps |
| GET | `?raw` | Bypass OpenGraph, force raw file |

### Archive Download

| Method | Params | Result |
|--------|--------|--------|
| GET | `?tar` | GNU tar |
| GET | `?tar=gz:9` | Gzip-compressed tar (level 9) |
| GET | `?tar=xz:9` | XZ-compressed tar (level 9) |
| GET | `?tar=bz2:9` | Bzip2-compressed tar (level 9) |
| GET | `?tar=pax` | PAX format tar |
| GET | `?tar=pax,xz` | PAX tar with XZ compression |
| GET | `?zip` | ZIP file |
| GET | `?zip=dos` | WinXP-compatible ZIP (cp437) |
| GET | `?zip=crc` | MSDOS-compatible ZIP with CRC |

Archive modifiers (append to tar/zip):
- `&opus` / `&mp3` - transcode audio to opus/mp3
- `&nodot` - skip dotfiles/dotfolders
- `&j` / `&w` / `&p` - include jpeg/webm thumbnails or audio waveforms

### Selective Archive Download

| Method | Params | Body | Result |
|--------|--------|------|--------|
| jPOST | `?tar` | `["foo","bar"]` | Download specific folders as tar |

### Thumbnails and Transcoding

| Method | Params | Result |
|--------|--------|--------|
| GET | `?th` | Get thumbnail |
| GET | `?th=opus` | Transcode audio to 128kbps opus |
| GET | `?th=caf` | Transcode to iOS opus container |
| GET | `?th=mp3` | Transcode to mp3 |
| GET | `?tar&w` | Pre-generate webp thumbnails |
| GET | `?tar&j` | Pre-generate jpg thumbnails |
| GET | `?tar&p` | Pre-generate audio waveforms |

### Tailing (Live Streaming)

| Method | Params | Result |
|--------|--------|--------|
| GET | `?tail` | Stream growing file in realtime |
| GET | `?tail=1024` | Start from byte 1024 |
| GET | `?tail=-128` | Start 128 bytes from end |

### Zip File Inspection

| Method | Params | Result |
|--------|--------|--------|
| GET | `?zls` | List files inside a zip |
| GET | `?zget=path` | Extract specific file from zip |

### Search

| Method | Body | Result |
|--------|------|--------|
| jPOST | `{"q":"search terms"}` | Server-wide search |

Search query syntax (use the raw field in UI):
- Space-separated terms are AND'ed
- Prefix with `-` to negate
- `( tags like *nhato* or tags like *taishi* )`
- `w = kFpDiztbZc8Z` (search by wark/checksum)

### Shares and Uploads

| Method | Params | Result |
|--------|--------|--------|
| GET | `?shares` | List your shared files/folders |
| GET | `?dls` | Show active downloads (admin) |
| GET | `?ups` | Show recent uploads from your IP |
| GET | `?ups&filter=f` | Filter by URL containing `f` |
| GET | `?ru` | All recent uploads |
| GET | `?ru&j` | Recent uploads as JSON |
| GET | `?ru&filter=f` | Filter recent uploads |

### Grid/View Control

| Method | Params | Result |
|--------|--------|--------|
| GET | `?grid` | Show grid view |
| GET | `?imgs` | Grid view with thumbnails |
| GET | `?grid=0` / `?imgs=0` | Show list view |
| GET | `?thumb` / `?thumb=0` | Toggle thumbnails in grid |

## Write Endpoints

### File Upload

| Method | Params | Body | Result |
|--------|--------|------|--------|
| PUT | | binary data | Upload as file at URL |
| PUT | `?j` | binary data | Upload, reply with JSON |
| PUT | `?ck` | binary data | Upload without checksum |
| PUT | `?ck=md5` | binary data | Return MD5 instead of SHA512 |
| PUT | `?gz` | binary data | Gzip compress then write |
| PUT | `?xz` | binary data | XZ compress then write |
| PUT | `?apnd` | binary data | Append to existing file |
| mPOST | | `f=FILE` | Upload file to folder at URL |
| mPOST | `?j` | `f=FILE` | Upload, reply with JSON |
| mPOST | `?ck` | `f=FILE` | Upload without checksum |
| mPOST | `?replace` | `f=FILE` | Overwrite existing files |
| mPOST | `?apnd` | `f=FILE` | Append to existing files |
| mPOST | `?media` | `f=FILE` | Return media link (not hotlink) |

### Upload Modifiers

| HTTP Header | URL Param | Effect |
|-------------|-----------|--------|
| `Accept: url` | `want=url` | Return just the file URL |
| `Accept: json` | `want=json` | Return upload info as JSON |
| `Rand: 4` | `rand=4` | Random filename (4 chars) |
| `Life: 30` | `life=30` | Delete file after 30 seconds |
| `Replace: 1` | `replace` | Overwrite if exists |
| `CK: no` | `ck` | Disable serverside checksum |
| `CK: md5` | `ck=md5` | Return MD5 checksum |
| `CK: sha1` | `ck=sha1` | Return SHA1 checksum |
| `CK: sha256` | `ck=sha256` | Return SHA256 checksum |
| `CK: b2` | `ck=b2` | Return BLAKE2b checksum |
| `CK: b2s` | `ck=b2s` | Return BLAKE2s checksum |

Notes:
- `life` requires volume lifetime volflag, and volume lifetime must exceed file lifetime
- `replace` header works for PUT and multipart-POST; URL param only for multipart-POST

### File/Folder Operations

| Method | Params | Body | Result |
|--------|--------|------|--------|
| POST | `?copy=/foo/bar` | | Copy file/folder to /foo/bar |
| POST | `?move=/foo/bar` | | Move/rename to /foo/bar |
| POST | `?delete` | | Delete URL recursively |
| jPOST | `?delete` | `["/foo","/bar"]` | Delete multiple paths |
| mPOST | | `act=mkdir`, `name=foo` | Create directory |
| mPOST | | `act=tput`, `body=TEXT` | Overwrite markdown document |

### Shares

| Method | Params | Body | Result |
|--------|--------|------|--------|
| jPOST | `?share` | (complex JSON) | Create temporary share link |
| POST | `?eshare=rm` | | Delete a share |
| POST | `?eshare=3` | | Set share expiry to 3 minutes |

### Messages

| Method | Params/Body | Result |
|--------|------------|--------|
| uPOST | `msg=foo` | Send message to server log |
| POST | `?smsg=foo` | Send message / run xm hook |

## Admin Endpoints

| Method | Params | Result |
|--------|--------|--------|
| GET | `?reload=cfg` | Reload config files, rescan volumes |
| GET | `?scan` | Rescan volume providing URL |
| GET | `?scan=/a,/b` | Rescan specific volumes |
| GET | `?stack` | Show stacktrace of all threads |
| GET | `?pw=x` | Logout |

## Up2k Protocol (Resumable Upload)

The up2k uploader:
1. Client splits file into optimal chunks (1 MiB default, up to 256 chunks max)
2. Client hashes each chunk (SHA-512 in web workers)
3. Client POSTs hash list + filename + size + last-modified
4. Server creates wark: `sha512(salt + filesize + chunk_hashes)`
5. Server creates sparse file
6. Client sends chunks as POSTs with chunk-hash headers
7. Server writes chunks into correct positions
8. Client does final handshake; server confirms or requests re-upload

Advantages:
- Autoresume on network interruption
- Resume after browser/PC reboot
- Server detects corruption; client re-uploads affected chunks
- Skips already-existing files (dedup)
- No filesize limit (even behind Cloudflare)
- Preserves last-modified timestamp
- Safe to restart server during uploads

## Prometheus Metrics

Enable with `--stats`. Available at `/.cpr/metrics` (admin accounts only).

```yaml
# prometheus.yml
scrape_configs:
  - job_name: copyparty
    metrics_path: /.cpr/metrics
    basic_auth:
      password: wark
    static_configs:
      - targets: ['192.168.1.1:3923']
```

Available metrics:
- `cpp_uptime_seconds`, `cpp_boot_unixtime_seconds`
- `cpp_active_dl`, `cpp_http_conns`, `cpp_http_reqs`
- `cpp_sus_reqs`, `cpp_active_bans`, `cpp_total_bans`
- `cpp_db_idle_seconds`, `cpp_db_act_seconds` (unless `--nos-vst`)
- `cpp_idle_vols`, `cpp_busy_vols`, `cpp_offline_vols`
- `cpp_hashing_files`, `cpp_tagq_files`, `cpp_mtpq_files`
- Per-volume: `cpp_disk_size_bytes`, `cpp_disk_free_bytes`
- Per-volume + total: `cpp_vol_bytes`, `cpp_vol_files`, `cpp_dupe_bytes`, `cpp_dupe_files`, `cpp_unf_bytes`

Disable options: `--nos-hdd`, `--nos-vol`, `--nos-vst`, `--nos-dup`, `--nos-unf`

## Breaking Changes

- `v1.9.16`: prometheus metric renames (`cpp_bans` -> `cpp_active_bans`)
- `v1.6.0`: delete/move changed from GET to POST; non-GET/HEAD must pass CORS
- `v1.5.0`: new chunksize formula for files > 128 GiB
