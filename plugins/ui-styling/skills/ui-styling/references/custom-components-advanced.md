# Custom Components: Advanced Patterns

Compound components, polymorphic rendering, responsive patterns.

## Compound Component Pattern

Related components sharing state via Context:

```tsx
import { createContext, useContext } from "react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { cn } from "@/lib/utils"

const StatCardContext = createContext<{ trend?: "up" | "down" | "neutral" }>({})

function StatCard({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <Card className={cn("", className)} {...props}>{children}</Card>
}

function StatCardHeader({ children, trend }: { children: React.ReactNode; trend?: "up" | "down" | "neutral" }) {
  return (
    <StatCardContext.Provider value={{ trend }}>
      <CardHeader className="pb-2">{children}</CardHeader>
    </StatCardContext.Provider>
  )
}

function StatCardTitle({ children }: { children: React.ReactNode }) {
  return <p className="text-sm font-medium text-muted-foreground">{children}</p>
}

function StatCardValue({ children }: { children: React.ReactNode }) {
  const { trend } = useContext(StatCardContext)
  return (
    <p className={cn("text-2xl font-bold", trend === "up" && "text-green-600", trend === "down" && "text-red-600")}>
      {children}
    </p>
  )
}

StatCard.Header = StatCardHeader
StatCard.Title = StatCardTitle
StatCard.Value = StatCardValue
StatCard.Content = ({ children }: { children: React.ReactNode }) => <CardContent className="pt-0">{children}</CardContent>

// Usage
<StatCard>
  <StatCard.Header trend="up">
    <StatCard.Title>Revenue</StatCard.Title>
    <StatCard.Value>$45,231</StatCard.Value>
  </StatCard.Header>
  <StatCard.Content>
    <p className="text-xs text-muted-foreground">+20.1% from last month</p>
  </StatCard.Content>
</StatCard>
```

## Polymorphic Component with asChild

```tsx
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

const textVariants = cva("", {
  variants: {
    variant: {
      h1: "text-4xl font-bold tracking-tight",
      h2: "text-3xl font-semibold tracking-tight",
      h3: "text-2xl font-semibold",
      body: "text-base",
      small: "text-sm text-muted-foreground",
    },
  },
  defaultVariants: { variant: "body" },
})

interface TextProps extends React.HTMLAttributes<HTMLParagraphElement>, VariantProps<typeof textVariants> {
  asChild?: boolean
}

export function Text({ className, variant, asChild = false, ...props }: TextProps) {
  const Comp = asChild ? Slot : "p"
  return <Comp className={cn(textVariants({ variant }), className)} {...props} />
}

// Renders as <p> / <h1> / <span> based on asChild
<Text variant="body">Regular paragraph</Text>
<Text variant="h1" asChild><h1>Page Title</h1></Text>
<Text variant="small" asChild><span>Inline</span></Text>
```

## Responsive Dialog/Drawer

Bottom sheet on mobile, modal on desktop:

```tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerDescription } from "@/components/ui/drawer"
import { useMediaQuery } from "@/hooks/use-media-query"

interface ResponsiveModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description?: string
  children: React.ReactNode
}

export function ResponsiveModal({ open, onOpenChange, title, description, children }: ResponsiveModalProps) {
  const isDesktop = useMediaQuery("(min-width: 768px)")

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{title}</DialogTitle>
            {description && <DialogDescription>{description}</DialogDescription>}
          </DialogHeader>
          {children}
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>{title}</DrawerTitle>
          {description && <DrawerDescription>{description}</DrawerDescription>}
        </DrawerHeader>
        <div className="px-4 pb-4">{children}</div>
      </DrawerContent>
    </Drawer>
  )
}
```

## Confirmation Dialog

```tsx
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription,
  AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"

interface ConfirmDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description: string
  confirmText?: string
  cancelText?: string
  variant?: "default" | "destructive"
  onConfirm: () => void
}

export function ConfirmDialog({ open, onOpenChange, title, description, confirmText = "Continue",
  cancelText = "Cancel", variant = "default", onConfirm }: ConfirmDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{cancelText}</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm}
            className={variant === "destructive" ? "bg-destructive text-destructive-foreground hover:bg-destructive/90" : ""}>
            {confirmText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

// Usage
<ConfirmDialog open={showDelete} onOpenChange={setShowDelete} title="Delete item?"
  description="This action cannot be undone." confirmText="Delete" variant="destructive" onConfirm={handleDelete} />
```
