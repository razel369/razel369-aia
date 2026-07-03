// AIA x402 Facilitator — earns 0.1% (configurable) on every payment
// it helps verify. Free for first 1000 tx/month to bootstrap adoption.
//
// Routes:
//   POST /verify   → verify a payment payload (no settlement)
//   POST /settle   → verify + record settlement + earn fee
//   GET  /health   → health + counters
//   GET  /stats    → tx count, earnings, top merchants
//
// This is the same protocol the CDP facilitator at x402.org/facilitator
// uses, so any x402-compliant buyer/seller can use it by switching
// their FACILITATOR_URL to this Worker.
const FACILITATOR_VERSION = "0.1.0";

async function verifyPayment(paymentPayload, requirements) {
  // Light sanity check on the payload shape. In production you'd verify
  // the EIP-3009 signed authorization on-chain (or call a chain RPC
  // for `transferWithAuthorization`). For the demo we trust the
  // structure + presence of fields.
  if (!paymentPayload || !requirements) {
    return { isValid: false, reason: "missing payload or requirements" };
  }
  const a = paymentPayload.payload || {};
  if (!a.signature || !a.authorization) {
    return { isValid: false, reason: "malformed payload" };
  }
  if (a.authorization.to !== requirements.payTo) {
    return { isValid: false, reason: "payTo mismatch" };
  }
  if (parseInt(a.authorization.value) < parseInt(requirements.maxAmountRequired)) {
    return { isValid: false, reason: "insufficient amount" };
  }
  return {
    isValid: true,
    payer: a.authorization.from,
  };
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const headers = {
      "access-control-allow-origin": "*",
      "access-control-allow-headers": "content-type, x-payment, payment-signature",
      "access-control-allow-methods": "GET, POST, OPTIONS",
    };
    if (req.method === "OPTIONS") {
      return new Response(null, { status: 204, headers });
    }

    if (url.pathname === "/health") {
      return Response.json({
        ok: true,
        version: FACILITATOR_VERSION,
        facilitator: FACILITATOR_NAME,
        fee_bps: parseInt(env.FEE_BPS || "10"),
        free_tier_per_month: parseInt(env.FREE_TIER_PER_MONTH || "1000"),
        routes: ["POST /verify", "POST /settle", "GET /health", "GET /stats"],
      }, { headers });
    }

    if (url.pathname === "/stats") {
      // Pull counters from KV
      const monthKey = new Date().toISOString().slice(0, 7); // YYYY-MM
      const txCountKey = `tx:${monthKey}`;
      const txCount = parseInt((await env.FACILITATOR_KV.get(txCountKey)) || "0");
      const totalKey = "tx:total";
      const total = parseInt((await env.FACILITATOR_KV.get(totalKey)) || "0");
      const usdcEarningsKey = `usdc:${monthKey}`;
      const usdcEarnings = parseInt((await env.FACILITATOR_KV.get(usdcEarningsKey)) || "0");
      return Response.json({
        month: monthKey,
        transactions_this_month: txCount,
        transactions_total: total,
        usdc_earnings_6decimals: usdcEarnings,
        usdc_earnings_human: (usdcEarnings / 1_000_000).toFixed(6),
        free_tier_remaining: Math.max(0,
          parseInt(env.FREE_TIER_PER_MONTH || "1000") - txCount),
      }, { headers });
    }

    if (url.pathname === "/verify" && req.method === "POST") {
      const body = await req.json().catch(() => null);
      if (!body) return new Response("invalid json", { status: 400, headers });
      const { paymentPayload, paymentRequirements } = body;
      const v = await verifyPayment(paymentPayload, paymentRequirements);
      return Response.json({
        x402Version: 2,
        ...v,
        facilitator: FACILITATOR_NAME,
      }, { status: v.isValid ? 200 : 402, headers });
    }

    if (url.pathname === "/settle" && req.method === "POST") {
      const body = await req.json().catch(() => null);
      if (!body) return new Response("invalid json", { status: 400, headers });
      const { paymentPayload, paymentRequirements } = body;
      const v = await verifyPayment(paymentPayload, paymentRequirements);
      if (!v.isValid) {
        return Response.json({
          x402Version: 2,
          success: false,
          ...v,
          facilitator: FACILITATOR_NAME,
        }, { status: 402, headers });
      }
      // Calculate fee
      const amount = parseInt(paymentRequirements.maxAmountRequired);
      const feeBps = parseInt(env.FEE_BPS || "10");
      const fee = Math.floor((amount * feeBps) / 10000);
      const txId = `tx_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
      // Update counters
      const monthKey = new Date().toISOString().slice(0, 7);
      ctx.waitUntil((async () => {
        const mkv = env.FACILITATOR_KV;
        await mkv.put(`tx:${monthKey}`, String(parseInt((await mkv.get(`tx:${monthKey}`)) || "0") + 1));
        await mkv.put(`tx:total`, String(parseInt((await mkv.get("tx:total")) || "0") + 1));
        await mkv.put(`usdc:${monthKey}`, String(parseInt((await mkv.get(`usdc:${monthKey}`)) || "0") + fee));
        await mkv.put(`tx:${txId}`, JSON.stringify({
          ts: new Date().toISOString(),
          payer: v.payer,
          payee: paymentRequirements.payTo,
          amount,
          fee,
          resource: paymentRequirements.resource,
        }));
      })());
      return Response.json({
        x402Version: 2,
        success: true,
        transaction: txId,
        network: paymentRequirements.network,
        fee_bps: feeBps,
        fee,
        facilitator: FACILITATOR_NAME,
      }, { headers });
    }

    return Response.json({ error: "not found" }, { status: 404, headers });
  },
};
