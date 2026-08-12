# React Hook Form: Submission, Nesting & Arrays

Split out of `react-hook-form.md`; see it for the preceding sections.

## Submission Handling

### With Toast Promise (DTX Pattern)

```typescript
import { toast } from 'sonner';
import { getLogger } from '~/lib/logger';

const log = getLogger('MyForm');

const onSubmit = (data: FormData) => {
  toast.promise(apiCall(data), {
    loading: 'Saving...',
    success: (response) => {
      setData(response);
      return 'Saved successfully!';
    },
    error: (err) => {
      log.error('API call failed', err);
      return `Failed: ${err?.response?.data ?? String(err)}`;
    },
  });
};
```

## Nested Fields

```typescript
const Schema = z.object({
  user: z.object({
    name: z.string(),
    address: z.object({
      city: z.string(),
    }),
  }),
});

// Access with dot notation
<FormField control={form.control} name="user.name" ... />
<FormField control={form.control} name="user.address.city" ... />
```

## Array Fields

```typescript
import { useFieldArray } from 'react-hook-form';

const { fields, append, remove } = useFieldArray({
  control: form.control,
  name: 'items',
});

{fields.map((field, index) => (
  <FormField
    key={field.id}
    control={form.control}
    name={`items.${index}.name`}
    render={({ field }) => <Input {...field} />}
  />
))}

<Button onClick={() => append({ name: '' })}>Add</Button>
```

## DTX Reference Implementation

See `~/pages/profile/profile.tsx`:

```typescript
export const ProfilePage: React.FC = () => {
  const currentUser = useUserStore((state) => state.currentUser);

  const form = useForm<z.infer<typeof UserSchema>>({
    resolver: zodResolver(UserSchema),
    defaultValues: {
      positions: { ...currentUser?.positions },
    },
  });

  async function onSubmit(data: z.infer<typeof UserSchema>) {
    toast.promise(UpdateProfile(data), {
      loading: 'Updating...',
      success: (response) => {
        setCurrentUser(response);
        return 'Profile updated!';
      },
      error: (err) => `Failed: ${err?.response?.data ?? String(err)}`,
    });
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <PositionForm form={form} />
        <Button type="submit">Save</Button>
      </form>
    </Form>
  );
};
```

## Accessibility (Built-in)

Shadcn form components provide:

```typescript
<input
  id="form-item-{unique-id}"
  aria-describedby="form-item-description form-item-message"
  aria-invalid={!!error}
/>
<label htmlFor="form-item-{unique-id}">...</label>
<p id="form-item-description">Helper text</p>
<p id="form-item-message" class="text-destructive">Error</p>
```
