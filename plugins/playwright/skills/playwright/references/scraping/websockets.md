# WebSocket Interception for Scraping

## Listen to All Messages

```typescript
page.on('websocket', ws => {
  console.log(`WS opened: ${ws.url()}`);

  ws.on('framesent', frame => {
    console.log('Sent:', frame.payload);
  });

  ws.on('framereceived', frame => {
    console.log('Received:', frame.payload);
  });

  ws.on('close', () => console.log('WS closed'));
});

await page.goto('/realtime-app');
```

## Collect WebSocket Data

```typescript
const wsData: any[] = [];

page.on('websocket', ws => {
  ws.on('framereceived', frame => {
    try {
      const data = JSON.parse(frame.payload as string);
      wsData.push(data);
    } catch {
      // Binary or non-JSON
      wsData.push(frame.payload);
    }
  });
});

await page.goto('/live-data');
await page.waitForTimeout(10000); // Collect data

console.log('Collected:', wsData.length, 'messages');
```

## Wait for Specific Message

```typescript
async function waitForWsMessage(page: Page, predicate: (data: any) => boolean) {
  return new Promise(resolve => {
    page.on('websocket', ws => {
      ws.on('framereceived', frame => {
        try {
          const data = JSON.parse(frame.payload as string);
          if (predicate(data)) resolve(data);
        } catch {}
      });
    });
  });
}

// Usage
const priceUpdate = await waitForWsMessage(page,
  data => data.type === 'price' && data.symbol === 'BTC'
);
```

## CDP for Advanced Interception (Chrome)

```typescript
const client = await page.context().newCDPSession(page);
await client.send('Network.enable');

client.on('Network.webSocketFrameReceived', params => {
  console.log('Frame:', params.response.payloadData);
});

client.on('Network.webSocketCreated', params => {
  console.log('WS created:', params.url);
});
```

## Scrape Live Feed

```typescript
const feed: any[] = [];
let collecting = true;

page.on('websocket', ws => {
  ws.on('framereceived', frame => {
    if (!collecting) return;
    const data = JSON.parse(frame.payload as string);
    feed.push({ timestamp: Date.now(), data });
  });
});

await page.goto('/live-feed');

// Collect for 60 seconds
await page.waitForTimeout(60000);
collecting = false;

// Process feed
console.log('Collected', feed.length, 'updates');
```

## Handle Binary WebSocket

```typescript
ws.on('framereceived', frame => {
  if (typeof frame.payload === 'string') {
    // Text frame
    console.log('Text:', frame.payload);
  } else {
    // Binary frame
    const buffer = Buffer.from(frame.payload);
    console.log('Binary:', buffer.length, 'bytes');
  }
});
```
