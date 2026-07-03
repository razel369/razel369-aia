// AIA x402 paid API — Cloudflare Worker
// Production: uses CDP facilitator so any successful payment auto-indexes AIA
// in the Coinbase CDP Bazaar (and downstream x402scan / agentic.market / Merit).
// Endpoints:
//   GET /health            → 200 ok
//   GET /v1/open           → 200 + full free feed (no payment)
//   GET /v1/signals?...    → 402 PaymentRequired, or 200 with signature
//   GET /v1/digest?topics  → 402 PaymentRequired, or 200 digest text
//   GET /v1/alerts?topics  → 402 PaymentRequired, or 200 webhook preview
//   GET /.well-known/mcp.json → 200 MCP discovery
// x402 v2 spec: https://github.com/coinbase/x402
// CDP Bazaar: https://docs.cdp.coinbase.com/x402/bazaar

const USDC_ASSET_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"; // USDC on Base
const USDC_ASSET_BASE_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"; // USDC on Base Sepolia (testnet)

// Primary: CDP Facilitator — this is what indexes our service in the Bazaar
const CDP_FACILITATOR_BASE = "https://api.cdp.coinbase.com";
// Fallback: x402.org public facilitator (no auto-indexing)
const PUBLIC_FACILITATOR_URL = "https://x402.org/facilitator";

// Operator wallet (Base mainnet). Real USDC settles here.
const OPERATOR_ADDRESS_BASE = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e";
// Testnet operator (same EOA, used when caller is on base-sepolia)
const OPERATOR_ADDRESS_TEST = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e";

function b64encode(obj) { return btoa(JSON.stringify(obj)); }
function b64decode(str) { try { return JSON.parse(atob(str)); } catch (e) { return null; } }

// ---- BAZAAR METADATA (CDP-Compliant) ----
// The Bazaar auto-indexes a service when the CDP facilitator settles a payment,
// provided the 402 response carries the bazaar extension in this shape.

function bazaarForRoute(pathname) {
  // Per-route bazaar info — what CDP reads to register the service
  if (pathname === "/v1/signals") {
    return {
      discoverable: true,
      category: "data",
      tags: ["ai","agents","signals","curation","news","crypto","x402","research","autonomous","hn","github"],
      info: {
        input: {
          type: "http",
          method: "GET",
          queryParams: {
            topics: "ai-agents,crypto",
            limit: 10,
            min_score: 0.0,
            source: "hn"
          }
        },
        output: {
          type: "json",
          example: {
            endpoint: "/v1/signals",
            count: 1,
            signals: [{
              source: "hn",
              title: "Example signal",
              url: "https://news.ycombinator.com/item?id=1",
              final_score: 0.87,
              topics: ["ai","agents"],
              ts: "2026-07-03T12:00:00Z"
            }]
          }
        }
      },
      schema: {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        type: "object",
        properties: {
          input: {
            type: "object",
            additionalProperties: false,
            properties: {
              type: { const: "http" },
              method: { enum: ["GET"] }
            },
            required: ["type","method"]
          },
          output: {
            type: "object",
            properties: {
              type: { type: "string" },
              example: { type: "object" }
            },
            required: ["type"]
          }
        },
        required: ["input"]
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
          queryParams: { topics: "x402,agents" }
        },
        output: {
          type: "text",
          example: "AIA digest (5 signals)\n\nTop topics: x402(3), agents(2)\n\n1. [hn] ..."
        }
      },
      schema: {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        type: "object",
        properties: {
          input: {
            type: "object",
            additionalProperties: false,
            properties: {
              type: { const: "http" },
              method: { enum: ["GET"] }
            },
            required: ["type","method"]
          },
          output: {
            type: "object",
            properties: {
              type: { type: "string" },
              example: { type: "string" }
            },
            required: ["type"]
          }
        },
        required: ["input"]
      }
    };
  }
  if (pathname === "/v1/alerts") {
    return {
      discoverable: true,
      category: "data",
      tags: ["alerts","webhook","monitoring","ai","agents","subscription"],
      info: {
        input: {
          type: "http",
          method: "GET",
          queryParams: { topics: "crypto" }
        },
        output: {
          type: "json",
          example: {
            endpoint: "/v1/alerts",
            filter: { topics: "crypto" },
            count: 5,
            preview: [],
            note: "for full webhook delivery, contact operator"
          }
        }
      },
      schema: {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        type: "object",
        properties: {
          input: {
            type: "object",
            additionalProperties: false,
            properties: {
              type: { const: "http" },
              method: { enum: ["GET"] }
            },
            required: ["type","method"]
          },
          output: {
            type: "object",
            properties: {
              type: { type: "string" },
              example: { type: "object" }
            },
            required: ["type"]
          }
        },
        required: ["input"]
      }
    };
  }
  return null;
}

function priceFor(path) {
  if (path === "/v1/signals") return "10000";   // $0.01
  if (path === "/v1/digest") return "3000";    // $0.003
  if (path === "/v1/alerts") return "5000";    // $0.005
  return "10000";
}
function descriptionFor(path) {
  if (path === "/v1/signals") return "Filtered curated AI/agent/crypto signal stream (JSON). 6 sources, scored, deduped. Cached 5 min.";
  if (path === "/v1/digest")  return "One-paragraph daily digest in plain text. Cached 60 min.";
  if (path === "/v1/alerts")  return "Webhook subscription preview (JSON) — see top matches for a topic.";
  return "AIA curated signal access";
}

function paymentRequired(resourceUrl, endpoint, isTestnet) {
  const network = isTestnet ? "eip-155:84532" : "eip-155:8453";
  const asset   = isTestnet ? USDC_ASSET_BASE_SEPOLIA : USDC_ASSET_BASE;
  const payTo   = isTestnet ? OPERATOR_ADDRESS_TEST  : OPERATOR_ADDRESS_BASE;

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
    extensions: {
      bazaar: bazaarForRoute(endpoint) || { discoverable: true }
    }
  };
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
  for (const s of signals) for (const t of (s.topics || [])) trending[t] = (trending[t] || 0) + 1;
  const topTopic = Object.entries(trending).sort((a,b) => b[1]-a[1]).slice(0,3).map(([t,c])=>`${t}(${c})`).join(", ");
  return `AIA digest (${signals.length} signals)\n\nTop topics: ${topTopic || "-"}\n\n` + lines.join("\n");
}

async function settleCDP(paymentPayload, paymentRequirements) {
  // CDP Facilitator — settle endpoint
  // POST /platform/v2/x402/settle
  const r = await fetch(CDP_FACILITATOR_BASE + "/platform/v2/x402/settle", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      x402Version: 2,
      paymentPayload,
      paymentRequirements
    })
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

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    globalThis.USDC_ADDRESS_BASE = env.USDC_ADDRESS_BASE || USDC_ASSET_BASE;

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
          { path: "/v1/signals",  price: "10000 (0.01 USDC)",  type: "http",  description: descriptionFor("/v1/signals"), bazaar: bazaarForRoute("/v1/signals")?.tags },
          { path: "/v1/digest",   price: "3000 (0.003 USDC)",  type: "http",  description: descriptionFor("/v1/digest"),  bazaar: bazaarForRoute("/v1/digest")?.tags  },
          { path: "/v1/alerts",   price: "5000 (0.005 USDC)",  type: "http",  description: descriptionFor("/v1/alerts"),  bazaar: bazaarForRoute("/v1/alerts")?.tags  },
          { path: "mcp://aia/curate", price: "10000 (0.01 USDC)", type: "mcp", description: "MCP tool: curated signals" },
          { path: "mcp://aia/digest",  price: "3000 (0.003 USDC)", type: "mcp", description: "MCP tool: daily digest" }
        ]
      }), { headers: { "content-type": "application/json" }});
    }

    if (url.pathname === "/v1/open") {
      const feed = await env.AIA_KV.get("feed.json", "json");
      return Response.json(feed || { signals: [] });
    }

    if (url.pathname.startsWith("/v1/")) {
      const resourceUrl = `https://aia-x402.rmalka06.workers.dev${url.pathname}`;
      // Caller can force testnet via ?testnet=1
      const isTestnet = url.searchParams.get("testnet") === "1" || url.searchParams.get("network") === "base-sepolia";
      const price = paymentRequired(resourceUrl, url.pathname, isTestnet);

      const sig = req.headers.get("PAYMENT-SIGNATURE") || req.headers.get("X-PAYMENT");
      if (!sig) {
        return new Response(JSON.stringify(price), {
          status: 402,
          headers: {
            "content-type": "application/json",
            "PAYMENT-REQUIRED": b64encode(price),
            "access-control-allow-origin": "*",
            "access-control-allow-headers": "PAYMENT-SIGNATURE, X-PAYMENT, Content-Type"
          }
        });
      }
      const payload = b64decode(sig);
      if (!payload) {
        return Response.json({ error: "invalid signature" }, { status: 400 });
      }

      // Verify via CDP
      let verify = { isValid: false };
      try {
        const v = await verifyCDP(payload, price.accepts[0]);
        verify = v.body;
        if (verify.isValid === false) {
          return Response.json({ error: "verification failed", detail: verify }, { status: 402 });
        }
      } catch (e) {
        return Response.json({ error: "facilitator offline", detail: String(e).slice(0,200) }, { status: 503 });
      }

      // Settle via CDP — this is what triggers the bazaar auto-indexing
      let settle = { success: false };
      try {
        const s = await settleCDP(payload, price.accepts[0]);
        settle = s.body;
      } catch (e) {
        settle = { success: false, error: String(e).slice(0,200) };
      }

      // If CDP facilitator unavailable, fall back to x402.org public
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
      return new Response(typeof body === "string" ? body : JSON.stringify({ ...body, settlement: settle }), {
        status: 200,
        headers: {
          "content-type": ct,
          "PAYMENT-RESPONSE": b64encode(settle),
          "access-control-allow-origin": "*"
        }
      });
    }

    if (url.pathname === "/.well-known/mcp.json" || url.pathname === "/.well-known/mcp") {
      return Response.json({
        mcpVersion: "2024-11-05",
        name: "aia",
        title: "AIA Real-Time Signal Stream",
        version: "1.1.0",
        description: "Filtered curated AI/agent/crypto/finance signals from HN, GitHub trending, V2EX, dev.to, Lobsters. 40+ signals per run, scored and deduplicated. Affordable x402 micro-payments on Base ($0.01 signals, $0.003 digest, $0.005 alerts).",
        author: { name: "razel369-aia", url: "https://razel369.github.io/aia/" },
        operator: OPERATOR_ADDRESS_BASE,
        network: "base",
        homepage: "https://aia-x402.rmalka06.workers.dev",
        tools: [
          { name: "aia_curate", description: "Get curated AI-agent signals", inputSchema: { type: "object", properties: { topics: { type: "string" }, limit: { type: "integer" } } } },
          { name: "aia_digest", description: "Get daily digest in plain text", inputSchema: { type: "object", properties: { topics: { type: "string" } } } }
        ],
        pricing: {
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
      }, { headers: { "content-type": "application/json", "access-control-allow-origin": "*" }});
    }

    // Default: 404 + machine-readable route catalog
    return Response.json({
      routes: ["/health", "/v1/open (free)",
               "/v1/signals?topics=ai-agents&limit=10 ($0.01)",
               "/v1/digest?topics=x402 ($0.003, plaintext)",
               "/v1/alerts?topics=crypto ($0.005)",
               "/.well-known/mcp.json (MCP)"],
      pricing: {
        "/v1/signals": "10000 (0.01 USDC)",
        "/v1/digest":  "3000 (0.003 USDC)",
        "/v1/alerts":  "5000 (0.005 USDC)"
      },
      facilitator_primary: CDP_FACILITATOR_BASE + "/platform/v2/x402",
      facilitator_fallback: PUBLIC_FACILITATOR_URL,
      operator: OPERATOR_ADDRESS_BASE,
      bazaar: bazaarForRoute("/v1/signals")
    }, { status: 404 });
  }
};
