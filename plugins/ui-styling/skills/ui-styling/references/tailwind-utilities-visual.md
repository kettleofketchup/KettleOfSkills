# Tailwind CSS: Typography, Colors & Visual

## Typography

**Font Size:** `text-xs(12) | text-sm(14) | text-base(16) | text-lg(18) | text-xl(20) | text-2xl(24) | text-3xl(30) | text-4xl(36) | text-5xl(48)`
**Font Weight:** `font-thin(100) | font-light(300) | font-normal(400) | font-medium(500) | font-semibold(600) | font-bold(700) | font-black(900)`
**Alignment:** `text-left | text-center | text-right | text-justify`
**Line Height:** `leading-none(1) | leading-tight(1.25) | leading-normal(1.5) | leading-relaxed(1.75) | leading-loose(2)`
**Combined:** `text-4xl/tight font-bold` (size + line-height shorthand)

**Transform:** `uppercase | lowercase | capitalize | normal-case`
**Decoration:** `underline | line-through | no-underline`
**Overflow:** `truncate | line-clamp-3 | text-ellipsis overflow-hidden`

## Colors

### Text & Background
```html
<p class="text-black | text-white | text-gray-500 | text-red-600 | text-blue-500">
<div class="bg-white | bg-gray-100 | bg-blue-500 | bg-red-600">
```

### Color Scale
Each color has 11 shades: `50` (lightest) through `950` (darkest), with `500` as base.

### Opacity Modifiers
```html
<div class="bg-black/75">     <!-- 75% opacity -->
<div class="text-blue-500/30"> <!-- 30% opacity -->
```

### Gradients
```html
<div class="bg-gradient-to-r from-blue-500 to-purple-600">
<div class="bg-gradient-to-br from-pink-500 via-red-500 to-yellow-500">
```
Directions: `to-t | to-tr | to-r | to-br | to-b | to-bl | to-l | to-tl`

## Borders

**Width:** `border | border-2 | border-t | border-r-4 | border-0`
**Color:** `border-gray-300 | border-blue-500 | border-red-600/50`
**Radius:** `rounded | rounded-md | rounded-lg | rounded-xl | rounded-2xl | rounded-full`
**Corners:** `rounded-t-lg | rounded-br-xl`
**Style:** `border-solid | border-dashed | border-dotted`

## Shadows

```html
<div class="shadow-sm | shadow | shadow-md | shadow-lg | shadow-xl | shadow-2xl | shadow-none">
<div class="shadow-lg shadow-blue-500/50"> <!-- Colored shadow -->
```

## Effects

**Opacity:** `opacity-0 | opacity-50 | opacity-75 | opacity-100`
**Cursor:** `cursor-pointer | cursor-wait | cursor-not-allowed | cursor-default`
**User Select:** `select-none | select-text | select-all`

## Arbitrary Values
```html
<div class="bg-[#bada55]">       <!-- Hex color -->
<div class="text-[rgb(123,45,67)]"> <!-- RGB -->
<div class="text-[22px]">        <!-- Custom font size -->
```
