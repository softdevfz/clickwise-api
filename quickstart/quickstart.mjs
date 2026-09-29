// Clickwise in five minutes, with Node 18+ (no dependencies).
// Run: node quickstart/quickstart.mjs      (set CLICKWISE_API_KEY for the keyed steps)
const BASE = "https://partners.clickwise.net";
const KEY = process.env.CLICKWISE_API_KEY;

async function getJson(path, { key, params } = {}) {
  const url = new URL(BASE + path);
  for (const [k, v] of Object.entries(params ?? {})) url.searchParams.set(k, v);
  const res = await fetch(url, { headers: { Accept: "application/json", ...(key ? { "X-API-Key": key } : {}) } });
  const body = await res.json();
  if (!res.ok) throw new Error(`${res.status} ${body?.error?.code}: ${body?.error?.message ?? body?.detail} (request ${body?.error?.request_id})`);
  return body;
}

async function mcpCall(name, args) {
  const res = await fetch(`${BASE}/api/v1/mcp`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json, text/event-stream" }, // public tool: no key
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/call", params: { name, arguments: args } }),
  });
  return (await res.json()).result;
}

// 1) No key: live catalog size
const stats = await getJson("/api/v1/public/catalog-stats/");
console.log(`1) ${stats.fresh.offers_with_gtin} fresh offers with GTIN in ${stats.fresh.countries} markets`);

// 2) No key: a sample product (no tracked link)
const sample = await getJson("/api/v1/public/catalog-sample/", { params: { country: "DE" } });
const first = sample.products[0];
console.log(`2) Sample: ${first.gtin} | ${first.name} | ${first.price} ${first.currency}`);

// 3) No key: programs that fit a site, through the MCP server
const programs = await mcpCall("find_affiliate_programs", { topic: "sneakers", country: "ES", channel: "site", limit: 3 });
console.log(`3) ${programs.structuredContent.count} programs fit a sneaker site in ES`);

if (!KEY) {
  console.log("Set CLICKWISE_API_KEY (https://partners.clickwise.net/developers/) to run steps 4-5.");
  process.exit(0);
}

// 4) With key: search products and get YOUR tracked links
const found = await getJson("/api/v1/publisher/products/", { key: KEY, params: { q: "sneaker", country: "DE", limit: "3" } });
for (const p of found.products) console.log(`4) ${p.gtin} ${p.title} ${p.price} ${p.currency} -> ${p.url}`);

// 5) With key: refresh the sample product by GTIN (omitted if your key cannot sell it)
const lookup = await getJson("/api/v1/publisher/products/lookup/", { key: KEY, params: { gtins: first.gtin, country: "DE" } });
console.log(lookup.products.length ? `5) ${lookup.products[0].url}` : "5) That GTIN is not available for your key; try one from step 4.");
