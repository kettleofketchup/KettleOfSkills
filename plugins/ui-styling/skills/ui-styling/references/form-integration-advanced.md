# Form Integration: Advanced Patterns

Complex Zod schemas, loading states, checkbox groups, Server Actions, and validation patterns.

## Complex Zod Schemas

```tsx
import { z } from "zod"
export const userSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email"),
  age: z.coerce.number().min(18, "Must be 18 or older").optional(),
  website: z.string().url("Invalid URL").optional().or(z.literal("")),
  role: z.enum(["admin", "user", "guest"], { errorMap: () => ({ message: "Select a role" }) }),
  bio: z.string().max(500, "Bio must be 500 characters or less").optional(),
  notifications: z.object({ email: z.boolean(), sms: z.boolean() }),
  tags: z.array(z.string()).min(1, "Select at least one tag"),
})
export type UserFormData = z.infer<typeof userSchema>
```

## Form with Loading State

```tsx
import { useState } from "react"
import { Loader2 } from "lucide-react"

export function SubmitForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const form = useForm({ resolver: zodResolver(schema), defaultValues: { email: "" } })

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
          <p className="text-sm text-destructive">{form.formState.errors.root.message}</p>
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
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Checkbox } from "@/components/ui/checkbox"

interface Option { value: string; label: string }

export function FormCheckboxGroup({ name, label, options }: {
  name: string; label: string; options: Option[]
}) {
  const { control } = useFormContext()
  return (
    <FormField control={control} name={name} render={() => (
      <FormItem>
        <FormLabel>{label}</FormLabel>
        <div className="space-y-2">
          {options.map((option) => (
            <FormField key={option.value} control={control} name={name} render={({ field }) => (
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
                <FormLabel className="font-normal cursor-pointer">{option.label}</FormLabel>
              </FormItem>
            )} />
          ))}
        </div>
        <FormMessage />
      </FormItem>
    )} />
  )
}
```

## Server Actions (Next.js)

```tsx
"use client"
import { useTransition } from "react"
import { createUser } from "@/actions/user"

export function CreateUserForm() {
  const [isPending, startTransition] = useTransition()
  const form = useForm({ resolver: zodResolver(schema), defaultValues: { name: "", email: "" } })
  const onSubmit = (data: FormData) => {
    startTransition(async () => {
      const result = await createUser(data)
      if (result.error) form.setError("root", { message: result.error })
    })
  }
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <Button type="submit" disabled={isPending}>{isPending ? "Creating..." : "Create User"}</Button>
      </form>
    </Form>
  )
}
```

## Validation Patterns

```tsx
const schema = z.object({
  name: z.string().min(1, "Required"),
  nickname: z.string().optional(),
  website: z.string().url().optional().or(z.literal("")),
  age: z.coerce.number().min(0).max(120),
  status: z.enum(["active", "inactive"], { errorMap: () => ({ message: "Select a status" }) }),
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})
```
