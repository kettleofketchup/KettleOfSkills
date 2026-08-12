# FFmpeg Encoding: Codecs

Video and audio codec selection with examples.

## Video Codecs

### H.264 (libx264)
Most widely supported codec, excellent compression/quality balance.

**Best for:** Universal compatibility, streaming, web video

```bash
# High quality
ffmpeg -i input.mkv -c:v libx264 -preset slow -crf 18 -c:a copy output.mp4

# Standard quality (recommended)
ffmpeg -i input.mkv -c:v libx264 -preset medium -crf 23 -c:a copy output.mp4

# Fast encoding
ffmpeg -i input.mkv -c:v libx264 -preset fast -crf 23 -c:a copy output.mp4
```

### H.265/HEVC (libx265)
25-50% better compression than H.264, slower encoding.

**Best for:** 4K video, file size reduction, archival

```bash
ffmpeg -i input.mkv -c:v libx265 -preset medium -crf 24 -c:a copy output.mp4
```

### VP9 (libvpx-vp9)
Royalty-free, WebM format, good for YouTube.

```bash
# Quality-based (recommended)
ffmpeg -i input.mkv -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm

# Two-pass
ffmpeg -i input.mkv -c:v libvpx-vp9 -b:v 2M -pass 1 -an -f null /dev/null
ffmpeg -i input.mkv -c:v libvpx-vp9 -b:v 2M -pass 2 -c:a libopus output.webm
```

### AV1 (libaom-av1, libsvtav1)
Next-generation codec, best compression, very slow encoding.

```bash
# Using SVT-AV1 (faster)
ffmpeg -i input.mkv -c:v libsvtav1 -crf 30 -preset 5 output.mp4
```

## Audio Codecs

### AAC (Industry Standard)
```bash
ffmpeg -i input.mp4 -c:a aac -b:a 128k output.mp4
ffmpeg -i input.mp4 -c:a aac -b:a 192k output.mp4
```

### MP3 (libmp3lame)
```bash
# Variable bitrate (best quality)
ffmpeg -i input.wav -c:a libmp3lame -q:a 0 output.mp3
ffmpeg -i input.wav -c:a libmp3lame -b:a 192k output.mp3
```

### Opus (libopus)
Best quality at low bitrates, ideal for streaming.

```bash
ffmpeg -i input.mp4 -c:a libopus -b:a 128k output.webm
ffmpeg -i input.mp4 -c:a libopus -b:a 32k -ac 1 output.webm  # Voice mono
```

### FLAC (Lossless)
```bash
ffmpeg -i input.wav -c:a flac output.flac
```

## Codec Selection Guide

| Use Case | Codec | Settings |
|----------|-------|----------|
| Web video | H.264 | CRF 23, preset medium |
| 4K streaming | H.265 | CRF 24, preset fast |
| YouTube upload | VP9 or H.264 | CRF 23 |
| Archive | H.265 or H.264 | CRF 18, preset slow |
| Low bandwidth | AV1 or H.265 | CRF 30 |
| Fast encoding | H.264 NVENC | preset fast |
| Max compatibility | H.264 | profile main, level 4.0 |

## Platform Compatibility

| Platform | Recommended | Supported |
|----------|------------|-----------|
| Web browsers | H.264 | H.264, VP9, AV1 |
| Mobile devices | H.264 | H.264, H.265 |
| YouTube | VP9, H.264 | All |
| Social media | H.264 | H.264 |
