# shadcn/ui Theming: Customization

Color customization, component variants, presets, and theming best practices.

## Color Customization

### Method 1: Update CSS Variables

Change colors by modifying CSS variables in `globals.css`:

```css
:root {
  --primary: 262.1 83.3% 57.8%;  /* Purple */
  --primary-foreground: 210 20% 98%;
}

.dark {
  --primary: 263.4 70% 50.4%;
  --primary-foreground: 210 20% 98%;
}
```

### Method 2: Theme Generator

Use shadcn/ui theme generator: https://ui.shadcn.com/themes

Select base color, generate theme, copy CSS variables.

### Method 3: Multiple Themes

```css
[data-theme="violet"] {
  --primary: 262.1 83.3% 57.8%;
  --primary-foreground: 210 20% 98%;
}

[data-theme="rose"] {
  --primary: 346.8 77.2% 49.8%;
  --primary-foreground: 355.7 100% 97.3%;
}
```

```tsx
<div data-theme="violet">
  <Button>Violet theme</Button>
</div>
```

## Component Customization

Components live in your codebase — modify directly.

### Add Custom Variants

```tsx
// components/ui/button.tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        destructive: "bg-destructive text-destructive-foreground",
        outline: "border border-input bg-background",
        // Custom variant:
        gradient: "bg-gradient-to-r from-purple-500 to-pink-500 text-white",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        // Custom size:
        xl: "h-14 rounded-md px-10 text-lg",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
)
```

```tsx
<Button variant="gradient" size="xl">Custom Button</Button>
```

### Modify Base Styles

```tsx
// components/ui/card.tsx
const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("rounded-xl border bg-card text-card-foreground shadow-lg", className)}
      {...props}
    />
  )
)
```

### Override with className

```tsx
<Card className="border-2 border-purple-500 shadow-2xl hover:scale-105 transition-transform">
  Custom styled card
</Card>
```

## Base Color Presets

Available during `npx shadcn@latest init`:

- **Slate**: Cool gray tones
- **Gray**: Neutral gray
- **Zinc**: Warm gray
- **Neutral**: Balanced gray
- **Stone**: Earthy gray

## Style Variants

Two component styles:

- **Default**: Softer, more rounded
- **New York**: Sharp, more contrast

Configure in `components.json`:
```json
{
  "style": "new-york",
  "tailwind": { "cssVariables": true }
}
```

## Radius Customization

```css
:root {
  --radius: 0.5rem;  /* Default */
  /* --radius: 0rem;  Sharp corners */
  /* --radius: 1rem;  Rounded */
}
```

## Best Practices

1. **CSS Variables**: Enables runtime theme switching
2. **Pair foregrounds**: Every color needs appropriate foreground variant
3. **Test both themes**: Verify components in light and dark
4. **Semantic naming**: Use `destructive` not `red`, `muted` not `gray`
5. **WCAG AA**: Maintain 4.5:1 contrast; use `className` for one-off overrides
