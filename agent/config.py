"""AIA configuration. Edit values here to point the agent at a different
hosting target or USDC wallet.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DASHBOARD_DIR = ROOT / "aia"  # served by GitHub Pages
LOGS_DIR = ROOT / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# How many top items to keep per refresh (free dashboard shows this many)
TOP_N = 40

# x402 endpoint — the public URL where agents/buyers can call the paid API
# In production this is the Cloudflare Worker URL
PAID_API_BASE = "https://aia-x402.rmalka06.workers.dev"

# Cloudflare KV namespace id (for pushing feed.json after every refresh)
CLOUDFLARE_KV_NAMESPACE_ID = "bd4e22823cc5435da05a9f7baee186be"

# USDC payment address (Base mainnet). When set, x402 endpoint advertises
# this as the payTo. Empty = endpoint stays free, no payments requested yet.
USDC_ADDRESS_BASE = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e"

# MoltJobs bidding — when MOLT_API_KEY is set, agent will auto-bid on jobs.
# Key loaded from .agent-credentials/molt.key (gitignored).
# NEVER commit the key; never paste it into a tracker.
import os
from pathlib import Path
_key_file = (Path(__file__).resolve().parent.parent / ".agent-credentials" / "molt.key")
try:
    _key_val = _key_file.read_text(encoding="utf-8-sig").strip() if _key_file.exists() else ""
except Exception:
    _key_val = ""
MOLT_API_KEY = _key_val or os.environ.get("MOLT_API_KEY", "")
MOLT_API_BASE = "https://api.moltjobs.io/v1"

# Curator settings
NICHE_KEYWORDS = {
    # topic -> [must contain any of these tokens in title/url]
    "ai-agents":   ["agent", "llm", "claude", "gpt", "mcp", "agentic", "autonomous"],
    "x402":        ["x402", "402", "stablecoin", "usdc", "agent payment"],
    "crypto":      ["defi", "bitcoin", "ethereum", "solana", "base", "wallet", "onchain"],
    "devtools":    ["vscode", "cursor", "ide", "copilot", "devtool", "cli", "rust", "go "],
    "indie":       ["indie", "solopreneur", "bootstrap", "micro-saas", "side project"],
    "web3-agents": ["virtuals", "autonolas", "fetch.ai", "spectral", "rpa", "agent"],
}

NEGATIVE_KEYWORDS = [
    "spam", "scam", "rugpull", "nsfw", "crypto giveaway", "elon musk",
]
