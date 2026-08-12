# Form Field Components

Shadcn UI form field patterns for common input types.

## Required Imports

```typescript
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage, FormDescription } from '~/components/ui/form';
import { Input } from '~/components/ui/input';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '~/components/ui/select';
import { Checkbox } from '~/components/ui/checkbox';
import { Textarea } from '~/components/ui/textarea';
import { Button } from '~/components/ui/button';
```

## Text Input

```typescript
<FormField
  control={form.control}
  name="username"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Username</FormLabel>
      <FormControl>
        <Input placeholder="Enter username" {...field} />
      </FormControl>
      <FormDescription>Your display name.</FormDescription>
      <FormMessage />
    </FormItem>
  )}
/>
```

## Email Input

```typescript
<FormField
  control={form.control}
  name="email"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Email</FormLabel>
      <FormControl>
        <Input type="email" placeholder="email@example.com" {...field} />
      </FormControl>
      <FormMessage />
    </FormItem>
  )}
/>
```

## Password Input

```typescript
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
```

## Number Input

```typescript
<FormField
  control={form.control}
  name="yearsExperience"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Years of Experience</FormLabel>
      <FormControl>
        <Input
          type="number"
          {...field}
          onChange={(e) => field.onChange(e.target.valueAsNumber || null)}
        />
      </FormControl>
      <FormMessage />
    </FormItem>
  )}
/>
```

## Textarea

```typescript
<FormField
  control={form.control}
  name="description"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Description</FormLabel>
      <FormControl>
        <Textarea placeholder="Enter description" {...field} />
      </FormControl>
      <FormMessage />
    </FormItem>
  )}
/>
```

## Select (String Values)

```typescript
<FormField
  control={form.control}
  name="role"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Role</FormLabel>
      <Select onValueChange={field.onChange} defaultValue={field.value}>
        <FormControl>
          <SelectTrigger>
            <SelectValue placeholder="Select role" />
          </SelectTrigger>
        </FormControl>
        <SelectContent>
          <SelectItem value="user">User</SelectItem>
          <SelectItem value="admin">Admin</SelectItem>
          <SelectItem value="moderator">Moderator</SelectItem>
        </SelectContent>
      </Select>
      <FormMessage />
    </FormItem>
  )}
/>
```

## Select (Number Values)

Rating and proficiency selects hold number values. Convert strings to numbers:

```typescript
<FormField
  control={form.control}
  name="proficiencies.frontend"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Frontend</FormLabel>
      <Select
        onValueChange={(value) => field.onChange(Number(value))}
        defaultValue={field.value?.toString()}
      >
        <FormControl>
          <SelectTrigger>
            <SelectValue placeholder="Select skill level" />
          </SelectTrigger>
        </FormControl>
        <SelectContent>
          <SelectItem value="1">1 - Beginner</SelectItem>
          <SelectItem value="2">2 - Novice</SelectItem>
          <SelectItem value="3">3 - Intermediate</SelectItem>
          <SelectItem value="4">4 - Advanced</SelectItem>
          <SelectItem value="5">5 - Expert</SelectItem>
        </SelectContent>
      </Select>
      <FormMessage />
    </FormItem>
  )}
/>
```

Continued in `form-fields-advanced.md`.
