"""End-to-end autonomous loop. Single CLI entry point. Run via Task
Scheduler, cron, or just `python -X utf8 -m agent.loop` in a loop.

Cycle:
  1. Refresh the curated feed (collect → curate → write JSON)
  2. Render the public dashboard
  3. Scan MoltJobs and submit bids on jobs AIA can do
  4. Log a one-line heartbeat for the agent's own audit trail
"""
import json
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


def run_once(do_dashboard=True, do_moltjobs=True):
    t0 = time.time()
    feed = refresh_mod.main()
    heartbeat("refresh", raw=feed.get("raw_collected"),
              ranked=feed.get("count"), sources=feed.get("sources_seen"))
    if do_dashboard:
        out = dash_mod.render_dashboard()
        heartbeat("dashboard", path=str(out), bytes=out.stat().st_size)
    if do_moltjobs:
        scan = molt_mod.scan()
        heartbeat("moltjobs", **scan["scan_summary"])
    heartbeat("cycle_done", elapsed_s=round(time.time() - t0, 2))


if __name__ == "__main__":
    run_once()
