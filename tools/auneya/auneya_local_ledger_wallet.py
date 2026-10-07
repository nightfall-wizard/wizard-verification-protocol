#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "reports/auneya/local-ledger-wallet-v0.1"

SCHEMA_VERSION = "auneya-local-ledger-wallet-v0.1"
UNIT = "simulated_neya_non_value_unit"

BOUNDARY = {
    "network": "none",
    "mainnet_active": False,
    "token_created": False,
    "market_value_claimed": False,
    "transferable": False,
    "not_investment_advice": True,
    "not_legal_advice": True,
    "not_financial_service": True,
    "legal_review_required_before_launch": True,
}

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def local_address(wallet_id: str) -> str:
    return "auneya-local-" + sha256_text("auneya-local-wallet:" + wallet_id)[:24]

def entry_hash(entry: dict[str, Any]) -> str:
    payload = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    return sha256_text(payload)

def build_demo_ledger(wallet_id: str = "local-wallet-001") -> dict[str, Any]:
    address = local_address(wallet_id)

    base_entries = [
        {
            "entry_id": "local-ledger-entry-0001",
            "entry_type": "claim_accepted",
            "amount": 1,
            "unit": UNIT,
            "claim_id": "claim-local-public-demo-001",
            "prooflet_id": None,
            "event_id": None,
            "memo": "Public claim accepted into local non-value simulation ledger.",
            "created_at": "2026-10-07T00:00:01Z",
        },
        {
            "entry_id": "local-ledger-entry-0002",
            "entry_type": "witness_prooflet",
            "amount": 1,
            "unit": UNIT,
            "claim_id": "claim-local-public-demo-001",
            "prooflet_id": "prooflet-local-demo-001",
            "event_id": None,
            "memo": "Local witness prooflet recorded as simulated evidence.",
            "created_at": "2026-10-07T00:00:02Z",
        },
        {
            "entry_id": "local-ledger-entry-0003",
            "entry_type": "event_finalized",
            "amount": 1,
            "unit": UNIT,
            "claim_id": "claim-local-public-demo-001",
            "prooflet_id": "prooflet-local-demo-001",
            "event_id": "event-local-demo-001",
            "memo": "Local AUNEYA event finalized in non-value simulation mode.",
            "created_at": "2026-10-07T00:00:03Z",
        },
    ]

    entries = []
    running_balance = 0

    for raw in base_entries:
        running_balance += int(raw["amount"])
        enriched = dict(raw)
        enriched["wallet_id"] = wallet_id
        enriched["wallet_address"] = address
        enriched["running_balance"] = running_balance
        enriched["entry_hash"] = entry_hash({
            k: v for k, v in enriched.items()
            if k not in {"entry_hash"}
        })
        entries.append(enriched)

    ledger_hash = sha256_text(json.dumps(entries, sort_keys=True, separators=(",", ":")))

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "local_non_value_simulation",
        "network": "none",
        "mainnet_active": False,
        "token_created": False,
        "market_value_claimed": False,
        "transferable": False,
        "wallet": {
            "wallet_id": wallet_id,
            "wallet_address": address,
            "wallet_type": "local_identity_wallet",
            "private_key_created": False,
            "seed_phrase_created": False,
            "custody_created": False,
            "send_enabled": False,
            "receive_enabled": False,
            "transfer_enabled": False,
            "balance": running_balance,
            "unit": UNIT,
        },
        "ledger": {
            "ledger_id": "auneya-local-ledger-v0.1",
            "ledger_type": "append_only_local_simulation_ledger",
            "entry_count": len(entries),
            "entries": entries,
            "ledger_hash": ledger_hash,
        },
        "history": [
            {
                "step": 1,
                "action": "claim accepted",
                "visible_effect": "+1 simulated_neya_non_value_unit",
            },
            {
                "step": 2,
                "action": "witness prooflet recorded",
                "visible_effect": "+1 simulated_neya_non_value_unit",
            },
            {
                "step": 3,
                "action": "event finalized",
                "visible_effect": "+1 simulated_neya_non_value_unit",
            },
        ],
        "export": {
            "json_report": "reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-LEDGER-WALLET-v0.1.json",
            "markdown_report": "reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-LEDGER-WALLET-v0.1.md",
            "wallet_view": "reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-WALLET-VIEW-v0.1.txt",
        },
        "boundary": BOUNDARY,
    }

def render_wallet_view(obj: dict[str, Any]) -> str:
    wallet = obj["wallet"]
    ledger = obj["ledger"]

    lines = [
        "AUNEYA LOCAL LEDGER",
        "",
        "Mode: local non-value simulation",
        "Network: none",
        "Mainnet active: false",
        "Token created: false",
        "Market value claimed: false",
        "Transferable: false",
        "",
        "Wallet",
        "------",
        f"Wallet ID: {wallet['wallet_id']}",
        f"Address: {wallet['wallet_address']}",
        f"Wallet type: {wallet['wallet_type']}",
        f"Private key created: {str(wallet['private_key_created']).lower()}",
        f"Seed phrase created: {str(wallet['seed_phrase_created']).lower()}",
        f"Send enabled: {str(wallet['send_enabled']).lower()}",
        f"Receive enabled: {str(wallet['receive_enabled']).lower()}",
        f"Transfer enabled: {str(wallet['transfer_enabled']).lower()}",
        "",
        "Balance",
        "-------",
        f"{wallet['balance']} simulated_neya_non_value_unit",
        "",
        "Entries",
        "-------",
    ]

    for idx, entry in enumerate(ledger["entries"], start=1):
        lines.append(
            f"#{idx:04d}  {entry['entry_type']}  "
            f"+{entry['amount']} {entry['unit']}  "
            f"balance={entry['running_balance']}  "
            f"hash={entry['entry_hash'][:16]}"
        )

    lines += [
        "",
        "History",
        "-------",
    ]

    for item in obj["history"]:
        lines.append(f"{item['step']}. {item['action']} -> {item['visible_effect']}")

    lines += [
        "",
        "Ledger",
        "------",
        f"Ledger ID: {ledger['ledger_id']}",
        f"Entry count: {ledger['entry_count']}",
        f"Ledger hash: {ledger['ledger_hash']}",
        "",
        "Boundary",
        "--------",
        "no token",
        "no market value",
        "no transferability",
        "no mainnet",
        "not investment advice",
        "not legal advice",
        "not a custody, broker, exchange or financial service",
        "legal review required before launch, listing, sale, transferability or market-value communication",
        "",
    ]

    return "\n".join(lines)

def render_markdown(obj: dict[str, Any]) -> str:
    wallet = obj["wallet"]
    ledger = obj["ledger"]

    lines = [
        "# AUNEYA Local Ledger + Wallet Simulator v0.1",
        "",
        "Status: PASS",
        "",
        "Mode: local non-value simulation",
        "Network: none",
        "Mainnet active: false",
        "Token created: false",
        "Market value claimed: false",
        "Transferable: false",
        "",
        "## Wallet",
        "",
        f"- Wallet ID: `{wallet['wallet_id']}`",
        f"- Address: `{wallet['wallet_address']}`",
        f"- Wallet type: `{wallet['wallet_type']}`",
        f"- Private key created: `{str(wallet['private_key_created']).lower()}`",
        f"- Seed phrase created: `{str(wallet['seed_phrase_created']).lower()}`",
        f"- Send enabled: `{str(wallet['send_enabled']).lower()}`",
        f"- Receive enabled: `{str(wallet['receive_enabled']).lower()}`",
        f"- Transfer enabled: `{str(wallet['transfer_enabled']).lower()}`",
        "",
        "## Balance",
        "",
        f"`{wallet['balance']} {wallet['unit']}`",
        "",
        "## Local ledger entries",
        "",
        "| # | Entry type | Amount | Running balance | Entry hash |",
        "|---:|---|---:|---:|---|",
    ]

    for idx, entry in enumerate(ledger["entries"], start=1):
        lines.append(
            f"| {idx} | `{entry['entry_type']}` | {entry['amount']} | "
            f"{entry['running_balance']} | `{entry['entry_hash']}` |"
        )

    lines += [
        "",
        "## History",
        "",
    ]

    for item in obj["history"]:
        lines.append(f"- Step {item['step']}: {item['action']} -> `{item['visible_effect']}`")

    lines += [
        "",
        "## Export",
        "",
        "- JSON report",
        "- Markdown report",
        "- terminal wallet view",
        "",
        "## Boundary",
        "",
        "This is a local ledger and local wallet simulator only.",
        "",
        "It creates no token.",
        "It creates no market value.",
        "It creates no transferability.",
        "It activates no mainnet.",
        "It creates no private key, no seed phrase and no custody.",
        "It is not investment advice.",
        "It is not legal advice.",
        "It is not a custody, broker, exchange or financial service.",
        "",
        "Legal review is required before any public token launch, listing, sale, transferability or market-value communication.",
        "",
    ]

    return "\n".join(lines)

def write_outputs(out_dir: Path, wallet_id: str, print_wallet: bool) -> dict[str, Any]:
    obj = build_demo_ledger(wallet_id=wallet_id)

    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "AUNEYA-LOCAL-LEDGER-WALLET-v0.1.json"
    md_path = out_dir / "AUNEYA-LOCAL-LEDGER-WALLET-v0.1.md"
    txt_path = out_dir / "AUNEYA-LOCAL-WALLET-VIEW-v0.1.txt"

    json_path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(render_markdown(obj), encoding="utf-8")
    txt_path.write_text(render_wallet_view(obj), encoding="utf-8")

    if print_wallet:
        print(render_wallet_view(obj))

    print("Evidence JSON:", json_path)
    print("Evidence MD:  ", md_path)
    print("Wallet view:  ", txt_path)
    print("Status:       PASS")
    print("Balance:      ", f"{obj['wallet']['balance']} {obj['wallet']['unit']}")
    print("Entries:      ", obj["ledger"]["entry_count"])
    print("Ledger hash:  ", obj["ledger"]["ledger_hash"])

    return obj

def main() -> int:
    parser = argparse.ArgumentParser(
        description="AUNEYA local ledger and local wallet simulator v0.1"
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help="Output directory for JSON, Markdown and wallet view artifacts.",
    )
    parser.add_argument(
        "--wallet-id",
        default="local-wallet-001",
        help="Local wallet identifier. This is not a real wallet seed or private key.",
    )
    parser.add_argument(
        "--print-wallet",
        action="store_true",
        help="Print the terminal wallet view.",
    )
    args = parser.parse_args()

    write_outputs(Path(args.out_dir), args.wallet_id, args.print_wallet)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

