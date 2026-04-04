# Data Extraction Patterns

## Basic Extraction

```typescript
// Single element
const title = await page.locator('h1').textContent();

// Multiple elements
const items = await page.locator('.item').allTextContents();

// Attribute
const href = await page.locator('a.link').getAttribute('href');

// Multiple attributes
const links = await page.locator('a').evaluateAll(
  els => els.map(el => ({ text: el.textContent, href: el.href }))
);
```

## Structured Data Extraction

```typescript
const products = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('.product')).map(el => ({
    name: el.querySelector('.name')?.textContent?.trim(),
    price: el.querySelector('.price')?.textContent?.trim(),
    image: el.querySelector('img')?.src,
    link: el.querySelector('a')?.href,
  }));
});
```

## Table Extraction

```typescript
const tableData = await page.evaluate(() => {
  const rows = document.querySelectorAll('table tr');
  return Array.from(rows).map(row => {
    const cells = row.querySelectorAll('td, th');
    return Array.from(cells).map(cell => cell.textContent?.trim());
  });
});
```

## Pagination

```typescript
const allData: any[] = [];

while (true) {
  const pageData = await extractPageData(page);
  allData.push(...pageData);

  const nextBtn = page.locator('.next-page');
  if (await nextBtn.isDisabled() || !(await nextBtn.isVisible())) {
    break;
  }

  await nextBtn.click();
  await page.waitForLoadState('networkidle');
}
```

## Infinite Scroll

```typescript
const items: any[] = [];
let prevCount = 0;

while (true) {
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(1000);

  const currentItems = await page.locator('.item').count();
  if (currentItems === prevCount) break;

  prevCount = currentItems;
}

// Now extract all items
const data = await page.locator('.item').allTextContents();
```

## Handle Dynamic Content

```typescript
// Wait for content to load
await page.waitForSelector('.content:not(.loading)');

// Wait for specific text
await page.waitForFunction(() =>
  document.querySelector('.status')?.textContent === 'Ready'
);

// Wait for element count
await page.waitForFunction(() =>
  document.querySelectorAll('.item').length >= 10
);
```

## Screenshot for Debugging

```typescript
await page.screenshot({
  path: 'debug.png',
  fullPage: true
});

// Element screenshot
await page.locator('.chart').screenshot({ path: 'chart.png' });
```

## Extract from Shadow DOM

```typescript
const shadowContent = await page.evaluate(() => {
  const host = document.querySelector('custom-element');
  const shadow = host?.shadowRoot;
  return shadow?.querySelector('.inner')?.textContent;
});
```

## Save Page Content

```typescript
const html = await page.content();
await fs.writeFile('page.html', html);

// Or just the element
const elementHtml = await page.locator('.content').innerHTML();
```
