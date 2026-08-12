# FFmpeg Video Filters

Scale, crop, rotate, overlay, denoise, speed, color, and more.

## Filter Basics

```bash
# Single filter
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4

# Chain filters
ffmpeg -i input.mp4 -vf "scale=1280:720,hqdn3d" output.mp4

# Complex filtergraph
ffmpeg -i input.mp4 -i logo.png \
  -filter_complex "[0:v][1:v]overlay=10:10" output.mp4
```

## Scale (Resize)

```bash
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4
ffmpeg -i input.mp4 -vf scale=1280:-1 output.mp4          # Auto height
ffmpeg -i input.mp4 -vf scale=-1:720 output.mp4           # Auto width
ffmpeg -i input.mp4 -vf scale=iw/2:ih/2 output.mp4        # Half size
ffmpeg -i input.mp4 -vf scale=1280:-1:flags=lanczos output.mp4  # Best quality
```

## Crop
```bash
ffmpeg -i input.mp4 -vf crop=1280:720:0:0 output.mp4
ffmpeg -i input.mp4 -vf crop=1280:720:(iw-1280)/2:(ih-720)/2 output.mp4
ffmpeg -i input.mp4 -vf cropdetect -f null -   # Auto-detect borders
```

## Rotate & Flip
```bash
ffmpeg -i input.mp4 -vf transpose=1 output.mp4   # 90° clockwise
ffmpeg -i input.mp4 -vf transpose=2 output.mp4   # 90° counter-clockwise
ffmpeg -i input.mp4 -vf hflip output.mp4          # Flip horizontal
ffmpeg -i input.mp4 -vf vflip output.mp4          # Flip vertical
ffmpeg -i input.mp4 -vf rotate=45*PI/180 output.mp4  # Arbitrary angle
```

## Overlay (Watermark)
```bash
ffmpeg -i video.mp4 -i logo.png -filter_complex overlay=10:10 output.mp4
ffmpeg -i video.mp4 -i logo.png -filter_complex "overlay=W-w-10:10" output.mp4
ffmpeg -i video.mp4 -i logo.png -filter_complex "overlay=W-w-10:H-h-10" output.mp4
ffmpeg -i video.mp4 -i logo.png -filter_complex "overlay=(W-w)/2:(H-h)/2" output.mp4
```

## Denoise & Deinterlace
```bash
ffmpeg -i input.mp4 -vf hqdn3d output.mp4           # Fast denoise
ffmpeg -i input.mp4 -vf hqdn3d=4:3:6:4.5 output.mp4 # Stronger
ffmpeg -i input.mp4 -vf nlmeans output.mp4           # Best quality (slow)
ffmpeg -i input.mp4 -vf yadif output.mp4             # Deinterlace
ffmpeg -i input.mp4 -vf bwdif output.mp4             # Better deinterlace
```

## Speed & Slow Motion
```bash
ffmpeg -i input.mp4 -vf setpts=0.5*PTS -af atempo=2.0 output.mp4   # 2x speed
ffmpeg -i input.mp4 -vf setpts=2.0*PTS -af atempo=0.5 output.mp4   # 0.5x speed
```

## Pad (Add Borders)
```bash
ffmpeg -i input.mp4 -vf "pad=1920:1080:(ow-iw)/2:(oh-ih)/2" output.mp4
ffmpeg -i input.mp4 -vf "scale=1080:-1,pad=1080:1080:(ow-iw)/2:(oh-ih)/2:color=black" output.mp4
```

## Sharpen & Blur
```bash
ffmpeg -i input.mp4 -vf unsharp=5:5:1.0 output.mp4   # Sharpen
ffmpeg -i input.mp4 -vf gblur=sigma=8 output.mp4     # Gaussian blur
ffmpeg -i input.mp4 -vf boxblur=5:1 output.mp4       # Box blur
```

## Color Adjustments
```bash
ffmpeg -i input.mp4 -vf eq=brightness=0.1 output.mp4
ffmpeg -i input.mp4 -vf eq=contrast=1.2 output.mp4
ffmpeg -i input.mp4 -vf eq=saturation=1.5 output.mp4
ffmpeg -i input.mp4 -vf eq=brightness=0.05:contrast=1.1:saturation=1.2 output.mp4
ffmpeg -i input.mp4 -vf curves=vintage output.mp4
ffmpeg -i input.mp4 -vf hue=h=90 output.mp4
```

## Grayscale & Effects
```bash
ffmpeg -i input.mp4 -vf hue=s=0 output.mp4                        # Grayscale
ffmpeg -i input.mp4 -vf colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131 output.mp4  # Sepia
ffmpeg -i input.mp4 -vf negate output.mp4                         # Negative
ffmpeg -i input.mp4 -vf vignette output.mp4
```

## Fade In/Out
```bash
ffmpeg -i input.mp4 -vf fade=in:0:60 output.mp4
ffmpeg -i input.mp4 -vf fade=out:st=28:d=2 output.mp4
ffmpeg -i input.mp4 -vf "fade=in:0:30,fade=out:st=28:d=2" output.mp4
```

## Stabilization
```bash
# Two-pass: detect motion, then stabilize
ffmpeg -i input.mp4 -vf vidstabdetect=shakiness=10:accuracy=15 -f null -
ffmpeg -i input.mp4 -vf vidstabtransform=smoothing=30:input="transforms.trf" output.mp4
```

## Text Overlay
```bash
ffmpeg -i input.mp4 -vf "drawtext=text='Hello World':fontsize=24:x=10:y=10" output.mp4
ffmpeg -i input.mp4 -vf "drawtext=text='%{pts\:hms}':fontsize=20:x=10:y=10:fontcolor=white" output.mp4
```
