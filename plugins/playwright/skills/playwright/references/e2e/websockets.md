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

## Multi-User Real-time Test

```typescript
test('chat between users', async ({ browser }) => {
  const ctx1 = await browser.newContext();
  const ctx2 = await browser.newContext();
  const page1 = await ctx1.newPage();
  const page2 = await ctx2.newPage();

  const user2Received: string[] = [];
  page2.on('websocket', ws => {
    ws.on('framereceived', f => {
      const data = JSON.parse(f.payload as string);
      if (data.type === 'chat') user2Received.push(data.text);
    });
  });

  await Promise.all([
    page1.goto('/chat/room-1'),
    page2.goto('/chat/room-1'),
  ]);

  await page1.fill('#message', 'Hello!');
  await page1.click('#send');

  // Poll until message arrives
  await expect.poll(() => user2Received).toContain('Hello!');

  // Also verify UI updated
  await expect(page2.locator('.message').last()).toContainText('Hello!');

  await ctx1.close();
  await ctx2.close();
});
```

## Mock WebSocket Server

```typescript
import { WebSocketServer, WebSocket } from 'ws';

let wss: WebSocketServer;
let connections: WebSocket[] = [];

test.beforeAll(() => {
  wss = new WebSocketServer({ port: 8080 });
  wss.on('connection', ws => {
    connections.push(ws);
    ws.on('message', data => {
      // Broadcast to all
      connections.forEach(c => c.send(data.toString()));
    });
    ws.on('close', () => {
      connections = connections.filter(c => c !== ws);
    });
  });
});

test.afterAll(() => wss.close());

test('works with mock server', async ({ page }) => {
  await page.goto('/app?ws=ws://localhost:8080');
  await expect(page.locator('.connected')).toBeVisible();
});
```

## Assert WebSocket Connected

```typescript
test('establishes WS connection', async ({ page }) => {
  const wsConnected = new Promise<string>(resolve => {
    page.on('websocket', ws => resolve(ws.url()));
  });

  await page.goto('/realtime-app');
  const wsUrl = await wsConnected;

  expect(wsUrl).toContain('/ws/feed');
});
```

## Test Reconnection

```typescript
test('reconnects after disconnect', async ({ page }) => {
  let connectionCount = 0;

  page.on('websocket', ws => {
    connectionCount++;
    ws.on('close', () => console.log('WS closed'));
  });

  await page.goto('/app');
  expect(connectionCount).toBe(1);

  // Simulate network drop
  await page.context().setOffline(true);
  await page.waitForTimeout(1000);
  await page.context().setOffline(false);

  // Wait for reconnect
  await page.waitForTimeout(3000);
  expect(connectionCount).toBe(2);
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
