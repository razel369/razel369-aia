"""Run a full refresh: collect from all sources, curate, write dashboard +
feed JSON, log stats.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from . import config
from . import sources
from .curate import curate


def collect_all():
    bag = []
    bag += sources.fetch_hn_top(limit=30)
    bag += sources.fetch_hn_algolia(limit=20)
    bag += sources.fetch_v2ex_hot(limit=25)
    bag += sources.fetch_github_trending(days=7, min_stars=15, limit=20)
    bag += sources.fetch_devto_top(limit=15)
    bag += sources.fetch_indiehackers(limit=15)
    bag += sources.fetch_lobsters(limit=10)
    for sub in ("MachineLearning", "LocalLLaMA", "cryptocurrency", "agentic_ai"):
        try:
            bag += sources.fetch_reddit(sub, limit=10)
        except Exception:
            pass
    return bag


def write_dashboard(ranked, raw_count, sources_seen):
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    feed = {
        "generated_at": now_iso,
        "agent": "AIA — Autonomous Insight Agent",
        "version": "0.1.0",
        "raw_collected": raw_count,
        "sources_seen": sorted(sources_seen),
        "count": len(ranked),
        "signals": ranked,
    }
    out_json = config.DATA_DIR / "feed.json"
    out_json.write_text(json.dumps(feed, indent=2, ensure_ascii=False), encoding="utf-8")

    hist_path = config.DATA_DIR / "history.jsonl"
    with hist_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": now_iso, "top_id": ranked[0]["id"] if ranked else None,
                            "top_score": ranked[0]["final_score"] if ranked else 0,
                            "count": len(ranked), "raw": raw_count}) + "\n")

    return feed


def main():
    t0 = time.time()
    raw = collect_all()
    ranked = curate(raw, top_n=config.TOP_N)
    sources_seen = {s.get("source","?") for s in raw}
    feed = write_dashboard(ranked, len(raw), sources_seen)
    dt = round(time.time() - t0, 2)
    log = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "raw": len(raw),
        "ranked": len(ranked),
        "sources": sorted(sources_seen),
        "elapsed_s": dt,
    }
    log_path = config.LOGS_DIR / "refresh.log.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")
    print(json.dumps(log))
    return feed


if __name__ == "__main__":
    main()
