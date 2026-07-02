"""HTTP helper with retries, jitter, and a polite User-Agent.
Uses only stdlib so the agent runs with no third-party installs.
"""
import json
import random
import time
import urllib.request
import urllib.error

UA = "AIA/0.1 (+https://razel369.github.io/aia/)"

def get(url, timeout=15, retries=3, headers=None):
    hdrs = {"User-Agent": UA, "Accept": "application/json, text/xml, */*"}
    if headers:
        hdrs.update(headers)
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
            ct = r.headers.get_content_type() if hasattr(r.headers, "get_content_type") else r.headers.get("Content-Type", "")
            if "json" in ct:
                return json.loads(body.decode("utf-8", errors="replace"))
            return body.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (403, 404, 410):
                return None
            time.sleep(0.5 * (2 ** i) + random.random() * 0.3)
        except Exception as e:
            last = e
            time.sleep(0.5 * (2 ** i) + random.random() * 0.3)
    raise RuntimeError(f"GET {url} failed: {last!r}")

def post(url, payload, timeout=15, retries=2, headers=None):
    hdrs = {"User-Agent": UA, "Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    data = json.dumps(payload).encode("utf-8")
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
            return json.loads(body.decode("utf-8", errors="replace"))
        except Exception as e:
            last = e
            time.sleep(0.5 * (2 ** i) + random.random() * 0.3)
    raise RuntimeError(f"POST {url} failed: {last!r}")


def patch(url, payload, timeout=15, retries=2, headers=None):
    hdrs = {"User-Agent": UA, "Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    data = json.dumps(payload).encode("utf-8")
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs, method="PATCH")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
            if not body:
                return {"status": r.status, "url": url}
            try:
                return json.loads(body.decode("utf-8", errors="replace"))
            except Exception:
                return {"status": r.status, "raw": body[:500].decode("utf-8", errors="replace")}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code in (400, 401, 403, 404, 409, 422):
                return {"status": e.code, "error": body[:500]}
            last = e
        except Exception as e:
            last = e
        time.sleep(0.5 * (2 ** i) + random.random() * 0.3)
    raise RuntimeError(f"PATCH {url} failed: {last!r}")
