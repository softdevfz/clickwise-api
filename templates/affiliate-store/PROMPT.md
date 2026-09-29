# Prompt: affiliate store on Clickwise (Lovable, Bolt, v0)

Copy everything below the line into Lovable, Bolt or v0. Replace the three values in square brackets first.

---

Build a fast, mobile-first affiliate store for **[NICHE, e.g. trail running gear]** aimed at shoppers in **[COUNTRY CODE: DE, ES, GB, PT, SE, FR or US]**.

**Data source: the Clickwise Publisher API** (docs: https://partners.clickwise.net/developers/, OpenAPI: https://partners.clickwise.net/api/v1/publisher/openapi.json).

1. The API key is a secret named `CLICKWISE_API_KEY`. Call the API **only from server-side code** (Lovable: a Supabase Edge Function; Bolt and v0: a Next.js server component or route handler). Never put the key in browser code, a `NEXT_PUBLIC_`/`VITE_` variable, a URL or the repository.
2. Featured products come from their GTINs: `GET https://partners.clickwise.net/api/v1/publisher/products/lookup/?gtins=GTIN1,GTIN2&country=[COUNTRY CODE]` with header `X-API-Key: <CLICKWISE_API_KEY>`. Start with these GTINs: **[COMMA-SEPARATED GTINS, or leave empty]**. Keep GTINs as strings (leading zeros matter).
3. If the GTIN list is empty, use search instead: `GET https://partners.clickwise.net/api/v1/publisher/products/?q=<phrase>&country=[COUNTRY CODE]&limit=24` (the phrase must be 3–200 characters and matches product titles).
4. Both return `{"products": [{"id", "gtin", "title", "price", "currency", "image", "url", "merchant": {"id", "name"}, "availability", "country", "updated_at"}], "count", "next_offset", "freshness_hours"}`. `price` is a decimal string.
5. `url` is the tracked affiliate link. Use it exactly as returned for the "View offer" button: never rewrite it, strip it, append parameters or link to the merchant directly. Open it in a new tab with `rel="sponsored nofollow noopener"`.
6. Show an affiliate disclosure near the top of every page: "This page contains affiliate links. If you buy through them we may earn a commission, at no extra cost to you."
7. Cache API responses for one hour on the server and never show a price older than 48 hours. Products missing from a lookup response are no longer available: hide them.
8. Errors have one shape: `{"error": {"code", "message", "status", "request_id"}}`. On 401 show "API key rejected"; on 429 respect `Retry-After`; log `request_id`.
9. **Preview mode:** if `CLICKWISE_API_KEY` is not set, load `GET https://partners.clickwise.net/api/v1/public/catalog-sample/?country=[COUNTRY CODE]` (no key; fields `gtin`, `name`, `brand`, `price`, `currency`, `image_url`, `availability`), show those products without buy buttons, and show a banner: "Preview mode: add CLICKWISE_API_KEY to show tracked links. Get a key at partners.clickwise.net/developers."

Design: a hero with the store name and a one-line promise, a responsive product grid (image, title, brand or merchant, price formatted for the currency, availability, a "View offer" button), filters by price and availability, and Product/Offer JSON-LD for each item. No sign-up, no cart, no checkout: the purchase happens on the merchant's site.
