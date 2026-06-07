# shadcn/ui Accessibility: Keyboard and Focus

Keyboard navigation, focus management, and component-specific keyboard patterns.

## Foundation: Radix UI Primitives

shadcn/ui built on Radix UI - unstyled, accessible components following WAI-ARIA patterns.

Built-in features:
- Keyboard navigation
- Screen reader announcements
- Focus management
- ARIA attributes automatically applied

## Focus Management

### Focus Visible States

```tsx
<Button className="focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
  Accessible Button
</Button>
```

### Skip to Content

```tsx
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2">
  Skip to content
</a>
<main id="main-content">{/* Content */}</main>
```

### Custom Focus Styles

```tsx
<a href="#" className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:underline">
  Link
</a>

{/* Don't remove focus styles */}
{/* Avoid: <button className="focus:outline-none"> */}
{/* Use: <button className="focus-visible:ring-2"> */}
```

## Component Keyboard Patterns

### Dialog/Modal

Dialogs trap focus automatically via Radix Dialog primitive:

```tsx
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    {/* Focus trapped here */}
    <input />  {/* Auto-focused */}
    <Button>Action</Button>
    {/* Esc to close, Tab to navigate */}
  </DialogContent>
</Dialog>
```

Keys: `Tab` cycle through elements, `Esc` close, focus returns to trigger on close.

### Dropdown Menu

```tsx
<DropdownMenu>
  <DropdownMenuTrigger>Open</DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>Profile</DropdownMenuItem>
    <DropdownMenuItem>Settings</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

Keys: `Space/Enter` open, `Arrow Up/Down` navigate, `Esc` close.

### Command Palette

```tsx
<Command>
  <CommandInput placeholder="Search..." />
  <CommandList>
    <CommandGroup heading="Suggestions"><CommandItem>Calendar</CommandItem></CommandGroup>
  </CommandList>
</Command>
```

Keys: type to filter, `Arrow` navigate, `Enter` select, `Esc` close.

### Accordion and Tabs

```tsx
<Accordion type="single" collapsible>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>Yes. Follows WAI-ARIA design pattern.</AccordionContent>
  </AccordionItem>
</Accordion>

<Tabs defaultValue="account">
  <TabsList role="tablist">
    {/* Arrow keys navigate, Space/Enter activates */}
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">
    {/* aria-labelledby links to trigger */}
    Account content
  </TabsContent>
</Tabs>
```

### Select

```tsx
<Select>
  <SelectTrigger aria-label="Choose theme">
    <SelectValue placeholder="Theme" />
  </SelectTrigger>
  <SelectContent>
    {/* Keyboard navigable, announced to screen readers */}
    <SelectItem value="light">Light</SelectItem>
    <SelectItem value="dark">Dark</SelectItem>
  </SelectContent>
</Select>
```

### Checkbox and Motion

```tsx
<div className="flex items-center space-x-2">
  <Checkbox id="terms" aria-describedby="terms-desc" />
  <Label htmlFor="terms">Accept terms</Label>
</div>
<p id="terms-desc" className="text-sm text-muted-foreground">You agree to our Terms</p>

<div className="transition-all motion-reduce:transition-none">Respects prefers-reduced-motion</div>
```

Checklist: keyboard accessible + visible focus; dialog focus trap; tab order + skip links; reduced motion; 200% zoom.
