# Affiliate store template (Next.js)

A one-page affiliate storefront: products by GTIN from the Clickwise Publisher API, live prices, and **your** tracked links. Refreshes hourly. No database, no client-side key.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fsoftdevfz%2Fclickwise-api&root-directory=templates%2Faffiliate-store&project-name=my-affiliate-store&repository-name=my-affiliate-store)
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/softdevfz/clickwise-api)

It deploys without a key in **preview mode** (the public Clickwise sample, no links). Add `CLICKWISE_API_KEY` in your hosting settings and redeploy to switch to your tracked links. Get a key at <https://partners.clickwise.net/developers/>.

## Run locally

```sh
cp .env.example .env.local      # then fill in CLICKWISE_API_KEY
npm install
npm run dev                     # http://localhost:3000
```

## Configure

| Variable | Default | Meaning |
|---|---|---|
| `CLICKWISE_API_KEY` | empty | Your publisher API key. Server-side only: never `NEXT_PUBLIC_…`. Empty = preview mode |
| `CLICKWISE_COUNTRY` | `DE` | Market: `DE`, `ES`, `GB`, `PT`, `SE`, `FR`, `US` |
| `CLICKWISE_GTINS` | empty | Comma-separated GTINs (1–100) to feature. Wins over the query |
| `CLICKWISE_QUERY` | `sneaker` | Used when there are no GTINs: products whose title contains this phrase |
| `STORE_TITLE` · `STORE_TAGLINE` | `Top Picks` · … | Storefront copy |

## How it works

- `lib/clickwise.js` calls `GET /api/v1/publisher/products/lookup/?gtins=…` (or `/products/?q=…`) on the server with `X-API-Key`, cached for an hour (`revalidate = 3600`). Product endpoints allow 60 requests per minute per account, so one request an hour is nothing.
- Each product's `url` is a Clickwise link already attributed to you. Publish it as is: do not rewrite it or append parameters.
- Lookup omits products that expired, went out of your access or no longer exist, so stale offers disappear by themselves.
- Links carry `rel="sponsored nofollow noopener"`, and the page shows an affiliate disclosure. Keep both.
- Prices are shown as of the last refresh; don't cache them for more than 48 hours.

## Build it with an AI app builder instead

Paste [`PROMPT.md`](PROMPT.md) into Lovable, Bolt or v0.
