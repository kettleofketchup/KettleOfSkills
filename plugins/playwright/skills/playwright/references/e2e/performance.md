# E2E Test Performance

## Config Optimizations

```typescript
// playwright.config.ts
export default defineConfig({
  workers: process.env.CI ? 4 : undefined,
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  use: {
    navigationTimeout: 15000,
    actionTimeout: 10000,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',
    launchOptions: { args: ['--disable-extensions'] },
  },
});
```

## Reuse Authentication State

```typescript
// global-setup.ts
export default async function globalSetup() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('/login');
  await page.fill('#email', 'test@example.com');
  await page.fill('#password', 'password');
  await page.click('#submit');
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: './auth.json' });
  await browser.close();
}

// Tests reuse (no login per test)
test.use({ storageState: './auth.json' });
```

## Block Unnecessary Resources

```typescript
await page.route('**/*', route => {
  const url = route.request().url();
  if (url.match(/\.(png|jpg|gif|svg|woff2?|ttf)(\?.*)?$/)) return route.abort();
  if (url.includes('analytics') || url.includes('hotjar')) return route.abort();
  route.continue();
});
```

## Mock Slow APIs

```typescript
test.beforeEach(async ({ page }) => {
  await page.route('**/api/external/**', route => {
    route.fulfill({ json: { data: 'mocked' } });
  });
});
```

## Disable Animations

```typescript
await page.addInitScript(() => {
  const style = document.createElement('style');
  style.textContent = `*, *::before, *::after {
    animation-duration: 0s !important;
    transition-duration: 0s !important;
  }`;
  document.head.appendChild(style);
});
```

## Wait Strategies (fastest to slowest)

```typescript
// 1. Auto-wait (built-in) - PREFERRED
await page.click('button');

// 2. Wait for element
await page.waitForSelector('.loaded');

// 3. Wait for response
const resp = page.waitForResponse('**/api/data');
await page.click('#load');
await resp;

// 4. Load states
await page.waitForLoadState('domcontentloaded'); // Fast
await page.waitForLoadState('networkidle');      // SLOW - avoid

// NEVER use fixed timeouts
await page.waitForTimeout(2000); // BAD
```

## Assertions (faster options)

```typescript
await expect(locator).toBeVisible();           // Fast
await expect(locator).toContainText('partial'); // Fast
await expect(locator).toHaveText('exact');      // Slower
```

## CI Sharding

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: npx playwright test --shard=${{ matrix.shard }}/4
```

## Database Seeding via API

```typescript
test.beforeEach(async ({ request }) => {
  await request.post('/api/test/seed', { data: { users: 10 } });
});

test.afterEach(async ({ request }) => {
  await request.post('/api/test/cleanup');
});
```

## Parallel in File

```typescript
test.describe.configure({ mode: 'parallel' });

test('test 1', async ({ page }) => {});
test('test 2', async ({ page }) => {});
```

## Measure Duration

```typescript
test('perf check', async ({ page }) => {
  const start = Date.now();
  await page.goto('/heavy-page');
  await page.waitForSelector('.content');
  expect(Date.now() - start).toBeLessThan(3000);
});
```
