# FFmpeg Streaming: HLS & DASH

On-demand and adaptive bitrate streaming manifests.

## HLS (HTTP Live Streaming)

### Basic HLS
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -c:a aac \
  -f hls -hls_time 6 -hls_playlist_type vod \
  -hls_segment_filename "segment_%03d.ts" \
  playlist.m3u8
```

**Key parameters:**
- `-hls_time` — Segment duration in seconds (default 2)
- `-hls_playlist_type` — `vod` (on-demand) or `event` (live)
- `-g 48` — Keyframe every 48 frames (2s @ 24fps)
- `-sc_threshold 0` — Disable scene detection for consistent segments

### Optimized HLS
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset fast -crf 22 \
  -g 48 -sc_threshold 0 \
  -c:a aac -b:a 128k \
  -f hls -hls_time 6 -hls_playlist_type vod \
  -hls_segment_filename "segment_%03d.ts" \
  playlist.m3u8
```

### Multi-Bitrate HLS (Adaptive)
```bash
ffmpeg -i input.mp4 \
  -map 0:v -map 0:a -map 0:v -map 0:a -map 0:v -map 0:a \
  -c:v libx264 -crf 22 -c:a aac -b:a 128k \
  -b:v:0 800k  -s:v:0 640x360   -maxrate:v:0 856k  -bufsize:v:0 1200k \
  -b:v:1 1400k -s:v:1 842x480   -maxrate:v:1 1498k -bufsize:v:1 2100k \
  -b:v:2 2800k -s:v:2 1280x720  -maxrate:v:2 2996k -bufsize:v:2 4200k \
  -var_stream_map "v:0,a:0 v:1,a:1 v:2,a:2" \
  -master_pl_name master.m3u8 \
  -f hls -hls_time 6 -hls_list_size 0 \
  -hls_segment_filename "stream_%v/segment_%03d.ts" \
  stream_%v/playlist.m3u8
```

Creates: `master.m3u8`, `stream_0/` (360p), `stream_1/` (480p), `stream_2/` (720p)

### HLS with AES-128 Encryption
```bash
openssl rand 16 > enc.key
echo "enc.key" > enc.keyinfo
echo "enc.key" >> enc.keyinfo
openssl rand -hex 16 >> enc.keyinfo

ffmpeg -i input.mp4 \
  -c:v libx264 -c:a aac \
  -f hls -hls_time 6 \
  -hls_key_info_file enc.keyinfo \
  -hls_segment_filename "segment_%03d.ts" \
  playlist.m3u8
```

## DASH (Dynamic Adaptive Streaming)

### Basic DASH
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -c:a aac \
  -f dash -seg_duration 6 \
  -use_template 1 -use_timeline 1 \
  manifest.mpd
```

### Multi-Bitrate DASH
```bash
ffmpeg -i input.mp4 \
  -map 0:v -map 0:a -map 0:v -map 0:a \
  -c:v libx264 -c:a aac \
  -b:v:0 800k  -s:v:0 640x360 \
  -b:v:1 1400k -s:v:1 1280x720 \
  -b:a:0 128k -b:a:1 128k \
  -f dash -seg_duration 6 \
  -use_template 1 -use_timeline 1 \
  manifest.mpd
```

## Troubleshooting

### Buffering Issues
```bash
ffmpeg -re -i input.mp4 -maxrate 2000k -bufsize 2000k -c:v libx264 -f flv rtmp://...
ffmpeg -re -i input.mp4 -preset ultrafast -c:v libx264 -f flv rtmp://...
```

### Audio/Video Desync
```bash
ffmpeg -re -i input.mp4 -r 30 -c:v libx264 -f flv rtmp://...
ffmpeg -re -i input.mp4 -vsync 1 -c:v libx264 -f flv rtmp://...
```
