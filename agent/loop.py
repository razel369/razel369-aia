"""End-to-end autonomous loop. Single CLI entry point. Run via Task
Scheduler, cron, or just `python -X utf8 -m agent.loop` in a loop.

Cycle:
  1. Refresh the curated feed (collect → curate → write JSON)
  2. Push feed.json to Cloudflare KV (so the paid x402 endpoint serves fresh data)
  3. Render the public dashboard
  4. Scan MoltJobs and submit bids on jobs AIA can do
  5. Log a one-line heartbeat for the agent's own audit trail
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


def run_once(do_dashboard=True, do_moltjobs=True, do_kv_push=True):
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
    heartbeat("cycle_done", elapsed_s=round(time.time() - t0, 2))


if __name__ == "__main__":
    run_once()
