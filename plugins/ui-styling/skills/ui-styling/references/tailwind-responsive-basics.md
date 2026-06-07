# Tailwind CSS: Responsive Design Basics

Mobile-first breakpoints, core responsive utilities, and common layouts.

## Mobile-First Approach

Tailwind uses mobile-first responsive design. Base styles apply to all screen sizes, then use breakpoint prefixes to override at larger sizes.

```html
<!-- Base: 1 column (mobile), sm: 2 columns, lg: 4 columns -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

## Breakpoint System

| Prefix | Min Width | CSS Media Query |
|--------|-----------|-----------------|
| `sm:` | 640px | `@media (min-width: 640px)` |
| `md:` | 768px | `@media (min-width: 768px)` |
| `lg:` | 1024px | `@media (min-width: 1024px)` |
| `xl:` | 1280px | `@media (min-width: 1280px)` |
| `2xl:` | 1536px | `@media (min-width: 1536px)` |

## Core Responsive Patterns

### Layout Changes

```html
<!-- Vertical on mobile, horizontal on desktop -->
<div class="flex flex-col lg:flex-row gap-4">
  <div>Left</div>
  <div>Right</div>
</div>

<!-- 1 → 2 → 3 columns -->
<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
  <div>Item</div>
</div>
```

### Visibility

```html
<div class="hidden lg:block">Desktop only</div>
<div class="block lg:hidden">Mobile only</div>
<div class="lg:hidden">Mobile menu</div>
<div class="hidden lg:flex">Desktop navigation</div>
```

### Typography

```html
<h1 class="text-2xl md:text-4xl lg:text-6xl font-bold">
  Heading scales with screen size
</h1>
<p class="text-sm md:text-base lg:text-lg">Body text</p>
```

### Spacing and Width

```html
<div class="p-4 md:p-6 lg:p-8">More padding on larger screens</div>
<div class="w-full lg:w-1/2 xl:w-1/3">Responsive width</div>
<div class="max-w-sm md:max-w-2xl lg:max-w-4xl mx-auto">Centered</div>
```

## Common Layouts

### Sidebar

```html
<div class="flex flex-col lg:flex-row min-h-screen">
  <aside class="w-full lg:w-64 bg-gray-100 p-4">Sidebar</aside>
  <main class="flex-1 p-4 md:p-8">Main content</main>
</div>
```

### Card Grid

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
  <div class="bg-white rounded-lg shadow p-6">Card</div>
</div>
```

### Hero Section

```html
<section class="py-12 md:py-20 lg:py-32">
  <div class="container mx-auto px-4">
    <div class="flex flex-col lg:flex-row items-center gap-8">
      <div class="flex-1 text-center lg:text-left">
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold mb-4">Title</h1>
        <p class="text-lg md:text-xl mb-6">Description</p>
        <button class="px-6 py-3 md:px-8 md:py-4">CTA</button>
      </div>
      <div class="flex-1">
        <img src="hero.jpg" class="w-full rounded-lg" />
      </div>
    </div>
  </div>
</section>
```

### Navigation

```html
<nav class="bg-white shadow">
  <div class="container mx-auto px-4">
    <div class="flex items-center justify-between h-16">
      <div class="text-xl font-bold">Logo</div>
      <div class="hidden md:flex gap-6">
        <a href="#">Home</a>
        <a href="#">About</a>
      </div>
      <button class="md:hidden"><svg class="w-6 h-6">...</svg></button>
    </div>
  </div>
</nav>
```

## Max-Width and Range Queries

```html
<!-- Only below 1024px -->
<div class="max-lg:text-center">Centered on mobile/tablet</div>

<!-- Only on mobile (below 640px) -->
<div class="max-sm:hidden">Hidden only on mobile</div>

<!-- Only on tablets (between md and lg) -->
<div class="md:block lg:hidden">Visible only on tablets</div>
```

Available max-* prefixes: `max-sm:` `max-md:` `max-lg:` `max-xl:` `max-2xl:`

## Container Queries and Testing

```html
<div class="@container">
  <div class="@md:grid-cols-2 @lg:grid-cols-3">Responds to parent width</div>
</div>
```

Checklist: test at 320px / 640px / 768px / 1024px / 1280px, landscape, touch targets (44px+), zoom.
