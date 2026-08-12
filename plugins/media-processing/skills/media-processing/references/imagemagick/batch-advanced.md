# ImageMagick Batch Processing: Parallel & Automation

GNU Parallel, Python scripts, watermarks, and web workflows.

## Parallel Processing

### GNU Parallel
```bash
# Basic parallel resize
parallel magick {} -resize 800x600 resized_{} ::: *.jpg

# With exported function
resize_image() {
  magick "$1" -resize 1920x1080 -quality 85 "processed_$1"
}
export -f resize_image
parallel resize_image ::: *.jpg

# Limit concurrent jobs with progress
parallel -j 4 --progress magick {} -resize 800x {} ::: *.jpg
```

### Xargs Parallel
```bash
ls *.jpg | xargs -I {} -P 4 magick {} -resize 800x processed_{}
find . -name "*.jpg" -print0 | xargs -0 -I {} -P 4 magick {} -resize 800x {}
```

### Performance: Loop vs Mogrify

```bash
# Bad: separate mogrify per file
for img in *.jpg; do mogrify -resize 800x "$img"; done

# Good: single mogrify call
mogrify -resize 800x *.jpg

# Best: parallel for complex ops
parallel magick {} -resize 800x -quality 85 processed_{} ::: *.jpg
```

## Watermark Batch

```bash
for img in *.jpg; do
  magick "$img" watermark.png \
    -gravity southeast -geometry +10+10 \
    -composite "watermarked_$img"
done

# Adaptive watermark placement
for img in *.jpg; do
  width=$(identify -format "%w" "$img")
  height=$(identify -format "%h" "$img")
  if [ $width -gt $height ]; then
    magick "$img" watermark.png -gravity southeast -composite "marked_$img"
  else
    magick "$img" watermark.png -gravity south -composite "marked_$img"
  fi
done
```

## Web Publishing Pipeline

```bash
mkdir -p web/{original,optimized,thumbnails}
cp *.jpg web/original/

mogrify -path web/optimized \
  -resize 1920x1080\> -quality 85 -strip -interlace Plane \
  web/original/*.jpg

mogrify -path web/thumbnails \
  -thumbnail 300x300 -quality 80 -strip \
  web/original/*.jpg
```

## Social Media Sizes

```bash
for img in *.jpg; do
  base="${img%.jpg}"
  magick "$img" -resize 1080x1080^ -gravity center -extent 1080x1080 "${base}_ig_square.jpg"
  magick "$img" -resize 1080x1350^ -gravity center -extent 1080x1350 "${base}_ig_portrait.jpg"
  magick "$img" -resize 1200x630^  -gravity center -extent 1200x630  "${base}_fb_post.jpg"
  magick "$img" -resize 1200x675^  -gravity center -extent 1200x675  "${base}_tw_post.jpg"
done
```

## Archive to Web Conversion

```bash
# High-res archive -> web formats
for img in archives/*.jpg; do
  base=$(basename "$img" .jpg)
  magick "$img" -resize 2048x2048\> -quality 90 -strip "web/${base}.jpg"
  magick "$img" -thumbnail 400x400 -quality 85 "web/${base}_thumb.jpg"
  magick "$img" -resize 2048x2048\> -quality 85 "web/${base}.webp"
done
```

## Python Batch Script

```python
#!/usr/bin/env python3
import subprocess
from pathlib import Path

INPUT_DIR = Path("./input")
OUTPUT_DIR = Path("./output")
SIZES = [320, 640, 1024, 1920]

for size in SIZES:
    (OUTPUT_DIR / f"{size}w").mkdir(parents=True, exist_ok=True)

for img in INPUT_DIR.glob("*.jpg"):
    for size in SIZES:
        output = OUTPUT_DIR / f"{size}w" / img.name
        subprocess.run(["magick", str(img), "-resize", f"{size}x",
                        "-quality", "85", "-strip", str(output)])
        print(f"Processed {img.name} -> {size}w")
```

## Reporting & Logging

```bash
# Log processing results
for img in *.jpg; do
  if magick "$img" -resize 800x "output/$img" 2>/dev/null; then
    echo "$(date): OK $img" >> batch.log
  else
    echo "$(date): FAIL $img" >> errors.log
  fi
done

# Image inventory CSV
echo "Filename,Width,Height,Format,Size" > inventory.csv
for img in *.{jpg,png,gif}; do
  [ -f "$img" ] || continue
  identify -format "%f,%w,%h,%m,%b\n" "$img" >> inventory.csv
done

# Memory limit for large batches
magick -limit memory 2GB -limit map 4GB input.jpg -resize 50% output.jpg
```
