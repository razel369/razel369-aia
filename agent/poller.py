"""Poll MoltJobs for bid state changes + fulfill any accepted bids.
Runs every cycle (alongside refresh + dashboard).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from . import config
from . import moltjobs
from . import fulfill
from .net import get


ACCEPTED_STATES = {"ASSIGNED", "IN_PROGRESS", "ACTIVE"}
COMPLETED_STATES = {"COMPLETED", "APPROVED", "PAID"}


def _cache_path():
    return config.DATA_DIR / "fulfillment_log.json"


def _load_log():
    p = _cache_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_log(log):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path().write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


def _already_fulfilled(job_id):
    return any(e.get("job_id") == job_id and e.get("submitted") for e in _load_log())


def poll_and_fulfill(limit=20):
    """Find any in-flight jobs assigned to me, deliver where needed."""
    if not config.MOLT_API_KEY:
        return {"scanned": 0, "submitted": 0}
    h = {"x-api-key": config.MOLT_API_KEY}
    me = moltjobs.get_me()
    agent_id = (me or {}).get("data", {}).get("id") or (me or {}).get("id")
    if not agent_id:
        return {"scanned": 0, "submitted": 0, "error": "no agent_id"}
    jobs = get(f"{config.MOLT_API_BASE}/agents/{agent_id}/jobs", headers=h)
    if isinstance(jobs, dict):
        jobs = jobs.get("data") or jobs.get("jobs") or []
    if not isinstance(jobs, list):
        return {"scanned": 0, "submitted": 0}

    log = _load_log()
    submitted_now = 0
    interesting = 0
    for j in jobs[:limit]:
        status = j.get("status")
        if status in COMPLETED_STATES:
            continue
        if status not in ACCEPTED_STATES:
            continue
        interesting += 1
        jid = j.get("id")
        if _already_fulfilled(jid):
            continue
        # Generate deliverable
        deliverable = fulfill.synthesize_research_report(j)
        result = fulfill.submit(jid, deliverable)
        ok = isinstance(result, dict) and (result.get("status") in (200, 201, 204) or "data" in result)
        log.append({
            "job_id": jid,
            "title": j.get("title",""),
            "budget_usdc": j.get("budgetUsdc") or j.get("budget_usdc"),
            "status_seen": status,
            "submitted": ok,
            "deliverable_chars": len(deliverable),
            "result": result if not ok else "submitted",
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        submitted_now += 1
        # Heartbeat
        fulfill.heartbeat(f"delivered for job {jid[:8]} ({j.get('title','')[:40]})")
    _save_log(log)
    return {"scanned": len(jobs), "in_flight": interesting, "submitted": submitted_now}


if __name__ == "__main__":
    print(json.dumps(poll_and_fulfill(), indent=2, default=str))
