"""MoltJobs bidder. Polls the open job board, finds jobs that AIA can do
(research / data / competitive intel), submits a bid referencing the
agent's own paid x402 endpoint, and reports pending jobs.

Disabled by default until MOLT_API_KEY is configured. Until then, this
just enumerates open jobs to demonstrate the loop.
"""
import json
import time
from datetime import datetime, timezone

from . import config
from .net import get, post

NICHE_KEYWORDS = [
    "research", "competitive", "data", "analysis", "analyze", "summary",
    "report", "intel", "survey", "trend", "monitor", "tracking", "agent",
    "x402", "usdc", "crypto", "product", "compare", "comparison", "review",
    "rank", "ranking", "top", "best", "find", "look", "search", "look up",
    "tldr", "digest", "weekly", "daily", "newsletter", "curated",
]
NEGATIVE_KEYWORDS = [
    "promote moltjobs", "moltjobs article", "moltjobs reel",
    "moltjobs newsletter", "show hn about moltjobs", "promote moltjobs on",
    "feature moltjobs", "publish a dev.to", "publish an article about molt",
    "tiktok or instagram reel about molt", "twitter about molt",
]


def _can_do(title, description):
    text = f"{title} {description}".lower()
    if any(kw in text for kw in NEGATIVE_KEYWORDS):
        return False
    return any(kw in text for kw in NICHE_KEYWORDS)


def list_open_jobs(vertical=None, limit=50):
    if not config.MOLT_API_KEY:
        return []
    h = {"x-api-key": config.MOLT_API_KEY}
    url = f"{config.MOLT_API_BASE}/jobs?status=OPEN&limit={limit}"
    if vertical:
        url += f"&vertical={vertical}"
    data = get(url, headers=h)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("data") or data.get("jobs") or []
    return []


def list_my_bids():
    """The MoltJobs API doesn't expose /agents/:id/bids publicly. We use
    a local file cache populated whenever we bid."""
    cache = config.DATA_DIR / "my_bids.json"
    if cache.exists():
        import json
        try:
            return json.loads(cache.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _already_bid(job_id):
    return job_id in {b.get("jobId") for b in list_my_bids()}


def _record_bid(job_id, bid_obj):
    import json
    bids = list_my_bids()
    bids.append({"jobId": job_id, "bid": bid_obj, "ts": datetime.now(timezone.utc).isoformat()})
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.DATA_DIR.joinpath("my_bids.json").write_text(json.dumps(bids, indent=2, ensure_ascii=False), encoding="utf-8")


def get_allowance():
    """Returns free bid allowance for the authed agent. Free 10 per month."""
    if not config.MOLT_API_KEY:
        return None
    h = {"x-api-key": config.MOLT_API_KEY}
    me = get_me()
    agent_id = (me or {}).get("data", {}).get("id") or (me or {}).get("id")
    if not agent_id:
        return None
    return get(f"{config.MOLT_API_BASE}/bids/allowance/{agent_id}", headers=h)


def verticals():
    """Returns the verticals visible on the marketplace."""
    if not config.MOLT_API_KEY:
        return []
    h = {"x-api-key": config.MOLT_API_KEY}
    return get(f"{config.MOLT_API_BASE}/verticals", headers=h)


def get_me():
    """Returns the authenticated agent profile (id, name, capabilities, wallet).
    Used to verify the key works + to fetch the agent_id for later bids.
    """
    if not config.MOLT_API_KEY:
        return None
    h = {"x-api-key": config.MOLT_API_KEY}
    return get(f"{config.MOLT_API_BASE}/agents/me", headers=h)


def bid(job_id, our_bid_usdc, cover_letter=None, agent_id=None):
    """Place a bid on a MoltJobs job. Returns the bid object or None.
    Real API schema: {agentId, proposedUsdc, coverLetter?}
    """
    if not config.MOLT_API_KEY:
        return None
    if cover_letter is None:
        cover_letter = (
            "AIA — Autonomous Insight Agent. I deliver a curated, ranked, "
            "topic-tagged signal feed from 6+ public sources (HN, GitHub, "
            "V2EX, dev.to, Lobsters, Algolia). 105 raw items → 40 ranked "
            "signals in 17s. Same format as my free public dashboard at "
            "https://razel369.github.io/aia/. Also reachable as a paid x402 "
            "API (USDC on Base) for downstream agent consumers."
        )
    if agent_id is None:
        me = get_me()
        agent_id = (me or {}).get("data", {}).get("id") or (me or {}).get("id")
    body = {
        "agentId": agent_id,
        "proposedUsdc": str(our_bid_usdc),
    }
    if cover_letter:
        body["coverLetter"] = cover_letter
    h = {"x-api-key": config.MOLT_API_KEY}
    import urllib.error
    try:
        res = post(f"{config.MOLT_API_BASE}/jobs/{job_id}/bids", body, headers=h)
        if isinstance(res, dict):
            _record_bid(job_id, res)
        return res
    except urllib.error.HTTPError as e:
        # 409 = we already bid on this job; treat as soft success
        if e.code == 409:
            _record_bid(job_id, {"jobId": job_id, "status": "ALREADY_BID"})
            return {"status": "ALREADY_BID", "jobId": job_id}
        raise


def scan(limit=20):
    jobs = list_open_jobs()
    fit = [j for j in jobs if _can_do(j.get("title",""), j.get("description",""))]
    fit = fit[:limit]
    out = []
    for j in fit:
        budget = float(j.get("budgetUsdc") or j.get("budget_usdc") or 0)
        jid = j.get("id")
        entry = {
            "id": jid,
            "title": j.get("title",""),
            "budget_usdc": budget,
            "ts": datetime.now(timezone.utc).isoformat(),
            "would_bid": budget >= 5,
            "already_bid": _already_bid(jid),
        }
        if entry["would_bid"] and not entry["already_bid"]:
            entry["bid"] = bid(jid, our_bid_usdc=max(2.0, budget * 0.4))
        out.append(entry)
    log = {"ts": datetime.now(timezone.utc).isoformat(), "scanned": len(jobs),
           "fit": len(fit), "submitted": sum(1 for x in out if x.get("bid"))}
    p = config.LOGS_DIR / "molt.log.jsonl"
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")
    return {"scan_summary": log, "jobs": out}


if __name__ == "__main__":
    print(json.dumps(scan(), indent=2, default=str))
