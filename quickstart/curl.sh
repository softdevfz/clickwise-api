#!/usr/bin/env sh
# Clickwise in five minutes, with curl. Steps 1-3 need no key.
# Run: sh quickstart/curl.sh            (add CLICKWISE_API_KEY=... to run steps 4-6)
set -e
BASE=https://partners.clickwise.net

echo "1) Live catalog size (no key)"
curl -s "$BASE/api/v1/public/catalog-stats/" | python3 -c 'import json,sys; d=json.load(sys.stdin)["fresh"]; print(d["offers_with_gtin"], "fresh offers with GTIN,", d["countries"], "markets,", d["brands"], "brands")'

echo "2) Sample products in one market (no key; no tracked links)"
curl -s "$BASE/api/v1/public/catalog-sample/?country=DE" | python3 -c 'import json,sys; p=json.load(sys.stdin)["products"][0]; print(p["gtin"], "|", p["name"], "|", p["price"], p["currency"])'

echo "3) Ask the MCP server which programs fit your site (no key)"
curl -s "$BASE/api/v1/mcp" \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"find_affiliate_programs","arguments":{"topic":"sneakers","country":"ES","channel":"site","limit":3}}}' \
  | python3 -c 'import json,sys; r=json.load(sys.stdin)["result"]["structuredContent"]; print(r["count"], "matching programs")'

if [ -z "$CLICKWISE_API_KEY" ]; then
  echo "Set CLICKWISE_API_KEY (https://partners.clickwise.net/developers/) to run steps 4-6."
  exit 0
fi

echo "4) Who am I, and what can this key do?"
curl -s "$BASE/api/v1/publisher/me/" -H "X-API-Key: $CLICKWISE_API_KEY"; echo

echo "5) Search products with YOUR tracked links"
curl -s --get "$BASE/api/v1/publisher/products/" -H "X-API-Key: $CLICKWISE_API_KEY" \
  --data-urlencode 'q=sneaker' --data-urlencode 'country=DE' --data-urlencode 'limit=3'; echo

echo "6) Look products up by GTIN (1-100, comma-separated) for fresh price, stock and link"
curl -s --get "$BASE/api/v1/publisher/products/lookup/" -H "X-API-Key: $CLICKWISE_API_KEY" \
  --data-urlencode 'gtins=4006381333931' --data-urlencode 'country=DE'; echo
