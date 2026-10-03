# Clickwise in n8n

Use the Clickwise MCP server from [n8n](https://n8n.io) with its built-in MCP nodes. There is no community node to install. Tested on self-hosted n8n 2.41: the first two workflows run end to end, and the AI agent one imports cleanly (it needs your own chat model credential to run).

| n8n node | Use it to |
|---|---|
| **MCP Client** | Call one Clickwise tool as a normal workflow step |
| **MCP Client Tool** | Give an **AI Agent** the Clickwise tools |

Both take the same settings:

- **MCP Endpoint URL:** `https://partners.clickwise.net/api/v1/mcp`
- **Server Transport:** HTTP Streamable
- **Authentication:** *None* for the public tools, or *Header Auth* with your key (see step 2)

Import a workflow in n8n with **Workflows → Import from File**, or paste the JSON into the canvas.

## 1. No key: find affiliate programs (2 minutes)

Import [`clickwise-find-programs.json`](clickwise-find-programs.json) and click **Execute workflow**.

The **MCP Client** node calls `find_affiliate_programs` with a topic, a country and a channel. You get `structuredContent.results`: programs ranked by fit, the reasons for each score, and whether a tracked link can be issued right away. Change the JSON in the node to describe your own site, newsletter or social channel.

Other tools that work without a key: `list_programs`, `list_deals`, `get_deal`, `list_news`, `get_news`, `get_catalog_stats` and `request_tracked_links`. The [tool list](../README.md#tools) has the full set.

## 2. With your key: products by GTIN with your tracked links

1. Get a key at <https://partners.clickwise.net/developers/>. To try it first, ask for a free **sandbox key** (no account, 14 days): `search_products` works the same, with example links that never earn. Switch to your **publisher key** to earn from every sale.
2. Import [`clickwise-products-by-gtin.json`](clickwise-products-by-gtin.json).
3. Open the **Clickwise: search products** node. Under **Credential**, choose *Create new credential*, then **Header Auth**. Set **Name** to `X-API-Key` and **Value** to your key. n8n stores it encrypted. Never put the key in the workflow JSON.
4. In **What to search**, set `gtin` (an EAN/UPC) or `text`, and `country` (two-letter code, for example `GB`). Leave unused fields empty.
5. Execute the workflow.

Each product comes back with `gtin`, `title`, `brand`, `category`, `price`, `regular_price`, `currency`, `description`, `size`, `color`, `image`, `url`, `merchant`, `availability`, `country` and `updated_at`. **`url` is your own Clickwise tracked link** (with a sandbox key, an example link). It stays the same between calls for the same product.

Feed the results into whatever comes next: a Google Sheet, a WordPress post, a Telegram or Discord deals bot, or a price-comparison table.

## 3. AI agent with the Clickwise tools

Import [`clickwise-ai-agent.json`](clickwise-ai-agent.json): **Chat Trigger → AI Agent**, with a **Chat model** and the **Clickwise MCP** node (*MCP Client Tool*).

1. Add a credential to **Chat model**. It uses OpenAI by default; any chat model node works.
2. Add the same Header Auth credential from step 2 to **Clickwise MCP**.
3. Open the chat and ask, for example: *"Find cordless drills in the UK with my links and make a comparison table."*

**Tools to Include → Selected** limits the agent to `find_affiliate_programs`, `search_products` and `list_deals` so it stays focused. Add more from the list if you need them. The system message tells the agent to return links exactly as the tools give them.

## Rules for links

- Publish `url` exactly as returned. Never rebuild, shorten or edit a Clickwise link.
- Mark links as affiliate links. On web pages, use `rel="sponsored"`.
- Prices and stock change. Refresh products before you publish them.

## Troubleshooting

| You see | Fix |
|---|---|
| `An active affiliate API key is required.` | A keyed tool ran without a valid key. Check the Header Auth credential (header name exactly `X-API-Key`), or use **Bearer Auth** with the same key. A sandbox key covers `search_products` only; the other account tools need your publisher key. |
| `Product feed access is not active for this affiliate.` | Your account does not have product feed access yet. Ask for it at [partnerships@clickwise.net](mailto:partnerships@clickwise.net) or on the AI line (+1 646 362 1368); the Clickwise team turns it on. The REST API answers the same until it is active. |
| `catalog_unavailable` | The catalog was busy for a moment. Run the workflow again after a few seconds. |
| The tool list in the node is empty | Check the endpoint URL and set **Server Transport** to *HTTP Streamable*. |
| HTTP 429 | You hit the rate limit. Wait and retry. |
