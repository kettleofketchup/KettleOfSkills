# Form Integration: Basics

React Hook Form + Zod setup, basic form pattern, and custom field components.

## Setup

```bash
npm install react-hook-form @hookform/resolvers zod
npx shadcn@latest add form input button
```
## Basic Form Pattern

```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const schema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
})

type FormData = z.infer<typeof schema>

export function LoginForm() {
  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit((data) => console.log(data))} className="space-y-4">
        <FormField control={form.control} name="email" render={({ field }) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl><Input type="email" placeholder="you@example.com" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <FormField control={form.control} name="password" render={({ field }) => (
          <FormItem>
            <FormLabel>Password</FormLabel>
            <FormControl><Input type="password" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit" className="w-full">Sign In</Button>
      </form>
    </Form>
  )
}
```

## Custom Text Field Component

```tsx
// components/custom/form-text-field.tsx
import { useFormContext } from "react-hook-form"
import { FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from "@/components/ui/form"
import { Input } from "@/components/ui/input"

interface FormTextFieldProps {
  name: string
  label: string
  placeholder?: string
  description?: string
  type?: "text" | "email" | "password" | "number" | "tel" | "url"
}

export function FormTextField({ name, label, placeholder, description, type = "text" }: FormTextFieldProps) {
  const { control } = useFormContext()
  return (
    <FormField control={control} name={name} render={({ field }) => (
      <FormItem>
        <FormLabel>{label}</FormLabel>
        <FormControl>
          <Input type={type} placeholder={placeholder} className="h-11" {...field} />
        </FormControl>
        {description && <FormDescription>{description}</FormDescription>}
        <FormMessage />
      </FormItem>
    )} />
  )
}

// Usage
<FormTextField name="email" label="Email" type="email" placeholder="you@example.com" />
<FormTextField name="phone" label="Phone" type="tel" description="We'll never share your phone." />
```

## Custom Select Field

```tsx
// components/custom/form-select-field.tsx
import { useFormContext } from "react-hook-form"
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface Option { value: string; label: string }

export function FormSelectField({ name, label, placeholder = "Select...", options }: {
  name: string; label: string; placeholder?: string; options: Option[]
}) {
  const { control } = useFormContext()
  return (
    <FormField control={control} name={name} render={({ field }) => (
      <FormItem>
        <FormLabel>{label}</FormLabel>
        <Select onValueChange={field.onChange} defaultValue={field.value}>
          <FormControl>
            <SelectTrigger className="h-11"><SelectValue placeholder={placeholder} /></SelectTrigger>
          </FormControl>
          <SelectContent>
            {options.map((opt) => <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>)}
          </SelectContent>
        </Select>
        <FormMessage />
      </FormItem>
    )} />
  )
}

// Usage
<FormSelectField name="country" label="Country" options={[{ value: "us", label: "United States" }]} />
```

## Responsive Form Layout

```tsx
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 md:space-y-6">
    <div className="grid gap-4 md:grid-cols-2">
      <FormTextField name="firstName" label="First Name" />
      <FormTextField name="lastName" label="Last Name" />
    </div>
    <FormTextField name="email" label="Email" type="email" />
    <div className="grid gap-4 md:grid-cols-3">
      <FormTextField name="city" label="City" />
      <FormSelectField name="state" label="State" options={states} />
      <FormTextField name="zip" label="ZIP" />
    </div>
    <Button type="submit" className="w-full md:w-auto">Save</Button>
  </form>
</Form>
```
