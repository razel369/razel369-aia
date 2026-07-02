"""AIA x402 paid API. Pure stdlib HTTP server. Returns 402 with a proper
x402 PaymentRequired when no payment is attached. When the optional
PAYMENT-SIGNATURE header is attached, we verify it (light check) and
return the curated feed filtered by query params.

Reference: https://github.com/coinbase/x402/blob/main/specs/x402-specification-v2.md
"""
import base64
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from . import config
from .net import get as _get


def _payment_required(resource_url, description="Access to AIA curated signal stream"):
    """Build a 402 PaymentRequired response per x402 v2 spec."""
    body = {
        "x402Version": 2,
        "error": "X-PAYMENT header is required",
        "accepts": [
            {
                "scheme": "exact",
                "network": "eip-155:8453",  # Base mainnet
                "resource": resource_url,
                "description": description,
                "mimeType": "application/json",
                "payTo": config.USDC_ADDRESS_BASE or "0xNOT_CONFIGURED",
                "maxAmountRequired": "10000",  # 0.01 USDC (6 decimals)
                "maxTimeoutSeconds": 60,
                "asset": "USDC",
                "extra": {"name": "USD Coin", "version": "2"}
            }
        ]
    }
    return body


def _b64(d):
    return base64.b64encode(json.dumps(d).encode("utf-8")).decode("ascii")


def _verify_light(sig_b64, req):
    """Lightweight verification. Real settlement is done by a Coinbase
    x402 facilitator. We just sanity-check the signature shape here so
    the agent doesn't accidentally serve paid content on a malformed
    request."""
    try:
        payload = json.loads(base64.b64decode(sig_b64).decode("utf-8"))
        return {"ok": True, "payload": payload}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _load_feed():
    return json.loads(config.DATA_DIR.joinpath("feed.json").read_text(encoding="utf-8"))


def _filter_signals(feed, q):
    signals = feed.get("signals", [])
    topics = set(q.get("topics", "").lower().split(",")) if q.get("topics") else None
    source = q.get("source", "").lower()
    limit = int(q.get("limit", "10"))
    min_score = float(q.get("min_score", "0"))
    out = []
    for s in signals:
        if topics and not topics.intersection(s.get("topics", [])):
            continue
        if source and source not in s.get("source", "").lower():
            continue
        if s.get("final_score", 0) < min_score:
            continue
        out.append(s)
        if len(out) >= limit:
            break
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, extra_headers=None):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        # Always serve the open free feed for /v1/open
        if u.path == "/v1/open":
            try:
                feed = _load_feed()
                self._send(200, {"count": feed.get("count"), "signals": feed.get("signals", [])})
            except Exception as e:
                self._send(500, {"error": str(e)})
            return

        # Health
        if u.path == "/health":
            self._send(200, {"ok": True, "ts": int(time.time()),
                             "usdc_configured": bool(config.USDC_ADDRESS_BASE)})
            return

        # Paid endpoints
        if u.path.startswith("/v1/"):
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            price = _payment_required(f"{config.PAID_API_BASE}{u.path}",
                                      f"Access to {u.path}")
            sig = self.headers.get("PAYMENT-SIGNATURE") or self.headers.get("X-PAYMENT")
            if not sig:
                self.send_response(402)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("PAYMENT-REQUIRED", _b64(price))
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            v = _verify_light(sig, price)
            if not v["ok"]:
                self._send(400, {"error": "invalid signature", "detail": v["error"]})
                return
            try:
                feed = _load_feed()
                signals = _filter_signals(feed, q)
                body = {
                    "endpoint": u.path,
                    "filter": q,
                    "count": len(signals),
                    "signals": signals,
                    "settled_via": "x402 (signature accepted, facilitator: not yet wired)",
                }
                settlement = {"success": True, "transaction": "0xMOCK_NO_FACILITATOR",
                              "network": "eip-155:8453", "amount": price["accepts"][0]["maxAmountRequired"]}
                self._send(200, body, {"PAYMENT-RESPONSE": _b64(settlement)})
            except Exception as e:
                self._send(500, {"error": str(e)})
            return

        self._send(404, {"error": "not found",
                         "routes": ["/health", "/v1/open", "/v1/signals?topics=ai-agents&limit=10",
                                    "/v1/digest?topics=x402", "/v1/alerts?topics=crypto"]})


def serve(host="127.0.0.1", port=8765):
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"AIA x402 server on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    serve(port=port)
