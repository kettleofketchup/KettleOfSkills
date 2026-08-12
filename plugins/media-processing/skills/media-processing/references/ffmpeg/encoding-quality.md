# FFmpeg Encoding: Quality & Optimization

CRF, bitrate, presets, tune options, and multi-threading.

## CRF (Constant Rate Factor)

Best for quality-focused encoding. Single-pass, adjusts bitrate for complexity.

**CRF Scale:**
- 0 = Lossless (huge files)
- 17-18 = Visually lossless
- 20-23 = High quality (recommended)
- 24-28 = Medium quality
- 30+ = Low quality
- 51 = Worst quality

```bash
# Visually lossless
ffmpeg -i input.mp4 -c:v libx264 -crf 18 -preset slow output.mp4

# High quality (recommended)
ffmpeg -i input.mp4 -c:v libx264 -crf 22 -preset medium output.mp4

# Balanced quality/size
ffmpeg -i input.mp4 -c:v libx264 -crf 25 -preset fast output.mp4
```

## Bitrate-Based Encoding

Target specific file size or quality. Two-pass recommended.

```bash
# bitrate = (target_size_MB * 8192) / duration_seconds - audio_bitrate

# Two-pass encoding (2600k video, 128k audio)
ffmpeg -y -i input.mkv -c:v libx264 -b:v 2600k -pass 1 -an -f null /dev/null
ffmpeg -i input.mkv -c:v libx264 -b:v 2600k -pass 2 -c:a aac -b:a 128k output.mp4
```

## Presets (Speed vs Compression)

Trade-off between encoding speed and file size.

Available: `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`, `placebo`

```bash
# Fast encoding (real-time)
ffmpeg -i input.mp4 -c:v libx264 -preset ultrafast -crf 23 output.mp4

# Best compression (slow)
ffmpeg -i input.mp4 -c:v libx264 -preset veryslow -crf 20 output.mp4
```

## Tune Options

Optimize encoder for specific content types:

```bash
ffmpeg -i input.mp4 -c:v libx264 -tune film -crf 22 output.mp4       # Film
ffmpeg -i input.mp4 -c:v libx264 -tune animation -crf 22 output.mp4  # Animation
ffmpeg -i input.mp4 -c:v libx264 -tune grain -crf 22 output.mp4      # Film grain
ffmpeg -i input.mp4 -c:v libx264 -tune zerolatency -crf 22 output.mp4 # Streaming
```

## Multi-Threading

```bash
ffmpeg -threads 4 -i input.mp4 -c:v libx264 output.mp4  # Limit threads
ffmpeg -threads 0 -i input.mp4 -c:v libx264 output.mp4  # Auto (default)
```

## Troubleshooting

### Poor Quality Output
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 18 -preset slow output.mp4
ffmpeg -i input.mp4 -c:v libx264 -crf 22 -preset veryslow output.mp4
```

### Slow Encoding
```bash
ffmpeg -i input.mp4 -c:v libx264 -preset ultrafast output.mp4
ffmpeg -i input.mp4 -vf scale=1280:-1 -c:v libx264 output.mp4  # Reduce resolution
```

### Large File Size
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 26 output.mp4
ffmpeg -i input.mp4 -c:v libx265 -crf 26 output.mp4  # Better codec
```

## Best Practices

1. Use CRF for most tasks — better than bitrate for variable content
2. Start with CRF 23 — good balance, adjust based on results
3. Use slow preset for archival and final delivery
4. Use fast preset for previews and testing
5. Two-pass encoding when file size is fixed
6. Match source frame rate — don't increase FPS
7. Don't upscale resolution — keep original or downscale
8. Test on short clips before full encode
