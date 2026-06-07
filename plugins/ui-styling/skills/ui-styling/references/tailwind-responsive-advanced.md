# Tailwind CSS: Responsive Design Advanced

Custom breakpoints, state variants, responsive utilities reference, and best practices.

## Custom Breakpoints

```css
@theme {
  --breakpoint-3xl: 120rem;  /* 1920px */
  --breakpoint-tablet: 48rem;  /* 768px */
}
```

```html
<div class="tablet:grid-cols-2 3xl:grid-cols-6">
  Uses custom breakpoints
</div>
```

## Responsive State Variants

Combine responsive with hover/focus:

```html
<!-- Hover effect only on desktop -->
<button class="lg:hover:scale-105">Scale on hover (desktop only)</button>

<!-- Different hover colors per breakpoint -->
<a class="hover:text-blue-600 lg:hover:text-purple-600">Link</a>
```

## Common Responsive Utilities

### Responsive Display

```html
<div class="block md:flex lg:grid">Changes display type per breakpoint</div>
```

### Responsive Position

```html
<div class="relative lg:absolute">Positioned differently per breakpoint</div>
```

### Responsive Order

```html
<div class="flex flex-col">
  <div class="order-2 lg:order-1">First on desktop</div>
  <div class="order-1 lg:order-2">First on mobile</div>
</div>
```

### Responsive Overflow

```html
<div class="overflow-auto lg:overflow-visible">
  Scrollable on mobile, expanded on desktop
</div>
```

## Best Practices

### 1. Mobile-First Design

Start with mobile styles, add complexity at larger breakpoints:

```html
<!-- Good: Mobile first -->
<div class="text-base md:text-lg lg:text-xl">

<!-- Avoid: Desktop first -->
<div class="text-xl lg:text-base">
```

### 2. Consistent Breakpoint Usage

Use same breakpoints across related elements:

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 lg:gap-8">
  Spacing scales with layout
</div>
```

### 3. Use Container for Content Width

```html
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl">Content with consistent max width</div>
</div>
```

### 4. Progressive Enhancement

```html
<!-- Core layout works on mobile, enhanced for desktop -->
<div class="p-4 lg:p-8">
  <div class="text-base lg:text-lg">Content</div>
</div>
```

### 5. Avoid Too Many Breakpoints

```html
<!-- Good: 2-3 breakpoints -->
<div class="grid-cols-1 md:grid-cols-2 lg:grid-cols-4">

<!-- Avoid: Too many breakpoints -->
<div class="grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6">
```

### 6. Test at Breakpoint Boundaries

Test at exact breakpoint widths (640px, 768px, 1024px) to catch edge cases.

## Responsive Typography Scale

```html
<!-- Hero text -->
<h1 class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold">

<!-- Section heading -->
<h2 class="text-2xl md:text-3xl lg:text-4xl font-semibold">

<!-- Body text -->
<p class="text-sm md:text-base lg:text-lg leading-relaxed">

<!-- Caption / label -->
<span class="text-xs md:text-sm text-muted-foreground">
```

## Responsive Spacing Scale

```html
<!-- Section padding -->
<section class="py-8 md:py-12 lg:py-16 xl:py-24">

<!-- Container padding -->
<div class="px-4 sm:px-6 lg:px-8">

<!-- Card padding -->
<div class="p-4 md:p-6 lg:p-8">

<!-- Gap between elements -->
<div class="gap-4 md:gap-6 lg:gap-8">
```
