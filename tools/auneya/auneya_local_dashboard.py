#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import http.server
import json
import os
import socketserver
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = ROOT / "reports/auneya/local-ledger-wallet-v0.1"
LEDGER_JSON = LEDGER_DIR / "AUNEYA-LOCAL-LEDGER-WALLET-v0.1.json"
OUT_DIR = ROOT / "reports/auneya/local-dashboard-v0.1"
SCHEMA_VERSION = "auneya-local-dashboard-v0.1"

BOUNDARY = {
    "network": "none",
    "mainnet_active": False,
    "token_created": False,
    "market_value_claimed": False,
    "transferable": False,
    "read_only": True,
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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def ensure_ledger() -> dict[str, Any]:
    if not LEDGER_JSON.exists():
        tool = ROOT / "tools/auneya/auneya_local_ledger_wallet.py"
        if not tool.exists():
            raise FileNotFoundError("Missing tools/auneya/auneya_local_ledger_wallet.py")
        subprocess.run(
            [sys.executable, str(tool), "--out-dir", str(LEDGER_DIR)],
            check=True,
        )

    return json.loads(LEDGER_JSON.read_text(encoding="utf-8"))


def validate_ledger(ledger: dict[str, Any]) -> None:
    if ledger.get("mode") != "local_non_value_simulation":
        raise ValueError("ledger mode must be local_non_value_simulation")

    if ledger.get("network") != "none":
        raise ValueError("ledger network must be none")

    for key in ["mainnet_active", "token_created", "market_value_claimed", "transferable"]:
        if ledger.get(key) is not False:
            raise ValueError(f"ledger boundary must be false: {key}")

    wallet = ledger.get("wallet", {})
    if not str(wallet.get("wallet_address", "")).startswith("auneya-local-"):
        raise ValueError("wallet address must be local-only")

    for key in [
        "private_key_created",
        "seed_phrase_created",
        "custody_created",
        "send_enabled",
        "receive_enabled",
        "transfer_enabled",
    ]:
        if wallet.get(key) is not False:
            raise ValueError(f"wallet field must be false: {key}")

    entries = ledger.get("ledger", {}).get("entries", [])
    if len(entries) < 1:
        raise ValueError("ledger entries missing")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_html(ledger: dict[str, Any]) -> str:
    wallet = ledger["wallet"]
    ledger_obj = ledger["ledger"]
    entries = ledger_obj["entries"]
    history = ledger["history"]

    entry_rows = []
    for idx, entry in enumerate(entries, start=1):
        entry_rows.append(
            "<tr>"
            f"<td>{idx}</td>"
            f"<td><code>{esc(entry['entry_type'])}</code></td>"
            f"<td>+{esc(entry['amount'])}</td>"
            f"<td>{esc(entry['running_balance'])}</td>"
            f"<td><code>{esc(str(entry['entry_hash'])[:16])}</code></td>"
            "</tr>"
        )

    history_items = []
    for item in history:
        history_items.append(
            f"<li><strong>Step {esc(item['step'])}</strong>: "
            f"{esc(item['action'])} -> <code>{esc(item['visible_effect'])}</code></li>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AUNEYA Local Dashboard</title>
  <style>
    :root {{
      color-scheme: light dark;
      --border: #8884;
      --bg-soft: #8881;
      --ok: #0a7;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0 auto;
      padding: 16px;
      max-width: 980px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    header, .card {{
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 14px;
      background: var(--bg-soft);
      margin-bottom: 12px;
      overflow-wrap: anywhere;
    }}
    h1 {{ margin: 0 0 8px 0; font-size: 1.55rem; }}
    h2 {{ margin-top: 0; font-size: 1.1rem; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 12px;
    }}
    .metric {{ font-size: 1.8rem; font-weight: 700; }}
    .ok {{ color: var(--ok); font-weight: 700; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      display: block;
      overflow-x: auto;
    }}
    th, td {{
      padding: 8px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      white-space: nowrap;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    footer {{
      margin-top: 18px;
      font-size: 0.9rem;
      opacity: 0.8;
    }}
  </style>
</head>
<body>
  <header>
    <h1>AUNEYA LOCAL DASHBOARD</h1>
    <div class="ok">Read-only local non-value simulation</div>
    <div>Network: <code>none</code> | Mainnet active: <code>false</code> | Transferable: <code>false</code></div>
  </header>

  <section class="grid">
    <div class="card">
      <h2>Wallet</h2>
      <div><strong>ID:</strong> <code>{esc(wallet['wallet_id'])}</code></div>
      <div><strong>Address:</strong> <code>{esc(wallet['wallet_address'])}</code></div>
      <div><strong>Type:</strong> <code>{esc(wallet['wallet_type'])}</code></div>
    </div>

    <div class="card">
      <h2>Balance</h2>
      <div class="metric">{esc(wallet['balance'])}</div>
      <div><code>{esc(wallet['unit'])}</code></div>
    </div>

    <div class="card">
      <h2>Ledger</h2>
      <div><strong>Ledger ID:</strong> <code>{esc(ledger_obj['ledger_id'])}</code></div>
      <div><strong>Entries:</strong> <code>{esc(ledger_obj['entry_count'])}</code></div>
      <div><strong>Hash:</strong> <code>{esc(ledger_obj['ledger_hash'])}</code></div>
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
    <h2>Ledger Entries</h2>
    <table>
      <thead>
        <tr><th>#</th><th>Type</th><th>Amount</th><th>Balance</th><th>Entry Hash</th></tr>
      </thead>
      <tbody>
        {"".join(entry_rows)}
      </tbody>
    </table>
  </section>

  <section class="card">
    <h2>History</h2>
    <ol>
      {"".join(history_items)}
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
    Generated from local ledger JSON. Static local read-only dashboard.
  </footer>
</body>
</html>
"""


def build_dashboard(out_dir: Path, host: str, port: int) -> dict[str, Any]:
    ledger = ensure_ledger()
    validate_ledger(ledger)

    out_dir.mkdir(parents=True, exist_ok=True)

    index_path = out_dir / "index.html"
    json_path = out_dir / "AUNEYA-LOCAL-DASHBOARD-v0.1.json"
    md_path = out_dir / "AUNEYA-LOCAL-DASHBOARD-v0.1.md"

    index_path.write_text(render_html(ledger), encoding="utf-8")

    wallet = ledger["wallet"]
    ledger_obj = ledger["ledger"]

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "local_browser_dashboard_read_only",
        "status": "pass",
        "source": {
            "ledger_json": rel(LEDGER_JSON),
            "wallet_view": "reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-WALLET-VIEW-v0.1.txt",
        },
        "dashboard": {
            "path": rel(index_path),
            "url": f"http://{host}:{port}/index.html",
            "mobile_first": True,
            "read_only": True,
            "static_html": True,
            "external_dependencies": False,
            "input_forms": False,
            "send_controls": False,
            "receive_controls": False,
            "transfer_controls": False,
            "private_key_fields": False,
            "seed_phrase_fields": False,
        },
        "wallet_snapshot": {
            "wallet_id": wallet["wallet_id"],
            "wallet_address": wallet["wallet_address"],
            "balance": wallet["balance"],
            "unit": wallet["unit"],
        },
        "ledger_snapshot": {
            "ledger_id": ledger_obj["ledger_id"],
            "entry_count": ledger_obj["entry_count"],
            "ledger_hash": ledger_obj["ledger_hash"],
        },
        "visible_sections": [
            "wallet",
            "balance",
            "ledger",
            "controls",
            "ledger_entries",
            "history",
            "boundary",
        ],
        "boundary": BOUNDARY,
    }

    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    md_text = f"""# AUNEYA Local Dashboard v0.1

Status: PASS

Mode: local browser dashboard read-only
Network: none
Mainnet active: false
Token created: false
Market value claimed: false
Transferable: false

## Dashboard

- Path: `{rel(index_path)}`
- Local URL: `http://{host}:{port}/index.html`
- Mobile-first: `true`
- Read-only: `true`
- Static HTML: `true`
- External dependencies: `false`

## Wallet snapshot

- Wallet ID: `{wallet['wallet_id']}`
- Address: `{wallet['wallet_address']}`
- Balance: `{wallet['balance']} {wallet['unit']}`

## Ledger snapshot

- Ledger ID: `{ledger_obj['ledger_id']}`
- Entry count: `{ledger_obj['entry_count']}`
- Ledger hash: `{ledger_obj['ledger_hash']}`

## Boundary

This is a local browser dashboard for the AUNEYA local ledger and wallet simulator.

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
    md_path.write_text(md_text, encoding="utf-8")

    print("Dashboard HTML:", index_path)
    print("Evidence JSON: ", json_path)
    print("Evidence MD:   ", md_path)
    print("Local URL:     ", f"http://{host}:{port}/index.html")
    print("Status:        PASS")

    return report


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        print("[dashboard]", fmt % args)


def serve(out_dir: Path, host: str, port: int) -> None:
    os.chdir(out_dir)
    with socketserver.TCPServer((host, port), QuietHandler) as httpd:
        print(f"AUNEYA Local Dashboard running at http://{host}:{port}/index.html")
        print("Stop with CTRL+C")
        httpd.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="AUNEYA local dashboard v0.1")
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--print-url", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    report = build_dashboard(out_dir, args.host, args.port)

    if args.print_url:
        print(report["dashboard"]["url"])

    if args.serve:
        serve(out_dir, args.host, args.port)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
