"""End-to-end autonomous loop. Single CLI entry point. Run via Task
Scheduler, cron, or just `python -X utf8 -m agent.loop` in a loop.

Cycle:
  1. Refresh the curated feed (collect → curate → write JSON)
  2. Push feed.json to Cloudflare KV (so the paid x402 endpoint serves fresh data)
  3. Render the public dashboard
  4. Scan MoltJobs and submit bids on jobs AIA can do
  5. Poll MoltJobs for accepted bids + fulfill them
  6. Log a one-line heartbeat for the agent's own audit trail
"""
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from . import config
from . import refresh as refresh_mod
from . import dashboard as dash_mod
from . import moltjobs as molt_mod
from . import poller as poller_mod
from . import fulfill


def heartbeat(stage, **kw):
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "stage": stage, **kw}
    p = config.LOGS_DIR / "heartbeat.log.jsonl"
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))


def push_to_kv():
    """Push data/feed.json to Cloudflare KV via wrangler CLI.
    On Windows, wrangler is a .ps1 wrapper, so invoke node directly.
    """
    feed_path = config.DATA_DIR / "feed.json"
    if not feed_path.exists():
        return False
    cmd = [
        "node.exe",
        r"C:\Users\rmalk\AppData\Roaming\npm\node_modules\wrangler\bin\wrangler.js",
        "kv", "key", "put", "--remote",
        "--namespace-id", config.CLOUDFLARE_KV_NAMESPACE_ID,
        "feed.json", "--path", str(feed_path),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            print("kv push stderr:", r.stderr[-300:])
        return r.returncode == 0
    except Exception as e:
        print("kv push exception:", str(e)[:200])
        return False


def smoke_test_x402(base_url=None):
    """Hit the live x402 endpoint, verify 402 + valid base64 PaymentRequired
    with our real USDC payTo, then send a mock signature and verify 200."""
    import base64
    import urllib.request
    import urllib.error
    base = base_url or config.PAID_API_BASE
    url = base.rstrip("/") + "/v1/signals?topics=ai-agents&limit=1"
    out = {"url": url, "stage_1_402": False, "stage_2_200": False}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "aia-smoke/0.1"})
        try:
            urllib.request.urlopen(req, timeout=15)
        except urllib.error.HTTPError as e:
            if e.code == 402:
                pr_b64 = e.headers.get("PAYMENT-REQUIRED")
                if pr_b64:
                    import json
                    pr = json.loads(base64.b64decode(pr_b64))
                    out["stage_1_402"] = True
                    out["payTo"] = pr["accepts"][0]["payTo"]
                    out["amount"] = pr["accepts"][0]["maxAmountRequired"]
                    # Stage 2: send a mock signature
                    payload = {
                        "x402Version": 2,
                        "accepted": pr["accepts"][0],
                        "payload": {
                            "signature": "0xAIA_SMOKE_TEST",
                            "authorization": {
                                "from": "0xAIA",
                                "to": pr["accepts"][0]["payTo"],
                                "value": pr["accepts"][0]["maxAmountRequired"],
                            },
                        },
                    }
                    sig = base64.b64encode(json.dumps(payload).encode()).decode()
                    req2 = urllib.request.Request(url, headers={
                        "PAYMENT-SIGNATURE": sig,
                        "User-Agent": "aia-smoke/0.1",
                    })
                    try:
                        with urllib.request.urlopen(req2, timeout=20) as r:
                            out["stage_2_200"] = r.status == 200
                            out["payment_response"] = r.headers.get("PAYMENT-RESPONSE") is not None
                            body = r.read().decode("utf-8", errors="replace")
                            out["response_bytes"] = len(body)
                    except urllib.error.HTTPError as e2:
                        out["stage_2_error"] = f"HTTP {e2.code}"
        return out
    except Exception as e:
        out["error"] = str(e)[:200]
        return out


def run_once(do_dashboard=True, do_moltjobs=True, do_kv_push=True, do_poller=True, do_smoke=True):
    t0 = time.time()
    feed = refresh_mod.main()
    heartbeat("refresh", raw=feed.get("raw_collected"),
              ranked=feed.get("count"), sources=feed.get("sources_seen"))
    if do_kv_push:
        ok = push_to_kv()
        heartbeat("kv_push", ok=ok, url=config.PAID_API_BASE)
    if do_dashboard:
        out = dash_mod.render_dashboard()
        heartbeat("dashboard", path=str(out), bytes=out.stat().st_size)
    if do_moltjobs:
        try:
            allowance = molt_mod.get_allowance()
            scan = molt_mod.scan()
            heartbeat("moltjobs",
                      allowance=(allowance or {}).get("data") if isinstance(allowance, dict) else None,
                      **scan["scan_summary"])
        except Exception as e:
            heartbeat("moltjobs_error", error=str(e)[:200])
    if do_poller:
        try:
            result = poller_mod.poll_and_fulfill()
            heartbeat("poller", **result)
        except Exception as e:
            heartbeat("poller_error", error=str(e)[:200])
    if do_smoke:
        try:
            smoke = smoke_test_x402()
            heartbeat("smoke", **smoke)
        except Exception as e:
            heartbeat("smoke_error", error=str(e)[:200])
    try:
        fulfill.heartbeat("cycle_ok elapsed_s={:.1f}".format(time.time()-t0))
    except Exception:
        pass
    heartbeat("cycle_done", elapsed_s=round(time.time() - t0, 2))


if __name__ == "__main__":
    run_once()
