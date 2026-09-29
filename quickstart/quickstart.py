"""Clickwise in five minutes, with Python 3.8+ (standard library only).

Run: python3 quickstart/quickstart.py      (set CLICKWISE_API_KEY for the keyed steps)
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://partners.clickwise.net"
KEY = os.environ.get("CLICKWISE_API_KEY")


def get_json(path, params=None, key=None):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    headers = {"Accept": "application/json", **({"X-API-Key": key} if key else {})}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        try:
            err = json.load(e).get("error", {})
        except ValueError:
            err = {}
        raise RuntimeError(f"{e.code} {err.get('code')}: {err.get('message')} (request {err.get('request_id')})") from None


def mcp_call(name, arguments):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}).encode()
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}  # public tool: no key
    with urllib.request.urlopen(urllib.request.Request(BASE + "/api/v1/mcp", data=body, headers=headers), timeout=60) as res:
        return json.load(res)["result"]


# 1) No key: live catalog size
try:
    fresh = get_json("/api/v1/public/catalog-stats/")["fresh"]
    print(f"1) {fresh['offers_with_gtin']} fresh offers with GTIN in {fresh['countries']} markets")
except RuntimeError:
    print("1) Catalog stats are refreshing; skipping to step 2")

# 2) No key: a sample product (no tracked link)
first = get_json("/api/v1/public/catalog-sample/", {"country": "DE"})["products"][0]
print(f"2) Sample: {first['gtin']} | {first['name']} | {first['price']} {first['currency']}")

# 3) No key: programs that fit a site, through the MCP server
found = mcp_call("find_affiliate_programs", {"topic": "sneakers", "country": "ES", "channel": "site", "limit": 3})
print(f"3) {found['structuredContent']['count']} programs fit a sneaker site in ES")

if not KEY:
    print("Set CLICKWISE_API_KEY (https://partners.clickwise.net/developers/) to run steps 4-5.")
    sys.exit(0)

try:
    # 4) With key: search products and get YOUR tracked links
    for p in get_json("/api/v1/publisher/products/", {"q": "sneaker", "country": "DE", "limit": 3}, KEY)["products"]:
        print(f"4) {p['gtin']} {p['title']} {p['price']} {p['currency']} -> {p['url']}")

    # 5) With key: refresh the sample product by GTIN (omitted if your key cannot sell it)
    products = get_json("/api/v1/publisher/products/lookup/", {"gtins": first["gtin"], "country": "DE"}, KEY)["products"]
    print(f"5) {products[0]['url']}" if products else "5) That GTIN is not available for your key; try one from step 4.")
except RuntimeError as e:
    sys.exit(str(e))
