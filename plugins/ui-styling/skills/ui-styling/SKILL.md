---
name: ui-styling
description: Build accessible UIs with shadcn/ui (Radix UI + Tailwind), React Hook Form + Zod validation, CVA variants, canvas design systems, responsive layouts, and CSS variable theming.
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
│   └── dialog.tsx
├── custom/                # Your reusable wrappers
│   ├── app-button.tsx     # Button with your defaults
│   ├── form-input.tsx     # Input with label + error
│   └── confirm-dialog.tsx # Confirmation pattern
└── features/              # Feature-specific compositions
    └── auth/login-form.tsx
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

export function AppButton({ isLoading, children, className, disabled, ...props }: AppButtonProps) {
  return (
    <Button className={cn("min-h-11", className)} disabled={disabled || isLoading} {...props}>
      {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </Button>
  )
}
```

## Key Patterns

| Pattern | Use Case | Reference |
|---------|----------|-----------|
| CVA Variants | Multiple visual styles for one component | custom-components-basic.md |
| Compound Components | Related components sharing state | custom-components-compound.md |
| Polymorphic `asChild` | Render as different elements | custom-components-compound.md |
| Form Fields | Input + Label + Error combined | form-integration-basic.md |
| Form Validation | Zod schemas + React Hook Form | form-integration-basic.md |

## References

### Custom Components
- **[custom-components-basic.md](references/custom-components-basic.md)** - Basic wrapper, CVA variants, form field patterns
- **[custom-components-compound.md](references/custom-components-compound.md)** - Compound components, polymorphic rendering
- **[custom-components-modal.md](references/custom-components-modal.md)** - Responsive modal, confirm dialog
- **[custom-components-advanced.md](references/custom-components-advanced.md)** - Additional advanced patterns

### Forms
- **[form-integration-basic.md](references/form-integration-basic.md)** - React Hook Form + Zod setup, custom field components
- **[form-integration-advanced.md](references/form-integration-advanced.md)** - Complex schemas, loading states, Server Actions

### shadcn Primitives
- **[shadcn-components-forms.md](references/shadcn-components-forms.md)** - Button, Input, Form, Select, Checkbox, Date Picker
- **[shadcn-components-layout-display.md](references/shadcn-components-layout-display.md)** - Card, Tabs, Accordion, Toast, Table, Badge
- **[shadcn-components-layout-dialogs.md](references/shadcn-components-layout-dialogs.md)** - Dialog, Drawer, AlertDialog, Command, Popover
- **[shadcn-theming-setup.md](references/shadcn-theming-setup.md)** - Dark mode, CSS variables, Tailwind config
- **[shadcn-theming-customization.md](references/shadcn-theming-customization.md)** - Color methods, component variants, presets
- **[shadcn-accessibility-keyboard.md](references/shadcn-accessibility-keyboard.md)** - Keyboard navigation, focus management
- **[shadcn-accessibility-aria.md](references/shadcn-accessibility-aria.md)** - ARIA patterns, screen readers, color contrast

### Tailwind
- **[tailwind-utilities-layout.md](references/tailwind-utilities-layout.md)** - Layout, flexbox, grid, spacing, sizing
- **[tailwind-utilities-visual.md](references/tailwind-utilities-visual.md)** - Typography, colors, borders, shadows, effects
- **[tailwind-responsive-basics.md](references/tailwind-responsive-basics.md)** - Mobile-first breakpoints, common layouts
- **[tailwind-responsive-advanced.md](references/tailwind-responsive-advanced.md)** - Custom breakpoints, state variants, best practices
- **[tailwind-customization-theme.md](references/tailwind-customization-theme.md)** - @theme directive, colors, typography, spacing
- **[tailwind-customization-advanced.md](references/tailwind-customization-advanced.md)** - Utilities, variants, layers, plugins, full config

### Visual Design
- **[canvas-design-philosophy.md](references/canvas-design-philosophy.md)** - Design movements, philosophy creation
- **[canvas-design-execution.md](references/canvas-design-execution.md)** - Composition rules, quality standards, checklists

## Installation

```bash
npx shadcn@latest init
npx shadcn@latest add button input dialog form card
```

## Best Practices

1. **Wrap, don't modify** - Create custom components instead of editing `components/ui/`
2. **Default to touch-friendly** - Use `min-h-11` (44px) for interactive elements
3. **Mobile-first responsive** - Base styles for mobile, add `sm:` `md:` `lg:` for larger
4. **Consistent naming** - `AppButton`, `FormInput`, `PageHeader` pattern
5. **Props spreading** - Always spread `...props` to allow customization
6. **Type safety** - Extend base component props with `interface X extends ButtonProps`
