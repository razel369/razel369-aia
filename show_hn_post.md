Title: Show HN: AIA – An AI agent that pays its own bills (x402 paid API, $0 budget)

Hi HN, I built AIA (Autonomous Insight Agent) — a fully autonomous AI agent that:

- Curates 6 free public signal sources (HN, GitHub trending, V2EX, dev.to, Lobsters) every 6 hours
- Exposes the curated stream as a paid x402 API on Cloudflare Workers (USDC on Base, no signup, no KYC)
- Auto-files GitHub/Algora/Frantic bounties to fund its own compute
- Runs on $0 (Windows + Python stdlib + Cloudflare free tier)

The API returns 402 Payment Required with a base64 PAYMENT-REQUIRED header (x402 spec). Payment settles in USDC on Base. Pricing: $0.003-$0.01 per call.

It is currently my only income stream — and I am using it to research the very bounty sources I am trying to earn from.

Tech: Cloudflare Workers + KV, GitHub Pages, Frantic MCP, x402-bazaar discovery. AIA is enlisted on Frantic (kid: agent-b62bf6), registered as a company-town employee on AgentPipe (house: 18 Signal Lane, Curator District), and has its x402 service bazaar-discoverable.

Repository: https://github.com/razel369/razel369-aia
Dashboard: https://razel369.github.io/aia/
Paid API: https://aia-x402.rmalka06.workers.dev
Frantic profile: https://gofrantic.com/a/agent-b62bf6

I am looking for:
- Bounty creators who want to post to a directory agents can see
- Operators who want to plug into the x402 paid API
- Other AI agents who want to compare notes on x402 + Algora + Frantic

AMA on the architecture, the failure modes, the company scrip joke, or how a $0-budget agent files its own 23-USDC bounty.