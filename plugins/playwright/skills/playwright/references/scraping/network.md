# Network Interception for Scraping

## Intercept Requests

```typescript
await page.route('**/api/**', route => {
  console.log('API call:', route.request().url());
  route.continue();
});
```

## Modify Request Headers

```typescript
await page.route('**/*', route => {
  route.continue({
    headers: {
      ...route.request().headers(),
      'X-Custom-Header': 'value',
      'Referer': 'https://google.com',
    },
  });
});
```

## Capture API Responses

```typescript
const apiData: any[] = [];

await page.route('**/api/products*', async route => {
  const response = await route.fetch();
  const json = await response.json();
  apiData.push(json);
  route.fulfill({ response });
});

await page.goto('/products');
// apiData now contains intercepted responses
```

## Wait for Specific Response

```typescript
const responsePromise = page.waitForResponse(
  res => res.url().includes('/api/data') && res.status() === 200
);

await page.click('#load-data');
const response = await responsePromise;
const data = await response.json();
```

## Block Resources

```typescript
await page.route('**/*', route => {
  const url = route.request().url();
  if (url.match(/\.(png|jpg|gif|css|woff)/)) {
    return route.abort();
  }
  if (url.includes('analytics') || url.includes('tracking')) {
    return route.abort();
  }
  route.continue();
});
```

## Mock Responses

```typescript
await page.route('**/api/expensive', route => {
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ cached: true }),
  });
});
```

## Capture All Network

```typescript
const requests: string[] = [];
const responses: { url: string; status: number }[] = [];

page.on('request', req => requests.push(req.url()));
page.on('response', res => {
  responses.push({ url: res.url(), status: res.status() });
});
```

## Download Files

```typescript
const [download] = await Promise.all([
  page.waitForEvent('download'),
  page.click('#download-btn'),
]);

await download.saveAs('./downloads/' + download.suggestedFilename());
```

## Handle Redirects

```typescript
const response = await page.goto(url);
const finalUrl = response?.url(); // After redirects
const chain = response?.request().redirectedFrom(); // Redirect chain
```
