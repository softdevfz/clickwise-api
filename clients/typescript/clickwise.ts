// Generated from openapi/openapi.json (Clickwise Publisher API 1.1) by clients/generate.py. Do not edit by hand.

export const DEFAULT_BASE_URL = "https://partners.clickwise.net/api/v1/publisher";

export type ApiError = {
  /** Human-readable message (kept for existing clients). */
  detail: unknown;
  error: {
    code: string;
    message: string;
    status: number;
    /** Also sent as X-Request-Id. */
    request_id: string;
  };
};

export type Me = {
  affiliate?: {
    ref?: string;
    status?: string;
  };
  api_version?: string;
  access?: Record<string, boolean>;
  rate_limits?: Record<string, number>;
};

export type Product = {
  id?: string;
  gtin?: string;
  title?: string;
  /** Decimal string in currency. */
  price?: string;
  currency?: string;
  image?: string;
  /** Clickwise link tracked to the caller. */
  url?: string;
  merchant?: {
    id?: number;
    name?: string;
  };
  availability?: "in_stock" | "out_of_stock" | "preorder" | "backorder";
  country?: string;
  updated_at?: string;
};

export type ProductPage = {
  products?: Array<Product>;
  count?: number;
  limit?: number;
  offset?: number;
  next_offset?: number | null;
  freshness_hours?: number;
};

export type Program = {
  /** Clickwise campaign id (links, reports). */
  id?: number | null;
  campaign_id?: string;
  campaign_name?: string;
  landing_url?: string;
  currency?: string;
  link_ready?: boolean;
  link_ready_error?: string | null;
  existing_links?: number;
  assignment_status?: "assigned" | "not_assigned";
  can_apply?: boolean;
  /** What this publisher earns. */
  commission?: {
    rate?: string;
    type?: string;
    source?: "campaign_payout" | "program_listing";
  };
  program?: {
    [key: string]: unknown;
  };
  [key: string]: unknown;
};

export type Page = {
  total?: number;
  page?: number;
  page_size?: number;
  pages?: number;
};

export type Link = {
  created?: boolean;
  deeplink_id?: string;
  /** The link to publish. */
  cw_link?: string;
  destination_link?: string;
  subid?: string;
  certified_tracking_link?: string;
  [key: string]: unknown;
};

export type LinkRequest = {
  campaign_id?: string | number;
  program_id?: number;
  subid?: string;
  /** A page on the merchant's own domain. */
  landing_url?: string;
};

export type LinkBatchResult = {
  data?: Array<{
    index?: number;
    status?: number;
    link?: Link;
    error?: {
      code: string;
      message: string;
      status: number;
      /** Also sent as X-Request-Id. */
      request_id: string;
    };
  }>;
  created?: number;
  existing?: number;
  failed?: number;
};

export type Conversion = {
  source?: string;
  transaction_id?: string;
  occurred_at?: string | null;
  campaign_id?: unknown;
  subid?: string | null;
  status?: "pending" | "approved" | "declined";
  /** What this publisher earns. */
  commission?: number;
  sale_amount?: number | null;
  currency?: string;
};

export type ReportRow = {
  key?: string;
  conversions?: number;
  pending?: number;
  approved?: number;
  declined?: number;
  /** Amounts per ISO currency code. */
  commission_by_currency?: Record<string, number>;
  /** Amounts per ISO currency code. */
  approved_commission_by_currency?: Record<string, number>;
  commission_usd?: number;
  approved_commission_usd?: number;
  /** Rows without a USD rate (not in *_usd). */
  unconverted?: number;
};

export type Report = {
  group_by?: string;
  date_from?: string;
  date_to?: string;
  data?: Array<ReportRow>;
  totals?: ReportRow;
  truncated?: boolean;
};

export type PostbackConfig = {
  configured?: boolean;
  url?: string;
  http_method?: "GET" | "POST";
  event_types?: Array<string>;
  active?: boolean;
  macros?: Array<string>;
  [key: string]: unknown;
};

/** POST body (GET postbacks receive the same values as macros). */
export type SaleEvent = {
  event?: string | number | null;
  subid?: string | number | null;
  click_id?: string | number | null;
  transaction_id?: string | number | null;
  order_ref?: string | number | null;
  sale_amount?: string | number | null;
  commission?: string | number | null;
  currency?: string | number | null;
  status?: string | number | null;
  campaign_id?: string | number | null;
};

export interface ClickwiseOptions {
  /** Publisher API key. Defaults to process.env.CLICKWISE_API_KEY. Keep it on the server. */
  apiKey?: string;
  baseUrl?: string;
  fetch?: typeof fetch;
  /** Extra headers for every request, e.g. X-Request-Id. */
  headers?: Record<string, string>;
}

export class ClickwiseError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly requestId: string | null,
    readonly retryAfter: number | null,
    readonly body: unknown,
  ) {
    super(message);
    this.name = "ClickwiseError";
  }
}

type Query = Record<string, string | number | boolean | undefined | null>;

export class Clickwise {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;
  private readonly headers: Record<string, string>;

  constructor(options: ClickwiseOptions = {}) {
    const env = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env ?? {};
    const apiKey = options.apiKey ?? env.CLICKWISE_API_KEY;
    if (!apiKey) throw new Error("Missing Clickwise API key: pass { apiKey } or set CLICKWISE_API_KEY.");
    this.apiKey = apiKey;
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, "");
    this.fetchImpl = options.fetch ?? fetch;
    this.headers = options.headers ?? {};
  }

  async request<T>(method: string, path: string, query?: Query, body?: unknown, headers: Record<string, string | undefined> = {}): Promise<T> {
    const url = new URL(this.baseUrl + path);
    for (const [k, v] of Object.entries(query ?? {})) if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
    const h: Record<string, string> = { Accept: "application/json", "X-API-Key": this.apiKey, ...this.headers };
    for (const [k, v] of Object.entries(headers)) if (v !== undefined) h[k] = v;
    if (body !== undefined) h["Content-Type"] = "application/json";
    const res = await this.fetchImpl(url, { method, headers: h, body: body === undefined ? undefined : JSON.stringify(body) });
    const text = await res.text();
    let data: any = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (!res.ok) {
      const err = data?.error ?? {};
      const retry = res.headers.get("Retry-After");
      throw new ClickwiseError(res.status, err.code ?? `http_${res.status}`, err.message ?? data?.detail ?? res.statusText,
        err.request_id ?? res.headers.get("X-Request-Id"), retry ? Number(retry) : null, data);
    }
    return data as T;
  }

  /** Who am I: account, access and limits */
  getMe(): Promise<Me> {
    return this.request("GET", "/me/", undefined, undefined, {});
  }

  /** Search GTIN products with your tracked links */
  searchProducts(params: { q: string; country?: string; merchant?: number; limit?: number; offset?: number }): Promise<ProductPage> {
    return this.request("GET", "/products/", params, undefined, {});
  }

  /** Refresh price and stock by id and/or GTIN (1-100) */
  lookupProducts(params: { ids?: string; gtins?: string; country?: string; merchant?: number; limit?: number; offset?: number } = {}): Promise<ProductPage> {
    return this.request("GET", "/products/lookup/", params, undefined, {});
  }

  /** Programs you may promote (and, optionally, can apply to) */
  listPrograms(params: { search?: string; include_available?: boolean; page?: number; page_size?: number } = {}): Promise<Page & {
    data?: Array<Program>;
  }> {
    return this.request("GET", "/programs/", params, undefined, {});
  }

  /** Programs open for application */
  listJoinablePrograms(params: { search?: string; page?: number; page_size?: number } = {}): Promise<Page & {
    data?: Array<Program>;
  }> {
    return this.request("GET", "/programs/joinable/", params, undefined, {});
  }

  /** Apply to a program (approved or pending review) */
  applyToProgram(body: {
    program_id?: number;
    campaign_id?: string | number;
  }, options: { idempotencyKey?: string } = {}): Promise<{
    [key: string]: unknown;
  }> {
    return this.request("POST", "/programs/apply/", undefined, body, { "Idempotency-Key": options.idempotencyKey });
  }

  /** Your tracking links */
  listLinks(params: { subid?: string; campaign_id?: string; page?: number; page_size?: number } = {}): Promise<Page & {
    data?: Array<Link>;
  }> {
    return this.request("GET", "/links/", params, undefined, {});
  }

  /** Create or return one tracking link */
  createLink(body: LinkRequest, options: { idempotencyKey?: string } = {}): Promise<Link> {
    return this.request("POST", "/links/", undefined, body, { "Idempotency-Key": options.idempotencyKey });
  }

  /** Create up to 50 links; each item reports its own status */
  createLinksBatch(body: {
    links: Array<LinkRequest>;
  }, options: { idempotencyKey?: string } = {}): Promise<LinkBatchResult> {
    return this.request("POST", "/links/batch/", undefined, body, { "Idempotency-Key": options.idempotencyKey });
  }

  /** Your conversions with a sub-ID rollup */
  listConversions(params: { date_from?: string; date_to?: string; subid?: string; status?: "pending" | "approved" | "declined"; source?: "all" | "v1" | "ledger"; page?: number; page_size?: number } = {}): Promise<Page & {
    data?: Array<Conversion>;
  }> {
    return this.request("GET", "/conversions/", params, undefined, {});
  }

  /** Conversions and commission grouped (time series or dimension) */
  getReport(params: { group_by?: "day" | "week" | "month" | "subid" | "campaign" | "status"; date_from?: string; date_to?: string; subid?: string; status?: "pending" | "approved" | "declined" } = {}): Promise<Report> {
    return this.request("GET", "/reports/", params, undefined, {});
  }

  /** Your clicks on Clickwise redirects */
  listClicks(params: { sub_id?: string; campaign_id?: string; deeplink_id?: string; include_bots?: boolean; page?: number; page_size?: number } = {}): Promise<{
    [key: string]: unknown;
  }> {
    return this.request("GET", "/clicks/", params, undefined, {});
  }

  /** Conversion postback (webhook) configuration */
  getPostback(): Promise<PostbackConfig> {
    return this.request("GET", "/postback/", undefined, undefined, {});
  }

  /** Not available with an API key: set the postback URL in the portal
   *
   * Always 403 `postback_write_requires_portal` with a publisher key, so a leaked key cannot redirect your conversions. Use the portal (Settings > Postback) or the portal API token. */
  setPostback(body: {
    /** https URL with {macro} placeholders. */
    url: string;
    http_method?: "GET" | "POST";
    event_types?: Array<string>;
    active?: boolean;
  }): Promise<PostbackConfig> {
    return this.request("PUT", "/postback/", undefined, body, {});
  }

  /** Not available with an API key: rotate the secret in the portal
   *
   * Always 403 `postback_write_requires_portal` with a publisher key. */
  rotatePostbackSecret(): Promise<{
    [key: string]: unknown;
  }> {
    return this.request("POST", "/postback/secret/", undefined, undefined, {});
  }

  /** Send a signed test event */
  testPostback(): Promise<{
    [key: string]: unknown;
  }> {
    return this.request("POST", "/postback/test/", undefined, undefined, {});
  }

  /** Recent postback delivery attempts */
  listPostbackDeliveries(): Promise<{
    [key: string]: unknown;
  }> {
    return this.request("GET", "/postback/deliveries/", undefined, undefined, {});
  }

}
