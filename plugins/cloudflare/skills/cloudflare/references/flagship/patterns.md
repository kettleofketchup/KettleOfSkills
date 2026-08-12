# Flagship Patterns & Best Practices

## Evaluating Flags in Workers (Binding)

### Simple Boolean Toggle

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const showNewUI = await env.FLAGS.getBooleanValue("new-ui", false, {
      userId: "user-42",
    });

    if (showNewUI) {
      return new Response("New UI");
    }
    return new Response("Classic UI");
  },
};
```

### Multi-Variant String Flag

```typescript
const checkoutFlow = await env.FLAGS.getStringValue(
  "checkout-flow",
  "original",
  { userId, country: "US" },
);

switch (checkoutFlow) {
  case "streamlined":
    return handleStreamlined(request);
  case "one-click":
    return handleOneClick(request);
  default:
    return handleOriginal(request);
}
```

### JSON Config Flag

```typescript
interface RateLimitConfig {
  rpm: number;
  burst: number;
}

const limits = await env.FLAGS.getObjectValue<RateLimitConfig>(
  "rate-limits",
  { rpm: 100, burst: 20 },
  { plan: userPlan },
);
```

### Using Details for Observability

```typescript
const details = await env.FLAGS.getBooleanDetails("new-checkout", false, {
  userId: "user-42",
});

console.log(details.value);     // true
console.log(details.variant);   // "on"
console.log(details.reason);    // "TARGETING_MATCH"
console.log(details.errorCode); // undefined (no error)
```

---

## Evaluating Flags with OpenFeature (Workers)

### Binding Passthrough (Recommended)

```typescript
import { OpenFeature } from "@openfeature/server-sdk";
import { FlagshipServerProvider } from "@cloudflare/flagship";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    await OpenFeature.setProviderAndWait(
      new FlagshipServerProvider({ binding: env.FLAGS }),
    );
    const client = OpenFeature.getClient();

    const enabled = await client.getBooleanValue("new-checkout", false, {
      targetingKey: "user-42",
      plan: "enterprise",
      country: "US",
    });

    return new Response(enabled ? "New checkout" : "Standard checkout");
  },
};
```

### Migration from Another Provider

Only the provider initialization changes — evaluation call sites stay the same:

```typescript
// ❌ Before (LaunchDarkly)
await OpenFeature.setProviderAndWait(
  new LaunchDarklyProvider({ sdkKey: "..." }),
);

// ✅ After (Flagship)
await OpenFeature.setProviderAndWait(
  new FlagshipServerProvider({ binding: env.FLAGS }),
);

// Evaluation code is unchanged
const enabled = await client.getBooleanValue("my-flag", false, {
  targetingKey: "user-42",
});
```

---

Continued in `patterns-management.md`.
