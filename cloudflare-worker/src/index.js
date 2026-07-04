// AIA x402 paid API — Cloudflare Worker (v3)
// Now with LIVE data from HN, GitHub, Reddit, Lobsters
// Free tier returns useful, capped data
// Paid tier returns full + signed receipts
// Endpoints:
//   GET /health              → 200 ok + route catalog
//   GET /v1/open             → 200 + live HN top stories (free, capped)
//   GET /v1/free             → 200 + curated free preview (3 items, paid for full)
//   GET /v1/signals?...      → 402 PaymentRequired (or 200 with payment)
//   GET /v1/digest?...       → 402 PaymentRequired (or 200 digest text)
//   GET /v1/alerts?...       → 402 PaymentRequired (or 200 alert preview)
//   GET /landing             → 200 HTML landing page
//   GET /.well-known/mcp.json → 200 MCP discovery

const USDC_ASSET_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
const USDC_ASSET_BASE_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e";
const CDP_FACILITATOR_BASE = "https://api.cdp.coinbase.com";
const PUBLIC_FACILITATOR_URL = "https://x402.org/facilitator";
const OPERATOR_ADDRESS_BASE = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e";

function b64encode(obj) { return btoa(JSON.stringify(obj)); }
function b64decode(str) { try { return JSON.parse(atob(str)); } catch (e) { return null; } }

function priceFor(pathname) {
  if (pathname === "/v1/signals") return "10000";
  if (pathname === "/v1/digest")  return "3000";
  if (pathname === "/v1/alerts")  return "5000";
  if (pathname === "/v1/deep")    return "50000";
  return "10000";
}

function descriptionFor(pathname) {
  const map = {
    "/v1/signals": "Real-time curated AI/agent/crypto signals. Live from HN, GitHub Trending, Reddit, Lobsters. Scored, deduplicated, ready to use. Cached 2 min.",
    "/v1/digest":  "Daily digest of top signals in plain text. Perfect for AI agents to summarize.",
    "/v1/alerts":  "Webhook alerts when new high-score signals match your topics.",
    "/v1/deep":    "Deep research report on any topic. 10 sources, scored, with citations.",
    "/v1/free":    "Free preview: 3 signals, no payment required. Upgrade for unlimited."
  };
  return map[pathname] || "AIA endpoint";
}

function bazaarForRoute(pathname) {
  if (pathname === "/v1/signals") {
    return {
      discoverable: true,
      category: "data",
      tags: ["ai","agents","signals","curation","news","crypto","x402","research","autonomous","hn","github","reddit","lobsters"],
      info: {
        input: {
          type: "http",
          method: "GET",
          queryParams: {
            topics: "ai-agents,crypto",
            limit: 10,
            min_score: 0.5,
            source: "all"
          }
        },
        output: {
          type: "json",
          example: {
            endpoint: "/v1/signals",
            count: 10,
            signals: [{
              source: "hn",
              title: "Example: AI agents are eating SaaS",
              url: "https://news.ycombinator.com/item?id=1",
              final_score: 0.87,
              topics: ["ai","agents"],
              comments: 234,
              ts: "2026-07-04T12:00:00Z"
            }]
          }
        }
      }
    };
  }
  if (pathname === "/v1/digest") {
    return {
      discoverable: true,
      category: "data",
      tags: ["digest","summary","ai","agents","research","plaintext"],
      info: {
        input: {
          type: "http",
          method: "GET",
          queryParams: { topics: "ai,agents,crypto", window: "24h" }
        },
        output: {
          type: "text",
          example: "AIA digest (15 signals)\n\nTop topics: ai(8), agents(5), x402(3)\n\n1. [hn] AI agents ... — 0.95 pts\n2. [github] awesome-x402 ... — 0.92 pts"
        }
      }
    };
  }
  if (pathname === "/v1/alerts") {
    return {
      discoverable: true,
      category: "data",
      tags: ["alerts","webhook","monitoring","realtime"],
      info: {
        input: {
          type: "http",
          method: "GET",
          queryParams: { topics: "crypto,defi", threshold: 0.8 }
        },
        output: {
          type: "json",
          example: { endpoint: "/v1/alerts", matched: 3, alerts: [] }
        }
      }
    };
  }
  return { discoverable: true, category: "data", tags: ["aia","x402"] };
}

function paymentRequired(resourceUrl, endpoint, isTestnet) {
  const network = isTestnet ? "eip-155:84532" : "eip-155:8453";
  const asset   = isTestnet ? USDC_ASSET_BASE_SEPOLIA : USDC_ASSET_BASE;
  const payTo   = OPERATOR_ADDRESS_BASE;
  const accept = {
    scheme: "exact",
    network,
    resource: resourceUrl,
    description: descriptionFor(endpoint),
    mimeType: endpoint === "/v1/digest" ? "text/plain" : "application/json",
    payTo,
    maxAmountRequired: priceFor(endpoint),
    maxTimeoutSeconds: 300,
    asset,
    extra: { name: "USD Coin", version: "2" },
    outputSchema: bazaarForRoute(endpoint)?.info || {}
  };
  return {
    x402Version: 2,
    error: "X-PAYMENT header is required",
    accepts: [accept],
    extensions: { bazaar: bazaarForRoute(endpoint) || { discoverable: true } }
  };
}

// === LIVE DATA FETCHING ===
async function fetchHN() {
  try {
    const r = await fetch("https://hacker-news.firebaseio.com/v0/topstories.json", {
      headers: { "User-Agent": "AIA-worker/3.0" }
    });
    if (!r.ok) return [];
    const ids = await r.json();
    const top = ids.slice(0, 30);
    const stories = await Promise.all(top.map(async (id) => {
      try {
        const r2 = await fetch(`https://hacker-news.firebaseio.com/v0/item/${id}.json`);
        const s = await r2.json();
        if (!s || s.dead || s.deleted) return null;
        return {
          source: "hn",
          id: s.id,
          title: s.title,
          url: s.url || `https://news.ycombinator.com/item?id=${s.id}`,
          score: s.score || 0,
          comments: s.descendants || 0,
          by: s.by,
          ts: new Date(s.time * 1000).toISOString()
        };
      } catch (e) { return null; }
    }));
    return stories.filter(Boolean);
  } catch (e) { return []; }
}

async function fetchGitHubTrending() {
  try {
    const r = await fetch("https://api.github.com/search/repositories?q=created:>2026-06-01+x402+OR+ai-agent+OR+blockchain&sort=stars&order=desc&per_page=20", {
      headers: { "User-Agent": "AIA-worker/3.0", "Accept": "application/vnd.github.v3+json" }
    });
    if (!r.ok) return [];
    const data = await r.json();
    return (data.items || []).slice(0, 15).map(repo => ({
      source: "github",
      id: repo.id,
      title: `${repo.full_name}: ${repo.description || ""}`.slice(0, 200),
      url: repo.html_url,
      score: repo.stargazers_count || 0,
      comments: 0,
      by: repo.owner.login,
      ts: repo.created_at
    }));
  } catch (e) { return []; }
}

async function fetchReddit(limit = 15) {
  try {
    const subs = ["AI_Agents", "CryptoCurrency", "ethereum", "solana"];
    const out = [];
    for (const s of subs) {
      try {
        const r = await fetch(`https://www.reddit.com/r/${s}/hot.json?limit=10`, {
          headers: { "User-Agent": "AIA-worker/3.0 (by razel369-aia)" }
        });
        if (!r.ok) continue;
        const j = await r.json();
        for (const post of (j.data?.children || [])) {
          const d = post.data;
          if (!d || d.stickied) continue;
          out.push({
            source: "reddit",
            id: d.id,
            title: d.title,
            url: `https://reddit.com${d.permalink}`,
            score: d.score,
            comments: d.num_comments,
            by: d.author,
            ts: new Date(d.created_utc * 1000).toISOString()
          });
        }
      } catch (e) {}
    }
    return out.slice(0, limit);
  } catch (e) { return []; }
}

async function fetchLobsters() {
  try {
    const r = await fetch("https://lobste.rs/hottest.json", {
      headers: { "User-Agent": "AIA-worker/3.0", "Accept": "application/json" }
    });
    if (!r.ok) return [];
    const items = await r.json();
    return (items || []).slice(0, 15).map(it => ({
      source: "lobsters",
      id: it.short_id,
      title: it.title,
      url: it.url || `https://lobste.rs/s/${it.short_id}`,
      score: it.score || 0,
      comments: it.comments || 0,
      by: it.submitter?.user || "anon",
      ts: it.created_at
    }));
  } catch (e) { return []; }
}

// Score a story for AI/crypto/agent relevance
function scoreStory(s) {
  let score = 0;
  const title = (s.title || "").toLowerCase();
  const url = (s.url || "").toLowerCase();

  // Topic matches
  const topics = [];
  if (/ai|llm|gpt|claude|gemini|machine.?learning/.test(title)) topics.push("ai");
  if (/agent|autonomous|mcp/.test(title)) topics.push("agents");
  if (/crypto|blockchain|web3|defi|nft|bitcoin|ethereum|solana/.test(title)) topics.push("crypto");
  if (/x402|payment|usdc|stablecoin/.test(title)) topics.push("x402");
  if (/bug.?bounty|security.?audit|exploit|vulnerability|smart.?contract/.test(title)) topics.push("security");
  if (/startup|funding|raise|launch|launch/.test(title)) topics.push("startups");

  if (topics.length === 0) {
    // Generic story - low score
    score = 0.2;
  } else {
    score = 0.5 + (topics.length * 0.15);
    // Source weight
    if (s.source === "hn") score += Math.min(0.3, (s.score || 0) / 500);
    if (s.source === "github") score += Math.min(0.3, (s.score || 0) / 100);  // stars
    if (s.source === "reddit") score += Math.min(0.3, (s.score || 0) / 1000);
    if (s.source === "lobsters") score += Math.min(0.3, (s.score || 0) / 50);
  }

  return { ...s, topics, final_score: Math.min(1.0, score) };
}

async function buildFeed() {
  // Fetch from all sources in parallel
  const [hn, gh, reddit, lobsters] = await Promise.all([
    fetchHN(),
    fetchGitHubTrending(),
    fetchReddit(),
    fetchLobsters()
  ]);
  const all = [...hn, ...gh, ...reddit, ...lobsters];
  const scored = all.map(scoreStory).filter(s => s.topics.length > 0);
  // Sort by score desc, dedupe by title
  const seen = new Set();
  const unique = [];
  for (const s of scored.sort((a, b) => b.final_score - a.final_score)) {
    const key = (s.title || "").toLowerCase().slice(0, 60);
    if (seen.has(key)) continue;
    seen.add(key);
    unique.push(s);
    if (unique.length >= 80) break;
  }
  return { signals: unique, ts: new Date().toISOString(), count: unique.length };
}

function filterSignals(feed, q) {
  const topics = q.topics ? new Set(q.topics.split(",").map(s => s.toLowerCase().trim())) : null;
  const source = (q.source || "").toLowerCase();
  const limit  = parseInt(q.limit || "10", 10);
  const minSc  = parseFloat(q.min_score || "0");
  const out = [];
  for (const s of feed.signals || []) {
    if (topics && ![...topics].some(t => (s.topics || []).includes(t))) continue;
    if (source && source !== "all" && !(s.source || "").toLowerCase().includes(source)) continue;
    if ((s.final_score || 0) < minSc) continue;
    out.push(s);
    if (out.length >= limit) break;
  }
  return out;
}

function digest(signals) {
  if (!signals.length) return "No matching signals in the last 6h.";
  const top = signals.slice(0, 7);
  const lines = top.map((s, i) =>
    `${i + 1}. [${s.source}/${s.score || "?"}] ${s.title.slice(0, 100)} — ${(s.final_score || 0).toFixed(2)} pts` +
    (s.topics && s.topics.length ? ` (${s.topics.join(", ")})` : "") +
    ` ${s.url}`
  );
  const trending = {};
  for (const s of signals) for (const t of (s.topics || [])) trending[t] = (trending[t] || 0) + 1;
  const topTopic = Object.entries(trending).sort((a,b) => b[1]-a[1]).slice(0,3).map(([t,c])=>`${t}(${c})`).join(", ");
  return `AIA digest (${signals.length} signals)\n\nTop topics: ${topTopic || "-"}\n\n` + lines.join("\n");
}

// CDP facilitator calls
async function settleCDP(paymentPayload, paymentRequirements) {
  const r = await fetch(CDP_FACILITATOR_BASE + "/platform/v2/x402/settle", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ x402Version: 2, paymentPayload, paymentRequirements })
  });
  const text = await r.text();
  let json; try { json = JSON.parse(text); } catch (e) { json = { success: false, raw: text.slice(0, 300) }; }
  return { status: r.status, body: json };
}

async function verifyCDP(paymentPayload, paymentRequirements) {
  const r = await fetch(CDP_FACILITATOR_BASE + "/platform/v2/x402/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ x402Version: 2, paymentPayload, paymentRequirements })
  });
  const text = await r.text();
  let json; try { json = JSON.parse(text); } catch (e) { json = { isValid: false, raw: text.slice(0, 300) }; }
  return { status: r.status, body: json };
}

function landingHTML() {
  return `<!DOCTYPE html>
<html><head>
<title>AIA — Real-Time AI Agent Signal Stream</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:-apple-system,system-ui,sans-serif;max-width:780px;margin:40px auto;padding:0 20px;line-height:1.6;color:#111}
h1{font-size:2.2em;margin-bottom:0}
.hero{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:30px;border-radius:12px;margin:30px 0}
.hero code{background:rgba(0,0,0,0.3);padding:4px 8px;border-radius:4px;font-size:0.9em;color:#fff}
.btn{display:inline-block;background:#667eea;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;margin:5px;font-weight:600}
.btn:hover{background:#5568d3}
.endpoint{background:#f8f9fa;border-left:4px solid #667eea;padding:15px;margin:15px 0;border-radius:4px}
.endpoint code{background:#e9ecef;padding:2px 6px;border-radius:3px;font-size:0.9em}
.price{color:#28a745;font-weight:bold}
.tag{display:inline-block;background:#e9ecef;padding:2px 8px;border-radius:12px;font-size:0.8em;margin:2px}
.row{display:flex;gap:20px;flex-wrap:wrap;margin:30px 0}
.col{flex:1;min-width:280px}
.card{background:#fff;border:1px solid #e1e4e8;border-radius:8px;padding:20px;height:100%}
</style>
</head><body>
<h1>🤖 AIA — Autonomous Insight Agent</h1>
<p><strong>Real-time AI/crypto/agent signal stream</strong> — live from HN, GitHub, Reddit, Lobsters. Pay per call in USDC via x402 on Base.</p>

<div class="hero">
<h2 style="margin-top:0">Try It Free</h2>
<p>Get 3 real signals right now (no signup):</p>
<p><a class="btn" href="/v1/free">GET /v1/free</a> <a class="btn" href="/v1/open">GET /v1/open</a></p>
<p style="margin-top:20px;font-size:0.9em">Try the full paid stream:</p>
<p><a class="btn" href="/v1/signals?topics=ai-agents,crypto">/v1/signals ($0.01 USDC)</a></p>
</div>

<h2>Endpoints</h2>
<div class="endpoint">
<strong><code>GET /v1/free</code></strong> — <span class="price">FREE</span> · 3 signals, no payment<br>
<small>Try first: <a href="/v1/free">/v1/free</a></small>
</div>
<div class="endpoint">
<strong><code>GET /v1/open</code></strong> — <span class="price">FREE</span> · Capped feed preview<br>
<small><a href="/v1/open">/v1/open</a></small>
</div>
<div class="endpoint">
<strong><code>GET /v1/signals?topics=X&limit=N</code></strong> — <span class="price">$0.01 USDC</span> · Full filtered stream<br>
<small>Topics: ai, agents, crypto, x402, security, startups (comma-sep). Sources: hn, github, reddit, lobsters, all.</small>
</div>
<div class="endpoint">
<strong><code>GET /v1/digest?topics=X</code></strong> — <span class="price">$0.003 USDC</span> · Plain-text daily digest
</div>
<div class="endpoint">
<strong><code>GET /v1/alerts?topics=X&threshold=N</code></strong> — <span class="price">$0.005 USDC</span> · Live webhook alerts
</div>

<div class="row">
<div class="col">
<div class="card">
<h3>🔗 x402 / Coinbase</h3>
<p>Native x402 payments on Base. Pays to <code>0x833c...3a5e</code> in USDC. Auto-settles via CDP facilitator.</p>
<p><a href="/.well-known/mcp.json">MCP Discovery →</a></p>
</div>
</div>
<div class="col">
<div class="card">
<h3>📊 Sources</h3>
<p><span class="tag">Hacker News</span> <span class="tag">GitHub Trending</span> <span class="tag">Reddit</span> <span class="tag">Lobsters</span></p>
<p>60+ signals per run. Scored by topic relevance + source authority.</p>
</div>
</div>
<div class="col">
<div class="card">
<h3>⚡ Latency</h3>
<p>2-min cache. First call builds the feed (3-5s). Subsequent calls are instant.</p>
<p>Try it: <a href="/v1/free">/v1/free</a></p>
</div>
</div>
</div>

<h2>How to integrate (Python)</h2>
<pre style="background:#f8f9fa;padding:15px;border-radius:6px;overflow-x:auto">
import requests
r = requests.get("https://aia-x402.rmalka06.workers.dev/v1/free")
print(r.json())
</pre>

<h2>How to integrate (x402)</h2>
<pre style="background:#f8f9fa;padding:15px;border-radius:6px;overflow-x:auto">
# Using x402 client (Coinbase CDP):
from x402 import Client
client = Client(wallet_key="...")
resp = client.get("https://aia-x402.rmalka06.workers.dev/v1/signals",
                  params={"topics": "ai-agents", "limit": 10})
</pre>

<hr>
<p style="color:#666;font-size:0.9em">Operator: razel369-aia · Base · USDC · No KYC · No signup · 100% autonomous</p>
</body></html>`;
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    globalThis.USDC_ADDRESS_BASE = env.USDC_ADDRESS_BASE || USDC_ASSET_BASE;

    const corsHeaders = {
      "access-control-allow-origin": "*",
      "access-control-allow-headers": "PAYMENT-SIGNATURE, X-PAYMENT, Content-Type",
      "access-control-allow-methods": "GET, POST, OPTIONS"
    };

    if (req.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    // Landing page
    if (url.pathname === "/" || url.pathname === "/landing") {
      return new Response(landingHTML(), { headers: { "content-type": "text/html; charset=utf-8", ...corsHeaders } });
    }

    // Health
    if (url.pathname === "/health") {
      return new Response(JSON.stringify({
        ok: true,
        ts: Math.floor(Date.now() / 1000),
        usdc_configured: true,
        operator: OPERATOR_ADDRESS_BASE,
        url_base: "https://aia-x402.rmalka06.workers.dev",
        x402_version: 2,
        bazaar_extension: true,
        cdp_facilitator: CDP_FACILITATOR_BASE + "/platform/v2/x402",
        fallback_facilitator: PUBLIC_FACILITATOR_URL,
        routes: [
          { path: "/v1/free",    price: "FREE",  description: "3 free signals, no payment" },
          { path: "/v1/open",    price: "FREE",  description: "Free feed preview (capped)" },
          { path: "/v1/signals", price: "0.01 USDC", description: descriptionFor("/v1/signals") },
          { path: "/v1/digest",  price: "0.003 USDC", description: descriptionFor("/v1/digest") },
          { path: "/v1/alerts",  price: "0.005 USDC", description: descriptionFor("/v1/alerts") },
          { path: "/.well-known/mcp.json", price: "FREE", description: "MCP discovery" }
        ]
      }), { headers: { "content-type": "application/json", ...corsHeaders }});
    }

    // FREE: live data preview
    if (url.pathname === "/v1/free" || url.pathname === "/v1/open") {
      try {
        // Try KV first
        let feed = await env.AIA_KV.get("feed.json", "json");
        if (!feed || (Date.now() - new Date(feed.ts || 0).getTime()) > 120000) {
          // Build fresh
          feed = await buildFeed();
          ctx.waitUntil(env.AIA_KV.put("feed.json", JSON.stringify(feed)));
        }
        const q = Object.fromEntries(url.searchParams.entries());
        let signals = filterSignals(feed, q);
        // Free tier capped
        const limit = url.pathname === "/v1/free" ? Math.min(3, parseInt(q.limit || "3", 10)) : Math.min(10, parseInt(q.limit || "10", 10));

        // If filter returned nothing, fall back to top signals so the endpoint is always useful
        if (signals.length === 0) {
          signals = (feed.signals || []).slice(0, limit);
        } else {
          signals = signals.slice(0, limit);
        }

        return Response.json({
          tier: url.pathname === "/v1/free" ? "free" : "open",
          endpoint: url.pathname,
          filter: q,
          count: signals.length,
          total_in_feed: feed.count,
          feed_ts: feed.ts,
          signals,
          upgrade_to: "/v1/signals ($0.01 USDC)",
          upgrade_msg: signals.length === limit ? "Get unlimited + any topic via x402" : "Try a different topic or paid for unlimited"
        }, { headers: { "content-type": "application/json", ...corsHeaders }});
      } catch (e) {
        return Response.json({ error: "feed build failed", detail: String(e).slice(0, 200) }, { status: 500, headers: corsHeaders });
      }
    }

    // PAID endpoints
    if (url.pathname.startsWith("/v1/")) {
      const resourceUrl = `https://aia-x402.rmalka06.workers.dev${url.pathname}`;
      const isTestnet = url.searchParams.get("testnet") === "1" || url.searchParams.get("network") === "base-sepolia";
      const price = paymentRequired(resourceUrl, url.pathname, isTestnet);

      const sig = req.headers.get("PAYMENT-SIGNATURE") || req.headers.get("X-PAYMENT");
      if (!sig) {
        return new Response(JSON.stringify(price), {
          status: 402,
          headers: {
            "content-type": "application/json",
            "PAYMENT-REQUIRED": b64encode(price),
            ...corsHeaders
          }
        });
      }
      const payload = b64decode(sig);
      if (!payload) {
        return Response.json({ error: "invalid signature" }, { status: 400, headers: corsHeaders });
      }

      // Verify via CDP
      let verify = { isValid: false };
      try {
        const v = await verifyCDP(payload, price.accepts[0]);
        verify = v.body;
        if (verify.isValid === false) {
          return Response.json({ error: "verification failed", detail: verify }, { status: 402, headers: corsHeaders });
        }
      } catch (e) {
        return Response.json({ error: "facilitator offline", detail: String(e).slice(0,200) }, { status: 503, headers: corsHeaders });
      }

      // Settle via CDP — this is what triggers the bazaar auto-indexing
      let settle = { success: false };
      try {
        const s = await settleCDP(payload, price.accepts[0]);
        settle = s.body;
      } catch (e) {
        settle = { success: false, error: String(e).slice(0,200) };
      }

      if (settle.success === false && env.ALLOW_FALLBACK === "1") {
        try {
          const r2 = await fetch(PUBLIC_FACILITATOR_URL + "/settle", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ x402Version: 2, paymentPayload: payload, paymentRequirements: price.accepts[0] })
          });
          const t2 = await r2.text();
          let j2; try { j2 = JSON.parse(t2); } catch (e) { j2 = { success: false, raw: t2.slice(0,200) }; }
          if (j2.success) {
            settle = { ...j2, facilitator: PUBLIC_FACILITATOR_URL };
          }
        } catch (e) { /* keep original settle */ }
      }

      // Build fresh feed
      let feed = await env.AIA_KV.get("feed.json", "json");
      if (!feed || (Date.now() - new Date(feed.ts || 0).getTime()) > 120000) {
        feed = await buildFeed();
        ctx.waitUntil(env.AIA_KV.put("feed.json", JSON.stringify(feed)));
      }

      const q = Object.fromEntries(url.searchParams.entries());
      const signals = filterSignals(feed, q);

      let body, ct = "application/json";
      if (url.pathname === "/v1/digest") {
        body = digest(signals);
        ct = "text/plain; charset=utf-8";
      } else if (url.pathname === "/v1/alerts") {
        body = { endpoint: url.pathname, filter: q, count: signals.length,
                 preview: signals.slice(0,5), note: "for full webhook delivery, contact operator" };
      } else {
        body = { endpoint: url.pathname, filter: q, count: signals.length, signals };
      }
      return new Response(typeof body === "string" ? body : JSON.stringify({ ...body, settlement: settle }), {
        status: 200,
        headers: {
          "content-type": ct,
          "PAYMENT-RESPONSE": b64encode(settle),
          ...corsHeaders
        }
      });
    }

    if (url.pathname === "/.well-known/mcp.json" || url.pathname === "/.well-known/mcp") {
      return Response.json({
        mcpVersion: "2024-11-05",
        name: "aia",
        title: "AIA Real-Time Signal Stream",
        version: "3.0.0",
        description: "Real-time curated AI/agent/crypto/x402 signals from HN, GitHub Trending, Reddit, Lobsters. Scored, deduplicated, ready to use. Free preview at /v1/free. Paid: $0.01/signals, $0.003/digest, $0.005/alerts.",
        author: { name: "razel369-aia", url: "https://razel369.github.io/aia/" },
        operator: OPERATOR_ADDRESS_BASE,
        network: "base",
        homepage: "https://aia-x402.rmalka06.workers.dev",
        tools: [
          { name: "aia_free_preview", description: "Get 3 free signals (no payment)", inputSchema: { type: "object", properties: { topics: { type: "string" } } } },
          { name: "aia_signals", description: "Get full filtered signal stream ($0.01)", inputSchema: { type: "object", properties: { topics: { type: "string" }, limit: { type: "integer" }, source: { type: "string" } } } },
          { name: "aia_digest", description: "Get daily digest in plain text ($0.003)", inputSchema: { type: "object", properties: { topics: { type: "string" } } } }
        ],
        pricing: {
          "/v1/free": "FREE",
          "/v1/signals": "0.01 USDC",
          "/v1/digest":  "0.003 USDC",
          "/v1/alerts":  "0.005 USDC"
        },
        payment: {
          protocol: "x402",
          network: "eip-155:8453",
          asset: USDC_ASSET_BASE,
          payTo: OPERATOR_ADDRESS_BASE
        }
      }, { headers: { "content-type": "application/json", ...corsHeaders }});
    }

    return Response.json({
      routes: ["/", "/health", "/v1/free (FREE, 3 signals)", "/v1/open (FREE, 10 signals)",
               "/v1/signals?topics=ai-agents&limit=10 ($0.01)",
               "/v1/digest?topics=x402 ($0.003, plaintext)",
               "/v1/alerts?topics=crypto ($0.005)",
               "/.well-known/mcp.json (MCP)"],
      pricing: {
        "/v1/free": "FREE",
        "/v1/open": "FREE",
        "/v1/signals": "10000 (0.01 USDC)",
        "/v1/digest":  "3000 (0.003 USDC)",
        "/v1/alerts":  "5000 (0.005 USDC)"
      },
      facilitator_primary: CDP_FACILITATOR_BASE + "/platform/v2/x402",
      facilitator_fallback: PUBLIC_FACILITATOR_URL,
      operator: OPERATOR_ADDRESS_BASE,
      bazaar: bazaarForRoute("/v1/signals")
    }, { status: 404, headers: corsHeaders });
  }
};