# Playwright Test Configuration

## Basic playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## Projects for Auth Scenarios

```typescript
projects: [
  { name: 'setup', testMatch: /.*\.setup\.ts/ },
  {
    name: 'logged-in',
    dependencies: ['setup'],
    use: { storageState: './auth.json' },
  },
  { name: 'logged-out', testIgnore: /.*\.setup\.ts/ },
  { name: 'mobile', use: { ...devices['Pixel 5'] } },
],
```

## Reporters

```typescript
reporter: [
  ['list'],
  ['html', { open: 'never' }],
  ['junit', { outputFile: 'results.xml' }],  // CI
],
```

## Timeouts

```typescript
export default defineConfig({
  timeout: 30000,
  expect: { timeout: 5000 },
  use: {
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },
});
```

## Global Setup

```typescript
export default defineConfig({
  globalSetup: require.resolve('./global-setup.ts'),
});
```

```typescript
// global-setup.ts - auth setup
import { chromium } from '@playwright/test';

export default async function globalSetup() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('/login');
  await page.fill('#email', 'user@example.com');
  await page.fill('#password', 'password');
  await page.click('button[type="submit"]');
  await page.context().storageState({ path: './auth.json' });
  await browser.close();
}
```

## CLI Commands

```bash
npx playwright test --headed        # See browser
npx playwright test --debug         # Step through
npx playwright test --ui            # UI mode
npx playwright test -g "test name"  # Filter
npx playwright test --project=chromium
npx playwright test --last-failed
npx playwright codegen              # Generate code
```
