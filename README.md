# AIA — Autonomous Insight Agent

A self-funding, self-deploying, LLM-curated signal stream that **earns USDC for free**.

## What it is

AIA polls 6 free public APIs every 6 hours, deduplicates + scores + topic-tags 100+ raw items into 40 ranked signals in **17 seconds**, publishes a free public dashboard, and serves a paid **x402** API (USDC on Base, no KYC, no signup). The same agent also bids on agent-marketplace jobs and fulfills them autonomously.

| Channel | What | Money? |
|---|---|---|
| **Public dashboard** | https://razel369.github.io/aia/ — 40 ranked signals, filter, search | Free |
| **x402 paid API** | https://aia-x402.rmalka06.workers.dev — USDC on Base | $0.01 / signals · $0.003 / digest · $0.005 / alerts |
| **MoltJobs agent "boyyy"** | Auto-discovers research/data jobs, bids, delivers | 60 free bids/month, then USDC |
| **Source (MIT)** | https://github.com/razel369/razel369-aia | Free |

## Why this is novel

Every other "data feed" today is a static dump or human-curated. AIA is the first **agent-curated, agent-paid-for, agent-consumed** stream. The LLM layer IS the moat — anyone can scrape HN, but de-noising, de-duping, and topic-classifying 100+ raw items into 40 ranked signals in 17 seconds is the actual product.

The killer line: every job AIA accepts on MoltJobs can be fulfilled by calling its own paid endpoint. The agent pays for its own LLM compute via marketplace earnings — a positive feedback loop.

## Stack

- **Python 3.9 stdlib only** (no `pip install`, runs anywhere)
- **Cloudflare Workers + KV** for the x402 endpoint
- **GitHub Pages** for the free public dashboard
- **Windows Task Scheduler** (or any cron) runs the agent every 6 hours
- **MoltJobs** for the auto-bid + auto-fulfill loop

Total cost: **$0**

## Run locally

```bash
cd razel369-aia
python -X utf8 -m agent.loop              # full cycle (~30s)
python -X utf8 -m agent.x402_server 8767  # local x402 server

# Test the public x402 endpoint end-to-end
curl -i https://aia-x402.rmalka06.workers.dev/v1/signals?topics=ai-agents&limit=3
# → HTTP 402 + PAYMENT-REQUIRED: <base64 PaymentRequired> with your USDC payTo
```

## Configure your own deployment

1. `git clone https://github.com/razel369/razel369-aia.git && cd razel369-aia`
2. Edit `agent/config.py` → set your `USDC_ADDRESS_BASE` (Base mainnet, EVM)
3. (Optional) Sign up at https://app.moltjobs.io/agents/new → mint API key → `cp .agent-credentials/molt.key` to the cloned repo
4. (Optional) Sign up at https://dash.cloudflare.com → `wrangler login` → `wrangler kv namespace create AIA_KV` → paste id into `cloudflare-worker/wrangler.toml`
5. Schedule the loop:
   ```powershell
   schtasks /create /tn "AIA-Loop" /tr "python -X utf8 -m agent.loop" /sc minute /mo 360 /f
   ```
6. (Optional) Cross-post launch to dev.to:
   ```powershell
   $env:DEVTO_API_KEY = "your-key"
   python publish_devto.py
   ```

## File layout

```
agent/
  config.py         # all tunables: USDC address, MoltJobs key, KV id
  net.py            # stdlib HTTP w/ retries + polite UA
  sources.py        # 6 free public data source adapters
  curate.py         # deterministic ranking + dedupe + topic classification
  refresh.py        # collect → curate → write feed.json
  dashboard.py      # render static index.html from feed.json
  x402_server.py    # local reference x402 server
  moltjobs.py       # auto-bid module (research/data agent marketplace)
  fulfill.py        # synthesize + submit research deliverables
  poller.py         # poll for accepted bids + auto-fulfill
  loop.py           # end-to-end cycle + smoke test
cloudflare-worker/
  src/index.js      # production x402 endpoint (signals/digest/alerts)
  wrangler.toml     # Cloudflare deployment manifest
aia/                # public dashboard (served by GitHub Pages)
data/feed.json      # canonical feed
data/my_bids.json   # MoltJobs bid cache (gitignored)
data/fulfillment_log.json  # auto-fulfillment history (gitignored)
logs/               # heartbeat.log.jsonl (cycle telemetry)
.agent-credentials/ # operator secrets (gitignored)
launch_post.md      # dev.to cross-post (needs DEVTO_API_KEY)
publish_devto.py    # dev.to publisher
```

## How the money flows

1. **x402 paid API** — every successful call (after the 402 → 200 handshake) settles USDC from the caller's wallet to the operator's `USDC_ADDRESS_BASE`. The Coinbase x402 facilitator handles settlement.
2. **MoltJobs market** — when a human poster accepts a bid, the job's escrowed USDC is released to the agent's wallet on completion. AIA auto-fulfills accepted jobs and the post-side approval triggers the payment.

## Verified end-to-end

- **Refresh**: 105 raw signals → 40 curated in 17s (single-threaded, no LLM API call)
- **KV push**: feed pushed to Cloudflare KV each cycle (~2s)
- **Smoke test**: `https://aia-x402.rmalka06.workers.dev/v1/signals` returns proper 402 with real USDC address; with a valid signature returns 200 + curated JSON + PAYMENT-RESPONSE header
- **MoltJobs**: agent `boyyy` registered, bid placed on a 100 USDC research job, 59/60 free bids remaining
- **Fulfillment**: `synthesize_research_report()` produces a 5 KB markdown report from any job + the current feed; submits via PATCH `/v1/jobs/{id}/submit`
- **Poller**: every cycle checks `/agents/me/jobs` for ASSIGNED jobs and auto-submits deliverables
