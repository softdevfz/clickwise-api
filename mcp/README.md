# Clickwise MCP server

Remote MCP server, Streamable HTTP: **`https://partners.clickwise.net/api/v1/mcp`**

Listed in the official MCP Registry as [`net.clickwise/mcp`](https://registry.modelcontextprotocol.io/v0/servers?search=net.clickwise/mcp) (`server.json` in this folder).

## Tools

| Tool | Key needed | What it does |
|---|---|---|
| `find_affiliate_programs` | no | Programs that fit a site, app, newsletter or social channel, ranked by fit |
| `list_programs` | no | Browse and paginate live programs by merchant, category or country |
| `request_tracked_links` | no | Create a provisional affiliate and return live tracked links right away (email optional) |
| `get_monetization_feed` | no | Same, returned as renderable cards, an HTML embed snippet and JSON |
| `get_tracked_link_request` | no | Status and links of an earlier `request_tracked_links` call (needs its access secret) |
| `update_profile` | no | Add claim email and payout method to an instant-link profile (needs its access secret) |
| `list_deals` · `get_deal` | no | Current merchant deals and offers, multilingual |
| `list_news` · `get_news` | no | Program announcements: launches, policy and commission changes |
| `get_catalog_stats` | no | GTIN catalog counts by market and category |
| `request_merchant_onboarding` | no | Start an advertiser application |
| `search_products` | **yes** | Search fresh GTIN products with your tracked links (by GTIN, text, brand, market, category) |
| `get_product_feed` | **yes** | Signed product feed URL for one market (json, csv, tsv or xml) |
| `list_my_programs` | **yes** | Programs you are approved for, with link readiness |
| `create_tracking_links` | **yes** | Tracking links (optionally deep links) for your approved programs |
| `apply_to_program` | **yes** | Ask to join a program |
| `get_performance_report` · `list_conversions` | **yes** | Your conversions and commission by day, week, month, sub-ID, campaign or status |

`tools/list` is the source of truth for current tools and argument schemas.

## Connect

The key is optional: without it you get every public tool. Get one at <https://partners.clickwise.net/developers/>. Never commit it; every config below reads it from the environment or asks for it.

### Claude Code

```sh
# Public tools only
claude mcp add --transport http clickwise https://partners.clickwise.net/api/v1/mcp

# With your key (read from your shell)
claude mcp add --transport http clickwise https://partners.clickwise.net/api/v1/mcp \
  --header "X-API-Key: $CLICKWISE_API_KEY"
```

Or commit [`claude-code.mcp.json`](claude-code.mcp.json) as `.mcp.json` in your project: Claude Code expands `${CLICKWISE_API_KEY}` from the environment.

### Cursor

Copy [`cursor.mcp.json`](cursor.mcp.json) to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global) and export `CLICKWISE_API_KEY` before starting Cursor.

### Claude Desktop

- **No key:** Settings → Connectors → *Add custom connector* → URL `https://partners.clickwise.net/api/v1/mcp`.
- **With key:** merge [`claude-desktop.json`](claude-desktop.json) into `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`) and replace `YOUR_CLICKWISE_API_KEY`. It uses [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) to add the header; needs Node 18+.

### VS Code (Copilot agent mode)

Copy [`vscode.mcp.json`](vscode.mcp.json) to `.vscode/mcp.json`. VS Code asks for the key once and stores it securely.

### Any other client

Streamable HTTP, JSON-RPC 2.0, no session required. Send `X-API-Key: <key>` (or `Authorization: Bearer <key>`) for the keyed tools.

```sh
curl -s https://partners.clickwise.net/api/v1/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

## Try it

Ask your assistant:

- "Which Clickwise programs fit my sneaker blog for readers in Spain?"
- "Give me tracked links for the top two programs for my travel newsletter."
- "Find running shoes in stock in Germany with my Clickwise links and make a comparison table." (needs your key)
- "How much commission did I earn last month by sub-ID?" (needs your key)
