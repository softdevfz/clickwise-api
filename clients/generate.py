#!/usr/bin/env python3
"""Generate the thin TypeScript and Python clients from openapi/openapi.json.

    curl -s https://partners.clickwise.net/api/v1/publisher/openapi.json -o openapi/openapi.json
    python3 clients/generate.py

Both clients are single files with no runtime dependencies: one method per
operationId, typed parameters, typed responses and one error class.
"""
import json
import keyword
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "openapi" / "openapi.json").read_text())
METHODS = ("get", "post", "put", "patch", "delete")
BASE_URL = SPEC["servers"][0]["url"]
VERSION = SPEC["info"]["version"]
HEADER = "Generated from openapi/openapi.json (Clickwise Publisher API {v}) by clients/generate.py. Do not edit by hand."


def resolve(ref):
    node = SPEC
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


RENAME = {"Error": "ApiError"}  # never shadow the built-in Error


def component_name(ref):
    parts = ref.lstrip("#/").split("/")
    if len(parts) == 3 and parts[:2] == ["components", "schemas"]:
        return RENAME.get(parts[2], parts[2])
    return None


def snake(name):
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name.replace("-", "_")).lower()
    return s + "_" if keyword.iskeyword(s) else s


def camel(name):
    head, *rest = re.split(r"[-_]", name)
    return head[:1].lower() + head[1:] + "".join(p[:1].upper() + p[1:] for p in rest)


def operations():
    for path, item in SPEC["paths"].items():
        for method in METHODS:
            op = item.get(method)
            if not op:
                continue
            params = [resolve(p["$ref"]) if "$ref" in p else p for p in op.get("parameters", [])]
            body = op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
            ok = [r for code, r in op["responses"].items() if code.startswith("2")]
            resp = ok[0].get("content", {}).get("application/json", {}).get("schema") if ok else None
            yield {
                "path": path, "method": method.upper(), "id": op["operationId"],
                "summary": op.get("summary", ""), "description": op.get("description", ""),
                "query": [p for p in params if p["in"] == "query"],
                "headers": [p for p in params if p["in"] == "header"],
                "body": body, "body_required": op.get("requestBody", {}).get("required", False),
                "response": resp,
            }


# ---------------------------------------------------------------- TypeScript

def ts_type(s, indent="  "):
    if not s:
        return "unknown"
    if "$ref" in s:
        return component_name(s["$ref"]) or ts_type(resolve(s["$ref"]), indent)
    if "allOf" in s:
        return " & ".join(ts_type(x, indent) for x in s["allOf"])
    if "oneOf" in s or "anyOf" in s:
        return " | ".join(ts_type(x, indent) for x in s.get("oneOf") or s["anyOf"])
    if "enum" in s:
        return " | ".join(json.dumps(v) for v in s["enum"])
    t = s.get("type")
    if isinstance(t, list):
        return " | ".join(ts_type({**s, "type": x}, indent) for x in t)
    if t == "array":
        inner = ts_type(s.get("items"), indent)
        return f"Array<{inner}>"
    if t == "object" or "properties" in s:
        req = set(s.get("required", []))
        lines = []
        for k, v in s.get("properties", {}).items():
            doc = f"{indent}/** {v['description']} */\n" if isinstance(v, dict) and v.get("description") else ""
            key = k if re.fullmatch(r"[A-Za-z_$][\w$]*", k) else json.dumps(k)
            lines.append(f"{doc}{indent}{key}{'' if k in req else '?'}: {ts_type(v, indent + '  ')};")
        extra = s.get("additionalProperties")
        if extra is True:
            lines.append(f"{indent}[key: string]: unknown;")
        elif isinstance(extra, dict):
            if not lines:
                return f"Record<string, {ts_type(extra, indent)}>"
            lines.append(f"{indent}[key: string]: unknown;")
        if not lines:
            return "Record<string, unknown>"
        return "{\n" + "\n".join(lines) + "\n" + indent[:-2] + "}"
    return {"string": "string", "integer": "number", "number": "number", "boolean": "boolean", "null": "null"}.get(t, "unknown")


def ts_client():
    out = [f"// {HEADER.format(v=VERSION)}", "", f'export const DEFAULT_BASE_URL = "{BASE_URL}";', ""]
    for name, schema in SPEC["components"]["schemas"].items():
        if schema.get("description"):
            out.append(f"/** {schema['description']} */")
        out.append(f"export type {RENAME.get(name, name)} = {ts_type(schema)};\n")
    out.append('''export interface ClickwiseOptions {
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
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\\/$/, "");
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
''')
    for op in operations():
        name = camel(op["id"])
        doc = op["summary"] + (f"\n   *\n   * {op['description']}" if op["description"] else "")
        args, call_query, call_headers = [], "undefined", "{}"
        if op["query"]:
            req = [p for p in op["query"] if p.get("required")]
            fields = "; ".join(f"{p['name']}{'' if p.get('required') else '?'}: {ts_type(p.get('schema'))}" for p in op["query"])
            args.append(f"params: {{ {fields} }}" + ("" if req else " = {}"))
            call_query = "params"
        if op["body"] is not None:
            args.append(f"body: {ts_type(op['body'], '    ')}")
        if op["headers"]:
            fields = "; ".join(f"{camel(h['name'].replace('-', '_'))}?: string" for h in op["headers"])
            args.append(f"options: {{ {fields} }} = {{}}")
            call_headers = "{ " + ", ".join(f'"{h["name"]}": options.{camel(h["name"].replace("-", "_"))}' for h in op["headers"]) + " }"
        ret = ts_type(op["response"], "    ") if op["response"] else "unknown"
        body_arg = "body" if op["body"] is not None else "undefined"
        out.append(f"  /** {doc} */")
        out.append(f"  {name}({', '.join(args)}): Promise<{ret}> {{")
        out.append(f'    return this.request("{op["method"]}", "{op["path"]}", {call_query}, {body_arg}, {call_headers});')
        out.append("  }\n")
    out.append("}\n")
    return "\n".join(out)


# ---------------------------------------------------------------- Python

def py_type(s, top=True):
    if not s:
        return "Any"
    if "$ref" in s:
        name = component_name(s["$ref"])
        return name or py_type(resolve(s["$ref"]), top)
    if "enum" in s:
        return "Literal[" + ", ".join(json.dumps(v) for v in s["enum"]) + "]"
    t = s.get("type")
    if isinstance(t, list):
        parts = [py_type({**s, "type": x}, top) for x in t if x != "null"]
        u = " | ".join(parts) if len(parts) > 1 else parts[0]
        return f"Optional[{u}]" if "null" in t else u
    if t == "array":
        return f"List[{py_type(s.get('items'), False)}]"
    if t == "object" or "properties" in s or "allOf" in s:
        return "Dict[str, Any]"
    return {"string": "str", "integer": "int", "number": "float", "boolean": "bool"}.get(t, "Any")


def py_client():
    out = [f'"""{HEADER.format(v=VERSION)}"""', "",
           "from __future__ import annotations", "",
           "import json", "import os", "import urllib.error", "import urllib.parse", "import urllib.request",
           "from typing import Any, Dict, List, Literal, Optional, TypedDict", "",
           f'DEFAULT_BASE_URL = "{BASE_URL}"', f'API_VERSION = "{VERSION}"', "", ""]
    for name, schema in SPEC["components"]["schemas"].items():
        props = schema.get("properties", {})
        out.append(f"class {RENAME.get(name, name)}(TypedDict, total=False):")
        if schema.get("description"):
            out.append(f'    """{schema["description"]}"""')
        if not props:
            out.append("    pass")
        for k, v in props.items():
            if k.isidentifier() and not keyword.iskeyword(k):
                out.append(f"    {k}: {py_type(v)}")
        out += ["", ""]
    out.append('''class ClickwiseError(Exception):
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
''')
    for op in operations():
        name = snake(op["id"])
        sig, qargs, hargs = ["self"], [], []
        if op["body"] is not None:
            sig.append(f"body: {py_type(op['body'])}")
        kw = []
        for p in sorted(op["query"], key=lambda p: not p.get("required")):
            arg = snake(p["name"])
            typ = py_type(p.get("schema"))
            kw.append(f"{arg}: {typ}" if p.get("required") else f"{arg}: Optional[{typ}] = None")
            qargs.append(f'"{p["name"]}": {arg}')
        for p in op["headers"]:
            arg = snake(p["name"])
            kw.append(f"{arg}: Optional[str] = None")
            hargs.append(f'"{p["name"]}": {arg}')
        if kw:
            sig.append("*")
            sig += kw
        ret = py_type(op["response"]) if op["response"] else "Any"
        out.append(f"    def {name}({', '.join(sig)}) -> {ret}:")
        doc = op["summary"] + (f"\n\n        {op['description']}" if op["description"] else "")
        out.append(f'        """{doc}"""')
        q = "{" + ", ".join(qargs) + "}" if qargs else "None"
        h = "{" + ", ".join(hargs) + "}" if hargs else "None"
        b = "body" if op["body"] is not None else "None"
        out.append(f'        return self.request("{op["method"]}", "{op["path"]}", {q}, {b}, {h})\n')
    return "\n".join(out)


if __name__ == "__main__":
    (ROOT / "clients" / "typescript" / "clickwise.ts").write_text(ts_client())
    (ROOT / "clients" / "python" / "clickwise" / "__init__.py").write_text(py_client())
    print("ok: clients/typescript/clickwise.ts, clients/python/clickwise/__init__.py")
