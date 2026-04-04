# Browser Contexts for Scraping

## Context = Isolated Session

Each context has separate cookies, storage, cache.

```typescript
const browser = await chromium.launch();
const context = await browser.newContext();
const page = await context.newPage();
```

## Rotating Contexts (Anti-Detection)

```typescript
async function scrapeWithRotation(urls: string[]) {
  const browser = await chromium.launch();
  const results = [];

  for (const url of urls) {
    const context = await browser.newContext({
      userAgent: getRandomUserAgent(),
    });

    const page = await context.newPage();
    await page.goto(url);
    results.push(await page.content());

    await context.close();
    await sleep(randomDelay(1000, 3000));
  }

  await browser.close();
  return results;
}
```

## Context Options

```typescript
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 ...',
  viewport: { width: 1920, height: 1080 },
  locale: 'en-US',
  timezoneId: 'America/New_York',
  geolocation: { latitude: 40.7128, longitude: -74.0060 },
  permissions: ['geolocation'],
  ignoreHTTPSErrors: true,
  extraHTTPHeaders: { 'Accept-Language': 'en-US,en' },
});
```

## Device Emulation

```typescript
import { devices } from 'playwright';

const context = await browser.newContext({
  ...devices['iPhone 13'],
});
```

## Proxy per Context

```typescript
const context = await browser.newContext({
  proxy: {
    server: 'http://proxy.example.com:8080',
    username: 'user',
    password: 'pass',
  },
});
```

## Cookie Management

```typescript
// Add cookies
await context.addCookies([
  { name: 'session', value: 'abc123', domain: '.example.com', path: '/' }
]);

// Get cookies
const cookies = await context.cookies();

// Clear
await context.clearCookies();
```

## Save/Restore Session

```typescript
// Save after login
await context.storageState({ path: 'session.json' });

// Restore later
const context = await browser.newContext({
  storageState: 'session.json',
});
```

## HTTP Auth

```typescript
const context = await browser.newContext({
  httpCredentials: { username: 'user', password: 'pass' },
});
```
