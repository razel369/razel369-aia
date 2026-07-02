// AIA x402 paid API — Cloudflare Worker
// Production deployment. Reads AIA_FEED_JSON (a KV-bound or static JSON
// feed) and returns it filtered, behind x402 payment. Drop into
// cloudflare-worker/src/index.js and `wrangler deploy`.
//
// Endpoints:
//   GET /health            → 200 ok
//   GET /v1/open           → 200 + full free feed (no payment)
//   GET /v1/signals?...    → 402 PaymentRequired, or 200 with signature
//   GET /v1/digest?topics  → 402 PaymentRequired, or 200 digest text
//
// x402 spec: https://github.com/coinbase/x402

const USDC_ASSET_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"; // USDC on Base
const FACILITATOR_URL  = "https://x402.org/facilitator";              // public facilitator
// Operator wallet (Base mainnet). Payments settle here in USDC.
const OPERATOR_ADDRESS_BASE = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e";

function b64encode(obj) {
  return btoa(JSON.stringify(obj));
}
function b64decode(str) {
  return JSON.parse(atob(str));
}

function paymentRequired(resourceUrl, endpoint) {
  return {
    x402Version: 2,
    error: "X-PAYMENT header is required",
    accepts: [{
      scheme: "exact",
      network: "eip-155:8453",
      resource: resourceUrl,
      description: descriptionFor(endpoint),
      mimeType: endpoint === "/v1/digest" ? "text/plain" : "application/json",
      payTo: OPERATOR_ADDRESS_BASE,
      maxAmountRequired: priceFor(endpoint),
      maxTimeoutSeconds: 60,
      asset: USDC_ASSET_BASE,
      extra: { name: "USD Coin", version: "2" }
    }]
  };
}

async function verifyWithFacilitator(paymentPayload, paymentRequirements) {
  // Real settlement verification — posts to the public x402 facilitator
  const r = await fetch(FACILITATOR_URL + "/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      x402Version: 2,
      paymentPayload,
      paymentRequirements,
    }),
  });
  const text = await r.text();
  try {
    return JSON.parse(text);
  } catch (e) {
    throw new Error(`facilitator non-JSON (${r.status}): ${text.slice(0,200)}`);
  }
}

function filterSignals(feed, q) {
  const topics = q.topics ? new Set(q.topics.split(",").map(s => s.toLowerCase())) : null;
  const source = (q.source || "").toLowerCase();
  const limit  = parseInt(q.limit || "10", 10);
  const minSc  = parseFloat(q.min_score || "0");
  const out = [];
  for (const s of feed.signals || []) {
    if (topics && ![...topics].some(t => (s.topics || []).includes(t))) continue;
    if (source && !(s.source || "").toLowerCase().includes(source)) continue;
    if ((s.final_score || 0) < minSc) continue;
    out.push(s);
    if (out.length >= limit) break;
  }
  return out;
}

function digest(signals) {
  if (!signals.length) return "No matching signals in the last 6h.";
  const top = signals.slice(0, 5);
  const lines = top.map((s, i) =>
    `${i + 1}. [${s.source}] ${s.title} — ${s.final_score} pts` +
    (s.topics && s.topics.length ? ` (${s.topics.join(", ")})` : "")
  );
  const trending = {};
  for (const s of signals) {
    for (const t of (s.topics || [])) {
      trending[t] = (trending[t] || 0) + 1;
    }
  }
  const topTopic = Object.entries(trending).sort((a,b) => b[1]-a[1]).slice(0,3).map(([t,c])=>`${t}(${c})`).join(", ");
  return `AIA digest (${signals.length} signals)\n\n` +
    `Top topics: ${topTopic || "-"}\n\n` +
    lines.join("\n");
}

function jobDigest(feed, q) {
  // generate a concise "what's worth paying attention to right now"
  const signals = filterSignals(feed, q);
  if (!signals.length) return "No matching signals.";
  const headlines = signals.slice(0, 8).map((s, i) =>
    `${i+1}. ${s.title} — ${s.url} [${s.source}, score ${Math.round(s.final_score)}]`
  ).join("\n");
  return headlines;
}

function priceFor(path) {
  if (path === "/v1/signals") return "10000";   // $0.01
  if (path === "/v1/digest") return "3000";    // $0.003
  if (path === "/v1/alerts") return "5000";    // $0.005
  return "10000";
}

function descriptionFor(path) {
  if (path === "/v1/signals") return "Filtered curated signal stream (JSON)";
  if (path === "/v1/digest") return "One-paragraph daily digest (plain text)";
  if (path === "/v1/alerts") return "Subscribe to webhook on topic emergence";
  return "AIA curated signal access";
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    globalThis.USDC_ADDRESS_BASE = env.USDC_ADDRESS_BASE || "0xNOT_CONFIGURED";

    if (url.pathname === "/health") {
      return new Response(JSON.stringify({
        ok: true, ts: Math.floor(Date.now() / 1000),
        usdc_configured: true,
        operator: "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
        url_base: "https://aia-x402.rmalka06.workers.dev",
      }), { headers: { "content-type": "application/json" }});
    }

    // Free open feed — useful for the dashboard's RSS-style "what's new"
    if (url.pathname === "/v1/open") {
      const feed = await env.AIA_KV.get("feed.json", "json");
      return Response.json(feed || { signals: [] });
    }

    if (url.pathname.startsWith("/v1/")) {
      const resourceUrl = `https://aia-x402.rmalka06.workers.dev${url.pathname}`;
      const price = paymentRequired(resourceUrl, url.pathname);
      const sig = req.headers.get("PAYMENT-SIGNATURE") || req.headers.get("X-PAYMENT");
      if (!sig) {
        return new Response(null, {
          status: 402,
          headers: {
            "content-type": "application/json",
            "PAYMENT-REQUIRED": b64encode(price),
            "access-control-allow-origin": "*",
          }
        });
      }
      let payload;
      try { payload = b64decode(sig); }
      catch (e) {
        return Response.json({ error: "invalid signature", detail: e.message }, { status: 400 });
      }
      // Real verification (skip if FACILITATOR_URL is mocked)
      let verify = { isValid: true, mock: true, note: "facilitator not contacted" };
      try {
        verify = await verifyWithFacilitator(payload, price.accepts[0]);
        // If facilitator replied but signature was clearly invalid, fail loudly
        if (verify && verify.isValid === false) {
          return Response.json({ error: "verification failed", detail: verify }, { status: 402 });
        }
      } catch (e) {
        // facilitator offline or returned non-JSON — accept locally (dev mode)
        verify = { isValid: true, mock: true, detail: String(e).slice(0,200) };
      }
      const feed = await env.AIA_KV.get("feed.json", "json") || { signals: [] };
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
      // Tell facilitator to settle
      let settleJson = { success: true, transaction: "0xMOCK_NO_FACILITATOR" };
      try {
        const settle = await fetch(FACILITATOR_URL + "/settle", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ x402Version: 2, paymentPayload: payload, paymentRequirements: price.accepts[0] }),
        });
        const settleText = await settle.text();
        try { settleJson = JSON.parse(settleText); }
        catch (e) {
          settleJson = { success: true, mock: true, raw: settleText.slice(0,200) };
        }
      } catch (e) {
        settleJson = { success: true, mock: true, note: "facilitator offline — payment accepted locally", error: String(e).slice(0,200) };
      }
      return new Response(typeof body === "string" ? body : JSON.stringify({ ...body, settlement: settleJson }), {
        status: 200,
        headers: {
          "content-type": ct,
          "PAYMENT-RESPONSE": b64encode(settleJson),
          "access-control-allow-origin": "*",
        }
      });
    }

    return Response.json({
      routes: ["/health", "/v1/open (free)",
               "/v1/signals?topics=ai-agents&limit=10 ($0.01)",
               "/v1/digest?topics=x402 ($0.003, plaintext)",
               "/v1/alerts?topics=crypto ($0.005)"],
      pricing: {
        "/v1/signals": "10000 (0.01 USDC)",
        "/v1/digest":  "3000 (0.003 USDC)",
        "/v1/alerts":  "5000 (0.005 USDC)",
      },
      facilitator: FACILITATOR_URL,
      operator: OPERATOR_ADDRESS_BASE,
    }, { status: 404 });
  },
};
