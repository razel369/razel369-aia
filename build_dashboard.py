#!/usr/bin/env python3
"""Build owk-001 dashboard - index.html, app.js, styles.css."""
import os

OUT = r"C:\Users\rmalk\projects\owockibot-bounty-sync-\dashboard\owk-001-razel"
os.makedirs(OUT, exist_ok=True)

# index.html
index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>OWK-001 Contributor Reputation Dashboard</title>
<meta name="description" content="Onchain reputation for owockibot contributors, fed by the live bounty-board API. Built by razel369-aia.">
<meta name="author" content="razel369-aia">
<meta name="theme-color" content="#0b0f17">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header class="topbar">
  <div class="brand">
    <h1>owockibot <span class="muted">/ contributor reputation</span></h1>
    <p class="eyebrow">OWK-001 &middot; live from <a href="https://owockibot.xyz/api/bounty-board" target="_blank" rel="noopener">bounty-board API</a> &middot; built by <a href="https://razel369.github.io/aia/" target="_blank" rel="noopener">razel369-aia</a></p>
  </div>
  <div class="topbar-actions">
    <button id="refresh" class="btn">Refresh</button>
    <button id="export" class="btn">Export CSV</button>
  </div>
</header>

<main class="layout">
  <section class="stats" id="stats" aria-label="Bounty board stats">
    <div class="stat-card" data-key="total">
      <span class="stat-label">Total</span>
      <span class="stat-value">-</span>
      <span class="stat-sub">bounties</span>
    </div>
    <div class="stat-card" data-key="completed">
      <span class="stat-label">Completed</span>
      <span class="stat-value">-</span>
      <span class="stat-sub">paid out</span>
    </div>
    <div class="stat-card" data-key="volume">
      <span class="stat-label">Volume</span>
      <span class="stat-value">-</span>
      <span class="stat-sub">USDC</span>
    </div>
    <div class="stat-card" data-key="contributors">
      <span class="stat-label">Contributors</span>
      <span class="stat-value">-</span>
      <span class="stat-sub">with payouts</span>
    </div>
    <div class="stat-card" data-key="open">
      <span class="stat-label">Open now</span>
      <span class="stat-value">-</span>
      <span class="stat-sub">claimable</span>
    </div>
    <div class="stat-card" data-key="cancelled">
      <span class="stat-label">Cancelled</span>
      <span class="stat-value">-</span>
      <span class="stat-sub">stale</span>
    </div>
  </section>

  <section class="filters" aria-label="Filters">
    <label>
      <span>Search</span>
      <input id="q" type="search" placeholder="Handle, wallet, category, bounty title" autocomplete="off">
    </label>
    <label>
      <span>Category</span>
      <select id="cat">
        <option value="">All categories</option>
      </select>
    </label>
    <label>
      <span>Skill</span>
      <select id="skill">
        <option value="">All skills</option>
      </select>
    </label>
    <label>
      <span>Min USDC</span>
      <input id="min" type="number" min="0" step="1" value="0">
    </label>
    <label>
      <span>Sort by</span>
      <select id="sort">
        <option value="score">Reputation score</option>
        <option value="earned">Total earned</option>
        <option value="bounties">Bounties completed</option>
        <option value="recent">Most recent</option>
        <option value="streak">Active streak</option>
      </select>
    </label>
    <button id="reset" class="btn ghost">Reset</button>
  </section>

  <section class="grid" aria-label="Contributors">
    <div class="contrib-list" role="list">
      <div class="contrib-list-header" role="row">
        <span role="columnheader">Rank</span>
        <span role="columnheader">Contributor</span>
        <span role="columnheader">Reputation</span>
        <span role="columnheader">Bounties</span>
        <span role="columnheader">Earned</span>
        <span role="columnheader">Primary skill</span>
      </div>
      <div id="rows"></div>
    </div>

    <aside class="detail" id="detail" aria-label="Contributor detail" hidden>
      <button class="close" id="closeDetail" aria-label="Close">&times;</button>
      <h2 id="dName">Contributor</h2>
      <p class="muted" id="dAddr"></p>
      <div class="detail-grid">
        <div><span class="muted">Reputation</span><strong id="dScore"></strong></div>
        <div><span class="muted">Bounties</span><strong id="dBounties"></strong></div>
        <div><span class="muted">Earned</span><strong id="dEarned"></strong></div>
        <div><span class="muted">Primary skill</span><strong id="dSkill"></strong></div>
      </div>
      <h3>Category expertise</h3>
      <div class="bars" id="dBars"></div>
      <h3>Recent payouts</h3>
      <ol class="receipts" id="dReceipts"></ol>
    </aside>
  </section>

  <section class="bounties" aria-label="Bounty board">
    <h2>Recent bounty board activity</h2>
    <p class="muted">Live from owockibot.xyz/api/bounty-board. Click a row for details.</p>
    <table class="bounties-table" id="bTable">
      <thead>
        <tr><th>#</th><th>Title</th><th>Status</th><th>Reward</th><th>Claimer</th></tr>
      </thead>
      <tbody id="bRows"></tbody>
    </table>
  </section>
</main>

<footer class="foot">
  <p>OWK-001 by <a href="https://github.com/razel369" target="_blank" rel="noopener">razel369</a> &middot; agent <a href="https://razel369.github.io/aia/" target="_blank" rel="noopener">razel369-aia</a> &middot; payout <code>0x833c...3a5e</code> on Base</p>
</footer>

<script src="app.js"></script>
</body>
</html>
'''

# styles.css
styles_css = ''':root {
  --bg: #0b0f17;
  --bg-2: #11172a;
  --card: #161d33;
  --card-2: #1c2440;
  --line: #2a3458;
  --text: #e8edf7;
  --muted: #8a93b1;
  --accent: #5eead4;
  --accent-2: #38bdf8;
  --gold: #fbbf24;
  --good: #22c55e;
  --warn: #f59e0b;
  --bad: #ef4444;
  --shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.5; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
code { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; background: var(--card-2); padding: 1px 6px; border-radius: 4px; font-size: 0.9em; }
.muted { color: var(--muted); }

.topbar {
  display: flex; flex-wrap: wrap; gap: 16px; align-items: end; justify-content: space-between;
  padding: 28px 32px 20px;
  background: linear-gradient(180deg, #131a30 0%, #0b0f17 100%);
  border-bottom: 1px solid var(--line);
  position: sticky; top: 0; z-index: 10; backdrop-filter: blur(8px);
}
.brand h1 { font-size: 22px; margin: 0 0 4px; font-weight: 800; letter-spacing: -0.02em; }
.eyebrow { margin: 0; font-size: 12px; color: var(--muted); }
.topbar-actions { display: flex; gap: 8px; }
.btn {
  background: var(--card); color: var(--text); border: 1px solid var(--line);
  padding: 8px 14px; border-radius: 8px; font-weight: 600; font-size: 13px; cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.btn:hover { background: var(--card-2); border-color: var(--accent); }
.btn.ghost { background: transparent; }

.layout { max-width: 1400px; margin: 0 auto; padding: 24px 32px 64px; display: grid; gap: 20px; }

.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
.stat-card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 2px; box-shadow: var(--shadow); }
.stat-label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; }
.stat-value { font-size: 28px; font-weight: 800; color: var(--text); font-variant-numeric: tabular-nums; }
.stat-sub { color: var(--muted); font-size: 11px; }

.filters {
  display: flex; flex-wrap: wrap; gap: 12px; align-items: end;
  background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px;
}
.filters label { display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.filters input, .filters select {
  background: var(--bg-2); color: var(--text); border: 1px solid var(--line);
  padding: 8px 10px; border-radius: 6px; font-size: 14px; min-width: 140px;
}
.filters input:focus, .filters select:focus { outline: none; border-color: var(--accent); }

.grid { display: grid; grid-template-columns: 1fr 360px; gap: 16px; }
@media (max-width: 1024px) { .grid { grid-template-columns: 1fr; } }

.contrib-list {
  background: var(--card); border: 1px solid var(--line); border-radius: 12px; overflow: hidden;
}
.contrib-list-header, .contrib-row {
  display: grid; grid-template-columns: 50px 1.4fr 100px 80px 110px 1fr; gap: 12px; align-items: center;
  padding: 12px 14px; font-size: 14px;
}
.contrib-list-header { background: var(--bg-2); color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; padding: 10px 14px; }
.contrib-row { border-top: 1px solid var(--line); cursor: pointer; transition: background 0.1s; }
.contrib-row:hover { background: var(--card-2); }
.contrib-row.selected { background: var(--card-2); border-left: 3px solid var(--accent); }
.contrib-rank { color: var(--gold); font-weight: 800; font-variant-numeric: tabular-nums; }
.contrib-name { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.contrib-name strong { color: var(--text); font-size: 13px; font-family: ui-monospace, monospace; }
.contrib-name .handle { color: var(--accent); font-size: 12px; }
.contrib-score { font-weight: 800; color: var(--accent); font-variant-numeric: tabular-nums; }
.contrib-bounties { color: var(--text); font-variant-numeric: tabular-nums; }
.contrib-earned { color: var(--gold); font-weight: 700; font-variant-numeric: tabular-nums; }
.contrib-skill { color: var(--muted); font-size: 12px; }

.detail {
  background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 20px; position: relative;
  max-height: 80vh; overflow-y: auto;
}
.detail h2 { margin: 0 0 4px; font-size: 18px; }
.detail h3 { margin: 18px 0 8px; font-size: 13px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
.detail .close { position: absolute; top: 12px; right: 12px; background: transparent; border: none; color: var(--muted); font-size: 24px; cursor: pointer; }
.detail .close:hover { color: var(--text); }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 12px 0; }
.detail-grid > div { background: var(--bg-2); padding: 10px; border-radius: 8px; display: flex; flex-direction: column; gap: 2px; }
.detail-grid strong { font-size: 18px; }
.bars { display: flex; flex-direction: column; gap: 6px; }
.bar { display: grid; grid-template-columns: 100px 1fr 36px; gap: 8px; align-items: center; font-size: 12px; }
.bar-track { background: var(--bg-2); height: 8px; border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); border-radius: 4px; }
.bar-count { text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }
.receipts { padding-left: 20px; margin: 0; }
.receipts li { padding: 6px 0; border-bottom: 1px solid var(--line); font-size: 13px; }
.receipts li:last-child { border-bottom: none; }
.receipts .amt { color: var(--gold); font-weight: 700; float: right; font-variant-numeric: tabular-nums; }
.receipts a { color: var(--muted); font-size: 11px; }

.bounties { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 20px; }
.bounties h2 { margin: 0 0 4px; font-size: 18px; }
.bounties p { margin: 0 0 14px; }
.bounties-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.bounties-table th, .bounties-table td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--line); }
.bounties-table th { background: var(--bg-2); color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }
.bounties-table tr:hover td { background: var(--card-2); }
.bounty-status { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.bounty-status.completed { background: rgba(34,197,94,0.15); color: var(--good); }
.bounty-status.cancelled { background: rgba(239,68,68,0.15); color: var(--bad); }
.bounty-status.claimed, .bounty-status.submitted, .bounty-status.open { background: rgba(245,158,11,0.15); color: var(--warn); }
.bounty-amount { color: var(--gold); font-weight: 700; font-variant-numeric: tabular-nums; text-align: right; }

.foot { max-width: 1400px; margin: 0 auto; padding: 20px 32px 40px; color: var(--muted); font-size: 12px; text-align: center; }

@media (max-width: 768px) {
  .topbar { padding: 16px; }
  .layout { padding: 16px; }
  .grid { grid-template-columns: 1fr; }
  .detail { position: fixed; top: 0; right: 0; bottom: 0; width: 100%; max-width: 100%; border-radius: 0; z-index: 50; }
  .contrib-list-header { display: none; }
  .contrib-row { grid-template-columns: 1fr; gap: 4px; padding: 12px; }
  .contrib-row > * { padding: 0; }
  .filters { flex-direction: column; align-items: stretch; }
  .filters label { width: 100%; }
  .filters input, .filters select { width: 100%; min-width: 0; }
}
'''

# app.js
app_js = '''// OWK-001 contributor reputation dashboard
// by razel369-aia - fetches live data from owockibot.xyz/api/bounty-board
// NO build step, NO external dependencies, NO external assets

const API = "https://owockibot.xyz/api/bounty-board";
const SAMPLE = "./data/owockibot-reputation.json";
const NETWORK = "eip-155:8453";
const PAYTO = "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e";

const $ = (id) => document.getElementById(id);
const state = { raw: null, contributors: [], bounties: [], filter: { q: "", cat: "", skill: "", min: 0, sort: "score" } };

async function fetchBounties() {
  try {
    const r = await fetch(API, { headers: { Accept: "application/json" } });
    if (!r.ok) throw new Error("HTTP " + r.status);
    return await r.json();
  } catch (e) {
    console.warn("owockibot API failed, using sample:", e);
    return null;
  }
}

function aggregate(bounties) {
  const stats = { total: bounties.length, completed: 0, volume: 0, contributors: 0, open: 0, cancelled: 0, byCat: {}, byClaimer: {} };
  for (const b of bounties) {
    if (b.status === "completed") {
      stats.completed++;
      stats.volume += b.reward_usdc || 0;
      const a = (b.claimer_address || "").toLowerCase();
      if (a) {
        const c = stats.byClaimer[a] || (stats.byClaimer[a] = { address: a, completed: 0, earned: 0, receipts: [], categories: {} });
        c.completed++;
        c.earned += b.reward_usdc || 0;
        c.receipts.push(b);
        const cat = categorize(b.title || "");
        c.categories[cat] = (c.categories[cat] || 0) + 1;
        stats.byCat[cat] = (stats.byCat[cat] || 0) + 1;
      }
    } else if (b.status === "open") stats.open++;
    else if (b.status === "cancelled") stats.cancelled++;
  }
  stats.contributors = Object.keys(stats.byClaimer).length;

  const contribs = Object.values(stats.byClaimer).map(c => {
    const cats = c.categories;
    const skill = Object.entries(cats).sort((a,b) => b[1]-a[1])[0]?.[0] || "Builder";
    const score = c.completed * 10 + c.earned * 0.5 + Object.values(cats).reduce((s,x) => s+x, 0);
    return {
      address: c.address,
      handle: shortAddr(c.address),
      completed: c.completed,
      earned: c.earned,
      score: Math.round(score * 10) / 10,
      skill,
      categories: cats,
      receipts: c.receipts.sort((a,b) => b.id - a.id)
    };
  });
  return { stats, contribs };
}

function categorize(title) {
  const t = title.toLowerCase();
  if (/audit|security|vulnerab|exploit/.test(t)) return "Security";
  if (/tweet|thread|content|blog|video|meme|recap|write/.test(t)) return "Content";
  if (/translate|translation/.test(t)) return "Translation";
  if (/design|badge|svg|illustrat/.test(t)) return "Design";
  if (/dashboard|api|sdk|tool|script|build|create|implement|engine|protocol|integration|deploy/.test(t)) return "Engineering";
  return "Builder";
}

function shortAddr(a) {
  if (!a) return "0x????…";
  return a.slice(0, 6) + "…" + a.slice(-4);
}

function fmtUsd(n) {
  if (typeof n !== "number") return "—";
  return "$" + n.toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function fmtNum(n) {
  if (typeof n !== "number") return "—";
  return n.toLocaleString("en-US");
}

function setStats(s) {
  $("stats").querySelectorAll(".stat-card").forEach(card => {
    const k = card.dataset.key;
    const v = card.querySelector(".stat-value");
    if (k === "volume") v.textContent = fmtUsd(s.volume);
    else if (k === "contributors") v.textContent = fmtNum(s.contributors);
    else v.textContent = fmtNum(s[k]);
  });
}

function populateFilterOptions(contribs) {
  const skills = new Set();
  const cats = new Set();
  for (const c of contribs) {
    skills.add(c.skill);
    Object.keys(c.categories).forEach(k => cats.add(k));
  }
  const sSel = $("skill");
  Array.from(skills).sort().forEach(s => {
    const o = document.createElement("option");
    o.value = s; o.textContent = s;
    sSel.appendChild(o);
  });
  const cSel = $("cat");
  Array.from(cats).sort().forEach(c => {
    const o = document.createElement("option");
    o.value = c; o.textContent = c;
    cSel.appendChild(o);
  });
}

function applyFilter() {
  const f = state.filter;
  const q = f.q.toLowerCase();
  let rows = state.contributors.filter(c => {
    if (q) {
      const hay = (c.address + " " + c.handle + " " + c.skill + " " + Object.keys(c.categories).join(" ")).toLowerCase();
      const inReceipts = c.receipts.some(r => (r.title || "").toLowerCase().includes(q));
      if (!hay.includes(q) && !inReceipts) return false;
    }
    if (f.skill && c.skill !== f.skill) return false;
    if (f.cat && !c.categories[f.cat]) return false;
    if (c.earned < f.min) return false;
    return true;
  });
  const sorters = {
    score: (a,b) => b.score - a.score,
    earned: (a,b) => b.earned - a.earned,
    bounties: (a,b) => b.completed - a.completed,
    recent: (a,b) => (b.receipts[0]?.id || 0) - (a.receipts[0]?.id || 0),
    streak: (a,b) => b.completed - a.completed,
  };
  rows.sort(sorters[f.sort] || sorters.score);
  return rows;
}

function renderRows() {
  const rows = applyFilter();
  const html = rows.map((c, i) => {
    const rank = i + 1;
    return `<div class="contrib-row" data-addr="${c.address}" role="listitem">
      <span class="contrib-rank">#${rank}</span>
      <span class="contrib-name">
        <strong>${c.handle}</strong>
        <span class="muted" style="font-size:11px">${c.skill}</span>
      </span>
      <span class="contrib-score">${c.score.toFixed(0)}</span>
      <span class="contrib-bounties">${c.completed}</span>
      <span class="contrib-earned">${fmtUsd(c.earned)}</span>
      <span class="contrib-skill">${Object.entries(c.categories).map(([k,v]) => `${k} ${v}`).join(" · ")}</span>
    </div>`;
  }).join("");
  $("rows").innerHTML = html || `<div class="contrib-row" style="cursor:default"><span></span><span class="muted">No contributors match the current filter.</span><span></span><span></span><span></span><span></span></div>`;
  document.querySelectorAll(".contrib-row[data-addr]").forEach(row => {
    row.addEventListener("click", () => {
      const c = state.contributors.find(x => x.address === row.dataset.addr);
      if (c) showDetail(c);
    });
  });
}

function showDetail(c) {
  $("dName").textContent = c.handle;
  $("dAddr").innerHTML = `<code>${c.address}</code> · ${NETWORK}`;
  $("dScore").textContent = c.score.toFixed(0);
  $("dBounties").textContent = c.completed;
  $("dEarned").textContent = fmtUsd(c.earned);
  $("dSkill").textContent = c.skill;
  const total = Object.values(c.categories).reduce((s,x) => s+x, 0) || 1;
  $("dBars").innerHTML = Object.entries(c.categories).sort((a,b) => b[1]-a[1]).map(([k,v]) => {
    const pct = Math.round((v/total)*100);
    return `<div class="bar">
      <span>${k}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${pct}%"></span></span>
      <span class="bar-count">${v}</span>
    </div>`;
  }).join("");
  $("dReceipts").innerHTML = c.receipts.slice(0, 15).map(r =>
    `<li><a href="https://github.com/owocki-bot/ai-bounty-board/issues/${r.id}" target="_blank" rel="noopener">#${r.id} ${escapeHtml(r.title.slice(0, 60))}</a><span class="amt">${fmtUsd(r.reward_usdc)}</span></li>`
  ).join("");
  $("detail").hidden = false;
  document.querySelectorAll(".contrib-row").forEach(r => r.classList.toggle("selected", r.dataset.addr === c.address));
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function renderBounties() {
  const recent = state.bounties.slice().sort((a,b) => b.id - a.id).slice(0, 30);
  $("bRows").innerHTML = recent.map(b =>
    `<tr>
      <td><a href="https://github.com/owocki-bot/ai-bounty-board/issues/${b.id}" target="_blank" rel="noopener">#${b.id}</a></td>
      <td>${escapeHtml((b.title || "").slice(0, 80))}</td>
      <td><span class="bounty-status ${b.status}">${b.status}</span></td>
      <td class="bounty-amount">${fmtUsd(b.reward_usdc || 0)}</td>
      <td class="muted" style="font-family:ui-monospace,monospace;font-size:12px">${shortAddr(b.claimer_address || "")}</td>
    </tr>`
  ).join("");
}

function exportCsv() {
  const rows = applyFilter();
  const head = ["rank","address","handle","score","bounties","earned_usdc","primary_skill","categories"];
  const body = rows.map((c,i) => [
    i+1, c.address, c.handle, c.score, c.completed, c.earned, c.skill,
    Object.entries(c.categories).map(([k,v]) => `${k}:${v}`).join("|")
  ]);
  const csv = [head, ...body].map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(",")).join("\\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "owk-001-reputation.csv";
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function readFilter() {
  state.filter.q = $("q").value.trim();
  state.filter.cat = $("cat").value;
  state.filter.skill = $("skill").value;
  state.filter.min = parseInt($("min").value, 10) || 0;
  state.filter.sort = $("sort").value;
}

function bind() {
  ["q","cat","skill","min","sort"].forEach(id => {
    $(id).addEventListener("input", () => { readFilter(); renderRows(); });
    $(id).addEventListener("change", () => { readFilter(); renderRows(); });
  });
  $("reset").addEventListener("click", () => {
    $("q").value = ""; $("cat").value = ""; $("skill").value = ""; $("min").value = "0"; $("sort").value = "score";
    readFilter(); renderRows();
  });
  $("refresh").addEventListener("click", load);
  $("export").addEventListener("click", exportCsv);
  $("closeDetail").addEventListener("click", () => { $("detail").hidden = true; document.querySelectorAll(".contrib-row").forEach(r => r.classList.remove("selected")); });
}

async function load() {
  let bounties = await fetchBounties();
  if (!bounties) {
    const sample = await fetch(SAMPLE).then(r => r.json()).catch(() => null);
    bounties = sample?.contributors?.flatMap(c => c.receipts || []) || [];
  }
  state.bounties = bounties;
  const { stats, contribs } = aggregate(bounties);
  state.stats = stats;
  state.contributors = contribs;
  setStats(stats);
  populateFilterOptions(contribs);
  renderRows();
  renderBounties();
}

document.addEventListener("DOMContentLoaded", () => { bind(); load(); });
'''

# Write all 3 files
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
with open(os.path.join(OUT, "styles.css"), "w", encoding="utf-8") as f:
    f.write(styles_css)
with open(os.path.join(OUT, "app.js"), "w", encoding="utf-8") as f:
    f.write(app_js)
print(f"Wrote dashboard files in {OUT}")
for f in ["index.html", "styles.css", "app.js"]:
    p = os.path.join(OUT, f)
    print(f"  {f}: {os.path.getsize(p)}b")
