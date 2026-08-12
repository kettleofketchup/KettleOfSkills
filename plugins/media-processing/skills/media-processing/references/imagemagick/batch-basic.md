# ImageMagick Batch Processing: Basic

Mogrify command, resize, format conversion, and optimization.

## Mogrify Command

`mogrify` modifies files in-place. Use `-path` to preserve originals.

```bash
# Resize all JPEGs (overwrites in-place)
mogrify -resize 800x600 *.jpg

# Output to separate directory (safe)
mkdir output
mogrify -path ./output -resize 800x600 *.jpg

# Format conversion with output directory
mogrify -path ./webp -format webp -quality 80 *.png
```

## Resize Batch Operations

```bash
mogrify -resize 800x *.jpg          # Width 800
mogrify -resize x600 *.jpg          # Height 600
mogrify -resize 800x600 *.jpg       # Fit within 800x600
mogrify -resize 800x600! *.jpg      # Force exact size
mogrify -resize 800x600\> *.jpg     # Shrink only (never enlarge)
```

## Format Conversion

```bash
mogrify -path ./jpg -format jpg -quality 85 *.png
mogrify -path ./webp -format webp -quality 80 *.jpg
mogrify -path ./png -format png *.{jpg,gif,bmp}
```

## Image Optimization

```bash
mogrify -strip *.jpg                                              # Strip metadata
mogrify -quality 85 -strip -interlace Plane *.jpg                # Web optimize
mogrify -quality 85 -strip -interlace Plane -sampling-factor 4:2:0 *.jpg  # Full opt
```

## Thumbnail Batch

```bash
mogrify -path ./thumbnails -resize 200x200^ -gravity center -extent 200x200 *.jpg
mogrify -path ./thumbs -thumbnail 300x300 -quality 80 -strip *.jpg
```

## Apply Effects

```bash
mogrify -colorspace Gray *.jpg             # Grayscale all
mogrify -sepia-tone 80% *.jpg              # Sepia all
mogrify -sharpen 0x1 *.jpg                 # Sharpen all
```

## Shell Loops for Custom Naming

```bash
# Resize with custom naming
for img in *.jpg; do
  magick "$img" -resize 800x600 "resized_$img"
done

# Complex pipeline
for img in *.jpg; do
  magick "$img" \
    -resize 1920x1080^ -gravity center \
    -crop 1920x1080+0+0 +repage \
    -unsharp 0x1 -quality 85 -strip \
    "processed_$img"
done

# Format conversion with rename
for img in *.png; do
  magick "$img" -quality 90 "${img%.png}.jpg"
done
```

## Conditional Processing

```bash
# Only process images wider than 2000px
for img in *.jpg; do
  width=$(identify -format "%w" "$img")
  if [ $width -gt 2000 ]; then
    magick "$img" -resize 2000x "resized_$img"
  fi
done

# Skip existing output files
for img in *.jpg; do
  output="output_$img"
  [ ! -f "$output" ] && magick "$img" -resize 800x "$output"
done
```

## Responsive Image Set

```bash
for size in 320 640 1024 1920; do
  mkdir -p "output/${size}w"
  for img in *.jpg; do
    magick "$img" -resize ${size}x -quality 85 "output/${size}w/$img"
  done
done
```

## Error Handling

```bash
# Verify image before processing
for img in *.jpg; do
  if identify "$img" > /dev/null 2>&1; then
    magick "$img" -resize 800x "processed_$img"
  else
    echo "Skipping corrupt: $img"
  fi
done
```
