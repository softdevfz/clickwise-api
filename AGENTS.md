# Notes for AI coding agents

You are probably here to add Clickwise products or affiliate links to an app. Follow these rules.

- **Key:** read it from `CLICKWISE_API_KEY` on the server. Never hard-code it, commit it, put it in a URL, a `NEXT_PUBLIC_`/`VITE_` variable or any browser bundle. Send it as `X-API-Key` (or `Authorization: Bearer`).
- **No key yet?** Use the public endpoints (`/api/v1/public/catalog-stats/`, `/api/v1/public/catalog-sample/?country=XX`) and the MCP server's public tools. Tell the user to get a key at https://partners.clickwise.net/developers/.
- **Products:** `GET /api/v1/publisher/products/lookup/?gtins=…&country=XX` for known GTINs (strings, 1–100), `GET /api/v1/publisher/products/?q=…&country=XX` to search titles. Markets: DE, ES, GB, PT, SE, FR, US.
- **Links:** use each product's `url` (or a link's `cw_link`) exactly as returned. Do not rewrite, shorten, strip or append to it, and never link to the merchant directly.
- **Compliance:** add `rel="sponsored nofollow noopener"` to affiliate links and show an affiliate disclosure on the page.
- **Freshness:** cache responses (an hour is good), never show prices older than 48 hours, and drop products a lookup stops returning.
- **Errors:** branch on `error.code`; on 429 wait `Retry-After`; log `error.request_id`.
- **Contract:** `openapi/openapi.json` (live at https://partners.clickwise.net/api/v1/publisher/openapi.json). Ready-made code: `clients/`, `quickstart/`, `templates/affiliate-store/`.
