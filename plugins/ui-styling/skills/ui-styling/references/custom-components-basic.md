# Custom Components: Basic Patterns

Patterns for wrapping shadcn/ui primitives into reusable custom components.

## Basic Wrapper Pattern

Extend primitive with custom defaults and additional props:

```tsx
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

## CVA Variants Pattern

Use `class-variance-authority` for multiple visual variants:

```tsx
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
  {
    variants: {
      status: {
        pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
        active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
        inactive: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
        error: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
      },
      size: { sm: "text-xs px-2 py-0.5", md: "text-sm px-2.5 py-0.5", lg: "text-base px-3 py-1" },
    },
    defaultVariants: { status: "pending", size: "md" },
  }
)

interface StatusBadgeProps extends React.HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

export function StatusBadge({ className, status, size, ...props }: StatusBadgeProps) {
  return <span className={cn(badgeVariants({ status, size }), className)} {...props} />
}

// Usage
<StatusBadge status="active">Online</StatusBadge>
```

## CVA Button with asChild

```tsx
import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "@radix-ui/react-slot"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      intent: {
        primary: "bg-primary text-primary-foreground hover:bg-primary/90",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        danger: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        ghost: "hover:bg-accent hover:text-accent-foreground",
      },
      size: { sm: "h-9 px-3 text-sm", md: "h-11 px-4 text-sm", lg: "h-12 px-6 text-base", icon: "h-11 w-11" },
      fullWidth: { true: "w-full", false: "" },
    },
    defaultVariants: { intent: "primary", size: "md", fullWidth: false },
  }
)

interface ActionButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

export function ActionButton({ className, intent, size, fullWidth, asChild = false, ...props }: ActionButtonProps) {
  const Comp = asChild ? Slot : "button"
  return <Comp className={cn(buttonVariants({ intent, size, fullWidth }), className)} {...props} />
}
```

## Form Field Wrapper

```tsx
import { Input, type InputProps } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { forwardRef } from "react"

interface FormInputProps extends InputProps {
  label: string
  error?: string
  description?: string
}

export const FormInput = forwardRef<HTMLInputElement, FormInputProps>(
  ({ label, error, description, className, id, ...props }, ref) => {
    const inputId = id || label.toLowerCase().replace(/\s+/g, "-")
    return (
      <div className="space-y-1.5">
        <Label htmlFor={inputId} className={error ? "text-destructive" : ""}>{label}</Label>
        <Input ref={ref} id={inputId} className={cn("h-11", error && "border-destructive", className)}
          aria-invalid={!!error} aria-describedby={error ? `${inputId}-error` : undefined} {...props} />
        {description && !error && <p className="text-sm text-muted-foreground">{description}</p>}
        {error && <p id={`${inputId}-error`} className="text-sm text-destructive">{error}</p>}
      </div>
    )
  }
)
FormInput.displayName = "FormInput"
```
