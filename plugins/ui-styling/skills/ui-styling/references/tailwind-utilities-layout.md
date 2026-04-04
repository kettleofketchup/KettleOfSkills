# Tailwind CSS: Layout, Spacing & Sizing

## Display

```html
<div class="block | inline-block | inline | flex | inline-flex | grid | hidden">
```

## Flexbox

**Direction:** `flex-row | flex-col | flex-row-reverse | flex-col-reverse`
**Justify (main):** `justify-start | justify-center | justify-end | justify-between | justify-around | justify-evenly`
**Align (cross):** `items-start | items-center | items-end | items-baseline | items-stretch`
**Gap:** `gap-4 | gap-x-6 gap-y-2`
**Wrap:** `flex-wrap | flex-nowrap`

## Grid

**Columns:** `grid-cols-1 | grid-cols-2 | grid-cols-3 | grid-cols-12 | grid-cols-[1fr_500px_2fr]`
**Rows:** `grid-rows-3 | grid-rows-[auto_1fr_auto]`
**Span:** `col-span-2 | row-span-3`
**Gap:** `gap-4 | gap-x-8 gap-y-4`

## Positioning

```html
<div class="static | relative | absolute | fixed | sticky">
<div class="absolute top-0 right-0">
<div class="absolute inset-0">      <!-- All sides 0 -->
<div class="absolute inset-x-4">    <!-- Left/right -->
```

**Z-Index:** `z-0 | z-10 | z-20 | z-50`

## Spacing

### Padding
```html
<div class="p-4">    <!-- All sides -->
<div class="px-6">   <!-- Left and right -->
<div class="py-3">   <!-- Top and bottom -->
<div class="pt-8">   <!-- Top only -->
```

### Margin
```html
<div class="m-4">       <!-- All sides -->
<div class="mx-auto">   <!-- Center horizontally -->
<div class="mt-8">      <!-- Top -->
<div class="-mt-4">     <!-- Negative top -->
<div class="ml-auto">   <!-- Push to right -->
```

**Space Between:** `space-x-4 | space-y-6`

### Spacing Scale
| Value | Size |
|-------|------|
| `0` | 0px |
| `px` | 1px |
| `1` | 0.25rem (4px) |
| `2` | 0.5rem (8px) |
| `4` | 1rem (16px) |
| `6` | 1.5rem (24px) |
| `8` | 2rem (32px) |
| `12` | 3rem (48px) |
| `16` | 4rem (64px) |
| `24` | 6rem (96px) |

## Width & Height

### Width
```html
<div class="w-full | w-1/2 | w-1/3 | w-64 | w-[500px] | w-screen">
<div class="min-w-0 | max-w-md | max-w-screen-xl">
```

### Height
```html
<div class="h-full | h-screen | h-64 | h-[500px]">
<div class="min-h-screen | max-h-96">
```

### Aspect Ratio
```html
<div class="aspect-square | aspect-video | aspect-[4/3]">
```

## Overflow

```html
<div class="overflow-auto | overflow-hidden | overflow-scroll">
<div class="overflow-x-auto | overflow-y-hidden">
```

## Arbitrary Values

```html
<div class="p-[17px]">          <!-- Custom spacing -->
<div class="top-[117px]">      <!-- Custom position -->
<div class="w-[500px]">        <!-- Custom width -->
<div class="bg-[var(--brand)]"> <!-- CSS var -->
<div class="grid-cols-[1fr_500px_2fr]"> <!-- Custom grid -->
```
