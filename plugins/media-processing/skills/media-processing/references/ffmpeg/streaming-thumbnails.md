# FFmpeg Thumbnails & Preview Generation

Extract frames, generate thumbnail sets, and create previews.

## Single Thumbnail

```bash
# At specific time
ffmpeg -ss 00:00:05 -i input.mp4 -vframes 1 -vf scale=320:-1 thumb.jpg

# At 10% of duration
ffmpeg -ss $(ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 input.mp4 | \
  awk '{print $1*0.1}') -i input.mp4 -vframes 1 thumb.jpg
```

## Multiple Thumbnails

```bash
# One per minute
ffmpeg -i input.mp4 -vf fps=1/60,scale=320:-1 thumb_%03d.jpg

# One per 10 seconds
ffmpeg -i input.mp4 -vf fps=1/10,scale=320:-1 thumb_%03d.jpg

# First 10 frames
ffmpeg -i input.mp4 -vframes 10 -vf scale=320:-1 thumb_%02d.jpg
```

## Thumbnail Sprite Sheet

Combine many thumbnails into a single image for seeking previews.

```bash
# Generate frames
ffmpeg -i input.mp4 -vf fps=1/10,scale=160:90 frames/thumb_%03d.jpg

# Combine into sprite (requires ImageMagick)
montage frames/thumb_*.jpg -tile 5x -geometry +0+0 sprite.jpg
```

## Video Preview (Trailer)

Extract multiple segments and concatenate.

```bash
ffmpeg -i input.mp4 -ss 00:00:30 -t 00:00:10 -c copy segment1.mp4
ffmpeg -i input.mp4 -ss 00:05:00 -t 00:00:10 -c copy segment2.mp4
ffmpeg -i input.mp4 -ss 00:10:00 -t 00:00:10 -c copy segment3.mp4

echo "file 'segment1.mp4'" > concat.txt
echo "file 'segment2.mp4'" >> concat.txt
echo "file 'segment3.mp4'" >> concat.txt
ffmpeg -f concat -safe 0 -i concat.txt -c copy preview.mp4
```

## Fast Preview (Low Quality)

Quick proxy for review.

```bash
ffmpeg -i input.mp4 \
  -vf scale=640:-1 \
  -c:v libx264 -preset ultrafast -crf 28 \
  -c:a aac -b:a 64k \
  preview.mp4
```

## Inspect Video Properties

```bash
# Detailed JSON output
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# Get resolution
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height \
  -of csv=s=x:p=0 input.mp4

# Get duration
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 input.mp4
```
