# FFmpeg Streaming: Live & RTMP

RTMP streaming to platforms, screen capture, UDP/RTP, and advanced streaming.

## RTMP Live Streaming

### Stream to Platforms
```bash
# Twitch
ffmpeg -re -i input.mp4 \
  -c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k \
  -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 \
  -f flv rtmp://live.twitch.tv/app/STREAM_KEY

# YouTube
ffmpeg -re -i input.mp4 \
  -c:v libx264 -preset veryfast -maxrate 2500k -bufsize 5000k \
  -pix_fmt yuv420p -g 60 -c:a aac -b:a 128k \
  -f flv rtmp://a.rtmp.youtube.com/live2/STREAM_KEY

# Facebook
ffmpeg -re -i input.mp4 \
  -c:v libx264 -preset veryfast -maxrate 4000k -bufsize 8000k \
  -pix_fmt yuv420p -g 60 -c:a aac -b:a 128k \
  -f flv rtmps://live-api-s.facebook.com:443/rtmp/STREAM_KEY

# Custom RTMP server
ffmpeg -re -i input.mp4 \
  -c:v libx264 -preset veryfast -tune zerolatency \
  -maxrate 2500k -bufsize 5000k \
  -pix_fmt yuv420p -g 50 \
  -c:a aac -b:a 128k -ar 44100 \
  -f flv rtmp://your-server.com/live/stream-key
```

**Important RTMP parameters:**
- `-re` — Read at native frame rate
- `-tune zerolatency` — Minimize latency
- `-g N` — Keyframe interval (fps × 2 recommended)
- `-maxrate`/`-bufsize` — Rate control
- `-pix_fmt yuv420p` — Maximum compatibility

## Bitrate Recommendations

| Resolution/FPS | Video | Audio |
|----------------|-------|-------|
| 1080p 60fps | 4500-6000k | 160k |
| 1080p 30fps | 3000-4500k | 128k |
| 720p 60fps | 2500-4000k | 128k |
| 720p 30fps | 1500-2500k | 128k |
| 480p | 500-1000k | 128k |

## Screen Capture & Stream

### Linux (X11)
```bash
ffmpeg -f x11grab -s 1920x1080 -framerate 30 -i :0.0 \
  -f pulse -ac 2 -i default \
  -c:v libx264 -preset veryfast -tune zerolatency \
  -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 \
  -f flv rtmp://live.twitch.tv/app/STREAM_KEY
```

### macOS (AVFoundation)
```bash
ffmpeg -f avfoundation -list_devices true -i ""   # List devices
ffmpeg -f avfoundation -framerate 30 -i "1:0" \
  -c:v libx264 -preset veryfast -tune zerolatency \
  -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  -f flv rtmp://live.twitch.tv/app/STREAM_KEY
```

### Windows (DirectShow)
```bash
ffmpeg -f dshow -i video="screen-capture-recorder":audio="Stereo Mix" \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -maxrate 750k -bufsize 3000k \
  -f flv rtmp://live.twitch.tv/app/STREAM_KEY
```

## UDP/RTP Streaming

```bash
# UDP sender/receiver
ffmpeg -re -i input.mp4 -c copy -f mpegts udp://192.168.1.100:1234
ffplay udp://192.168.1.100:1234

# RTP stream
ffmpeg -re -i input.mp4 -c:v libx264 -preset ultrafast \
  -c:a aac -f rtp rtp://192.168.1.100:5004

# Multicast
ffmpeg -re -i input.mp4 -c copy -f mpegts udp://239.255.0.1:1234
```

## Advanced Streaming

### Hardware-Accelerated Stream
```bash
ffmpeg -re -i input.mp4 \
  -c:v h264_nvenc -preset fast -maxrate 3000k -bufsize 6000k \
  -c:a aac -b:a 128k \
  -f flv rtmp://live.twitch.tv/app/STREAM_KEY
```

### Stream with Overlay
```bash
ffmpeg -re -i input.mp4 -i logo.png \
  -filter_complex "[0:v][1:v]overlay=10:10" \
  -c:v libx264 -preset veryfast -maxrate 3000k \
  -c:a copy -f flv rtmp://live.twitch.tv/app/STREAM_KEY
```

### Loop Stream (24/7)
```bash
ffmpeg -stream_loop -1 -re -i input.mp4 \
  -c:v libx264 -preset veryfast -maxrate 2500k \
  -c:a aac -b:a 128k \
  -f flv rtmp://live.twitch.tv/app/STREAM_KEY
```

### Reconnect on Failure
```bash
while true; do
  ffmpeg -re -i input.mp4 -c:v libx264 -f flv rtmp://...
  sleep 5
done
```
