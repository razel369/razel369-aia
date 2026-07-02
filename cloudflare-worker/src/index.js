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

function b64encode(obj) {
  return btoa(JSON.stringify(obj));
}
function b64decode(str) {
  return JSON.parse(atob(str));
}

function paymentRequired(resourceUrl) {
  return {
    x402Version: 2,
    error: "X-PAYMENT header is required",
    accepts: [{
      scheme: "exact",
      network: "eip-155:8453",
      resource: resourceUrl,
      description: "Access to AIA curated signal stream",
      mimeType: "application/json",
      payTo: USDC_ADDRESS_BASE || "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
      maxAmountRequired: "10000",              // 0.01 USDC
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
  return await r.json();
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
    (s.topics.length ? ` (${s.topics.join(", ")})` : "")
  );
  return `AIA digest — top ${top.length} signals:\n\n` + lines.join("\n");
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    globalThis.USDC_ADDRESS_BASE = env.USDC_ADDRESS_BASE || "0xNOT_CONFIGURED";

    if (url.pathname === "/health") {
      return new Response(JSON.stringify({
        ok: true, ts: Math.floor(Date.now() / 1000),
        usdc_configured: !!env.USDC_ADDRESS_BASE,
      }), { headers: { "content-type": "application/json" }});
    }

    // Free open feed — useful for the dashboard's RSS-style "what's new"
    if (url.pathname === "/v1/open") {
      const feed = await env.AIA_KV.get("feed.json", "json");
      return Response.json(feed || { signals: [] });
    }

    if (url.pathname.startsWith("/v1/")) {
      const resourceUrl = `https://aia.razel369.com${url.pathname}`;
      const price = paymentRequired(resourceUrl);
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
      // Real verification
      const verify = await verifyWithFacilitator(payload, price.accepts[0]);
      if (!verify.isValid) {
        return Response.json({ error: "verification failed", detail: verify }, { status: 402 });
      }
      const feed = await env.AIA_KV.get("feed.json", "json");
      const q = Object.fromEntries(url.searchParams.entries());
      const signals = filterSignals(feed, q);
      const body = (url.pathname === "/v1/digest")
        ? { endpoint: url.pathname, digest: digest(signals) }
        : { endpoint: url.pathname, filter: q, count: signals.length, signals };
      // Tell facilitator to settle
      const settle = await fetch(FACILITATOR_URL + "/settle", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ x402Version: 2, paymentPayload: payload, paymentRequirements: price.accepts[0] }),
      });
      const settleJson = await settle.json();
      return new Response(JSON.stringify({ ...body, settlement: settleJson }), {
        status: 200,
        headers: {
          "content-type": "application/json",
          "PAYMENT-RESPONSE": b64encode(settleJson),
          "access-control-allow-origin": "*",
        }
      });
    }

    return Response.json({
      routes: ["/health", "/v1/open", "/v1/signals?topics=ai-agents&limit=10",
               "/v1/digest?topics=x402"],
    }, { status: 404 });
  },
};
