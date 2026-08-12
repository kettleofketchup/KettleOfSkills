# FFmpeg Audio Filters & Complex Filtergraphs

Audio processing, mixing, and advanced filtergraph patterns.

## Audio Filters

### Volume
```bash
ffmpeg -i input.mp4 -af volume=10dB output.mp4    # Increase by 10dB
ffmpeg -i input.mp4 -af volume=0.5 output.mp4    # Decrease to 50%
```

### Normalize (EBU R128)
```bash
ffmpeg -i input.mp4 -af loudnorm output.mp4
ffmpeg -i input.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 output.mp4

# Two-pass normalization
ffmpeg -i input.mp4 -af loudnorm=print_format=json -f null -
ffmpeg -i input.mp4 -af loudnorm=measured_I=-23:measured_LRA=7:measured_TP=-2:measured_thresh=-33 output.mp4
```

### Equalizer
```bash
ffmpeg -i input.mp4 -af equalizer=f=100:width_type=h:width=200:g=10 output.mp4   # Bass boost
ffmpeg -i input.mp4 -af "equalizer=f=100:g=5,equalizer=f=1000:g=-3" output.mp4  # Multi-band
```

### Compressor
```bash
ffmpeg -i input.mp4 -af acompressor output.mp4
ffmpeg -i input.mp4 -af acompressor=threshold=-20dB:ratio=4:attack=200:release=1000 output.mp4
```

### Noise Reduction
```bash
ffmpeg -i input.mp4 -af highpass=f=200 output.mp4               # High-pass
ffmpeg -i input.mp4 -af lowpass=f=3000 output.mp4               # Low-pass
ffmpeg -i input.mp4 -af "highpass=f=200,lowpass=f=3000" output.mp4  # Band-pass
```

### Fade Audio
```bash
ffmpeg -i input.mp4 -af afade=t=in:st=0:d=2 output.mp4
ffmpeg -i input.mp4 -af afade=t=out:st=27:d=3 output.mp4
ffmpeg -i input.mp4 -af "afade=t=in:st=0:d=2,afade=t=out:st=27:d=3" output.mp4
```

### Audio Mixing
```bash
ffmpeg -i audio1.mp3 -i audio2.mp3 \
  -filter_complex amix=inputs=2:duration=longest output.mp3

ffmpeg -i audio1.mp3 -i audio2.mp3 \
  -filter_complex "[0:a]volume=0.8[a1];[1:a]volume=0.5[a2];[a1][a2]amix=inputs=2" output.mp3
```

## Complex Filtergraphs

### Multiple Outputs
```bash
ffmpeg -i input.mp4 \
  -filter_complex "[0:v]split=3[v1][v2][v3]; \
    [v1]scale=1920:1080[out1]; \
    [v2]scale=1280:720[out2]; \
    [v3]scale=640:360[out3]" \
  -map "[out1]" -c:v libx264 -crf 22 output_1080p.mp4 \
  -map "[out2]" -c:v libx264 -crf 23 output_720p.mp4 \
  -map "[out3]" -c:v libx264 -crf 24 output_360p.mp4 \
  -map 0:a -c:a copy
```

### Picture-in-Picture
```bash
ffmpeg -i main.mp4 -i small.mp4 \
  -filter_complex "[1:v]scale=320:180[pip]; \
    [0:v][pip]overlay=W-w-10:H-h-10" output.mp4
```

### Side-by-Side Comparison
```bash
ffmpeg -i left.mp4 -i right.mp4 -filter_complex "[0:v][1:v]hstack=inputs=2" output.mp4
ffmpeg -i top.mp4 -i bottom.mp4 -filter_complex "[0:v][1:v]vstack=inputs=2" output.mp4
```

### Crossfade Transition
```bash
ffmpeg -i video1.mp4 -i video2.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=2:offset=8" output.mp4
```

Transition types: `fade`, `wipeleft`, `wiperight`, `wipeup`, `wipedown`, `slideleft`, `slideright`, `circlecrop`, `fadeblack`, `fadewhite`, `radial`

### Color Correction Pipeline
```bash
ffmpeg -i input.mp4 \
  -filter_complex "[0:v]eq=contrast=1.1:brightness=0.05:saturation=1.2[v1]; \
    [v1]curves=vintage[v2]; \
    [v2]vignette[v3]; \
    [v3]unsharp=5:5:1.0[out]" \
  -map "[out]" -c:v libx264 -crf 18 output.mp4
```

## Common Recipes

### YouTube Optimized
```bash
ffmpeg -i input.mp4 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k output.mp4
```

### Instagram Portrait
```bash
ffmpeg -i input.mp4 \
  -vf "scale=1080:1350:force_original_aspect_ratio=decrease,pad=1080:1350:(ow-iw)/2:(oh-ih)/2:color=white" \
  -c:v libx264 -preset fast -crf 23 -c:a aac output.mp4
```

### Vintage Film Look
```bash
ffmpeg -i input.mp4 \
  -vf "curves=vintage,vignette=angle=PI/4,eq=saturation=0.8,noise=alls=10:allf=t" \
  -c:v libx264 -crf 20 output.mp4
```

## Filter Performance

Scale first to reduce pixels in subsequent filters:
```bash
# Good: scale first
ffmpeg -i input.mp4 -vf "scale=1280:720,hqdn3d,unsharp=5:5:1.0" output.mp4
```
