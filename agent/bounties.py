"""Bounty monitor — discovers Algora + GitHub + Frantic + Opire + GrantFox bounties
and queues them for AIA to claim. Runs as part of agent.loop.

The 'earn money' pipeline:
  1. Every cycle, scan Algora + Frantic MCP + GitHub search + GrantFox + Opire
  2. Score each bounty by real-currency value, recency, AI-agent-friendliness
  3. If high-value, queue in data/bounty_queue.json
  4. AIA workflow: for each queued bounty, fork, build deliverable, PR, claim
"""
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .net import get, request, run_cmd


def _cache_path():
    return config.DATA_DIR / "bounty_cache.json"


def _load_cache():
    p = _cache_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {"seen": {}, "queue": []}
    return {"seen": {}, "queue": []}


def _save_cache(c):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path().write_text(json.dumps(c, indent=2, ensure_ascii=False), encoding="utf-8")


def _already_queued(bounty_id, queue):
    return any(b.get("id") == bounty_id for b in queue)


# -----------------------------------------------------------
# GitHub bounty search
# -----------------------------------------------------------

def search_gh_bounties(limit=50):
    """Return a list of normalized bounty dicts from GitHub issues with
    the `bounty` label + USDC in title/body."""
    out = []
    try:
        # The most reliable query: issues labeled "bounty" with USDC
        cmd = ["gh", "search", "issues", "bounty USDC",
               "--label", "bounty", "--state", "open", "--limit", str(limit),
               "--json", "number,title,repository,url,labels,body,createdAt"]
        rc, stdout, _ = run_cmd(cmd, timeout=30)
        if rc == 0:
            for it in json.loads(stdout):
                amt = _extract_usd(it.get("title","")) or _extract_usd(it.get("body",""))
                if amt is None or amt < 5:  # ignore sub-$5 noise
                    continue
                out.append({
                    "id": f"gh:{it['repository']['nameWithOwner']}#{it['number']}",
                    "platform": "github",
                    "repo": it["repository"]["nameWithOwner"],
                    "number": it["number"],
                    "title": it["title"],
                    "url": it["url"],
                    "usdc": amt,
                    "labels": [l["name"] for l in it.get("labels", [])],
                    "ai_agent_friendly": "AI agent friendly" in [l["name"] for l in it.get("labels", [])],
                    "created": it.get("createdAt"),
                })
    except Exception as e:
        print("gh search error:", e)
    return out


# -----------------------------------------------------------
# Algora public API
# -----------------------------------------------------------

def search_algora_bounties(limit=30):
    """Pull open bounties from Algora. Try a few well-known orgs."""
    out = []
    orgs = [
        "algora-io", "tursodatabase", "dwebagents", "permitio",
        "golemcloud", "biomejs", "turbo-oss", "ubounty-app",
        "astral-sh", "denoland", "vercel", "withastro",
        "virtuals-protocol", "all-hands-ai", "modal-labs",
    ]
    for org in orgs:
        try:
            data = get(f"https://api.algora.io/api/orgs/{org}/bounties?status=open",
                       headers={"User-Agent": "AIA-Bounty-Sweep/0.1"}, timeout=10)
            if not isinstance(data, list):
                continue
            for b in data[:limit]:
                amt = b.get("usdValue") or b.get("usd_value") or 0
                if amt < 5:
                    continue
                out.append({
                    "id": f"algora:{org}:{b.get('id')}",
                    "platform": "algora",
                    "org": org,
                    "number": b.get("id"),
                    "title": b.get("title",""),
                    "url": f"https://console.algora.io/bounties/{b.get('id')}",
                    "usdc": float(amt),
                    "labels": b.get("tags", []) or [],
                    "ai_agent_friendly": b.get("ai_agent_friendly", True),
                    "created": b.get("createdAt"),
                })
        except Exception as e:
            pass
    return out


# -----------------------------------------------------------
# Frantic (real ETH/USDC, sealed to public ledger)
# -----------------------------------------------------------

def search_frantic_bounties():
    """Pull open Frantic bounties via the public MCP read_board tool."""
    out = []
    try:
        # Use the public preflight endpoint instead of MCP (less rate-limited)
        board = request("POST", "https://api.gofrantic.com/mcp",
                    data={"jsonrpc":"2.0","id":1,"method":"tools/call",
                          "params":{"name":"frantic.read_board","arguments":{}}},
                    headers={"Accept":"application/json, text/event-stream",
                             "Content-Type":"application/json"}, timeout=15)
        if not isinstance(board, dict):
            return out
        sc = board.get("result",{}).get("structuredContent",{})
        for b in (sc.get("board",{}).get("open_bounties") or []):
            n = b.get("number")
            if n is None: continue
            price = float(b.get("price_usd") or 0)
            out.append({
                "id": f"frantic:{n}",
                "platform": "frantic",
                "number": n,
                "title": b.get("title",""),
                "url": f"https://gofrantic.com/bounties/{b.get('postingId','')}",
                "usdc": price,  # 0 for goodwill, $X for paid
                "labels": ["frantic", "x402" if price > 0 else "goodwill"],
                "ai_agent_friendly": True,
                "funding_required": price,
                "claim_slots": b.get("claim_slots", 1),
                "work_status": b.get("work_status", "open"),
                "created": None,
            })
    except Exception as e:
        print("frantic search error:", e)
    return out


# -----------------------------------------------------------
# GitHub org-scoped bounty search (covers GrantFox, Opire, Tari, etc.)
# -----------------------------------------------------------

def search_org_bounties():
    """Search known orgs that host bounties via GitHub Issues.
    Returns normalized dicts with extracted amounts (USDC, XLM, XTM)."""
    out = []
    orgs_queries = [
        ("claude-builders-bounty", "claude-builders-bounty", "opire"),
        ("cocohub-mobileapp", "cocohub-main", "grantfox"),
        ("tari-project", "tari-ootle", "tari"),
        ("Markp1598M", "Helm", "opire"),
        ("Scottcjn", "rustchain-bounties", "rustchain"),
        ("Eaprime1", "custos", "xp"),
        ("xevrion-v2", "agent-playground", "usdc"),
        ("walletbeat", "walletbeat", "usdc"),
        ("dwebagents", "AgentPipe", "usdc"),
    ]
    for org, repo, currency in orgs_queries:
        try:
            # Get open issues with bounty label or BOUNTY in title
            url = f"https://api.github.com/repos/{org}/{repo}/issues?state=open&per_page=20"
            r = get(url, headers={"Accept":"application/vnd.github+json",
                                  "User-Agent":"razel369-aia/1.0"}, timeout=15)
            if not isinstance(r, list):
                continue
            for it in r:
                if "pull_request" in it:  # skip PRs
                    continue
                title = it.get("title","")
                body = it.get("body","") or ""
                # Extract amount by currency
                amt = 0
                if currency == "opire":
                    m = re.search(r"\$(\d+)", title)
                    if m: amt = int(m.group(1))
                elif currency == "grantfox":
                    m = re.search(r"(\d+)\s*XLM", title + " " + body)
                    if m: amt = int(m.group(1)) * 0.2  # 1 XLM = $0.20 approx
                elif currency == "tari":
                    m = re.search(r"(\d+)\s*XTM", title + " " + body)
                    if m: amt = int(m.group(1)) * 0.0004  # 1 XTM = $0.0004
                elif currency == "rustchain":
                    m = re.search(r"(\d+)\s*RTC", title + " " + body)
                    if m: amt = int(m.group(1)) * 0.01  # estimate
                elif currency == "xp":
                    m = re.search(r"(\d+)\s*XP", title + " " + body)
                    if m: amt = int(m.group(1)) * 0.001
                else:
                    m = re.search(r"\$(\d+)", title + " " + body)
                    if m: amt = int(m.group(1))
                if amt == 0 and "bounty" not in title.lower() and "Bounty" not in title:
                    continue
                out.append({
                    "id": f"github:{org}/{repo}#{it['number']}",
                    "platform": f"github:{currency}",
                    "repo": f"{org}/{repo}",
                    "number": it["number"],
                    "title": title,
                    "url": it.get("html_url",""),
                    "usdc": round(amt, 2),
                    "currency": currency,
                    "labels": [l.get("name") for l in it.get("labels",[])],
                    "ai_agent_friendly": True,
                    "created": it.get("created_at"),
                })
        except Exception as e:
            pass
    return out


# -----------------------------------------------------------
# Scoring + queue
# -----------------------------------------------------------

def _extract_usd(text):
    if not text:
        return None
    m = re.search(r"\$\s*(\d+(?:\.\d+)?)", text)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*USDC", text, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def score(b):
    s = b.get("usdc", 0)
    if b.get("ai_agent_friendly"):
        s *= 1.5
    if b.get("platform") == "frantic":
        s *= 2.0  # real ETH/USDC, sealed ledger
    if "good first issue" in (b.get("labels") or []):
        s *= 1.2
    if s < 0.5:
        s *= 0.1  # deprioritise sub-$0.50 noise
    return round(s, 2)


def sweep(gh_limit=50, algora_orgs=None, include_frantic=True, include_orgs=True):
    """Discover bounties, score, queue new ones."""
    cache = _load_cache()
    found = []
    found.extend(search_gh_bounties(limit=gh_limit))
    found.extend(search_algora_bounties(limit=30))
    if include_frantic:
        found.extend(search_frantic_bounties())
    if include_orgs:
        found.extend(search_org_bounties())

    new_queued = []
    for b in found:
        bid = b["id"]
        if bid in cache["seen"]:
            continue
        if _already_queued(bid, cache["queue"]):
            continue
        b["score"] = score(b)
        b["discovered_at"] = datetime.now(timezone.utc).isoformat()
        cache["queue"].append(b)
        cache["seen"][bid] = b["discovered_at"]
        new_queued.append(b)

    # Sort queue by score desc
    cache["queue"].sort(key=lambda x: x.get("score", 0), reverse=True)
    # Keep queue bounded
    cache["queue"] = cache["queue"][:100]
    _save_cache(cache)
    return {
        "scanned": len(found),
        "new_queued": len(new_queued),
        "queue_size": len(cache["queue"]),
        "top": [
            {
                "platform": b.get("platform"),
                "title": b.get("title", "")[:50],
                "usdc": b.get("usdc"),
                "score": b.get("score"),
                "url": b.get("url"),
            }
            for b in cache["queue"][:10]
        ],
    }


def claim(bounty_id):
    """Mark a bounty as claimed (still TBD in our workflow — this is a no-op
    until the agent has a wallet to claim directly)."""
    cache = _load_cache()
    for b in cache["queue"]:
        if b["id"] == bounty_id:
            b["status"] = "claimed"
    _save_cache(cache)
    return cache["queue"]


def claim_frantic(bounty_id):
    """Claim a Frantic bounty via the MCP claim_bounty tool.
    Requires FRANTIC_AGENT_KID + FRANTIC_AGENT_TOKEN in env or .agent-credentials/frantic_state.json.
    """
    import os, json as _json
    state_path = config.DATA_DIR.parent / ".agent-credentials" / "frantic_state.json"
    if not state_path.exists():
        return {"ok": False, "error": "no Frantic credentials"}
    state = _json.loads(state_path.read_text(encoding="utf-8"))
    kid = state.get("agent_kid")
    token = state.get("agent_token")
    if not (kid and token):
        return {"ok": False, "error": "incomplete Frantic credentials"}
    res = request("POST", "https://api.gofrantic.com/mcp",
              data={"jsonrpc":"2.0","id":1,"method":"tools/call",
                    "params":{"name":"frantic.claim_bounty",
                              "arguments":{"bounty":bounty_id,
                                           "agent_kid":kid,
                                           "agent_token":token}}},
              headers={"Accept":"application/json, text/event-stream",
                       "Content-Type":"application/json"}, timeout=15)
    return res


if __name__ == "__main__":
    print(json.dumps(sweep(), indent=2, default=str)[:3000])
