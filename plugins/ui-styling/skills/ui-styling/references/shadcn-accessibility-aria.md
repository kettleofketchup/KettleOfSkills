# shadcn/ui Accessibility: ARIA and Screen Readers

ARIA labels, screen reader support, form accessibility, and color contrast.

## Semantic HTML

```tsx
// Good: Semantic HTML
<button>Click me</button>
<nav><a href="/">Home</a></nav>

// Avoid: Div soup
<div onClick={handler}>Click me</div>
```

## ARIA Labels

```tsx
{/* Label icon-only buttons */}
<Button aria-label="Close dialog">
  <X className="h-4 w-4" />
</Button>

<Input aria-label="Email address" type="email" />

{/* Describe elements */}
<Button aria-describedby="delete-description">Delete Account</Button>
<p id="delete-description" className="sr-only">
  This action permanently deletes your account and cannot be undone
</p>
```

## Screen Reader Only Text

```tsx
<Button>
  <Trash className="h-4 w-4" />
  <span className="sr-only">Delete item</span>
</Button>
```

Tailwind includes `.sr-only` (1px absolute positioned, overflow hidden, clipped).

## Live Regions

```tsx
<div aria-live="polite" aria-atomic="true">{message}</div>
<div aria-live="assertive">{error}</div>
```

Toast includes live region automatically — `toast({ title, description })` is announced.

## Form Accessibility

```tsx
{/* Always label inputs */}
<Label htmlFor="email">Email</Label>
<Input id="email" type="email" />

{/* Add descriptions */}
<FormItem>
  <FormLabel>Username</FormLabel>
  <FormControl><Input {...field} /></FormControl>
  <FormDescription>Your public display name</FormDescription>
  <FormMessage />
</FormItem>
```

### ARIA Invalid + Error Association

```tsx
<FormField control={form.control} name="email" render={({ field, fieldState }) => (
  <FormItem>
    <FormLabel>Email</FormLabel>
    <FormControl>
      <Input
        {...field}
        aria-invalid={!!fieldState.error}
        aria-describedby={fieldState.error ? "email-error" : undefined}
      />
    </FormControl>
    <FormMessage id="email-error" />
  </FormItem>
)} />
```

### Required Fields

```tsx
<Label htmlFor="name">
  Name <span className="text-destructive">*</span>
  <span className="sr-only">(required)</span>
</Label>
<Input id="name" required />
```

### Fieldset and Legend

```tsx
<fieldset>
  <legend className="text-lg font-semibold mb-4">Contact Information</legend>
  <div className="space-y-4">
    <FormField name="email" />
    <FormField name="phone" />
  </div>
</fieldset>
```

## Alert Component

```tsx
<Alert role="alert">
  {/* Announced immediately to screen readers */}
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>Your session has expired</AlertDescription>
</Alert>
```

## Color Contrast (WCAG)

- **AA**: 4.5:1 for normal text, 3:1 for large text
- **AAA**: 7:1 for normal text, 4.5:1 for large text

```tsx
// Good: High contrast
<p className="text-gray-900 dark:text-gray-100">Text</p>

// Avoid: Low contrast
<p className="text-gray-400 dark:text-gray-600">Hard to read</p>

// Use semantic muted foreground
<p className="text-muted-foreground">Secondary text with accessible contrast</p>
```

## Testing Tools and Checklist

Tools: Lighthouse, axe DevTools, NVDA/JAWS, keyboard-only navigation, WebAIM contrast checker.

```bash
npm install -D @axe-core/react
```

Checklist:
- [ ] Screen reader announces all content correctly
- [ ] Form errors announced and associated with inputs
- [ ] Color contrast meets WCAG AA (4.5:1 normal, 3:1 large text)
- [ ] Semantic HTML used throughout
- [ ] ARIA labels provided for icon-only buttons
- [ ] Live regions announce dynamic updates
