# Advanced Form Field Components

Split out of `form-fields.md`; see it for the preceding sections.

## Checkbox

```typescript
<FormField
  control={form.control}
  name="isActive"
  render={({ field }) => (
    <FormItem className="flex flex-row items-start space-x-3 space-y-0">
      <FormControl>
        <Checkbox checked={field.value} onCheckedChange={field.onChange} />
      </FormControl>
      <div className="space-y-1 leading-none">
        <FormLabel>Active</FormLabel>
        <FormDescription>Enable this option.</FormDescription>
      </div>
    </FormItem>
  )}
/>
```

## Date Picker

```typescript
import { Calendar } from '~/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '~/components/ui/popover';
import { CalendarIcon } from 'lucide-react';
import { format } from 'date-fns';

<FormField
  control={form.control}
  name="startDate"
  render={({ field }) => (
    <FormItem className="flex flex-col">
      <FormLabel>Date</FormLabel>
      <Popover>
        <PopoverTrigger asChild>
          <FormControl>
            <Button variant="outline" className="w-full justify-start text-left font-normal">
              <CalendarIcon className="mr-2 h-4 w-4" />
              {field.value ? format(field.value, 'PPP') : <span>Pick a date</span>}
            </Button>
          </FormControl>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0">
          <Calendar mode="single" selected={field.value} onSelect={field.onChange} />
        </PopoverContent>
      </Popover>
      <FormMessage />
    </FormItem>
  )}
/>
```

## Multi-Select / Checkbox Group

```typescript
const items = [
  { id: 'frontend', label: 'Frontend' },
  { id: 'backend', label: 'Backend' },
  { id: 'devops', label: 'DevOps' },
];

<FormField
  control={form.control}
  name="roles"
  render={() => (
    <FormItem>
      <FormLabel>Preferred Roles</FormLabel>
      <div className="space-y-2">
        {items.map((item) => (
          <FormField
            key={item.id}
            control={form.control}
            name="roles"
            render={({ field }) => (
              <FormItem className="flex items-center space-x-2">
                <FormControl>
                  <Checkbox
                    checked={field.value?.includes(item.id)}
                    onCheckedChange={(checked) => {
                      return checked
                        ? field.onChange([...field.value, item.id])
                        : field.onChange(field.value?.filter((val) => val !== item.id));
                    }}
                  />
                </FormControl>
                <FormLabel className="font-normal">{item.label}</FormLabel>
              </FormItem>
            )}
          />
        ))}
      </div>
      <FormMessage />
    </FormItem>
  )}
/>
```

## Grid Layouts

### Two Columns

```typescript
<div className="grid grid-cols-2 gap-4">
  <FormField control={form.control} name="firstName" ... />
  <FormField control={form.control} name="lastName" ... />
</div>
```

### Five Columns (Position Form)

```typescript
<div className="grid grid-cols-5 gap-4">
  <FormField control={form.control} name="proficiencies.frontend" ... />
  <FormField control={form.control} name="proficiencies.backend" ... />
  <FormField control={form.control} name="proficiencies.devops" ... />
  <FormField control={form.control} name="proficiencies.design" ... />
  <FormField control={form.control} name="proficiencies.testing" ... />
</div>
```

## Disabled Fields

```typescript
<FormField
  control={form.control}
  name="employeeId"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Employee ID (read-only)</FormLabel>
      <FormControl>
        <Input {...field} disabled />
      </FormControl>
    </FormItem>
  )}
/>
```

## Conditional Fields

```typescript
const watchType = form.watch('type');

{watchType === 'business' && (
  <FormField
    control={form.control}
    name="businessName"
    render={({ field }) => (
      <FormItem>
        <FormLabel>Business Name</FormLabel>
        <FormControl>
          <Input {...field} />
        </FormControl>
        <FormMessage />
      </FormItem>
    )}
  />
)}
```

## Form Actions

```typescript
<div className="flex gap-2">
  <Button type="submit" disabled={form.formState.isSubmitting}>
    {form.formState.isSubmitting ? 'Saving...' : 'Save'}
  </Button>
  <Button type="button" variant="outline" onClick={() => form.reset()}>
    Reset
  </Button>
</div>
```
