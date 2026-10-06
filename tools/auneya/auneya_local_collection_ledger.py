#!/usr/bin/env python3

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


LEDGER_SCHEMA_VERSION = "auneya-local-collection-ledger-v0.1"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_json(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail(f"cannot read JSON {path}: {exc}")


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n")


def empty_ledger() -> dict:
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "ledger_type": "local_non_value_collection_simulation",
        "network": "none",
        "mainnet_active": False,
        "token_created": False,
        "auneya_created": False,
        "neya_created": False,
        "real_reward_created": False,
        "market_value_claimed": False,
        "transferable": False,
        "unit": "simulated_neya",
        "total_simulated_entries": 0,
        "total_simulated_neya_counted": 0,
        "entries": [],
        "non_value_notice": "Local collection ledger simulation only. No token, AUNEYA, neya, real reward, market value, mainnet or transferability is created.",
    }


def load_ledger(path: Path) -> dict:
    if not path.exists():
        return empty_ledger()

    ledger = read_json(path)

    if ledger.get("schema_version") != LEDGER_SCHEMA_VERSION:
        fail("ledger schema_version is invalid")

    if ledger.get("ledger_type") != "local_non_value_collection_simulation":
        fail("ledger_type is invalid")

    for key in [
        "mainnet_active",
        "token_created",
        "auneya_created",
        "neya_created",
        "real_reward_created",
        "market_value_claimed",
        "transferable",
    ]:
        if ledger.get(key) is not False:
            fail(f"ledger boundary violation: {key} must be false")

    if ledger.get("unit") != "simulated_neya":
        fail("ledger unit must be simulated_neya")

    return ledger


def validate_flow(flow: dict) -> None:
    if flow.get("schema_version") != "auneya-pulse-flow-v0.1":
        fail("flow schema_version must be auneya-pulse-flow-v0.1")

    if flow.get("flow_type") != "phone_witness_loop":
        fail("flow_type must be phone_witness_loop")

    witness = flow.get("witness", {})

    if witness.get("device_class") != "android_termux":
        fail("flow witness device_class must be android_termux")

    if witness.get("environment_class") != "phone_safe":
        fail("flow witness environment_class must be phone_safe")

    boundary = flow.get("lawful_boundary_confirmation", {})

    for key in [
        "public_or_authorized_target",
        "no_private_data_accessed",
        "no_hacked_data_used",
        "no_paywall_bypass_used",
        "no_credentials_used",
        "no_surveillance_performed",
    ]:
        if boundary.get(key) is not True:
            fail(f"flow lawful boundary failed: {key}")

    reward = flow.get("simulated_reward_entry", {})

    if reward.get("entry_type") != "non_value_simulation":
        fail("reward entry must be non_value_simulation")

    if reward.get("unit") != "simulated_neya":
        fail("reward unit must be simulated_neya")

    if reward.get("transferable") is not False:
        fail("reward entry must be non-transferable")

    if reward.get("market_value_claimed") is not False:
        fail("reward entry must not claim market value")

    amount = reward.get("amount")

    if not isinstance(amount, int) or amount <= 0:
        fail("reward amount must be a positive simulated integer")


def run_selected_demo(claim_key: str, out_dir: Path, witness_id: str, start_time: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python3",
        "tools/auneya/auneya_local_claim_select.py",
        "--claim-key",
        claim_key,
        "--run-demo",
        "--out-dir",
        str(out_dir),
        "--witness-id",
        witness_id,
        "--start-time",
        start_time,
    ]

    result = subprocess.run(cmd, text=True)

    if result.returncode != 0:
        fail(f"selected local demo failed for claim-key {claim_key}")

    flow_path = out_dir / "local-flow.json"

    if not flow_path.exists():
        fail(f"selected local demo did not create {flow_path}")

    return flow_path


def make_entry(flow: dict, claim_key: str, sequence: int, source_flow_path: Path) -> dict:
    reward = flow["simulated_reward_entry"]
    prooflet = flow["prooflet"]
    claim_ref = flow["claim_ref"]

    entry = {
        "entry_sequence": sequence,
        "entry_type": "local_non_value_collection_simulation",
        "claim_key": claim_key,
        "claim_id": claim_ref["claim_id"],
        "claim_hash": claim_ref["claim_hash"],
        "flow_id": flow["flow_id"],
        "prooflet_id": prooflet["prooflet_id"],
        "simulated_unit": reward["unit"],
        "simulated_amount": reward["amount"],
        "transferable": False,
        "market_value_claimed": False,
        "token_created": False,
        "auneya_created": False,
        "neya_created": False,
        "real_reward_created": False,
        "mainnet_active": False,
        "source_flow_path": str(source_flow_path),
        "created_at": flow.get("created_at", now_iso()),
        "notice": "Counted locally as non-value simulation only.",
    }

    entry["entry_hash"] = sha256_json(entry)
    return entry


def recompute_totals(ledger: dict) -> None:
    entries = ledger.get("entries", [])
    ledger["total_simulated_entries"] = len(entries)
    ledger["total_simulated_neya_counted"] = sum(int(e.get("simulated_amount", 0)) for e in entries)


def record_entry(args) -> None:
    ledger_path = Path(args.ledger)
    out_dir = Path(args.out_dir)

    flow_path = run_selected_demo(
        claim_key=args.claim_key,
        out_dir=out_dir,
        witness_id=args.witness_id,
        start_time=args.start_time,
    )

    flow = read_json(flow_path)
    validate_flow(flow)

    ledger = load_ledger(ledger_path)
    sequence = len(ledger["entries"]) + 1

    entry = make_entry(flow, args.claim_key, sequence, flow_path)
    ledger["entries"].append(entry)
    recompute_totals(ledger)

    write_json(ledger_path, ledger)

    print("AUNEYA LOCAL COLLECTION LEDGER SIMULATION v0.1")
    print("Recorded local non-value entry.")
    print(f"ledger: {ledger_path}")
    print(f"entry_sequence: {entry['entry_sequence']}")
    print(f"claim_key: {entry['claim_key']}")
    print(f"claim_id: {entry['claim_id']}")
    print(f"simulated_amount: {entry['simulated_amount']} simulated_neya")
    print(f"total_simulated_entries: {ledger['total_simulated_entries']}")
    print(f"total_simulated_neya_counted: {ledger['total_simulated_neya_counted']}")
    print("Token created: false")
    print("AUNEYA created: false")
    print("neya created: false")
    print("Real reward created: false")
    print("Market value claimed: false")
    print("Transferable: false")
    print("Mainnet: not active")


def show_ledger(args) -> None:
    ledger_path = Path(args.ledger)
    ledger = load_ledger(ledger_path)

    print("AUNEYA LOCAL COLLECTION LEDGER SIMULATION v0.1")
    print(f"ledger: {ledger_path}")
    print(f"total_simulated_entries: {ledger['total_simulated_entries']}")
    print(f"total_simulated_neya_counted: {ledger['total_simulated_neya_counted']}")
    print("unit: simulated_neya")
    print("Token created: false")
    print("AUNEYA created: false")
    print("neya created: false")
    print("Real reward created: false")
    print("Market value claimed: false")
    print("Transferable: false")
    print("Mainnet: not active")

    if ledger["entries"]:
        print()
        print("Entries:")
        for entry in ledger["entries"]:
            print(
                f"- #{entry['entry_sequence']} "
                f"{entry['claim_key']} "
                f"{entry['simulated_amount']} simulated_neya "
                f"{entry['claim_id']}"
            )


def reset_ledger(args) -> None:
    ledger_path = Path(args.ledger)
    write_json(ledger_path, empty_ledger())

    print("AUNEYA LOCAL COLLECTION LEDGER SIMULATION v0.1")
    print(f"reset ledger: {ledger_path}")
    print("Token created: false")
    print("AUNEYA created: false")
    print("neya created: false")
    print("Real reward created: false")
    print("Market value claimed: false")
    print("Transferable: false")
    print("Mainnet: not active")


def main() -> int:
    parser = argparse.ArgumentParser(description="AUNEYA Local Collection Ledger Simulation v0.1")
    parser.add_argument("--ledger", default=".auneya/local-collection-ledger.json")
    parser.add_argument("--claim-key", default="release-reality")
    parser.add_argument("--out-dir", default=".tmp/auneya-local-collection-ledger")
    parser.add_argument("--witness-id", default="witness_android_termux_local_001")
    parser.add_argument("--start-time", default="2026-10-06T00:14:00Z")
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    selected_actions = sum([args.record, args.show, args.reset])

    if selected_actions != 1:
        fail("choose exactly one action: --record, --show or --reset")

    if args.reset:
        reset_ledger(args)
        return 0

    if args.record:
        record_entry(args)
        return 0

    if args.show:
        show_ledger(args)
        return 0

    fail("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
