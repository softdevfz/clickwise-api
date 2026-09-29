# TypeScript client

One file, [`clickwise.ts`](clickwise.ts), no dependencies, generated from the OpenAPI. Works in Node 18+, Bun, Deno, Next.js route handlers and edge functions: anywhere with `fetch`. **Server-side only**: the key must not reach a browser.

Copy the file into your project (for example `lib/clickwise.ts`), then:

```ts
import { Clickwise, ClickwiseError } from "./lib/clickwise";

const cw = new Clickwise(); // reads process.env.CLICKWISE_API_KEY, or pass { apiKey }

const { products } = await cw.lookupProducts({ gtins: "4006381333931,5901234123457", country: "DE" });
for (const p of products ?? []) console.log(p.title, p.price, p.currency, p.url); // url = your tracked link

const page = await cw.searchProducts({ q: "running shoes", country: "ES", limit: 20 });

const link = await cw.createLink({ campaign_id: 123, subid: "post_4711" }, { idempotencyKey: "post-4711" });
console.log(link.cw_link);

try {
  await cw.getReport({ group_by: "day" });
} catch (e) {
  if (e instanceof ClickwiseError) console.error(e.status, e.code, e.requestId, e.retryAfter);
}
```

Every method maps to one operation in the [OpenAPI](../../openapi/openapi.json): `getMe`, `searchProducts`, `lookupProducts`, `listPrograms`, `listJoinablePrograms`, `applyToProgram`, `listLinks`, `createLink`, `createLinksBatch`, `listConversions`, `getReport`, `listClicks`, `getPostback`, `testPostback`, `listPostbackDeliveries` (plus `setPostback` and `rotatePostbackSecret`, which answer 403 to API keys: set those in the portal). Regenerate with `python3 clients/generate.py`.
