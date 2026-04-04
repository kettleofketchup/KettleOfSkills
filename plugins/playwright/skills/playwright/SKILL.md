---
name: playwright
description: Playwright browser automation for E2E testing and web scraping. This skill should be used when writing Playwright tests, creating browser automation scripts, handling WebSockets, managing multiple browser contexts, parallelizing test execution, optimizing test speed, debugging flaky tests, working with playwright.config.ts configuration, or setting up GitHub Actions CI workflows for Playwright tests with browser caching and sharding.
version: 1.1.0
last_updated: 2026-02-01
playwright_version: "1.50+"
---

# Playwright Browser Automation

TypeScript/JavaScript patterns for E2E testing and web scraping.

## Quick Reference

### E2E Test

```typescript
import { test, expect } from '@playwright/test';

test('should work', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByText('Success')).toBeVisible();
});
```

### Scraping Script

```typescript
import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('https://example.com');
const data = await page.locator('.item').allTextContents();
await browser.close();
```

## Selectors (prefer in order)

1. `page.getByRole()` - accessibility-based (buttons, links, headings)
2. `page.getByTestId()` or `[data-testid="..."]` - **explicit test hooks (most reliable)**
3. `page.getByText()` - visible text (exact match preferred)
4. `page.locator()` - CSS/XPath fallback

### Avoid `has-text()` for Buttons

**Bad** - fragile, breaks if text changes:
```typescript
page.locator('button:has-text("Start Draft")')
```

**Good** - stable, explicit test contract:
```typescript
page.locator('[data-testid="startDraftButton"]')
// or
page.getByTestId('startDraftButton')
```

When adding new UI elements, always add `data-testid` attributes for testability.

## E2E Testing References

- `references/e2e/ci.md` - **GitHub Actions CI**, browser caching, sharding, Docker pitfalls
- `references/e2e/config.md` - playwright.config.ts, projects, global setup
- `references/e2e/performance.md` - Speed optimization, resource blocking, wait strategies
- `references/e2e/parallel.md` - Workers, sharding, test parallelization
- `references/e2e/debugging.md` - Traces, flaky tests, CI artifacts
- `references/e2e/websockets.md` - WS testing, mocking, reconnection, multi-user

## Web Scraping References

- `references/scraping/performance.md` - Parallel contexts, concurrency, speed
- `references/scraping/contexts.md` - Rotation, proxies, anti-detection
- `references/scraping/network.md` - Request interception, blocking, mocking
- `references/scraping/websockets.md` - WS data capture, live feeds
- `references/scraping/extraction.md` - Data extraction, pagination, infinite scroll
