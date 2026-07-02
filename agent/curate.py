"""Curator: turns a raw signal list into a ranked, deduplicated, topic-tagged
stream. No LLM API calls — pure deterministic heuristics so the agent runs
for $0.

Scoring:
  recency_bonus = exp(-age_hours / 24)           (freshness, 0..1)
  source_weight  = {"hackernews": 1.2, "hackernews-algolia": 1.0,
                    "github": 1.3, "v2ex": 0.7, "dev.to": 0.9,
                    "indiehackers": 0.8, "lobsters": 0.9,
                    "reddit:...": 0.6, "moltjobs": 1.4}
  topic_boost    = 2.0 if any niche keyword hit, else 1.0
  negative_pen   = 0.1 if any negative keyword hit
  score          = (engagement + 5) * source_weight * topic_boost * negative_pen
                   * (0.3 + 0.7 * recency_bonus)
"""
import re
import time
from .config import NICHE_KEYWORDS, NEGATIVE_KEYWORDS

SOURCE_WEIGHT = {
    "hackernews":        1.2,
    "hackernews-algolia":1.0,
    "github":            1.3,
    "v2ex":              0.7,
    "dev.to":            0.9,
    "indiehackers":      0.8,
    "lobsters":          0.9,
    "moltjobs":          1.4,
}

def _classify(title, url):
    text = f"{title} {url}".lower()
    topics = []
    for topic, kws in NICHE_KEYWORDS.items():
        for kw in kws:
            if kw.lower() in text:
                topics.append(topic)
                break
    bad = any(kw in text for kw in NEGATIVE_KEYWORDS)
    return topics, bad

def _recency(ts, now=None):
    now = now or int(time.time())
    age_h = max(0, (now - ts) / 3600.0)
    import math
    return math.exp(-age_h / 24.0)

def _normalize_title(t):
    return re.sub(r"\s+", " ", t).strip()

def _dedupe(signals):
    """Dedupe by normalized title; keep highest-scoring copy."""
    seen = {}
    for s in signals:
        key = re.sub(r"[^a-z0-9 ]+", "", _normalize_title(s["title"]).lower())[:80]
        if not key:
            key = s["url"]
        prev = seen.get(key)
        if prev is None or s.get("score", 0) > prev.get("score", 0):
            seen[key] = s
    return list(seen.values())

def curate(signals, top_n=40, now=None):
    now = now or int(time.time())
    signals = _dedupe(signals)
    out = []
    for s in signals:
        topics, bad = _classify(s.get("title",""), s.get("url",""))
        rec = _recency(s.get("ts", now), now)
        sw  = SOURCE_WEIGHT.get(s.get("source",""), 0.7)
        boost = 2.0 if topics else 1.0
        pen   = 0.1 if bad else 1.0
        eng   = max(0, int(s.get("score", 0))) + int(s.get("comments", 0))
        score = (eng + 5) * sw * boost * pen * (0.3 + 0.7 * rec)
        out.append({
            **s,
            "title": _normalize_title(s.get("title","")),
            "topics": topics,
            "recency": round(rec, 3),
            "final_score": round(score, 2),
            "flagged": bad,
        })
    out.sort(key=lambda x: x["final_score"], reverse=True)
    return out[:top_n]
