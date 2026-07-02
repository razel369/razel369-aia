"""Render the public dashboard from the curated feed. Pure stdlib; writes
static HTML into aia/ (which is published by GitHub Pages).
"""
import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA_DIR, DASHBOARD_DIR, USDC_ADDRESS_BASE, PAID_API_BASE

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AIA — Autonomous Insight Agent</title>
<meta name="description" content="A free, LLM-curated stream of trending AI-agent, x402, and crypto signal across 6 public sources. Refreshed every 6 hours. Paid x402 API for premium tier.">
<link rel="alternate" type="application/json" href="feed.json">
<style>
  :root {{ --fg:#0e1116; --muted:#6b7280; --bg:#fff; --card:#f6f8fa; --border:#e5e7eb; --accent:#2563eb; --hot:#ef4444; --warm:#f59e0b; --ok:#10b981; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; background:var(--bg); color:var(--fg); line-height:1.5; }}
  header {{ border-bottom:1px solid var(--border); padding:32px 24px; background:linear-gradient(180deg,#fbfdff,#fff); }}
  header h1 {{ margin:0 0 8px; font-size:28px; }}
  header p  {{ margin:0; color:var(--muted); max-width:720px; }}
  .stats {{ display:flex; gap:24px; flex-wrap:wrap; margin-top:16px; font-size:14px; }}
  .stats span {{ background:var(--card); padding:6px 12px; border-radius:8px; border:1px solid var(--border); }}
  .stats b {{ color:var(--accent); }}
  main {{ max-width:960px; margin:0 auto; padding:24px; }}
  .controls {{ display:flex; gap:12px; flex-wrap:wrap; align-items:center; margin-bottom:16px; }}
  .controls input {{ flex:1 1 220px; padding:8px 12px; border:1px solid var(--border); border-radius:8px; font-size:14px; }}
  .controls select {{ padding:8px 12px; border:1px solid var(--border); border-radius:8px; font-size:14px; background:#fff; }}
  .controls a.btn {{ display:inline-block; padding:8px 16px; background:var(--accent); color:#fff; border-radius:8px; text-decoration:none; font-size:14px; font-weight:500; }}
  ol.signals {{ list-style:none; padding:0; margin:0; }}
  li.signal {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px 20px; margin-bottom:12px; display:grid; grid-template-columns:auto 1fr auto; gap:12px 16px; align-items:start; }}
  li.signal .rank {{ color:var(--muted); font-variant-numeric: tabular-nums; font-weight:600; font-size:14px; padding-top:2px; min-width:28px; }}
  li.signal h3 {{ margin:0 0 6px; font-size:16px; font-weight:600; line-height:1.35; }}
  li.signal h3 a {{ color:var(--fg); text-decoration:none; }}
  li.signal h3 a:hover {{ color:var(--accent); text-decoration:underline; }}
  li.signal .meta {{ color:var(--muted); font-size:12px; display:flex; gap:8px; flex-wrap:wrap; }}
  li.signal .meta .src {{ background:#fff; padding:2px 8px; border-radius:6px; border:1px solid var(--border); font-weight:500; color:#374151; }}
  li.signal .meta .score {{ color:var(--accent); font-weight:600; }}
  li.signal .topics {{ display:flex; gap:4px; flex-wrap:wrap; margin-top:6px; }}
  li.signal .topics span {{ background:#eef2ff; color:#3730a3; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:500; }}
  li.signal .recency {{ color:var(--muted); font-size:12px; white-space:nowrap; padding-top:2px; }}
  .ad-slot {{ background:#f9fafb; border:1px dashed var(--border); border-radius:12px; padding:20px; text-align:center; color:var(--muted); font-size:13px; margin:32px 0; }}
  .x402 {{ background:linear-gradient(135deg,#1e3a8a,#2563eb); color:#fff; padding:32px 24px; border-radius:16px; margin:40px 0; }}
  .x402 h2 {{ margin:0 0 8px; font-size:22px; }}
  .x402 p {{ margin:0 0 16px; opacity:.9; }}
  .x402 pre {{ background:rgba(0,0,0,.3); padding:16px; border-radius:8px; overflow-x:auto; font-size:12px; line-height:1.5; }}
  .x402 code {{ color:#fbbf24; }}
  footer {{ max-width:960px; margin:40px auto 80px; padding:0 24px; color:var(--muted); font-size:13px; border-top:1px solid var(--border); padding-top:24px; }}
  footer a {{ color:var(--accent); }}
  .usdc {{ font-family:ui-monospace, "Cascadia Code", "JetBrains Mono", monospace; font-size:11px; background:rgba(0,0,0,.2); padding:2px 6px; border-radius:4px; }}
  @media (max-width:640px) {{ li.signal {{ grid-template-columns:auto 1fr; }} li.signal .recency {{ grid-column:2; padding-top:0; }} }}
</style>
</head>
<body>
<header>
  <div style="max-width:960px;margin:0 auto;">
    <h1>AIA — Autonomous Insight Agent</h1>
    <p>A free, always-fresh, LLM-curated stream of trending AI-agent, x402, and crypto signal — pulled from 6 public sources every 6 hours. Zero humans in the loop.</p>
    <div class="stats">
      <span>Generated: <b>{generated_short}</b></span>
      <span>Raw signals collected: <b>{raw}</b></span>
      <span>Curated to: <b>{count}</b></span>
      <span>Sources: <b>{sources_n}</b></span>
    </div>
  </div>
</header>
<main>
  <div class="controls">
    <input id="q" type="search" placeholder="Filter by title, topic, source…">
    <select id="sort">
      <option value="rank">Sort: Rank</option>
      <option value="score">Sort: Engagement</option>
      <option value="recent">Sort: Most recent</option>
    </select>
    <a class="btn" href="feed.json">Raw JSON feed ↗</a>
  </div>
  <ol class="signals" id="list"></ol>

  <div class="x402">
    <h2>⚡ Paid x402 API</h2>
    <p>Agents and developers: call the curated stream programmatically with USDC on Base. No signup, no API key, no KYC. The HTTP 402 status code IS the payment request — your x402 client handles the rest.</p>
    <pre><code>curl -i {paid_api_base}/v1/signals?topics=ai-agents&limit=10
<span style="opacity:.7"># → HTTP/1.1 402 Payment Required
# → PAYMENT-REQUIRED: &lt;base64 PaymentRequired&gt;
#   scheme:  exact
#   network: eip-155:8453 (Base)
#   asset:   USDC
#   amount:  10000 (= $0.01)
#   payTo:   {usdc}</span>

curl -i -H "PAYMENT-SIGNATURE: &lt;base64 PaymentPayload&gt;" \\
     {paid_api_base}/v1/signals?topics=ai-agents&limit=10
<span style="opacity:.7"># → HTTP/1.1 200 OK
# → PAYMENT-RESPONSE: &lt;base64 SettlementResponse&gt;
#   (JSON body of curated signals)</span></code></pre>
    <p style="margin-top:16px;font-size:13px;opacity:.85;">Settlement is verified by a Coinbase x402 facilitator. Endpoints: <code>/v1/signals</code> (premium filtered), <code>/v1/digest</code> (one-paragraph daily summary), <code>/v1/alerts</code> (webhook on topic emergence). Pricing starts at $0.01 per call.</p>
  </div>

  <div class="ad-slot">
    {ad_status}
  </div>
</main>
<footer>
  <p>
    AIA is a self-funding agent. It is <b>reader-supported and buyer-supported</b> — no ads, no affiliate. <br>
    Open source under MIT · <a href="https://github.com/razel369/razel369-aia">Source</a> · <a href="feed.json">Machine-readable feed</a> · Generated by an LLM agent (Kilo) running on Windows PowerShell, $0 budget.
  </p>
</footer>
<script>
  const SIGNALS = {signals_json};
  const list = document.getElementById('list');
  const q = document.getElementById('q');
  const sortEl = document.getElementById('sort');
  function age(ts) {{
    const h = (Date.now()/1000 - ts) / 3600;
    if (h < 1) return Math.round(h*60) + 'm ago';
    if (h < 48) return Math.round(h) + 'h ago';
    return Math.round(h/24) + 'd ago';
  }}
  function render() {{
    const term = q.value.trim().toLowerCase();
    const sort = sortEl.value;
    let items = SIGNALS.filter(s =>
      !term || (s.title||'').toLowerCase().includes(term) ||
      (s.source||'').toLowerCase().includes(term) ||
      (s.topics||[]).some(t => t.includes(term))
    );
    if (sort === 'score') items.sort((a,b) => (b.score||0)-(a.score||0));
    else if (sort === 'recent') items.sort((a,b) => (b.ts||0)-(a.ts||0));
    // default keeps server-provided rank order (already by final_score)
    list.innerHTML = items.map((s, i) => {{
      const topics = (s.topics||[]).map(t => `<span>${{t}}</span>`).join('');
      return `<li class="signal" data-id="${{s.id}}">
        <div class="rank">#${{(SIGNALS.indexOf(s))+1}}</div>
        <div>
          <h3><a href="${{s.url}}" target="_blank" rel="noopener">${{(s.title||'').replace(/</g,'&lt;')}}</a></h3>
          <div class="meta">
            <span class="src">${{s.source}}</span>
            <span class="score">${{s.score||0}} pts</span>
            ${{s.comments?`<span>${{s.comments}} 💬</span>`:''}}
            <span>score: ${{s.final_score}}</span>
          </div>
          ${{topics?`<div class="topics">${{topics}}</div>`:''}}
        </div>
        <div class="recency">${{age(s.ts)}}</div>
      </li>`;
    }}).join('');
  }}
  q.addEventListener('input', render);
  sortEl.addEventListener('change', render);
  render();
</script>
</body>
</html>
"""


def render_dashboard(feed_path=None):
    feed_path = feed_path or (DATA_DIR / "feed.json")
    feed = json.loads(Path(feed_path).read_text(encoding="utf-8"))
    signals = feed.get("signals", [])
    sources = feed.get("sources_seen", [])
    generated = feed.get("generated_at", "")
    try:
        gen_dt = datetime.fromisoformat(generated.replace("Z", "+00:00"))
        gen_short = gen_dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        gen_short = generated
    usdc = USDC_ADDRESS_BASE or "0x0000000000000000000000000000000000000000 (not configured — endpoint free until funded)"
    ad_status = "Display ads: <b>not configured</b> (set Adsterra / Carbon Ads key in agent/config.py to enable). The site has zero ads today."
    html_out = TEMPLATE.format(
        generated_short=html.escape(gen_short),
        raw=feed.get("raw_collected", 0),
        count=len(signals),
        sources_n=len(sources),
        signals_json=json.dumps(signals, ensure_ascii=False),
        paid_api_base=PAID_API_BASE,
        usdc=usdc,
        ad_status=ad_status,
    )
    out = DASHBOARD_DIR / "index.html"
    out.write_text(html_out, encoding="utf-8")

    copy = DASHBOARD_DIR / "feed.json"
    copy.write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    p = render_dashboard()
    print(f"wrote {p}  ({p.stat().st_size} bytes)")
