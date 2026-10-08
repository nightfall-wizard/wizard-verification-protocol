#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import http.server
import json
import os
import socketserver
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

LEDGER_DIR = ROOT / "reports/auneya/local-ledger-wallet-v0.1"
LEDGER_JSON = LEDGER_DIR / "AUNEYA-LOCAL-LEDGER-WALLET-v0.1.json"

OUT_DIR = ROOT / "reports/auneya/local-claim-composer-v0.1"
STATE_JSON = OUT_DIR / "AUNEYA-LOCAL-CLAIM-COMPOSER-STATE-v0.1.json"
EVIDENCE_JSON = OUT_DIR / "AUNEYA-LOCAL-CLAIM-COMPOSER-v0.1.json"
EVIDENCE_MD = OUT_DIR / "AUNEYA-LOCAL-CLAIM-COMPOSER-v0.1.md"
INDEX_HTML = OUT_DIR / "index.html"

SCHEMA_VERSION = "auneya-local-claim-composer-v0.1"
UNIT = "simulated_neya_non_value_unit"

BOUNDARY = {
    "network": "none",
    "mainnet_active": False,
    "token_created": False,
    "market_value_claimed": False,
    "transferable": False,
    "local_only": True,
    "live_refresh_sandbox": True,
    "private_key_created": False,
    "seed_phrase_created": False,
    "custody_created": False,
    "send_enabled": False,
    "receive_enabled": False,
    "transfer_enabled": False,
    "not_investment_advice": True,
    "not_legal_advice": True,
    "not_financial_service": True,
    "legal_review_required_before_launch": True,
}

FORBIDDEN_CLAIM_TERMS = [
    "token price",
    "market value",
    "investment",
    "profit",
    "listing",
    "exchange listing",
    "mainnet launch",
    "transferable token",
    "seed phrase",
    "private key",
    "custody",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def ensure_base_ledger() -> dict[str, Any]:
    if not LEDGER_JSON.exists():
        tool = ROOT / "tools/auneya/auneya_local_ledger_wallet.py"
        if not tool.exists():
            raise FileNotFoundError("Missing tools/auneya/auneya_local_ledger_wallet.py")
        subprocess.run(
            [sys.executable, str(tool), "--out-dir", str(LEDGER_DIR)],
            check=True,
        )

    obj = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))

    if obj.get("mode") != "local_non_value_simulation":
        raise ValueError("base ledger must be local_non_value_simulation")

    if obj.get("network") != "none":
        raise ValueError("base ledger network must be none")

    for key in ["mainnet_active", "token_created", "market_value_claimed", "transferable"]:
        if obj.get(key) is not False:
            raise ValueError("base ledger boundary must be false: " + key)

    return obj


def entry_hash(entry: dict[str, Any]) -> str:
    payload = json.dumps(
        {k: v for k, v in entry.items() if k != "entry_hash"},
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256_text(payload)


def ledger_hash(entries: list[dict[str, Any]]) -> str:
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":"))
    return sha256_text(payload)


def initial_state() -> dict[str, Any]:
    base = ensure_base_ledger()
    wallet = dict(base["wallet"])
    entries = [dict(e) for e in base["ledger"]["entries"]]

    state = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": now_utc(),
        "mode": "local_claim_composer_live_refresh_sandbox",
        "network": "none",
        "mainnet_active": False,
        "token_created": False,
        "market_value_claimed": False,
        "transferable": False,
        "wallet": {
            "wallet_id": wallet["wallet_id"],
            "wallet_address": wallet["wallet_address"],
            "wallet_type": wallet["wallet_type"],
            "balance": wallet["balance"],
            "unit": wallet["unit"],
            "private_key_created": False,
            "seed_phrase_created": False,
            "custody_created": False,
            "send_enabled": False,
            "receive_enabled": False,
            "transfer_enabled": False,
        },
        "ledger": {
            "ledger_id": "auneya-local-claim-composer-ledger-v0.1",
            "ledger_type": "append_only_local_claim_composer_simulation_ledger",
            "entry_count": len(entries),
            "entries": entries,
            "ledger_hash": ledger_hash(entries),
        },
        "claims": [],
        "history": list(base.get("history", [])),
        "composer": {
            "claim_count": 0,
            "accepted_claim_count": 0,
            "rejected_claim_count": 0,
            "live_refresh_enabled": True,
            "api_state_endpoint": "/api/state",
            "claim_post_endpoint": "/claim",
            "form_enabled": True,
            "local_only": True,
            "non_value_simulation": True,
        },
        "boundary": BOUNDARY,
    }
    return state


def load_state(reset: bool = False) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if reset or not STATE_JSON.exists():
        state = initial_state()
        save_state(state)
        return state

    return json.loads(STATE_JSON.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    state["generated_at_utc"] = now_utc()
    STATE_JSON.write_text(
        json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def clean_claim_text(raw: str) -> str:
    value = " ".join(str(raw).strip().split())

    if len(value) < 3:
        raise ValueError("claim must contain at least 3 characters")

    if len(value) > 240:
        raise ValueError("claim must be at most 240 characters")

    low = value.lower()
    for term in FORBIDDEN_CLAIM_TERMS:
        if term in low:
            raise ValueError("claim contains forbidden boundary term: " + term)

    return value


def add_claim(state: dict[str, Any], raw_claim: str, source: str) -> dict[str, Any]:
    claim_text = clean_claim_text(raw_claim)
    claim_hash = sha256_text(claim_text)
    claim_no = len(state["claims"]) + 1

    claim_id = f"claim-local-user-{claim_no:04d}-{claim_hash[:8]}"
    prooflet_id = f"prooflet-local-user-{claim_no:04d}-{claim_hash[8:16]}"
    event_id = f"event-local-user-{claim_no:04d}-{claim_hash[16:24]}"

    created_at = now_utc()
    wallet = state["wallet"]
    entries = state["ledger"]["entries"]

    planned_entries = [
        {
            "entry_type": "claim_accepted",
            "claim_id": claim_id,
            "prooflet_id": None,
            "event_id": None,
            "memo": "Local user claim accepted into composer sandbox.",
        },
        {
            "entry_type": "witness_prooflet",
            "claim_id": claim_id,
            "prooflet_id": prooflet_id,
            "event_id": None,
            "memo": "Local witness prooflet simulated for composer claim.",
        },
        {
            "entry_type": "event_finalized",
            "claim_id": claim_id,
            "prooflet_id": prooflet_id,
            "event_id": event_id,
            "memo": "Local event finalized for composer claim.",
        },
    ]

    running_balance = int(wallet["balance"])

    for planned in planned_entries:
        running_balance += 1
        entry_no = len(entries) + 1
        entry = {
            "entry_id": f"local-composer-entry-{entry_no:04d}",
            "entry_type": planned["entry_type"],
            "amount": 1,
            "unit": UNIT,
            "claim_id": planned["claim_id"],
            "prooflet_id": planned["prooflet_id"],
            "event_id": planned["event_id"],
            "claim_text": claim_text,
            "claim_hash": claim_hash,
            "claim_source": source,
            "memo": planned["memo"],
            "wallet_id": wallet["wallet_id"],
            "wallet_address": wallet["wallet_address"],
            "running_balance": running_balance,
            "transferable": False,
            "created_at": created_at,
        }
        entry["entry_hash"] = entry_hash(entry)
        entries.append(entry)

    wallet["balance"] = running_balance
    state["ledger"]["entry_count"] = len(entries)
    state["ledger"]["ledger_hash"] = ledger_hash(entries)

    claim_record = {
        "claim_id": claim_id,
        "claim_text": claim_text,
        "claim_hash": claim_hash,
        "source": source,
        "status": "local_event_finalized",
        "prooflet_id": prooflet_id,
        "event_id": event_id,
        "entries_added": 3,
        "simulated_balance_delta": 3,
        "created_at": created_at,
        "boundary": {
            "token_created": False,
            "market_value_claimed": False,
            "transferable": False,
            "mainnet_active": False,
        },
    }

    state["claims"].append(claim_record)
    state["composer"]["claim_count"] = len(state["claims"])
    state["composer"]["accepted_claim_count"] = len(state["claims"])

    state["history"].append(
        {
            "step": len(state["history"]) + 1,
            "action": "local composer claim finalized",
            "visible_effect": "+3 simulated_neya_non_value_unit",
            "claim_id": claim_id,
        }
    )

    save_state(state)
    return claim_record


def render_entries(entries: list[dict[str, Any]]) -> str:
    rows = []
    for idx, entry in enumerate(entries, start=1):
        rows.append(
            "<tr>"
            f"<td>{idx}</td>"
            f"<td><code>{esc(entry.get('entry_type'))}</code></td>"
            f"<td>+{esc(entry.get('amount'))}</td>"
            f"<td>{esc(entry.get('running_balance'))}</td>"
            f"<td><code>{esc(str(entry.get('entry_hash', ''))[:16])}</code></td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_claims(claims: list[dict[str, Any]]) -> str:
    if not claims:
        return "<li>No local composer claims yet.</li>"

    items = []
    for claim in claims:
        items.append(
            "<li>"
            f"<strong>{esc(claim['claim_id'])}</strong><br>"
            f"{esc(claim['claim_text'])}<br>"
            f"<code>{esc(claim['status'])}</code>"
            "</li>"
        )
    return "\n".join(items)


def render_history(history: list[dict[str, Any]]) -> str:
    items = []
    for item in history:
        items.append(
            "<li>"
            f"<strong>Step {esc(item.get('step'))}</strong>: "
            f"{esc(item.get('action'))} -> "
            f"<code>{esc(item.get('visible_effect'))}</code>"
            "</li>"
        )
    return "\n".join(items)


def render_html(state: dict[str, Any]) -> str:
    wallet = state["wallet"]
    ledger = state["ledger"]
    composer = state["composer"]

    template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AUNEYA Local Claim Composer</title>
  <style>
    :root {
      color-scheme: light dark;
      --border: #8884;
      --bg-soft: #8881;
      --ok: #0a7;
      --warn: #b70;
      --bad: #d33;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0 auto;
      padding: 16px;
      max-width: 980px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }
    header, .card {
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 14px;
      background: var(--bg-soft);
      margin-bottom: 12px;
      overflow-wrap: anywhere;
    }
    h1 { margin: 0 0 8px 0; font-size: 1.45rem; }
    h2 { margin-top: 0; font-size: 1.1rem; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 12px;
    }
    .metric { font-size: 1.8rem; font-weight: 700; }
    .ok { color: var(--ok); font-weight: 700; }
    .warn { color: var(--warn); font-weight: 700; }
    table {
      width: 100%;
      border-collapse: collapse;
      display: block;
      overflow-x: auto;
    }
    th, td {
      padding: 8px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      white-space: nowrap;
    }
    code, textarea {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    textarea {
      width: 100%;
      min-height: 94px;
      padding: 10px;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: transparent;
      font-size: 1rem;
    }
    button {
      width: 100%;
      margin-top: 10px;
      padding: 12px;
      border-radius: 12px;
      border: 1px solid var(--border);
      font-weight: 700;
      font-size: 1rem;
    }
    .small { font-size: 0.9rem; opacity: 0.8; }
    footer { margin-top: 18px; font-size: 0.9rem; opacity: 0.8; }
  </style>
</head>
<body>
  <header>
    <h1>AUNEYA LOCAL CLAIM COMPOSER</h1>
    <div class="ok">Local live-refresh sandbox</div>
    <div>Network: <code>none</code> | Mainnet active: <code>false</code> | Transferable: <code>false</code></div>
    <div class="small">Auto-refresh: <code>enabled</code> via <code>/api/state</code></div>
  </header>

  <section class="card">
    <h2>Create Local Claim</h2>
    <form method="post" action="/claim">
      <textarea name="claim_text" maxlength="240" required placeholder="Enter a public local demo claim. Do not enter secrets, private keys, seed phrases, market-value claims or investment language."></textarea>
      <button type="submit">Create local simulated claim</button>
    </form>
    <p class="small">Adds exactly three local simulated entries: claim_accepted, witness_prooflet, event_finalized.</p>
  </section>

  <section class="grid">
    <div class="card">
      <h2>Wallet</h2>
      <div><strong>ID:</strong> <code>__WALLET_ID__</code></div>
      <div><strong>Address:</strong> <code>__WALLET_ADDRESS__</code></div>
      <div><strong>Type:</strong> <code>__WALLET_TYPE__</code></div>
    </div>

    <div class="card">
      <h2>Balance</h2>
      <div id="balance" class="metric">__BALANCE__</div>
      <div><code>__UNIT__</code></div>
    </div>

    <div class="card">
      <h2>Composer</h2>
      <div><strong>Claims:</strong> <code id="claim-count">__CLAIM_COUNT__</code></div>
      <div><strong>Live refresh:</strong> <code>true</code></div>
      <div><strong>Form enabled:</strong> <code>true</code></div>
    </div>

    <div class="card">
      <h2>Controls</h2>
      <div>Send: <code>false</code></div>
      <div>Receive: <code>false</code></div>
      <div>Transfer: <code>false</code></div>
      <div>Private key: <code>false</code></div>
      <div>Seed phrase: <code>false</code></div>
    </div>
  </section>

  <section class="card">
    <h2>Ledger</h2>
    <div><strong>Ledger ID:</strong> <code>__LEDGER_ID__</code></div>
    <div><strong>Entries:</strong> <code id="entry-count">__ENTRY_COUNT__</code></div>
    <div><strong>Hash:</strong> <code id="ledger-hash">__LEDGER_HASH__</code></div>
  </section>

  <section class="card">
    <h2>Ledger Entries</h2>
    <table>
      <thead>
        <tr><th>#</th><th>Type</th><th>Amount</th><th>Balance</th><th>Entry Hash</th></tr>
      </thead>
      <tbody id="entry-table">
        __ENTRY_ROWS__
      </tbody>
    </table>
  </section>

  <section class="card">
    <h2>Claims</h2>
    <ol id="claims-list">
      __CLAIM_ITEMS__
    </ol>
  </section>

  <section class="card">
    <h2>History</h2>
    <ol id="history-list">
      __HISTORY_ITEMS__
    </ol>
  </section>

  <section class="card">
    <h2>Boundary</h2>
    <ul>
      <li>no token</li>
      <li>no market value</li>
      <li>no transferability</li>
      <li>no mainnet</li>
      <li>no private key</li>
      <li>no seed phrase</li>
      <li>no custody</li>
      <li>not investment advice</li>
      <li>not legal advice</li>
      <li>not a custody, broker, exchange or financial service</li>
      <li>legal review required before launch, listing, sale, transferability or market-value communication</li>
    </ul>
  </section>

  <footer>
    Generated from local composer state JSON. Local sandbox only.
  </footer>

  <script>
    async function refreshState() {
      try {
        const response = await fetch('/api/state', {cache: 'no-store'});
        if (!response.ok) return;
        const state = await response.json();
        document.getElementById('balance').textContent = state.wallet.balance;
        document.getElementById('claim-count').textContent = state.composer.claim_count;
        document.getElementById('entry-count').textContent = state.ledger.entry_count;
        document.getElementById('ledger-hash').textContent = state.ledger.ledger_hash;
      } catch (err) {
        console.log('refresh failed', err);
      }
    }
    setInterval(refreshState, 2000);
    refreshState();
  </script>
</body>
</html>
"""

    replacements = {
        "__WALLET_ID__": esc(wallet["wallet_id"]),
        "__WALLET_ADDRESS__": esc(wallet["wallet_address"]),
        "__WALLET_TYPE__": esc(wallet["wallet_type"]),
        "__BALANCE__": esc(wallet["balance"]),
        "__UNIT__": esc(wallet["unit"]),
        "__CLAIM_COUNT__": esc(composer["claim_count"]),
        "__LEDGER_ID__": esc(ledger["ledger_id"]),
        "__ENTRY_COUNT__": esc(ledger["entry_count"]),
        "__LEDGER_HASH__": esc(ledger["ledger_hash"]),
        "__ENTRY_ROWS__": render_entries(ledger["entries"]),
        "__CLAIM_ITEMS__": render_claims(state["claims"]),
        "__HISTORY_ITEMS__": render_history(state["history"]),
    }

    for key, value in replacements.items():
        template = template.replace(key, value)

    return template


def build_outputs(state: dict[str, Any], host: str, port: int) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    INDEX_HTML.write_text(render_html(state), encoding="utf-8")

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": now_utc(),
        "mode": "local_claim_composer_live_refresh_sandbox",
        "status": "pass",
        "dashboard": {
            "path": rel(INDEX_HTML),
            "url": f"http://{host}:{port}/index.html",
            "mobile_first": True,
            "live_refresh_enabled": True,
            "api_state_endpoint": "/api/state",
            "claim_post_endpoint": "/claim",
            "local_only": True,
            "external_dependencies": False,
        },
        "state": {
            "path": rel(STATE_JSON),
            "claim_count": state["composer"]["claim_count"],
            "entry_count": state["ledger"]["entry_count"],
            "balance": state["wallet"]["balance"],
            "ledger_hash": state["ledger"]["ledger_hash"],
        },
        "composer": state["composer"],
        "wallet_snapshot": {
            "wallet_id": state["wallet"]["wallet_id"],
            "wallet_address": state["wallet"]["wallet_address"],
            "balance": state["wallet"]["balance"],
            "unit": state["wallet"]["unit"],
        },
        "ledger_snapshot": {
            "ledger_id": state["ledger"]["ledger_id"],
            "entry_count": state["ledger"]["entry_count"],
            "ledger_hash": state["ledger"]["ledger_hash"],
        },
        "claims": state["claims"],
        "boundary": BOUNDARY,
    }

    EVIDENCE_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    md_text = f"""# AUNEYA Local Claim Composer v0.1

Status: PASS

Mode: local claim composer live-refresh sandbox
Network: none
Mainnet active: false
Token created: false
Market value claimed: false
Transferable: false

## Local URL

`http://{host}:{port}/index.html`

## Composer

- Claim count: `{state['composer']['claim_count']}`
- Live refresh enabled: `true`
- API state endpoint: `/api/state`
- Claim post endpoint: `/claim`
- Form enabled: `true`
- Local only: `true`

## Wallet snapshot

- Wallet ID: `{state['wallet']['wallet_id']}`
- Address: `{state['wallet']['wallet_address']}`
- Balance: `{state['wallet']['balance']} {state['wallet']['unit']}`

## Ledger snapshot

- Ledger ID: `{state['ledger']['ledger_id']}`
- Entry count: `{state['ledger']['entry_count']}`
- Ledger hash: `{state['ledger']['ledger_hash']}`

## Boundary

This is a local claim composer and dashboard live-refresh sandbox.

It creates no token.
It creates no market value.
It creates no transferability.
It activates no mainnet.
It creates no private key.
It creates no seed phrase.
It creates no custody.
It is not investment advice.
It is not legal advice.
It is not a custody, broker, exchange or financial service.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
"""
    EVIDENCE_MD.write_text(md_text, encoding="utf-8")

    print("Composer HTML:", INDEX_HTML)
    print("State JSON:   ", STATE_JSON)
    print("Evidence JSON:", EVIDENCE_JSON)
    print("Evidence MD:  ", EVIDENCE_MD)
    print("Local URL:    ", f"http://{host}:{port}/index.html")
    print("Status:       PASS")
    print("Claims:       ", state["composer"]["claim_count"])
    print("Balance:      ", f"{state['wallet']['balance']} {state['wallet']['unit']}")
    print("Entries:      ", state["ledger"]["entry_count"])

    return report


class ClaimComposerHandler(http.server.BaseHTTPRequestHandler):
    server_version = "AUNEYAClaimComposer/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        print("[composer]", fmt % args)

    def _send_bytes(self, data: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        state = load_state(reset=False)
        build_outputs(state, self.server.host, self.server.port_number)

        path = urllib.parse.urlparse(self.path).path

        if path in ["/", "/index.html"]:
            data = INDEX_HTML.read_bytes()
            self._send_bytes(data, "text/html; charset=utf-8")
            return

        if path == "/api/state":
            data = STATE_JSON.read_bytes()
            self._send_bytes(data, "application/json; charset=utf-8")
            return

        self._send_bytes(b"not found\n", "text/plain; charset=utf-8", status=404)

    def do_POST(self) -> None:
        path = urllib.parse.urlparse(self.path).path

        if path != "/claim":
            self._send_bytes(b"not found\n", "text/plain; charset=utf-8", status=404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        parsed = urllib.parse.parse_qs(body)
        claim_text = parsed.get("claim_text", [""])[0]

        try:
            state = load_state(reset=False)
            add_claim(state, claim_text, source="local_browser_form")
            state = load_state(reset=False)
            build_outputs(state, self.server.host, self.server.port_number)
            self.send_response(303)
            self.send_header("Location", "/index.html")
            self.end_headers()
        except Exception as exc:
            message = ("claim rejected: " + str(exc) + "\n").encode("utf-8")
            self._send_bytes(message, "text/plain; charset=utf-8", status=400)


def serve(host: str, port: int) -> None:
    state = load_state(reset=False)
    build_outputs(state, host, port)

    class Server(socketserver.TCPServer):
        allow_reuse_address = True

    with Server((host, port), ClaimComposerHandler) as httpd:
        httpd.host = host
        httpd.port_number = port
        print(f"AUNEYA Local Claim Composer running at http://{host}:{port}/index.html")
        print("Stop with CTRL+C")
        httpd.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="AUNEYA local claim composer v0.1")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--demo-claim", default="")
    parser.add_argument("--print-url", action="store_true")
    args = parser.parse_args()

    state = load_state(reset=args.reset)

    if args.demo_claim:
        add_claim(state, args.demo_claim, source="local_cli_demo")
        state = load_state(reset=False)

    build_outputs(state, args.host, args.port)

    if args.print_url:
        print(f"http://{args.host}:{args.port}/index.html")

    if args.serve:
        serve(args.host, args.port)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
