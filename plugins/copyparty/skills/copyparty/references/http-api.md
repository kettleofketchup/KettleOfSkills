# Copyparty HTTP API: Read Endpoints

Methods: `GET`, `POST`, `PUT`, `jPOST` (JSON POST), `mPOST` (multipart POST), `uPOST` (URL-encoded POST).

## Authentication

Clients authenticate via (first non-blank wins):
1. URL param `&pw=password`
2. Header `PW: password`
3. Basic auth
4. Cookie `cppwd=password` (HTTP) or `cppws=password` (HTTPS)

With `--usernames`: format is `user:password` everywhere.

## File/Directory Listing

| Method | Params | Result |
|--------|--------|--------|
| GET | `?ls` | List files/folders as JSON |
| GET | `?ls=t` | List as plaintext |
| GET | `?ls=v` | List with terminal colors |
| GET | `?b` | Simplified HTML listing |
| GET | `?tree=.` | One level of subdirectories |
| GET | `?opds` | OPDS feed (e-readers) |

## File Download

| Method | Params | Result |
|--------|--------|--------|
| GET | `?dl` | Force download (not in-browser) |
| GET | `?txt` | Get as plaintext |
| GET | `?mime=foo` | Return with specific mimetype |
| GET | `?v` | Render markdown / open in mediaplayer |
| GET | `?raw` | Bypass OpenGraph, force raw file |
| GET | `?tail` | Stream growing file in realtime |
| GET | `?tail=-128` | Start 128 bytes from end |

## Archive Download

| Method | Params | Result |
|--------|--------|--------|
| GET | `?tar` | GNU tar |
| GET | `?tar=gz:9` | Gzip-compressed tar (level 9) |
| GET | `?tar=xz:9` | XZ-compressed tar (level 9) |
| GET | `?tar=pax` | PAX format tar |
| GET | `?zip` | ZIP file |
| GET | `?zip=dos` | WinXP-compatible ZIP (cp437) |

Archive modifiers:
- `&opus` / `&mp3` - transcode audio to opus/mp3
- `&nodot` - skip dotfiles/dotfolders
- `&j` / `&w` / `&p` - include jpeg/webm thumbnails or audio waveforms

Selective archive: jPOST `?tar` with body `["foo","bar"]`

## Thumbnails and Transcoding

| Method | Params | Result |
|--------|--------|--------|
| GET | `?th` | Get thumbnail |
| GET | `?th=opus` | Transcode audio to 128kbps opus |
| GET | `?th=mp3` | Transcode to mp3 |
| GET | `?tar&w` | Pre-generate webp thumbnails |
| GET | `?tar&j` | Pre-generate jpg thumbnails |

## Search and Other

| Method | Body/Params | Result |
|--------|-------------|--------|
| jPOST | `{"q":"search terms"}` | Server-wide search |
| GET | `?zls` | List files inside a zip |
| GET | `?zget=path` | Extract specific file from zip |
| GET | `?ups` | Show recent uploads from your IP |
| GET | `?ru&j` | Recent uploads as JSON |
| GET | `?shares` | List your shared files/folders |
| GET | `?grid` | Show grid view |
| GET | `?imgs` | Grid view with thumbnails |

## Admin Endpoints

| Method | Params | Result |
|--------|--------|--------|
| GET | `?reload=cfg` | Reload config files, rescan volumes |
| GET | `?scan` | Rescan volume providing URL |
| GET | `?stack` | Show stacktrace of all threads |

## Prometheus Metrics

Enable with `--stats`. Available at `/.cpr/metrics` (admin accounts only).

Available metrics: uptime, active connections, requests, bans, db activity, volume stats (disk size/free, file counts, dedup bytes).

Disable options: `--nos-hdd`, `--nos-vol`, `--nos-vst`, `--nos-dup`, `--nos-unf`

## Breaking Changes

- `v1.9.16`: prometheus metric renames (`cpp_bans` -> `cpp_active_bans`)
- `v1.6.0`: delete/move changed from GET to POST; non-GET/HEAD must pass CORS
- `v1.5.0`: new chunksize formula for files > 128 GiB
