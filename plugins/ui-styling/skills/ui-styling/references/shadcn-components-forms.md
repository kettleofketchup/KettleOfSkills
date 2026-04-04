# shadcn/ui: Form & Input Components

## Installation
```bash
npx shadcn@latest add button
npx shadcn@latest add button card dialog  # Multiple
npx shadcn@latest add --all              # All components
```

Components install to `components/ui/` with automatic dependency management.

## Button
```tsx
import { Button } from "@/components/ui/button"

<Button variant="default">Default</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline" size="sm">Small Outline</Button>
<Button variant="ghost" size="icon"><Icon /></Button>
<Button variant="link">Link Style</Button>
```
Variants: `default | destructive | outline | secondary | ghost | link`
Sizes: `default | sm | lg | icon`

## Input & Label
```tsx
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input id="email" type="email" placeholder="you@example.com" />
</div>
```

## Form (React Hook Form + Zod)
```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"

const schema = z.object({
  username: z.string().min(2).max(50),
  email: z.string().email()
})

function ProfileForm() {
  const form = useForm({ resolver: zodResolver(schema), defaultValues: { username: "", email: "" } })
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(console.log)} className="space-y-8">
        <FormField control={form.control} name="username" render={({ field }) => (
          <FormItem>
            <FormLabel>Username</FormLabel>
            <FormControl><Input placeholder="shadcn" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

## Select
```tsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

<Select>
  <SelectTrigger className="w-[180px]"><SelectValue placeholder="Theme" /></SelectTrigger>
  <SelectContent>
    <SelectItem value="light">Light</SelectItem>
    <SelectItem value="dark">Dark</SelectItem>
    <SelectItem value="system">System</SelectItem>
  </SelectContent>
</Select>
```

## Checkbox
```tsx
import { Checkbox } from "@/components/ui/checkbox"
<div className="flex items-center space-x-2">
  <Checkbox id="terms" />
  <Label htmlFor="terms">Accept terms</Label>
</div>
```

## Radio Group
```tsx
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
<RadioGroup defaultValue="option-one">
  <div className="flex items-center space-x-2">
    <RadioGroupItem value="option-one" id="option-one" />
    <Label htmlFor="option-one">Option One</Label>
  </div>
</RadioGroup>
```

## Textarea
```tsx
import { Textarea } from "@/components/ui/textarea"
<Textarea placeholder="Type your message here." />
```

## Switch
```tsx
import { Switch } from "@/components/ui/switch"
<div className="flex items-center space-x-2">
  <Switch id="airplane-mode" />
  <Label htmlFor="airplane-mode">Airplane Mode</Label>
</div>
```

## Date Picker
```tsx
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { format } from "date-fns"

const [date, setDate] = useState<Date>()

<Popover>
  <PopoverTrigger asChild>
    <Button variant="outline">
      <CalendarIcon className="mr-2 h-4 w-4" />
      {date ? format(date, "PPP") : "Pick a date"}
    </Button>
  </PopoverTrigger>
  <PopoverContent className="w-auto p-0">
    <Calendar mode="single" selected={date} onSelect={setDate} />
  </PopoverContent>
</Popover>
```
