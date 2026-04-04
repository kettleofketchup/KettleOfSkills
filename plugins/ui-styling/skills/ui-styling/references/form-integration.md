# Form Integration Patterns

React Hook Form + Zod validation with shadcn/ui components.

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
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
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

  const onSubmit = (data: FormData) => {
    console.log(data)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="you@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full">
          Sign In
        </Button>
      </form>
    </Form>
  )
}
```

## Custom Form Field Component

Wrap repetitive FormField pattern:

```tsx
// components/custom/form-text-field.tsx
import { useFormContext } from "react-hook-form"
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

interface FormTextFieldProps {
  name: string
  label: string
  placeholder?: string
  description?: string
  type?: "text" | "email" | "password" | "number" | "tel" | "url"
}

export function FormTextField({
  name,
  label,
  placeholder,
  description,
  type = "text",
}: FormTextFieldProps) {
  const { control } = useFormContext()

  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              type={type}
              placeholder={placeholder}
              className="h-11"
              {...field}
            />
          </FormControl>
          {description && <FormDescription>{description}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  )
}

// Usage - much cleaner!
<FormTextField name="email" label="Email" type="email" placeholder="you@example.com" />
<FormTextField name="phone" label="Phone" type="tel" description="We'll never share your phone." />
```

## Custom Select Field

```tsx
// components/custom/form-select-field.tsx
import { useFormContext } from "react-hook-form"
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface Option {
  value: string
  label: string
}

interface FormSelectFieldProps {
  name: string
  label: string
  placeholder?: string
  options: Option[]
}

export function FormSelectField({
  name,
  label,
  placeholder = "Select...",
  options,
}: FormSelectFieldProps) {
  const { control } = useFormContext()

  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <Select onValueChange={field.onChange} defaultValue={field.value}>
            <FormControl>
              <SelectTrigger className="h-11">
                <SelectValue placeholder={placeholder} />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              {options.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )}
    />
  )
}

// Usage
<FormSelectField
  name="country"
  label="Country"
  options={[
    { value: "us", label: "United States" },
    { value: "uk", label: "United Kingdom" },
  ]}
/>
```

## Complex Zod Schemas

```tsx
// schemas/user.ts
import { z } from "zod"

export const userSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email"),
  age: z.coerce.number().min(18, "Must be 18 or older").optional(),
  website: z.string().url("Invalid URL").optional().or(z.literal("")),
  role: z.enum(["admin", "user", "guest"], {
    errorMap: () => ({ message: "Select a role" }),
  }),
  bio: z.string().max(500, "Bio must be 500 characters or less").optional(),
  notifications: z.object({
    email: z.boolean(),
    sms: z.boolean(),
  }),
  tags: z.array(z.string()).min(1, "Select at least one tag"),
})

export type UserFormData = z.infer<typeof userSchema>
```

## Form with Loading State

```tsx
import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Loader2 } from "lucide-react"

export function SubmitForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { email: "" },
  })

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true)
    try {
      await submitToAPI(data)
      form.reset()
    } catch (error) {
      form.setError("root", { message: "Something went wrong" })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* Fields... */}

        {form.formState.errors.root && (
          <p className="text-sm text-destructive">
            {form.formState.errors.root.message}
          </p>
        )}

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isSubmitting ? "Submitting..." : "Submit"}
        </Button>
      </form>
    </Form>
  )
}
```

## Checkbox Group

```tsx
// components/custom/form-checkbox-group.tsx
import { useFormContext } from "react-hook-form"
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Checkbox } from "@/components/ui/checkbox"

interface Option {
  value: string
  label: string
}

interface FormCheckboxGroupProps {
  name: string
  label: string
  options: Option[]
}

export function FormCheckboxGroup({ name, label, options }: FormCheckboxGroupProps) {
  const { control } = useFormContext()

  return (
    <FormField
      control={control}
      name={name}
      render={() => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <div className="space-y-2">
            {options.map((option) => (
              <FormField
                key={option.value}
                control={control}
                name={name}
                render={({ field }) => (
                  <FormItem className="flex items-center space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value?.includes(option.value)}
                        onCheckedChange={(checked) => {
                          const current = field.value || []
                          field.onChange(
                            checked
                              ? [...current, option.value]
                              : current.filter((v: string) => v !== option.value)
                          )
                        }}
                      />
                    </FormControl>
                    <FormLabel className="font-normal cursor-pointer">
                      {option.label}
                    </FormLabel>
                  </FormItem>
                )}
              />
            ))}
          </div>
          <FormMessage />
        </FormItem>
      )}
    />
  )
}
```

## Responsive Form Layout

```tsx
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 md:space-y-6">
    {/* Side by side on tablet+ */}
    <div className="grid gap-4 md:grid-cols-2">
      <FormTextField name="firstName" label="First Name" />
      <FormTextField name="lastName" label="Last Name" />
    </div>

    {/* Full width always */}
    <FormTextField name="email" label="Email" type="email" />

    {/* Three columns on desktop */}
    <div className="grid gap-4 md:grid-cols-3">
      <FormTextField name="city" label="City" />
      <FormSelectField name="state" label="State" options={states} />
      <FormTextField name="zip" label="ZIP" />
    </div>

    {/* Full width button on mobile, auto on desktop */}
    <Button type="submit" className="w-full md:w-auto">
      Save
    </Button>
  </form>
</Form>
```

## Server Actions (Next.js)

```tsx
"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useTransition } from "react"
import { createUser } from "@/actions/user"

export function CreateUserForm() {
  const [isPending, startTransition] = useTransition()

  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { name: "", email: "" },
  })

  const onSubmit = (data: FormData) => {
    startTransition(async () => {
      const result = await createUser(data)
      if (result.error) {
        form.setError("root", { message: result.error })
      }
    })
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* Fields */}
        <Button type="submit" disabled={isPending}>
          {isPending ? "Creating..." : "Create User"}
        </Button>
      </form>
    </Form>
  )
}
```

## Validation Patterns

```tsx
const schema = z.object({
  // Required string
  name: z.string().min(1, "Required"),

  // Optional string (can be empty or undefined)
  nickname: z.string().optional(),

  // Optional but if provided must be valid
  website: z.string().url().optional().or(z.literal("")),

  // Number from string input
  age: z.coerce.number().min(0).max(120),

  // Enum with custom error
  status: z.enum(["active", "inactive"], {
    errorMap: () => ({ message: "Select a status" }),
  }),

  // Conditional validation
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})
```
