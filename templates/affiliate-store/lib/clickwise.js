// Server-side only. The API key never reaches the browser.
const API = "https://partners.clickwise.net/api/v1";
const REVALIDATE_SECONDS = 3600; // product endpoints allow 60 requests/minute; an hourly refresh is plenty

export const config = {
  apiKey: process.env.CLICKWISE_API_KEY || "",
  country: (process.env.CLICKWISE_COUNTRY || "DE").toUpperCase(),
  gtins: (process.env.CLICKWISE_GTINS || "").split(",").map((g) => g.trim()).filter(Boolean).slice(0, 100),
  query: process.env.CLICKWISE_QUERY || "sneaker",
  title: process.env.STORE_TITLE || "Top Picks",
  tagline: process.env.STORE_TAGLINE || "Hand-picked products with live prices.",
};

async function get(path, params, headers = {}) {
  const url = new URL(API + path);
  for (const [k, v] of Object.entries(params)) if (v) url.searchParams.set(k, v);
  const res = await fetch(url, {
    headers: { Accept: "application/json", ...headers },
    next: { revalidate: REVALIDATE_SECONDS },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(body?.error?.message || body?.detail || res.statusText);
    err.code = body?.error?.code || `http_${res.status}`;
    err.status = res.status;
    err.requestId = body?.error?.request_id || res.headers.get("X-Request-Id");
    throw err;
  }
  return body;
}

// Returns { mode: "live" | "preview", products: [{ id, gtin, title, brand, price, currency, image, url, merchant, availability }] }
export async function loadProducts() {
  if (!config.apiKey) {
    // Preview: the public catalog sample (no key, no tracked links).
    const data = await get("/public/catalog-sample/", { country: config.country });
    return {
      mode: "preview",
      products: (data.products || []).map((p) => ({
        id: p.gtin, gtin: p.gtin, title: p.name, brand: p.brand, price: p.price, currency: p.currency,
        image: p.image_url, url: null, merchant: null, availability: p.availability,
      })),
    };
  }
  const auth = { "X-API-Key": config.apiKey };
  const data = config.gtins.length
    ? await get("/publisher/products/lookup/", { gtins: config.gtins.join(","), country: config.country }, auth)
    : await get("/publisher/products/", { q: config.query, country: config.country, limit: "24" }, auth);
  // Lookup omits missing, expired or unauthorized items: they simply disappear from the store.
  return { mode: "live", products: data.products || [] };
}
