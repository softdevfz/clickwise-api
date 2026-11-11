# Clickwise MCP server

Remote MCP server, Streamable HTTP: **`https://partners.clickwise.net/api/v1/mcp`**

Listed in the official MCP Registry as [`net.clickwise/mcp`](https://registry.modelcontextprotocol.io/v0/servers?search=net.clickwise/mcp) (`server.json` in this folder).

## Tools

| Tool | Key needed | What it does |
|---|---|---|
| `find_affiliate_programs` | no | Programs that fit a site, app, newsletter or social channel, ranked by fit |
| `list_programs` | no | Browse and paginate live programs by merchant, category or country |
| `request_tracked_links` | no | Create a provisional affiliate and return live tracked links (email optional) |
| `get_monetization_feed` | no | Same, returned as renderable cards, an HTML embed snippet and JSON |
| `get_tracked_link_request` | no | Status and links of an earlier `request_tracked_links` call (needs its access secret) |
| `update_profile` | no | Add claim email and payout method to a provisional link profile (needs its access secret) |
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

### Partial product feeds

`get_product_feed` still returns a working feed when a few rows cannot carry your tracked link. In that case the response adds `catalog_warning`, and `products` counts only the rows that are in the feed:

```json
"catalog_warning": {"code": "partial_catalog", "skipped_rows": 3, "reasons": {"<reason_code>": 3}}
```

`reasons` gives a count per fixed reason code. A complete feed has no `catalog_warning`.

## Connect

The key is optional: without it you get every public tool. Get one at <https://partners.clickwise.net/developers/>. Never commit it; every config below reads it from the environment or asks for it.

Links returned by these tools are affiliate links: if someone buys through them, the publisher who shares them may receive a commission from the store.

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

[![Add to Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=clickwise&config=eyJ1cmwiOiJodHRwczovL3BhcnRuZXJzLmNsaWNrd2lzZS5uZXQvYXBpL3YxL21jcCJ9)

The button adds the server without a key (public tools). Cursor asks you to confirm before it installs it. For the tools that need a key, copy [`cursor.mcp.json`](cursor.mcp.json) to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global) and export `CLICKWISE_API_KEY` before starting Cursor.

### Replit (Agent)

[![Add to Replit](https://replit.com/badge?caption=Add%20to%20Replit)](https://replit.com/integrations?mcp=eyJkaXNwbGF5TmFtZSI6IkNsaWNrd2lzZSIsImJhc2VVcmwiOiJodHRwczovL3BhcnRuZXJzLmNsaWNrd2lzZS5uZXQvYXBpL3YxL21jcCJ9)

The button adds the server to your Replit account without a key (public tools), and Replit asks you to authorize it. To add it by hand: Integrations → MCP Servers → add a server with the URL `https://partners.clickwise.net/api/v1/mcp`. For the tools that need a key, add the header `X-API-Key` with your key.

### Claude Desktop

- **No key:** Settings → Connectors → *Add custom connector* → URL `https://partners.clickwise.net/api/v1/mcp`.
- **With key:** merge [`claude-desktop.json`](claude-desktop.json) into `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`) and replace `YOUR_CLICKWISE_API_KEY`. It uses [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) to add the header; needs Node 18+.

### VS Code (Copilot agent mode)

Copy [`vscode.mcp.json`](vscode.mcp.json) to `.vscode/mcp.json`. VS Code asks for the key once and stores it securely.

### ChatGPT (developer mode)

For ChatGPT Business and Enterprise/Edu workspaces on the web; a workspace admin turns on developer mode first.

1. Plugins → **+** → *Add custom MCP server*.
2. Name `Clickwise`, URL `https://partners.clickwise.net/api/v1/mcp`.
3. Authentication: *No authentication* gives the public tools. *OAuth or no authentication* also lets you sign in with your Clickwise affiliate account for the tools that need it (OAuth 2.1 with dynamic client registration).
4. Review the warning, create it and install it.

Menu names can change: see OpenAI's guide, [Connecting custom MCP servers in ChatGPT](https://help.openai.com/en/articles/12584461).

### Grok

1. Open [grok.com/connectors](https://grok.com/connectors) → *New Connector* → *Custom*.
2. URL `https://partners.clickwise.net/api/v1/mcp`.
3. If Grok asks you to sign in, use your Clickwise affiliate account; the public tools work without it.

On Grok Business and Enterprise, an admin adds the connector first. See xAI's guide, [Connectors](https://docs.x.ai/grok/connectors).

### Bolt

1. Connectors → *Custom MCP server*.
2. URL `https://partners.clickwise.net/api/v1/mcp`, transport Streamable HTTP.
3. Authentication: *None* gives the public tools. You can turn the connector on for all your projects.

### v0

1. *Add MCP* in the prompt form, or in MCP Connections.
2. URL `https://partners.clickwise.net/api/v1/mcp`.
3. Authentication: *No Auth* gives the public tools. For the tools that need a key, choose *Custom Headers* with `X-API-Key` and your key, or *Bearer* with your key.

### Lovable

1. Connectors → *Add custom* → *MCP server*, with the URL `https://partners.clickwise.net/api/v1/mcp`. If *MCP server* is grayed out, a workspace admin has turned custom MCP servers off.
2. Authentication: *No authentication* gives the public tools. For the tools that need a key, choose *Bearer token or API key* and paste your key.
3. In Lovable, an MCP server gives context to the chat while you build. It is not part of your published app. To show products and tracked links in the published app, the app calls the REST API from its server code: paste [`templates/affiliate-store/PROMPT.md`](../templates/affiliate-store/PROMPT.md) to set that up.

Menu names in Bolt, v0 and Lovable can change: check each tool's own guide for custom MCP servers.

### n8n

Use n8n's built-in **MCP Client** node (one tool per step) or **MCP Client Tool** node (tools for an AI Agent) with the endpoint above and *HTTP Streamable*. Three importable workflows and a step-by-step guide are in [`n8n/`](n8n/README.md).

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
- "Find products with a GTIN in my program feeds, with my Clickwise links." (needs your key)
- "Find smartwatches sold in Germany, with my Clickwise links." (publisher key or sandbox key)
- "How much commission did I earn last month by sub-ID?" (needs your key)

## Directory listing

The text we use when a directory or marketplace lists this server.

- **Name:** Clickwise
- **Short description:** Affiliate programs, deals, tracked links and product search.
- **Description:** Clickwise is an affiliate network with a remote MCP server and a REST API. With this server an agent can find affiliate programs that fit a site or channel, list current deals and create tracked affiliate links; with an API key it can also search products by GTIN or title. Program discovery and deals work without a key. Commission rates and terms are shown for each program. Links returned by these tools are affiliate links: if someone buys through them, the publisher who shares them may receive a commission from the store.
- **Server (Streamable HTTP, no key):** `https://partners.clickwise.net/api/v1/mcp`
- **Icon:** [`assets/icon.png`](../assets/icon.png)
- **Contact:** partnerships@clickwise.net
