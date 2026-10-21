# Earn commission from your AI assistant

Your assistant searches products in one market, shows offers with a tracked link and earns commission on approved sales. You read the results per sub-ID through the API or receive a signed postback.

Same guide as the developers page, where you get the sandbox key: https://partners.clickwise.net/developers/#monetize-agent

1. Try it with a sandbox key (form on the developers page): search with q and country, for example q=headphones and country=GB. Sandbox links are examples and do not track clicks or earn commission, and a sandbox search returns at most 10 offers.
2. To earn, create a publisher account and use its key. List the programs open to you with GET /api/v1/publisher/programs/joinable/ and apply with POST /api/v1/publisher/programs/apply/; an application is approved or goes to review. A search returns offers only from the programs you are approved in.
3. Search when the user asks for something: GET /api/v1/publisher/products/?q=<3-200 chars>&country=<ISO-2>, or the MCP tool search_products. Each offer has url, its tracked link, and rules, the program's rules for that offer: follow them.
4. Tag each conversation: add subid=<your id: up to 36 characters, letters, digits, _ or -, no personal data> to the search. The links come back with it, and a sale made through one of those links reports it in your conversions.
5. Show the url exactly as returned and let the user open it. Never request the url yourself or prefetch it: every request counts as a click. Tell your users that the links are affiliate links.
6. Read results with GET /api/v1/publisher/conversions/ (per-sub-ID totals in by_subid) or GET /api/v1/publisher/reports/?group_by=subid. Or set a postback URL in the portal: each conversion arrives as a signed request with subid, click_id, transaction_id, order_ref, event and status. If you choose event types for it, only those arrive, and choosing sale.approved also brings sale.commission_validated. Sales from network programs can show as pending validation, with no commission amount until the sale is validated; the amount then arrives in a sale.commission_validated postback with the same transaction_id.
7. Verify every postback: for a POST postback, X-CW-Signature is the hex HMAC-SHA256 of X-CW-Timestamp, a dot and the raw request body, keyed with the postback secret from your portal. Send a test event with POST /api/v1/publisher/postback/test/.
8. Commission is paid on approved sales; the network or the merchant approves each sale.

## curl

```sh
# 1. Search in one market (sandbox key or your publisher key)
curl --get "https://partners.clickwise.net/api/v1/publisher/products/" \
  -H "X-API-Key: $CLICKWISE_API_KEY" \
  --data-urlencode "q=headphones" --data-urlencode "country=GB" --data-urlencode "limit=5" \
  --data-urlencode "subid=chat-42"

# 2. Programs you can apply to, and an application (publisher key)
curl "https://partners.clickwise.net/api/v1/publisher/programs/joinable/" -H "X-API-Key: $CLICKWISE_API_KEY"
curl -X POST "https://partners.clickwise.net/api/v1/publisher/programs/apply/" -H "X-API-Key: $CLICKWISE_API_KEY" \
  -H "Content-Type: application/json" -d '{"program_id": 123}'

# 3. Results per sub-ID
curl --get "https://partners.clickwise.net/api/v1/publisher/reports/" -H "X-API-Key: $CLICKWISE_API_KEY" \
  --data-urlencode "group_by=subid"
```

## JavaScript

```js
// Node 18+. Verify a Clickwise postback before trusting it.
import crypto from "node:crypto";

export function verifyPostback(rawBody, timestamp, signature, secret) {
  const expected = crypto.createHmac("sha256", secret)
    .update(`${timestamp}.`).update(rawBody).digest("hex");
  const a = Buffer.from(expected, "utf8");
  const b = Buffer.from(String(signature || ""), "utf8");
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
// In your handler: verifyPostback(req.rawBody, req.headers["x-cw-timestamp"],
//   req.headers["x-cw-signature"], process.env.CLICKWISE_POSTBACK_SECRET)
```

## Python

```python
# Verify a Clickwise postback before trusting it.
import hashlib
import hmac
import os


def verify_postback(raw_body: bytes, timestamp: str, signature: str) -> bool:
    secret = os.environ["CLICKWISE_POSTBACK_SECRET"].encode()
    expected = hmac.new(secret, timestamp.encode() + b"." + raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")
```
