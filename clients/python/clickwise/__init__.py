"""Generated from openapi/openapi.json (Clickwise Publisher API 1.1) by clients/generate.py. Do not edit by hand."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Literal, Optional, TypedDict

DEFAULT_BASE_URL = "https://partners.clickwise.net/api/v1/publisher"
API_VERSION = "1.1"


class ApiError(TypedDict, total=False):
    detail: Any
    error: Dict[str, Any]


class Me(TypedDict, total=False):
    affiliate: Dict[str, Any]
    api_version: str
    access: Dict[str, Any]
    rate_limits: Dict[str, Any]


class Product(TypedDict, total=False):
    id: str
    gtin: str
    title: str
    price: str
    currency: str
    image: str
    url: str
    merchant: Dict[str, Any]
    availability: Literal["in_stock", "out_of_stock", "preorder", "backorder"]
    country: str
    updated_at: str


class ProductPage(TypedDict, total=False):
    products: List[Product]
    count: int
    limit: int
    offset: int
    next_offset: Optional[int]
    freshness_hours: int


class Program(TypedDict, total=False):
    id: Optional[int]
    campaign_id: str
    campaign_name: str
    landing_url: str
    currency: str
    link_ready: bool
    link_ready_error: Optional[str]
    existing_links: int
    assignment_status: Literal["assigned", "not_assigned"]
    can_apply: bool
    commission: Dict[str, Any]
    program: Dict[str, Any]


class Page(TypedDict, total=False):
    total: int
    page: int
    page_size: int
    pages: int


class Link(TypedDict, total=False):
    created: bool
    deeplink_id: str
    cw_link: str
    destination_link: str
    subid: str
    certified_tracking_link: str


class LinkRequest(TypedDict, total=False):
    campaign_id: str | int
    program_id: int
    subid: str
    landing_url: str


class LinkBatchResult(TypedDict, total=False):
    data: List[Dict[str, Any]]
    created: int
    existing: int
    failed: int


class Conversion(TypedDict, total=False):
    source: str
    transaction_id: str
    occurred_at: Optional[str]
    campaign_id: Any
    subid: Optional[str]
    status: Literal["pending", "approved", "declined"]
    commission: float
    sale_amount: Optional[float]
    currency: str


class ReportRow(TypedDict, total=False):
    key: str
    conversions: int
    pending: int
    approved: int
    declined: int
    commission_by_currency: Dict[str, Any]
    approved_commission_by_currency: Dict[str, Any]
    commission_usd: float
    approved_commission_usd: float
    unconverted: int


class Report(TypedDict, total=False):
    group_by: str
    date_from: str
    date_to: str
    data: List[ReportRow]
    totals: ReportRow
    truncated: bool


class PostbackConfig(TypedDict, total=False):
    configured: bool
    url: str
    http_method: Literal["GET", "POST"]
    event_types: List[str]
    active: bool
    macros: List[str]


class SaleEvent(TypedDict, total=False):
    """POST body (GET postbacks receive the same values as macros)."""
    event: Optional[str | float]
    subid: Optional[str | float]
    click_id: Optional[str | float]
    transaction_id: Optional[str | float]
    order_ref: Optional[str | float]
    sale_amount: Optional[str | float]
    commission: Optional[str | float]
    currency: Optional[str | float]
    status: Optional[str | float]
    campaign_id: Optional[str | float]


class ClickwiseError(Exception):
    """Any non-2xx answer. Branch on .code (not_authenticated, throttled, invalid_request, ...)."""

    def __init__(self, status: int, code: str, message: str, request_id: Optional[str], retry_after: Optional[float], body: Any):
        super().__init__(f"{status} {code}: {message}")
        self.status, self.code, self.message = status, code, message
        self.request_id, self.retry_after, self.body = request_id, retry_after, body


class Clickwise:
    """Thin client for the Clickwise Publisher API. Keep the key on your server."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0, headers: Optional[Dict[str, str]] = None):
        self.api_key = api_key or os.environ.get("CLICKWISE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing Clickwise API key: pass api_key= or set CLICKWISE_API_KEY.")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}

    def request(self, method: str, path: str, query: Optional[Dict[str, Any]] = None, body: Any = None, headers: Optional[Dict[str, Optional[str]]] = None) -> Any:
        q = {k: (str(v).lower() if isinstance(v, bool) else v) for k, v in (query or {}).items() if v is not None}
        url = self.base_url + path + ("?" + urllib.parse.urlencode(q) if q else "")
        h = {"Accept": "application/json", "X-API-Key": self.api_key, "User-Agent": f"clickwise-python/{API_VERSION}", **self.headers}
        h.update({k: v for k, v in (headers or {}).items() if v is not None})
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                text = res.read().decode()
                return json.loads(text) if text else None
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")
            try:
                payload = json.loads(text)
            except ValueError:
                payload = text
            err = payload.get("error", {}) if isinstance(payload, dict) else {}
            detail = payload.get("detail") if isinstance(payload, dict) else None
            retry = e.headers.get("Retry-After")
            raise ClickwiseError(e.code, err.get("code", f"http_{e.code}"), err.get("message") or detail or e.reason,
                                 err.get("request_id") or e.headers.get("X-Request-Id"), float(retry) if retry else None, payload) from None

    def get_me(self) -> Me:
        """Who am I: account, access and limits"""
        return self.request("GET", "/me/", None, None, None)

    def search_products(self, *, q: str, country: Optional[str] = None, merchant: Optional[int] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> ProductPage:
        """Search GTIN products with your tracked links"""
        return self.request("GET", "/products/", {"q": q, "country": country, "merchant": merchant, "limit": limit, "offset": offset}, None, None)

    def lookup_products(self, *, ids: Optional[str] = None, gtins: Optional[str] = None, country: Optional[str] = None, merchant: Optional[int] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> ProductPage:
        """Refresh price and stock by id and/or GTIN (1-100)"""
        return self.request("GET", "/products/lookup/", {"ids": ids, "gtins": gtins, "country": country, "merchant": merchant, "limit": limit, "offset": offset}, None, None)

    def list_programs(self, *, search: Optional[str] = None, include_available: Optional[bool] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Programs you may promote (and, optionally, can apply to)"""
        return self.request("GET", "/programs/", {"search": search, "include_available": include_available, "page": page, "page_size": page_size}, None, None)

    def list_joinable_programs(self, *, search: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Programs open for application"""
        return self.request("GET", "/programs/joinable/", {"search": search, "page": page, "page_size": page_size}, None, None)

    def apply_to_program(self, body: Dict[str, Any], *, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Apply to a program (approved or pending review)"""
        return self.request("POST", "/programs/apply/", None, body, {"Idempotency-Key": idempotency_key})

    def list_links(self, *, subid: Optional[str] = None, campaign_id: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Your tracking links"""
        return self.request("GET", "/links/", {"subid": subid, "campaign_id": campaign_id, "page": page, "page_size": page_size}, None, None)

    def create_link(self, body: LinkRequest, *, idempotency_key: Optional[str] = None) -> Link:
        """Create or return one tracking link"""
        return self.request("POST", "/links/", None, body, {"Idempotency-Key": idempotency_key})

    def create_links_batch(self, body: Dict[str, Any], *, idempotency_key: Optional[str] = None) -> LinkBatchResult:
        """Create up to 50 links; each item reports its own status"""
        return self.request("POST", "/links/batch/", None, body, {"Idempotency-Key": idempotency_key})

    def list_conversions(self, *, date_from: Optional[str] = None, date_to: Optional[str] = None, subid: Optional[str] = None, status: Optional[Literal["pending", "approved", "declined"]] = None, source: Optional[Literal["all", "v1", "ledger"]] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Your conversions with a sub-ID rollup"""
        return self.request("GET", "/conversions/", {"date_from": date_from, "date_to": date_to, "subid": subid, "status": status, "source": source, "page": page, "page_size": page_size}, None, None)

    def get_report(self, *, group_by: Optional[Literal["day", "week", "month", "subid", "campaign", "status"]] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, subid: Optional[str] = None, status: Optional[Literal["pending", "approved", "declined"]] = None) -> Report:
        """Conversions and commission grouped (time series or dimension)"""
        return self.request("GET", "/reports/", {"group_by": group_by, "date_from": date_from, "date_to": date_to, "subid": subid, "status": status}, None, None)

    def list_clicks(self, *, sub_id: Optional[str] = None, campaign_id: Optional[str] = None, deeplink_id: Optional[str] = None, include_bots: Optional[bool] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Your clicks on Clickwise redirects"""
        return self.request("GET", "/clicks/", {"sub_id": sub_id, "campaign_id": campaign_id, "deeplink_id": deeplink_id, "include_bots": include_bots, "page": page, "page_size": page_size}, None, None)

    def get_postback(self) -> PostbackConfig:
        """Conversion postback (webhook) configuration"""
        return self.request("GET", "/postback/", None, None, None)

    def set_postback(self, body: Dict[str, Any]) -> PostbackConfig:
        """Not available with an API key: set the postback URL in the portal

        Always 403 `postback_write_requires_portal` with a publisher key, so a leaked key cannot redirect your conversions. Use the portal (Settings > Postback) or the portal API token."""
        return self.request("PUT", "/postback/", None, body, None)

    def rotate_postback_secret(self) -> Dict[str, Any]:
        """Not available with an API key: rotate the secret in the portal

        Always 403 `postback_write_requires_portal` with a publisher key."""
        return self.request("POST", "/postback/secret/", None, None, None)

    def test_postback(self) -> Dict[str, Any]:
        """Send a signed test event"""
        return self.request("POST", "/postback/test/", None, None, None)

    def list_postback_deliveries(self) -> Dict[str, Any]:
        """Recent postback delivery attempts"""
        return self.request("GET", "/postback/deliveries/", None, None, None)
