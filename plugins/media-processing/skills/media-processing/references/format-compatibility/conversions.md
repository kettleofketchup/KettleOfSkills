# Format Compatibility: Conversions

Common image, video, and audio format conversion commands.

## Image Conversions

```bash
# PNG to JPEG
magick input.png -quality 85 -strip output.jpg
# With transparency handling
magick input.png -background white -flatten -quality 85 output.jpg

# JPEG to WebP
magick input.jpg -quality 80 output.webp
ffmpeg -i input.jpg -quality 80 output.webp

# RAW to JPEG (requires dcraw)
magick input.CR2 -quality 90 output.jpg

# HEIC to JPEG (requires libheif)
magick input.heic -quality 85 output.jpg
```

## Video Conversions

```bash
# MKV to MP4 (fast, copy streams)
ffmpeg -i input.mkv -c copy output.mp4

# MKV to MP4 (re-encode if needed)
ffmpeg -i input.mkv -c:v libx264 -crf 23 -c:a aac output.mp4

# AVI to MP4
ffmpeg -i input.avi -c:v libx264 -crf 23 -c:a aac output.mp4

# MOV to MP4
ffmpeg -i input.mov -c copy output.mp4                           # If already H.264
ffmpeg -i input.mov -c:v libx264 -crf 18 -c:a aac output.mp4   # ProRes -> H.264

# Any to WebM (VP9)
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm
```

## Audio Conversions

```bash
# Extract audio from video
ffmpeg -i video.mp4 -vn -c:a copy audio.m4a         # Keep codec
ffmpeg -i video.mp4 -vn -q:a 0 audio.mp3            # MP3
ffmpeg -i video.mp4 -vn -c:a flac audio.flac         # Lossless

# Audio format conversion
ffmpeg -i input.wav -c:a libmp3lame -b:a 192k output.mp3
ffmpeg -i input.mp3 -c:a aac -b:a 192k output.m4a
ffmpeg -i input.wav -c:a libopus -b:a 128k output.opus
```

## Migration Strategies

### Archive to Web
```bash
for img in archive/*.tif; do
  base=$(basename "$img" .tif)
  magick "$img" -resize 2000x2000\> -quality 85 -strip "web/${base}.jpg"
  magick "$img" -resize 2000x2000\> -quality 85 "web/${base}.webp"
done
```

### Legacy Video to Modern
```bash
for video in legacy/*.avi; do
  base=$(basename "$video" .avi)
  ffmpeg -i "$video" -c:v libx264 -crf 23 -preset slow -c:a aac "modern/${base}.mp4"
done
```

### Multi-Format Publishing
```bash
input="source.mp4"
ffmpeg -i "$input" -c:v libx264 -crf 23 -c:a aac output.mp4
ffmpeg -i "$input" -c:v libvpx-vp9 -crf 30 -c:a libopus output.webm
ffmpeg -ss 5 -i "$input" -vframes 1 poster.jpg
magick poster.jpg -quality 80 poster.webp
```

## Troubleshooting

```bash
# Check FFmpeg supported formats
ffmpeg -formats
ffmpeg -encoders | grep h264

# Check ImageMagick formats
magick identify -list format

# Install codec support (Ubuntu)
sudo apt-get install libx264-dev libx265-dev libvpx-dev

# Force compatible encoding
ffmpeg -i input.mp4 \
  -c:v libx264 -profile:v high -level 4.0 \
  -pix_fmt yuv420p \
  -c:a aac -b:a 128k output.mp4

# Avoid quality loss: use lossless intermediate
ffmpeg -i source.mp4 -c:v ffv1 intermediate.mkv
ffmpeg -i intermediate.mkv -c:v libx264 final.mp4
```
