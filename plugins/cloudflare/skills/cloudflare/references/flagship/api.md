# Flagship API Reference

## Binding API (Workers)

The binding is available as `env.FLAGS` (type `Flagship` from `@cloudflare/workers-types`).

### Evaluation Methods

All methods are async, never throw, and return the `defaultValue` on errors.

| Method | Signature | Returns |
|--------|-----------|---------|
| `get` | `get(flagKey, defaultValue?, context?)` | `Promise<unknown>` |
| `getBooleanValue` | `getBooleanValue(flagKey, defaultValue, context?)` | `Promise<boolean>` |
| `getStringValue` | `getStringValue(flagKey, defaultValue, context?)` | `Promise<string>` |
| `getNumberValue` | `getNumberValue(flagKey, defaultValue, context?)` | `Promise<number>` |
| `getObjectValue` | `getObjectValue<T>(flagKey, defaultValue, context?)` | `Promise<T>` |
| `getBooleanDetails` | `getBooleanDetails(flagKey, defaultValue, context?)` | `Promise<FlagshipEvaluationDetails<boolean>>` |
| `getStringDetails` | `getStringDetails(flagKey, defaultValue, context?)` | `Promise<FlagshipEvaluationDetails<string>>` |
| `getNumberDetails` | `getNumberDetails(flagKey, defaultValue, context?)` | `Promise<FlagshipEvaluationDetails<number>>` |
| `getObjectDetails` | `getObjectDetails<T>(flagKey, defaultValue, context?)` | `Promise<FlagshipEvaluationDetails<T>>` |

### Parameters (shared across all methods)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `flagKey` | `string` | Yes | Flag key to evaluate |
| `defaultValue` | varies | Yes (except `get`) | Fallback if evaluation fails or flag not found |
| `context` | `FlagshipEvaluationContext` | No | Attributes for targeting rules (`{ userId: "user-42", country: "US" }`) |

### Types

```typescript
type FlagshipEvaluationContext = Record<string, string | number | boolean>;

interface FlagshipEvaluationDetails<T> {
  flagKey: string;
  value: T;
  variant?: string;     // name of the matched variation
  reason?: string;      // "TARGETING_MATCH" | "DEFAULT" | "DISABLED" | "SPLIT"
  errorCode?: string;   // "TYPE_MISMATCH" | "GENERAL"
  errorMessage?: string;
}
```

### Example

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const enabled = await env.FLAGS.getBooleanValue("new-feature", false, {
      userId: "user-42",
    });
    return new Response(enabled ? "Feature on" : "Feature off");
  },
};
```

---

## OpenFeature SDK

Package: `@cloudflare/flagship`

### Server Provider (`FlagshipServerProvider`)

For Workers, Node.js, and server-side JavaScript.

**With binding (recommended inside Workers):**

```typescript
import { OpenFeature } from "@openfeature/server-sdk";
import { FlagshipServerProvider } from "@cloudflare/flagship";

await OpenFeature.setProviderAndWait(
  new FlagshipServerProvider({ binding: env.FLAGS }),
);
const client = OpenFeature.getClient();
const enabled = await client.getBooleanValue("new-checkout", false, {
  targetingKey: "user-42",
});
```

**With app ID (Node.js / non-Worker runtimes):**

```typescript
import { OpenFeature } from "@openfeature/server-sdk";
import { FlagshipServerProvider } from "@cloudflare/flagship";

await OpenFeature.setProviderAndWait(
  new FlagshipServerProvider({
    appId: "<APP_ID>",
    accountId: "<ACCOUNT_ID>",
    authToken: "<API_TOKEN>",
  }),
);
const client = OpenFeature.getClient();
const enabled = await client.getBooleanValue("new-checkout", false, {
  targetingKey: "user-42",
});
```

### Client Provider (`FlagshipClientProvider`)

For browser applications. Pre-fetches flags on init, evaluates synchronously.

```typescript
import { OpenFeature } from "@openfeature/web-sdk";
import { FlagshipClientProvider } from "@cloudflare/flagship";

await OpenFeature.setProviderAndWait(
  new FlagshipClientProvider({
    appId: "<APP_ID>",
    accountId: "<ACCOUNT_ID>",
    authToken: "<API_TOKEN>",
    prefetchFlags: ["promo-banner", "dark-mode"],
  }),
);
await OpenFeature.setContext({ targetingKey: "user-42", plan: "enterprise" });
const client = OpenFeature.getClient();

// Synchronous — no await needed
const showBanner = client.getBooleanValue("promo-banner", false);
```

**Important:** Only flags listed in `prefetchFlags` are available. Unlisted flags return `FLAG_NOT_FOUND`.

### SDK Hooks

```typescript
import { LoggingHook, TelemetryHook } from "@cloudflare/flagship";
OpenFeature.addHooks(new LoggingHook(), new TelemetryHook());
```

---

Continued in `api-rest.md`.
