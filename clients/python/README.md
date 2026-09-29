# Python client

One module, standard library only, generated from the OpenAPI. Python 3.8+.

```sh
pip install "git+https://github.com/softdevfz/clickwise-api#subdirectory=clients/python"
# or copy clients/python/clickwise/__init__.py into your project as clickwise.py
```

```python
from clickwise import Clickwise, ClickwiseError

cw = Clickwise()  # reads CLICKWISE_API_KEY, or Clickwise(api_key=...)

for p in cw.lookup_products(gtins="4006381333931,5901234123457", country="DE")["products"]:
    print(p["title"], p["price"], p["currency"], p["url"])  # url = your tracked link

page = cw.search_products(q="running shoes", country="ES", limit=20)

link = cw.create_link({"campaign_id": 123, "subid": "post_4711"}, idempotency_key="post-4711")
print(link["cw_link"])

try:
    cw.get_report(group_by="day")
except ClickwiseError as e:
    print(e.status, e.code, e.request_id, e.retry_after)
```

Methods: `get_me`, `search_products`, `lookup_products`, `list_programs`, `list_joinable_programs`, `apply_to_program`, `list_links`, `create_link`, `create_links_batch`, `list_conversions`, `get_report`, `list_clicks`, `get_postback`, `test_postback`, `list_postback_deliveries` (plus `set_postback` and `rotate_postback_secret`, which answer 403 to API keys: set those in the portal). Responses are plain dicts typed with `TypedDict`s. Regenerate with `python3 clients/generate.py`.
