# ImageMagick Editing: Effects & Adjustments

Blur, sharpen, color effects, artistic filters, borders, text, and composition.

## Blur & Sharpen

```bash
# Blur
magick input.jpg -blur 0x8 output.jpg
magick input.jpg -gaussian-blur 5x3 output.jpg
magick input.jpg -motion-blur 0x20+45 output.jpg
magick input.jpg -radial-blur 10 output.jpg

# Sharpen
magick input.jpg -sharpen 0x1 output.jpg
magick input.jpg -unsharp 0x1 output.jpg
```

## Color Effects

```bash
magick input.jpg -colorspace Gray output.jpg       # Grayscale
magick input.jpg -sepia-tone 80% output.jpg        # Sepia
magick input.jpg -negate output.jpg                # Invert
magick input.jpg -posterize 8 output.jpg           # Reduce colors
```

## Artistic Filters

```bash
magick input.jpg -edge 3 output.jpg         # Edge detection
magick input.jpg -emboss 2 output.jpg       # Emboss
magick input.jpg -paint 4 output.jpg        # Oil painting
magick input.jpg -charcoal 2 output.jpg     # Charcoal drawing
magick input.jpg -sketch 0x20+120 output.jpg # Sketch
magick input.jpg -swirl 90 output.jpg       # Swirl
```

## Adjustments

```bash
# Brightness/contrast
magick input.jpg -brightness-contrast 10x20 output.jpg

# Saturation, hue (format: brightness,saturation,hue)
magick input.jpg -modulate 100,150,100 output.jpg    # More saturation
magick input.jpg -modulate 105,120,100 output.jpg    # Brighter + saturated

# Auto corrections
magick input.jpg -auto-level output.jpg   # Normalize contrast
magick input.jpg -auto-gamma output.jpg   # Auto gamma
magick input.jpg -normalize output.jpg    # Stretch histogram
```

## Borders & Frames

```bash
magick input.jpg -border 10x10 output.jpg
magick input.jpg -bordercolor red -border 10x10 output.jpg

# Raised frame
magick input.jpg -mattecolor gray -frame 10x10+5+5 output.jpg

# Shadow effect
magick input.jpg \
  \( +clone -background black -shadow 80x3+5+5 \) \
  +swap -background white -layers merge +repage output.jpg

# Vignette
magick input.jpg -vignette 0x20 output.jpg
```

## Text Annotations

```bash
# Simple text overlay
magick input.jpg -pointsize 30 -fill white -annotate +10+30 "Hello" output.jpg

# Positioned text
magick input.jpg -gravity south -pointsize 20 -fill white \
  -annotate +0+10 "Caption" output.jpg

# Semi-transparent watermark
magick input.jpg \
  \( -background none -fill "rgba(255,255,255,0.5)" \
  -pointsize 50 label:"DRAFT" \) \
  -gravity center -compose over -composite output.jpg

# Custom font with stroke
magick input.jpg -gravity center \
  -stroke black -strokewidth 2 -fill white \
  -pointsize 60 -annotate +0+0 "Title" output.jpg
```

## Composition & Overlay

```bash
magick input.jpg watermark.png -gravity southeast \
  -geometry +10+10 -composite output.jpg

# Composite modes
magick input.jpg texture.png -compose multiply -composite output.jpg
magick input.jpg light.png -compose screen -composite output.jpg

# Side by side
magick image1.jpg image2.jpg +append output.jpg   # Horizontal
magick image1.jpg image2.jpg -append output.jpg   # Vertical
```

## Transparency

```bash
magick input.jpg -transparent white output.png
magick input.jpg -fuzz 10% -transparent white output.png

# Remove transparency
magick input.png -background white -flatten output.jpg
```

## Color Management

```bash
magick input.jpg -strip output.jpg                # Strip profile
magick input.jpg -colorspace sRGB output.jpg      # Convert to sRGB
magick input.jpg -colorspace CMYK output.tif      # Convert to CMYK (print)
```

## Memory Management

```bash
magick -limit memory 2GB -limit map 4GB input.jpg -resize 50% output.jpg
magick -limit thread 4 input.jpg -resize 50% output.jpg
```
