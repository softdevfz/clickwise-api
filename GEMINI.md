# Clickwise extension for Gemini CLI

This extension connects the Clickwise remote MCP server at <https://partners.clickwise.net/api/v1/mcp>. Clickwise is an affiliate network: use its tools to find affiliate programs, deals and products and to return tracked links.

## Which tool

- Programs that fit a site, app, newsletter or social channel: `find_affiliate_programs`.
- A tracked link without an account: `request_tracked_links` (creates a provisional affiliate; email optional). With an API key: `create_tracking_links`.
- Link cards, an HTML embed or a JSON feed: `get_monetization_feed`. Product feed for one market (needs a key): `get_product_feed`.
- Products by GTIN or title (needs a key): `search_products`.
- Deals and news: `list_deals`, `get_deal`, `list_news`, `get_news`.

## Rules

- Give each tracked link exactly as the tool returns it. Do not shorten, rewrite or replace it with the merchant's own URL.
- When links go on a page: `rel="sponsored nofollow noopener"` and a visible affiliate disclosure.
- Report commission rates and terms only as the tools return them. Do not promise earnings or approval.
- Never print or store an API key or an access secret in files, URLs or logs.

## Using an API key

Tools such as `search_products` and `get_product_feed` need a publisher key, which you request at <https://partners.clickwise.net/developers/>. Add the server with the key from your environment:

```sh
gemini mcp add --transport http clickwise https://partners.clickwise.net/api/v1/mcp --header "X-API-Key: $CLICKWISE_API_KEY"
```

More: https://github.com/softdevfz/clickwise-api
