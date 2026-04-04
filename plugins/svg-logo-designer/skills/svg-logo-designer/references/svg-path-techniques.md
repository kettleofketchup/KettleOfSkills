# SVG Path Techniques for Logos

## Path Command Reference

| Cmd | Name | Params | Logo Use |
|-----|------|--------|----------|
| `M/m` | Move To | `x y` | Start of every subpath |
| `L/l` | Line To | `x y` | Straight edges, angular shapes |
| `H/h` | Horizontal | `x` | Horizontal edges (compact) |
| `V/v` | Vertical | `y` | Vertical edges (compact) |
| `C/c` | Cubic Bezier | `x1 y1, x2 y2, x y` | Smooth curves, most common for logos |
| `S/s` | Smooth Cubic | `x2 y2, x y` | Continuing smooth curves (reflects prev control point) |
| `Q/q` | Quadratic | `x1 y1, x y` | Simpler curves, single control point |
| `T/t` | Smooth Quad | `x y` | Continuing quadratic curves |
| `A/a` | Arc | `rx ry rot large sweep x y` | Circles, arcs, rounded corners |
| `Z/z` | Close | none | Close shape to start |

Uppercase = absolute coords; lowercase = relative.

## Cubic Bezier (C) -- The Workhorse

First control point determines departure angle. Second determines arrival angle.

```xml
<!-- Smooth S-curve -->
<path d="M 10 80 C 40 10, 65 10, 95 80"/>

<!-- S-curve chain with smooth continuation -->
<path d="M 10 80 C 40 10, 65 10, 95 80 S 150 150, 180 80"/>
```

For professional curves, place control points symmetrically or at golden ratio proportions.

## Arc Command (A)

```xml
<!-- Arc: rx ry x-rotation large-arc-flag sweep-flag x y -->
<path d="M 10 50 A 40 40 0 1 1 90 50" fill="blue"/>

<!-- Rounded rectangle with arc corners -->
<path d="M 20 10 H 80 A 10 10 0 0 1 90 20 V 80 A 10 10 0 0 1 80 90
         H 20 A 10 10 0 0 1 10 80 V 20 A 10 10 0 0 1 20 10 Z"/>
```

Arc flag combinations:
- `large=0, sweep=0` -- small arc, counterclockwise
- `large=0, sweep=1` -- small arc, clockwise
- `large=1, sweep=0` -- large arc, counterclockwise
- `large=1, sweep=1` -- large arc, clockwise

## Professional Shape Patterns

### Shield

```xml
<path d="M 50 10 L 90 30 L 90 60 Q 90 90 50 100 Q 10 90 10 60 L 10 30 Z"/>
```

### Leaf / Organic

```xml
<path d="M 50 10 C 80 10, 95 40, 90 70 C 85 90, 60 95, 50 90
         C 40 95, 15 90, 10 70 C 5 40, 20 10, 50 10 Z"/>
```

### Infinity Symbol

```xml
<path d="M 50 50 C 50 20, 90 20, 90 50 C 90 80, 50 80, 50 50
         C 50 20, 10 20, 10 50 C 10 80, 50 80, 50 50 Z"/>
```

### Checkmark

```xml
<path d="M 30 55 L 45 70 L 75 35" stroke="#FFF" stroke-width="4"
      fill="none" stroke-linecap="round" stroke-linejoin="round"/>
```

### Arrow / Chevron

```xml
<path d="M 25 20 L 75 50 L 25 80" stroke="#333" stroke-width="4"
      fill="none" stroke-linecap="round" stroke-linejoin="round"/>
```

### Star (5-point)

```xml
<polygon points="50,5 61,35 95,35 68,57 79,91 50,70 21,91 32,57 5,35 39,35"/>
```

### Hexagon

```xml
<polygon points="50,5 95,27.5 95,72.5 50,95 5,72.5 5,27.5"/>
```

## Tips

- Use relative commands (`c`, `s`, `q`) for symmetric/repeating patterns -- easier to mirror
- Use absolute (`C`, `S`, `Q`) when precision positioning matters
- Combine basic shapes with path clips for complex effects
- Round coordinates to integers for even-width strokes; use `.5` offset for odd-width
