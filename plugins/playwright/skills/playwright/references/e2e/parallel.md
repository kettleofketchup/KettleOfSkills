# Test Parallelization

## Config-level

```typescript
// playwright.config.ts
export default defineConfig({
  workers: process.env.CI ? 4 : undefined,
  fullyParallel: true,
});
```

## File-level (default)

Each test file runs in parallel. Tests within same file run serially.

## Test-level

```typescript
test.describe.configure({ mode: 'parallel' });
test('test 1', async ({ page }) => {});
test('test 2', async ({ page }) => {});
```

## Serial when needed

```typescript
test.describe.configure({ mode: 'serial' });
// Fail stops subsequent tests
```

## Sharding (CI)

```bash
npx playwright test --shard=1/4
npx playwright test --shard=2/4
npx playwright test --shard=3/4
npx playwright test --shard=4/4
```

## Speed Optimizations

### Reuse auth state

```typescript
// Setup once
await page.context().storageState({ path: 'auth.json' });

// Reuse
test.use({ storageState: 'auth.json' });
```

### Mock slow APIs

```typescript
await page.route('**/api/slow', route => {
  route.fulfill({ json: { data: 'mocked' } });
});
```

### Disable animations

```typescript
await page.addStyleTag({
  content: `*, *::before, *::after {
    animation-duration: 0s !important;
    transition-duration: 0s !important;
  }`
});
```

### Reduce timeouts

```typescript
test.use({ actionTimeout: 5000 });
```

## Multiple Users in Test

```typescript
test('chat between users', async ({ browser }) => {
  const ctx1 = await browser.newContext({ storageState: './user1.json' });
  const ctx2 = await browser.newContext({ storageState: './user2.json' });
  const page1 = await ctx1.newPage();
  const page2 = await ctx2.newPage();
  // ...
  await ctx1.close();
  await ctx2.close();
});
```
