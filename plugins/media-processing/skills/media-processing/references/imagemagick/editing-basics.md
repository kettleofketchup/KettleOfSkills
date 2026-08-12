# ImageMagick Editing: Basics

Format conversion, resizing, cropping, and thumbnails.

## Format Conversion

```bash
magick input.png output.jpg
magick input.jpg output.webp
magick input.png output.jpg output.webp output.gif   # Multiple outputs
magick input.png -quality 85 output.jpg
```

**JPEG Quality:**
- 95-100: Archival, minimal compression
- 85-94: High quality, web publishing (recommended)
- 75-84: Medium quality, web optimized
- Below 60: Visible artifacts

```bash
# Web optimized
magick input.png -quality 85 -strip output.jpg

# Progressive JPEG (better web loading)
magick input.png -quality 85 -interlace Plane output.jpg

# WebP lossless
magick input.png -define webp:lossless=true output.webp
```

## Resizing

```bash
magick input.jpg -resize 800x600 output.jpg    # Fit within (aspect preserved)
magick input.jpg -resize 800x output.jpg       # Width only
magick input.jpg -resize x600 output.jpg       # Height only
magick input.jpg -resize 50% output.jpg        # Percentage

# Modifiers
magick input.jpg -resize 800x600\> output.jpg  # Shrink only
magick input.jpg -resize 800x600\< output.jpg  # Enlarge only
magick input.jpg -resize 800x600! output.jpg   # Force exact (ignore aspect)
magick input.jpg -resize 800x600^ output.jpg   # Fill (may crop)
```

**Resize algorithms:**
- `-filter Lanczos` — Highest quality, slower
- `-filter Mitchell` — Good quality, fast
- `-filter Box` — Fastest, acceptable quality

## Cropping

```bash
# Crop width×height+x+y
magick input.jpg -crop 400x400+100+100 +repage output.jpg

# From center
magick input.jpg -gravity center -crop 400x400+0+0 output.jpg

# Aspect ratio
magick input.jpg -gravity center -crop 16:9 +repage output.jpg

# Auto-trim same-color borders
magick input.png -trim +repage output.png
magick input.jpg -fuzz 10% -trim +repage output.jpg
```

## Thumbnails

```bash
# Square thumbnail (resize and crop)
magick input.jpg -resize 200x200^ -gravity center -extent 200x200 thumb.jpg

# With background (no crop)
magick input.jpg -resize 200x200 -background white -gravity center -extent 200x200 thumb.jpg

# Circular avatar (PNG)
magick input.jpg -resize 200x200^ -gravity center -extent 200x200 \
  \( +clone -threshold -1 -negate -fill white -draw "circle 100,100 100,0" \) \
  -alpha off -compose copy_opacity -composite avatar.png
```

## Rotation & Flip

```bash
magick input.jpg -rotate 90 output.jpg
magick input.jpg -rotate 180 output.jpg
magick input.jpg -rotate -90 output.jpg
magick input.jpg -background white -rotate 45 output.jpg
magick input.jpg -auto-orient output.jpg   # EXIF auto-orient

magick input.jpg -flip output.jpg   # Flip vertical
magick input.jpg -flop output.jpg   # Flip horizontal (mirror)
```

## Image Information

```bash
identify image.jpg              # Basic info
identify -verbose image.jpg     # Detailed info
identify -format "%f: %wx%h %b\n" image.jpg  # Custom format
```
