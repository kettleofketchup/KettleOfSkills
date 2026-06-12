# Copyparty HTTP API: Write Endpoints

## File Upload

| Method | Params | Body | Result |
|--------|--------|------|--------|
| PUT | | binary data | Upload as file at URL |
| PUT | `?j` | binary data | Upload, reply with JSON |
| PUT | `?gz` | binary data | Gzip compress then write |
| PUT | `?xz` | binary data | XZ compress then write |
| PUT | `?apnd` | binary data | Append to existing file |
| mPOST | | `f=FILE` | Upload file to folder at URL |
| mPOST | `?j` | `f=FILE` | Upload, reply with JSON |
| mPOST | `?replace` | `f=FILE` | Overwrite existing files |
| mPOST | `?apnd` | `f=FILE` | Append to existing files |

## Upload Modifiers

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

Notes:
- `life` requires volume `lifetime` volflag; volume lifetime must exceed file lifetime
- `replace` header works for PUT and multipart-POST; URL param only for multipart-POST

## File/Folder Operations

| Method | Params | Body | Result |
|--------|--------|------|--------|
| POST | `?copy=/foo/bar` | | Copy file/folder to /foo/bar |
| POST | `?move=/foo/bar` | | Move/rename to /foo/bar |
| POST | `?delete` | | Delete URL recursively |
| jPOST | `?delete` | `["/foo","/bar"]` | Delete multiple paths |
| mPOST | | `act=mkdir`, `name=foo` | Create directory |
| mPOST | | `act=tput`, `body=TEXT` | Overwrite markdown document |

## Shares

| Method | Params | Body | Result |
|--------|--------|------|--------|
| jPOST | `?share` | (complex JSON) | Create temporary share link |
| POST | `?eshare=rm` | | Delete a share |
| POST | `?eshare=3` | | Set share expiry to 3 minutes |

## Messages

| Method | Params/Body | Result |
|--------|------------|--------|
| uPOST | `msg=foo` | Send message to server log |
| POST | `?smsg=foo` | Send message / run xm hook |

## Up2k Protocol (Resumable Upload)

1. Client splits file into chunks (1 MiB default, up to 256 chunks max)
2. Client hashes each chunk (SHA-512 in web workers)
3. Client POSTs hash list + filename + size + last-modified
4. Server creates wark: `sha512(salt + filesize + chunk_hashes)`
5. Server creates sparse file
6. Client sends chunks as POSTs with chunk-hash headers
7. Client does final handshake; server confirms or requests re-upload

Advantages:
- Autoresume on network interruption (even after browser/PC reboot)
- Server detects corruption; client re-uploads affected chunks
- Skips already-existing files (dedup)
- No filesize limit (even behind Cloudflare)
- Preserves last-modified timestamp
- Safe to restart server during uploads

## curl Examples

```bash
# Upload file
curl -F f=@movie.mkv http://127.0.0.1:3923/?pw=wark

# Upload, get URL back
curl -F f=@movie.mkv 'http://127.0.0.1:3923/?want=url&pw=wark'

# PUT upload with random filename
curl -H pw:wark -H rand:8 -T movie.mkv http://127.0.0.1:3923/

# Append to file
curl -H pw:wark -T- http://127.0.0.1:3923/logfile.txt?apnd

# Stream upload via netcat
(printf 'PUT /junk?pw=wark HTTP/1.1\r\n\r\n'; cat movie.mkv) | nc 127.0.0.1 3923
```
