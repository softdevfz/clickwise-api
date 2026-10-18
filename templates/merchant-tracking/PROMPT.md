# Prompt: Clickwise sales tracking for your app (Lovable, Bolt, v0)

Copy everything below the line into Lovable, Bolt or v0.

---

Add Clickwise affiliate tracking to this app. Do not change anything else.
1. When a page loads with a `cwclk` query parameter, keep that value for your program's cookie days, use it only to
   attribute the sale to the referring partner, and delete it after that.
   Where the law requires consent for tracking (for example in the EU/EEA and the UK), keep it only after the
   visitor accepts tracking or marketing cookies in your consent banner — whether you store it on the server or
   in a cookie. If the visitor declines, don't keep it.
   Prefer storing it on the server (session or user record). If you use a cookie: first-party, Secure, SameSite=Lax.
   Mention it in your privacy or cookie policy: purpose (affiliate attribution), retention (your program's cookie days)
   and that the click ID is shared with Clickwise.
2. Pass the stored value to checkout:
   - Stripe Checkout or Payment Links, one-time payment: client_reference_id = <cwclk>.
   - Stripe subscriptions: subscription_data.metadata.cwclk = <cwclk> (client_reference_id alone is not enough).
   - Lemon Squeezy: checkout[custom][cwclk] = <cwclk>.
3. Any other payment stack: after a successful payment, from the server only, call
   POST https://partners.clickwise.net/api/v1/conversions/
   Header: X-Merchant-Key: <read from the CLICKWISE_MERCHANT_KEY environment variable>
   JSON: {"campaign": <your campaign ID from the merchant dashboard>, "order_id": <your order id>, "amount": <amount without tax>, "currency": <ISO code>, "cwclk": <stored value>}
   For a subscription, send only its first payment. Only when the whole order is refunded, POST the same order_id again with
   "status": "refunded". For a partial refund, send nothing.
4. Never put the merchant key in browser code or in the repository.
