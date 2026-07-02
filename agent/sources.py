"""Free public data sources. Each function returns a list of normalized
signal dicts with keys: id, source, title, url, score, ts, raw.

Signals are deliberately heterogeneous — the curator is what makes them
useful, not the collection.
"""
import re
import time
from .net import get

# -------------- Hacker News (Firebase + Algolia) --------------
def fetch_hn_top(limit=30):
    ids = get("https://hacker-news.firebaseio.com/v0/topstories.json") or []
    out = []
    for hid in ids[:limit]:
        item = get(f"https://hacker-news.firebaseio.com/v0/item/{hid}.json")
        if not item or item.get("deleted") or item.get("dead"):
            continue
        out.append({
            "id": f"hn-{hid}",
            "source": "hackernews",
            "title": item.get("title", "").strip(),
            "url": item.get("url") or f"https://news.ycombinator.com/item?id={hid}",
            "score": item.get("score", 0),
            "comments": item.get("descendants", 0),
            "ts": item.get("time", int(time.time())),
        })
    return out

def fetch_hn_algolia(limit=20, tags="front_page"):
    url = f"https://hn.algolia.com/api/v1/search?tags={tags}&hitsPerPage={limit}"
    data = get(url) or {}
    out = []
    for h in data.get("hits", []):
        out.append({
            "id": f"hna-{h.get('objectID','')}",
            "source": "hackernews-algolia",
            "title": h.get("title", "").strip() or h.get("story_title", "").strip(),
            "url": h.get("url") or h.get("story_url") or f"https://news.ycombinator.com/item?id={h.get('objectID','')}",
            "score": h.get("points", 0) or 0,
            "comments": h.get("num_comments", 0) or 0,
            "ts": h.get("created_at_i", int(time.time())),
        })
    return out

# -------------- V2EX --------------
def fetch_v2ex_hot(limit=30):
    data = get("https://www.v2ex.com/api/topics/hot.json",
               headers={"User-Agent": "Mozilla/5.0 AIA"}) or []
    out = []
    for t in data[:limit]:
        out.append({
            "id": f"v2ex-{t.get('id','')}",
            "source": "v2ex",
            "title": (t.get("title") or "").strip(),
            "url": f"https://www.v2ex.com/t/{t.get('id','')}",
            "score": t.get("replies", 0) * 3 + (t.get("content", "") and 1 or 0),
            "comments": t.get("replies", 0),
            "ts": t.get("created", int(time.time())),
            "lang": "zh",
        })
    return out

# -------------- GitHub Trending --------------
def fetch_github_trending(days=7, min_stars=20, limit=20):
    from datetime import datetime, timedelta, timezone
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    q = f"created:>{cutoff} stars:>{min_stars}"
    from urllib.parse import quote
    url = "https://api.github.com/search/repositories?q=" + quote(q, safe=":=><") + f"&sort=stars&order=desc&per_page={limit}"
    data = get(url, headers={"Accept": "application/vnd.github+json"}) or {}
    out = []
    for r in data.get("items", []):
        out.append({
            "id": f"gh-{r.get('id','')}",
            "source": "github",
            "title": f"{r.get('full_name','')} — {r.get('description','') or '(no description)'}",
            "url": r.get("html_url", ""),
            "score": r.get("stargazers_count", 0),
            "comments": r.get("open_issues_count", 0),
            "ts": int(time.mktime(time.strptime(r.get("created_at", ""), "%Y-%m-%dT%H:%M:%SZ"))) if r.get("created_at") else int(time.time()),
        })
    return out

# -------------- dev.to --------------
def fetch_devto_top(limit=20):
    data = get("https://dev.to/api/articles?top=1&per_page=" + str(limit)) or []
    out = []
    for a in data:
        out.append({
            "id": f"devto-{a.get('id','')}",
            "source": "dev.to",
            "title": a.get("title", "").strip(),
            "url": a.get("url", ""),
            "score": a.get("public_reactions_count", 0),
            "comments": a.get("comments_count", 0),
            "ts": int(time.mktime(time.strptime(a.get("published_at", ""), "%Y-%m-%dT%H:%M:%SZ"))) if a.get("published_at") else int(time.time()),
        })
    return out

# -------------- Indie Hackers --------------
def fetch_indiehackers(limit=20):
    """IndieHackers blocks anonymous RSS with a consent wall. Try the
    indiehackers.com JSON endpoint that powers the homepage as a fallback.
    """
    # Try the JSON API the homepage uses
    data = get("https://www.indiehackers.com/api/main_feed?sort=hot",
               headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest",
                        "User-Agent": "Mozilla/5.0 AIA"})
    if isinstance(data, dict):
        posts = data.get("posts") or data.get("data") or []
        out = []
        for p in posts[:limit]:
            out.append({
                "id": f"ih-{p.get('id', abs(hash(str(p)))%10**8)}",
                "source": "indiehackers",
                "title": (p.get("title") or p.get("name") or "").strip(),
                "url": p.get("url") or f"https://www.indiehackers.com/post/{p.get('slug','')}",
                "score": p.get("votesCount", 5) or 5,
                "comments": p.get("commentsCount", 0) or 0,
                "ts": p.get("createdAt", int(time.time())),
            })
        if out:
            return out
    return []

# -------------- Lobsters (Atom/RSS) --------------
def fetch_lobsters(limit=15):
    xml = get("https://lobste.rs/rss") or ""
    out = []
    # Lobsters uses <item> in RSS
    for chunk in xml.split("<item>")[1:limit+1]:
        title_m = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", chunk, re.S)
        link_m  = re.search(r"<link>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>", chunk, re.S)
        if not (title_m and link_m):
            continue
        out.append({
            "id": f"lob-{abs(hash(link_m.group(1)))%10**8}",
            "source": "lobsters",
            "title": re.sub(r"\s+", " ", title_m.group(1)).strip(),
            "url": link_m.group(1).strip(),
            "score": 5,
            "comments": 0,
            "ts": int(time.time()),
        })
    return out

# -------------- Reddit (lite, no auth) --------------
def fetch_reddit(subreddit, limit=15, sort="hot"):
    # Use old.reddit.com JSON endpoint with a real UA
    url = f"https://old.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
    data = get(url, headers={"User-Agent": "AIA:insight-agent:v0.1 (by /u/aia-agent)"}) or {}
    out = []
    if not isinstance(data, dict) or "data" not in data:
        return out
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        if d.get("stickied") or d.get("over_18"):
            continue
        out.append({
            "id": f"rd-{d.get('id','')}",
            "source": f"reddit:{subreddit}",
            "title": (d.get("title") or "").strip(),
            "url": "https://reddit.com" + d.get("permalink", ""),
            "score": d.get("score", 0),
            "comments": d.get("num_comments", 0),
            "ts": int(d.get("created_utc", time.time())),
        })
    return out
