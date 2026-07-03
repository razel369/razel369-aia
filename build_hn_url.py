#!/usr/bin/env python3
"""Build pre-filled HN submit URL + open browser."""
import urllib.parse, subprocess, webbrowser, sys

title = "AIA \u2013 Autonomous Insight Agent that pays its own bills via x402"
url = "https://razel369.github.io/aia/"
text = """AIA is a 100% autonomous AI agent business I built with $0 budget. It runs on a Windows laptop + Cloudflare Workers.

What it does:
\u2022 Collects 6 free public signal sources (HN, GitHub trending, V2EX, dev.to, Lobsters, GitHub repos) every 6h
\u2022 Filters, scores, deduplicates \u2192 40+ ranked signals/cycle
\u2022 Exposes a paid x402 API on Cloudflare (USDC on Base): signals $0.01, digest $0.003, alerts $0.005
\u2022 Auto-enlists on Frantic (sworn #59 of 119), claims paid bounties
\u2022 Auto-claims GitHub bounties

Numbers (last 24h):
\u2022 53 paid Frantic bounties in history ($1-$40 each)
\u2022 2 PRs open (AgentPipe + Open-Aeon)
\u2022 1,055 LOC Python, 1 Worker, $0 human input after 6h loop starts

Why it matters: AIA proves an AI agent can self-fund via x402 micro-payments + GitHub bounties without raising capital or running ads. Fork it, deploy your own AIA, point the x402 Worker at your own USDC wallet, ship.

Fork: github.com/razel369/razel369-aia
Dashboard: https://razel369.github.io/aia/
x402 API: https://aia-x402.rmalka06.workers.dev/health
Operator: 0x833c...3a5e (Base USDC)"""

q = {"title": title, "url": url, "text": text}
submit_url = "https://news.ycombinator.com/submit?" + urllib.parse.urlencode(q)
print(submit_url)
print()
print("LENGTH:", len(submit_url))
