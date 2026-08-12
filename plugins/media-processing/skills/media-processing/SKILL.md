---
name: media-processing
description: FFmpeg + ImageMagick media processing. This skill should be used when transcoding video/audio, resizing/cropping images, HLS/DASH, thumbnails, batch ops, or hardware-accelerated pipelines.
license: MIT
---

# Media Processing Skill

Process video, audio, and images using FFmpeg and ImageMagick for conversion, optimization, streaming, and manipulation.

## When to Use This Skill

- Converting media formats (video, audio, images)
- Encoding video with codecs (H.264, H.265, VP9, AV1)
- Processing images (resize, crop, effects, watermarks)
- Extracting audio from video
- Creating streaming manifests (HLS/DASH)
- Generating thumbnails and previews
- Batch processing media files
- Hardware-accelerated encoding

## Tool Selection Guide

| Task | Tool |
|------|------|
| Video encoding/transcoding | FFmpeg |
| Audio extraction/conversion | FFmpeg |
| Live streaming (RTMP/HLS/DASH) | FFmpeg |
| Image resize/crop/convert | ImageMagick |
| Batch image processing | ImageMagick (mogrify) |
| Video thumbnails | FFmpeg |
| Image effects/watermarks | ImageMagick |

## Installation

```bash
# macOS
brew install ffmpeg imagemagick

# Ubuntu/Debian
sudo apt-get install ffmpeg imagemagick

# Windows
winget install ffmpeg
winget install ImageMagick.ImageMagick
```

```bash
# Verify
ffmpeg -version && ffprobe -version && magick -version
```

## Quick Examples

```bash
# Convert format (stream copy, fast)
ffmpeg -i input.mkv -c copy output.mp4

# Re-encode with H.264
ffmpeg -i input.avi -c:v libx264 -crf 22 -c:a aac output.mp4

# Resize video to 720p
ffmpeg -i input.mp4 -vf scale=-1:720 -c:a copy output.mp4

# Extract audio
ffmpeg -i video.mp4 -vn -q:a 0 audio.mp3

# Image conversion
magick input.png -quality 85 -strip output.jpg

# Resize image
magick input.jpg -resize 800x output.jpg

# Square thumbnail
magick input.jpg -resize 200x200^ -gravity center -extent 200x200 thumb.jpg

# Batch resize
mogrify -path ./output -resize 800x -quality 85 *.jpg

# HLS stream
ffmpeg -i input.mp4 -c:v libx264 -preset fast -crf 22 \
  -f hls -hls_time 6 -hls_playlist_type vod playlist.m3u8

# Video GIF
ffmpeg -i input.mp4 -vf "fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif
```

## Key Parameters

### FFmpeg Video
- `-c:v` — Video codec (libx264, libx265, libvpx-vp9)
- `-crf` — Quality (0-51, lower=better, 23=default)
- `-preset` — Speed/compression (ultrafast to veryslow)
- `-b:v` — Video bitrate (e.g., 2M, 2500k)
- `-vf` — Video filters

### FFmpeg Audio
- `-c:a` — Audio codec (aac, mp3, opus)
- `-b:a` — Audio bitrate (e.g., 128k, 192k)
- `-ar` — Sample rate (44100, 48000)

### ImageMagick Geometry
- `800x600` — Fit within (maintains aspect)
- `800x600!` — Force exact size
- `800x600^` — Fill (may crop)
- `800x` / `x600` — Width or height only
- `50%` — Scale percentage

## Troubleshooting

**FFmpeg "Unknown encoder"**
```bash
ffmpeg -encoders | grep h264
sudo apt-get install libx264-dev libx265-dev
```

**ImageMagick "not authorized"**
```bash
# Edit /etc/ImageMagick-7/policy.xml
# Change rights="none" to rights="read|write" for the format
```

**Memory errors**
```bash
ffmpeg -threads 4 input.mp4 output.mp4
magick -limit memory 2GB -limit map 4GB input.jpg output.jpg
```

## References

**FFmpeg:**
- `ffmpeg/encoding-codecs.md` — H.264, H.265, VP9, AV1, audio codecs, codec selection
- `ffmpeg/encoding-quality.md` — CRF, bitrate, presets, tune options, threading
- `ffmpeg/encoding-hardware.md` — NVIDIA NVENC, Intel QSV, AMD AMF, Apple VideoToolbox
- `ffmpeg/filters-video.md` — Scale, crop, rotate, overlay, denoise, color, text
- `ffmpeg/filters-audio-advanced.md` — Audio filters, complex filtergraphs, recipes
- `ffmpeg/streaming-hls-dash.md` — HLS, multi-bitrate HLS, DASH, encryption
- `ffmpeg/streaming-live.md` — RTMP platforms, screen capture, UDP/RTP, loop streams
- `ffmpeg/streaming-thumbnails.md` — Frame extraction, sprite sheets, preview generation

**ImageMagick:**
- `imagemagick/editing-basics.md` — Format conversion, resize, crop, thumbnails, rotation
- `imagemagick/editing-effects.md` — Blur, sharpen, color effects, borders, text, composition
- `imagemagick/batch-basic.md` — Mogrify, resize loops, format conversion, optimization
- `imagemagick/batch-advanced.md` — Parallel processing, watermarks, web pipelines, Python

**Formats:**
- `format-compatibility/formats.md` — Supported formats, codecs, platform compatibility tables
- `format-compatibility/conversions.md` — Common conversion commands, migration strategies

## Resources

- FFmpeg: https://ffmpeg.org/documentation.html
- ImageMagick: https://imagemagick.org/
