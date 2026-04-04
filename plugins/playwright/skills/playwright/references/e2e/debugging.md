# E2E Test Debugging & Flaky Tests

## Debug Mode

```bash
npx playwright test --debug              # Interactive
npx playwright test --headed --slow-mo=500
DEBUG=pw:api npx playwright test         # Verbose logs
```

## Trace Viewer

```typescript
// playwright.config.ts
use: { trace: 'on-first-retry' }
```

```bash
npx playwright show-trace trace.zip
npx playwright show-report
```

## Screenshots & Video

```typescript
use: {
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
}
```

## Fixing Flaky Tests

### 1. Use web-first assertions (auto-retry)

```typescript
// Bad
const text = await page.textContent('.status');
expect(text).toBe('Ready');

// Good
await expect(page.locator('.status')).toHaveText('Ready');
```

### 2. Wait for network, not time

```typescript
// Bad
await page.click('#save');
await page.waitForTimeout(2000);

// Good
const response = page.waitForResponse('**/api/save');
await page.click('#save');
await response;
```

### 3. Isolate state

```typescript
test.beforeEach(async ({ page }) => {
  await page.request.post('/api/test/reset');
});
```

### 4. Retry flaky externals

```typescript
// playwright.config.ts
retries: process.env.CI ? 2 : 0,
```

## Pause Execution

```typescript
await page.pause(); // Opens inspector
```

## Console/Network Logs

```typescript
page.on('console', msg => console.log(`[${msg.type()}] ${msg.text()}`));
page.on('pageerror', err => console.log('Error:', err.message));
page.on('request', req => console.log('>>', req.method(), req.url()));
```

## CI Artifacts

```yaml
- uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: playwright-report
    path: playwright-report/
```

## Common Fixes

| Symptom | Fix |
|---------|-----|
| Element not found | `await expect(locator).toBeVisible()` |
| Wrong text | Use `toHaveText()` not `textContent()` |
| Click missed | Wait for animations, `force: true` |
| State leak | Reset in beforeEach |
