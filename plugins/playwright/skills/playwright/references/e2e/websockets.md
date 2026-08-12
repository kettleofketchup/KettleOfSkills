# WebSocket Testing

## Setup Listener Before Navigation

```typescript
test('receives realtime update', async ({ page }) => {
  // Setup listener BEFORE navigation
  const wsPromise = new Promise<string>(resolve => {
    page.on('websocket', ws => {
      ws.on('framereceived', frame => {
        const data = JSON.parse(frame.payload as string);
        if (data.type === 'update') resolve(data.value);
      });
    });
  });

  await page.goto('/dashboard');
  const value = await wsPromise;
  expect(value).toBeDefined();
});
```

## Wait for Specific Message

```typescript
async function waitForWsMessage(
  page: Page,
  predicate: (data: any) => boolean,
  timeout = 10000
): Promise<any> {
  return Promise.race([
    new Promise(resolve => {
      page.on('websocket', ws => {
        ws.on('framereceived', frame => {
          try {
            const data = JSON.parse(frame.payload as string);
            if (predicate(data)) resolve(data);
          } catch {}
        });
      });
    }),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('WS timeout')), timeout)
    ),
  ]);
}

// Usage
test('notification arrives', async ({ page }) => {
  await page.goto('/app');
  await page.click('#trigger');

  const msg = await waitForWsMessage(page, d => d.type === 'notification');
  expect(msg.text).toBe('Done');
});
```

## Collect Messages During Test

```typescript
test('tracks all updates', async ({ page }) => {
  const messages: any[] = [];

  page.on('websocket', ws => {
    ws.on('framereceived', f => {
      try { messages.push(JSON.parse(f.payload as string)); } catch {}
    });
  });

  await page.goto('/live-feed');
  await page.click('#start');
  await page.waitForTimeout(3000);
  await page.click('#stop');

  expect(messages.filter(m => m.type === 'data').length).toBeGreaterThan(5);
});
```

## Debug Logging

```typescript
page.on('websocket', ws => {
  console.log(`[WS] OPEN ${ws.url()}`);
  ws.on('framesent', f => console.log(`[WS] >>> ${f.payload}`));
  ws.on('framereceived', f => console.log(`[WS] <<< ${f.payload}`));
  ws.on('close', () => console.log(`[WS] CLOSED`));
  ws.on('socketerror', e => console.log(`[WS] ERROR ${e}`));
});
```

See also: [websockets-advanced.md](websockets-advanced.md) — multi-user tests, mock server, reconnection, assert connected.
