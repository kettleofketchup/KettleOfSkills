# Scraping Performance

## Parallel Scraping

### Multiple contexts (recommended)

```typescript
const browser = await chromium.launch();

const results = await Promise.all(
  urls.map(async url => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await page.goto(url);
    const data = await page.locator('.data').textContent();
    await context.close();
    return data;
  })
);

await browser.close();
```

### Limit concurrency

```typescript
import pLimit from 'p-limit';
const limit = pLimit(5); // max 5 concurrent

const results = await Promise.all(
  urls.map(url => limit(async () => {
    const page = await context.newPage();
    await page.goto(url);
    const data = await extractData(page);
    await page.close();
    return data;
  }))
);
```

## Block Unnecessary Resources

```typescript
await page.route('**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2}', r => r.abort());
await page.route('**/analytics/**', r => r.abort());
await page.route('**/*google*/**', r => r.abort());
await page.route('**/*facebook*/**', r => r.abort());
await page.route('**/ads/**', r => r.abort());
```

## Headless Mode (faster)

```typescript
const browser = await chromium.launch({ headless: true });
```

## Wait Strategies

```typescript
// Wait for specific element (faster than networkidle)
await page.waitForSelector('.content-loaded');

// Wait for specific API response
const response = await page.waitForResponse('**/api/data');
const json = await response.json();

// Avoid networkidle when possible (slow)
await page.goto(url, { waitUntil: 'domcontentloaded' });
```

## Reduce Timeouts

```typescript
const context = await browser.newContext();
context.setDefaultTimeout(10000); // 10s instead of 30s
```

## Batch Page Operations

```typescript
// Extract multiple elements at once
const data = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('.item')).map(el => ({
    title: el.querySelector('.title')?.textContent,
    price: el.querySelector('.price')?.textContent,
    link: el.querySelector('a')?.href,
  }));
});
```

## Reuse Browser Instance

```typescript
// Don't launch/close per URL
const browser = await chromium.launch();

for (const url of urls) {
  const page = await browser.newPage();
  // ...
  await page.close(); // Close page, not browser
}

await browser.close(); // Close at end
```
