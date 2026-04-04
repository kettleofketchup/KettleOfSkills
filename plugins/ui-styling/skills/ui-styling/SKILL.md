---
name: ui-styling
description: Create beautiful, accessible user interfaces with shadcn/ui components (built on Radix UI + Tailwind), Tailwind CSS utility-first styling, and canvas-based visual designs. Use when building user interfaces, creating reusable React components, implementing forms with validation, establishing design systems, working with responsive layouts, or theming applications. Covers component composition, CVA variants, React Hook Form + Zod integration, mobile-first patterns, and CSS variable theming.
---

# UI Styling

Build consistent, accessible UIs with shadcn/ui and Tailwind CSS.

## Core Principle: Component-First

**Never use shadcn primitives directly in pages/features. Always wrap in custom components.**

```tsx
// WRONG: Using primitives directly throughout the app
import { Button } from "@/components/ui/button"
<Button variant="default" size="sm" className="bg-brand-500">Save</Button>

// CORRECT: Create custom component once, reuse everywhere
// components/custom/submit-button.tsx
export function SubmitButton({ children, isLoading, ...props }) {
  return (
    <Button variant="default" size="default" disabled={isLoading} {...props}>
      {isLoading && <Spinner className="mr-2 h-4 w-4" />}
      {children}
    </Button>
  )
}

// Usage - consistent everywhere
<SubmitButton isLoading={isPending}>Save Changes</SubmitButton>
```

**Why component-first?**
- **Single source of truth** - Change button style once, updates everywhere
- **Consistent UX** - Same behavior, loading states, sizing across app
- **Easier maintenance** - Brand changes require editing one file
- **Better DX** - Simpler API for feature developers

## Component Organization

```
components/
├── ui/                    # shadcn primitives (don't modify directly)
│   ├── button.tsx
│   ├── input.tsx
│   └── dialog.tsx
├── custom/                # Your reusable wrappers
│   ├── app-button.tsx     # Button with your defaults
│   ├── form-input.tsx     # Input with label + error
│   ├── page-header.tsx    # Consistent page headers
│   └── confirm-dialog.tsx # Confirmation pattern
└── features/              # Feature-specific compositions
    ├── auth/login-form.tsx
    └── settings/profile-card.tsx
```

## Quick Start: Custom Component

```tsx
// components/custom/app-button.tsx
import { Button, type ButtonProps } from "@/components/ui/button"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface AppButtonProps extends ButtonProps {
  isLoading?: boolean
}

export function AppButton({
  isLoading,
  children,
  className,
  disabled,
  ...props
}: AppButtonProps) {
  return (
    <Button
      className={cn("min-h-11", className)}  // Touch-friendly default
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </Button>
  )
}
```

## Mobile-First with Components

Apply responsive styling at the custom component level:

```tsx
// components/custom/responsive-dialog.tsx
export function ResponsiveDialog({ children, ...props }) {
  return (
    <Dialog {...props}>
      <DialogContent className="
        fixed bottom-0 inset-x-0 rounded-t-xl max-h-[85vh]
        sm:relative sm:bottom-auto sm:inset-x-auto sm:rounded-xl sm:max-w-lg
      ">
        {children}
      </DialogContent>
    </Dialog>
  )
}
```

## Key Patterns

| Pattern | Use Case | Reference |
|---------|----------|-----------|
| CVA Variants | Multiple visual styles for one component | custom-components.md |
| Compound Components | Related components that share state | custom-components.md |
| Polymorphic `asChild` | Render as different elements | custom-components.md |
| Form Fields | Input + Label + Error combined | form-integration.md |
| Form Validation | Zod schemas + React Hook Form | form-integration.md |

## References

### Custom Components (Start Here)
- **[custom-components-basic.md](references/custom-components-basic.md)** - Basic wrapper, CVA variants, form field patterns
- **[custom-components-advanced.md](references/custom-components-advanced.md)** - Compound components, polymorphic, responsive modal, confirm dialog

### Forms
- **[form-integration.md](references/form-integration.md)** - React Hook Form + Zod validation, custom form fields, error handling

### Primitives (For Reference)
- **[shadcn-components-forms.md](references/shadcn-components-forms.md)** - Button, Input, Form, Select, Checkbox, Radio, Date Picker
- **[shadcn-components-layout.md](references/shadcn-components-layout.md)** - Card, Tabs, Dialog, Drawer, Toast, Table, Alert, Avatar
- **[shadcn-theming.md](references/shadcn-theming.md)** - Theme configuration, CSS variables, dark mode
- **[shadcn-accessibility.md](references/shadcn-accessibility.md)** - ARIA patterns, keyboard navigation

### Tailwind
- **[tailwind-utilities-layout.md](references/tailwind-utilities-layout.md)** - Layout, flexbox, grid, spacing, sizing, positioning
- **[tailwind-utilities-visual.md](references/tailwind-utilities-visual.md)** - Typography, colors, borders, shadows, effects
- **[tailwind-responsive.md](references/tailwind-responsive.md)** - Mobile-first breakpoints
- **[tailwind-customization.md](references/tailwind-customization.md)** - Config and extensions

### Visual Design
- **[canvas-design-system.md](references/canvas-design-system.md)** - Canvas-based design philosophy

## Installation

```bash
# Initialize shadcn/ui (configures Tailwind too)
npx shadcn@latest init

# Add components as needed
npx shadcn@latest add button input dialog form card
```

## Best Practices

1. **Wrap, don't modify** - Create custom components instead of editing `components/ui/`
2. **Default to touch-friendly** - Use `min-h-11` (44px) for interactive elements
3. **Mobile-first responsive** - Base styles for mobile, add `sm:` `md:` `lg:` for larger
4. **Consistent naming** - `AppButton`, `FormInput`, `PageHeader` pattern
5. **Props spreading** - Always spread `...props` to allow customization
6. **Type safety** - Extend base component props with `interface X extends ButtonProps`

## Resources

- shadcn/ui: https://ui.shadcn.com
- Tailwind CSS: https://tailwindcss.com
- Radix UI: https://radix-ui.com
- CVA: https://cva.style
