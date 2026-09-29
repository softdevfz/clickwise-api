import { config, loadProducts } from "../lib/clickwise";

export const revalidate = 3600;

const AVAILABILITY = {
  in_stock: "In stock",
  out_of_stock: "Out of stock",
  preorder: "Pre-order",
  backorder: "Backorder",
};

function formatPrice(price, currency) {
  const n = Number(price);
  if (!Number.isFinite(n) || !currency) return price;
  try {
    return new Intl.NumberFormat("en", { style: "currency", currency }).format(n);
  } catch {
    return `${n.toFixed(2)} ${currency}`;
  }
}

function explain(err) {
  if (err.code === "authentication_failed" || err.code === "not_authenticated") {
    return "Your CLICKWISE_API_KEY was rejected. Check the value in your hosting settings.";
  }
  if (err.code === "api_key_scope" || err.status === 403) {
    return "Your key has no product feed access for this market yet. Ask partnerships@clickwise.net to enable it.";
  }
  if (err.code === "throttled") return "Rate limited. The page will retry on the next refresh.";
  return "Products are temporarily unavailable.";
}

export default async function Home() {
  let result = { mode: config.apiKey ? "live" : "preview", products: [] };
  let error = null;
  try {
    result = await loadProducts();
  } catch (err) {
    console.error("Clickwise request failed", err.code, err.requestId);
    error = err;
  }
  const preview = result.mode === "preview";
  const itemList = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: result.products.map((p, i) => ({
      "@type": "ListItem",
      position: i + 1,
      item: {
        "@type": "Product",
        name: p.title,
        gtin: p.gtin,
        image: p.image,
        offers: { "@type": "Offer", price: p.price, priceCurrency: p.currency },
      },
    })),
  };

  return (
    <main>
      <header className="hero">
        <h1>{config.title}</h1>
        <p>{config.tagline}</p>
        <p className="disclosure">
          This page contains affiliate links. If you buy through them we may earn a commission, at no extra cost to you.
        </p>
      </header>

      {preview && (
        <div className="notice">
          <strong>Preview mode.</strong> You are seeing the public Clickwise sample for {config.country}, without links.
          Add <code>CLICKWISE_API_KEY</code> to your environment to show your own tracked links (get a key at{" "}
          <a href="https://partners.clickwise.net/developers/">partners.clickwise.net/developers</a>), then redeploy.
        </div>
      )}
      {error && <div className="notice error">{explain(error)}</div>}

      <section className="grid">
        {result.products.map((p) => (
          <article key={p.id || p.gtin} className="card">
            {p.image && <img src={p.image} alt={p.title} loading="lazy" referrerPolicy="no-referrer" />}
            <h2>{p.title}</h2>
            <p className="meta">
              {[p.brand, p.merchant?.name, AVAILABILITY[p.availability]].filter(Boolean).join(" · ")}
            </p>
            <p className="price">{formatPrice(p.price, p.currency)}</p>
            {p.url ? (
              <a className="buy" href={p.url} target="_blank" rel="sponsored nofollow noopener">
                View offer
              </a>
            ) : (
              <span className="buy disabled">Link appears with your API key</span>
            )}
          </article>
        ))}
      </section>

      {!error && result.products.length === 0 && (
        <p className="empty">No products right now. Try other GTINs, another query or another market.</p>
      )}

      <footer>
        Prices and availability as last checked (refreshed hourly). Product data by{" "}
        <a href="https://partners.clickwise.net/developers/">Clickwise</a>.
      </footer>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(itemList).replace(/</g, "\\u003c") }} />
    </main>
  );
}
