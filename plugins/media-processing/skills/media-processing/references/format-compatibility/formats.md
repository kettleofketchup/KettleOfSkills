# Format Compatibility: Supported Formats

Image, video, and audio format/codec reference.

## Image Formats

### ImageMagick Support
**Raster:** JPEG, PNG, WebP, GIF, TIFF, BMP, ICO
**RAW:** CR2, NEF, ARW, DNG (requires dcraw/ufraw-batch)
**Other:** HEIC (requires libheif), AVIF (requires libavif), PSD

### Platform Compatibility (2025)
**Web browsers:** JPEG, PNG, WebP, GIF, SVG, AVIF
**iOS:** JPEG, PNG, HEIC
**Android:** JPEG, PNG, WebP

## Video Formats

### Container Formats
**Universal:** MP4, MKV, WebM, AVI, MOV
**Streaming:** TS (HLS segments), M3U8 (HLS playlist), MPD (DASH), FLV
**Professional:** ProRes (.mov), DNxHD/DNxHR (.mxf, .mov), MXF

### Video Codecs
**Modern:** H.264 (libx264), H.265 (libx265), VP9 (libvpx-vp9), AV1 (libsvtav1)
**Legacy:** MPEG-4, MPEG-2, VP8
**Professional:** ProRes, DNxHD, rawvideo

### Audio Codecs
**Modern:** AAC, Opus, MP3
**Lossless:** FLAC, ALAC, WAV (pcm_s16le)
**Other:** Vorbis, AC-3 (Dolby), DTS

## Use Case Matrix

| Use Case | Image Format | Video Codec | Audio Codec |
|----------|--------------|-------------|-------------|
| Web general | JPEG 85% | H.264 | AAC 128k |
| Web modern | WebP | VP9 | Opus |
| 4K streaming | — | H.265 | AAC 192k |
| Archive | PNG/TIFF | H.265 CRF 18 | FLAC |
| Email | JPEG 75% | — | — |
| YouTube | — | H.264/VP9 | AAC/Opus |
| Live stream | — | H.264 | AAC |
| Editing | — | ProRes/DNxHD | PCM |

## Platform Compatibility

| Platform | Recommended Video | Support |
|----------|------------------|---------|
| Web browsers | H.264 (MP4) | H.264, VP9, AV1 |
| Mobile devices | H.264 | H.264, H.265 |
| Smart TVs | H.264 | H.264, H.265 |
| YouTube | VP9, H.264 | All |
| Social media | H.264 | H.264 |

## Quality vs Size Reference

### Image Quality
**JPEG vs Modern formats (same quality):**
- WebP: 25-35% smaller than JPEG
- HEIC: 40-50% smaller than JPEG
- AVIF: 50-60% smaller than JPEG
- PNG: 2-5x larger than JPEG (lossless)

### Video Quality
**H.264 CRF:** CRF 18 = ~8-15 Mbps 1080p; CRF 23 = ~4-8 Mbps; CRF 28 = ~2-4 Mbps

**Codec efficiency vs H.264:**
- H.265: 40-50% smaller
- VP9: 30-40% smaller
- AV1: 50-60% smaller

### Audio Bitrates
- 320 kbps AAC: Transparent/archival
- 192 kbps: High quality
- 128 kbps: Good streaming quality
- 96 kbps: Acceptable
- Opus at 128k outperforms MP3 at 192k

## Codec Selection

| Use H.264 | Use H.265 | Use VP9 | Use AV1 |
|-----------|-----------|---------|---------|
| Max compat | 4K video | YouTube | Future-proof |
| Older devices | Storage limited | Open-source | Max compression |
| Social media | Archival | Chrome/Firefox primary | Encoding time ok |
| Fast encoding | Bandwidth limited | Royalty-free | |
