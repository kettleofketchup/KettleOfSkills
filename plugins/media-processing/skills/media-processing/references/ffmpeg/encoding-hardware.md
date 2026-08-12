# FFmpeg Encoding: Hardware Acceleration

GPU-accelerated encoding with NVIDIA, Intel, AMD, and Apple.

## NVIDIA NVENC

5-10x faster encoding, slightly larger files than software encoding.

**Requirements:** NVIDIA GPU (GTX 10xx or newer)

```bash
# H.264 with NVENC
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc -preset fast -crf 22 output.mp4

# H.265 with NVENC
ffmpeg -hwaccel cuda -i input.mp4 -c:v hevc_nvenc -preset slow -crf 24 output.mp4

# Quality levels (instead of CRF)
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc -preset slow -rc vbr -cq 22 output.mp4
```

**NVENC Presets:**
`default`, `slow`, `medium`, `fast`, `hp` (high perf), `hq` (high quality), `bd` (Bluray), `ll` (low latency), `llhq`, `llhp`

## Intel QuickSync (QSV)

Fast hardware encoding on Intel CPUs with integrated graphics.

```bash
# H.264 with QSV
ffmpeg -hwaccel qsv -c:v h264_qsv -i input.mp4 \
  -c:v h264_qsv -preset fast -global_quality 22 output.mp4

# H.265 with QSV
ffmpeg -hwaccel qsv -c:v hevc_qsv -i input.mp4 \
  -c:v hevc_qsv -preset medium -global_quality 24 output.mp4
```

## AMD VCE/VCN

Hardware encoding on AMD GPUs.

```bash
# H.264 with AMF
ffmpeg -hwaccel auto -i input.mp4 \
  -c:v h264_amf -quality balanced -rc cqp -qp 22 output.mp4

# H.265 with AMF
ffmpeg -hwaccel auto -i input.mp4 \
  -c:v hevc_amf -quality quality -rc cqp -qp 24 output.mp4
```

## Apple VideoToolbox (macOS)

```bash
ffmpeg -i input.mp4 -c:v h264_videotoolbox -b:v 2M output.mp4
ffmpeg -i input.mp4 -c:v hevc_videotoolbox -b:v 1.5M output.mp4
```

## GPU Filters (NVIDIA CUDA)

```bash
# Hardware scale + encode
ffmpeg -hwaccel cuda -i input.mp4 \
  -vf scale_cuda=1280:720 \
  -c:v h264_nvenc output.mp4

# Multiple GPU filters
ffmpeg -hwaccel cuda -i input.mp4 \
  -vf "scale_cuda=1280:720,hwdownload,format=nv12" \
  -c:v h264_nvenc output.mp4
```

## When to Use Hardware Acceleration

- Real-time streaming where encoding speed is critical
- Batch processing large volumes of video
- Live streaming (RTMP, HLS) where CPU can't keep up
- Preview generation when quality is not paramount

## Checking Available Encoders

```bash
# List hardware encoders
ffmpeg -encoders | grep nvenc
ffmpeg -encoders | grep qsv
ffmpeg -encoders | grep amf
ffmpeg -encoders | grep videotoolbox
```
