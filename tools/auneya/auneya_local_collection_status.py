#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path


LEDGER_SCHEMA_VERSION = "auneya-local-collection-ledger-v0.1"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


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


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail(f"cannot read ledger JSON {path}: {exc}")


def validate_ledger(ledger: dict) -> None:
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

    entries = ledger.get("entries")

    if not isinstance(entries, list):
        fail("ledger entries must be a list")

    total_entries = ledger.get("total_simulated_entries")

    if total_entries != len(entries):
        fail("ledger total_simulated_entries does not match entries length")

    recomputed_total = 0

    for index, entry in enumerate(entries, start=1):
        if entry.get("entry_type") != "local_non_value_collection_simulation":
            fail("entry_type is invalid")

        if entry.get("entry_sequence") != index:
            fail("entry_sequence is not contiguous")

        if entry.get("simulated_unit") != "simulated_neya":
            fail("entry simulated_unit must be simulated_neya")

        amount = entry.get("simulated_amount")

        if not isinstance(amount, int) or amount <= 0:
            fail("entry simulated_amount must be a positive integer")

        recomputed_total += amount

        for key in [
            "transferable",
            "market_value_claimed",
            "token_created",
            "auneya_created",
            "neya_created",
            "real_reward_created",
            "mainnet_active",
        ]:
            if entry.get(key) is not False:
                fail(f"entry boundary violation: {key} must be false")

        if not str(entry.get("entry_hash", "")).startswith("sha256:"):
            fail("entry_hash is missing or invalid")

    if ledger.get("total_simulated_neya_counted") != recomputed_total:
        fail("ledger total_simulated_neya_counted does not match entry sum")


def load_ledger(path: Path) -> tuple[dict, bool]:
    if not path.exists():
        return empty_ledger(), False

    ledger = read_json(path)
    validate_ledger(ledger)
    return ledger, True


def line(label: str, value) -> str:
    return f"{label:<31} {value}"


def render_status(ledger: dict, ledger_path: Path, exists: bool, compact: bool = False) -> str:
    entries = ledger.get("entries", [])
    latest = entries[-1] if entries else None

    if compact:
        return "\n".join([
            "AUNEYA LOCAL COLLECTION STATUS",
            f"ledger_exists={str(exists).lower()}",
            f"total_entries={ledger['total_simulated_entries']}",
            f"total_simulated_neya={ledger['total_simulated_neya_counted']}",
            "unit=simulated_neya",
            "token_created=false",
            "auneya_created=false",
            "neya_created=false",
            "real_reward_created=false",
            "market_value_claimed=false",
            "transferable=false",
            "mainnet=not_active",
        ])

    lines = []

    lines.append("AUNEYA LOCAL COLLECTION STATUS")
    lines.append("=" * 31)
    lines.append(line("Mode:", "local non-value simulation"))
    lines.append(line("Ledger exists:", str(exists).lower()))
    lines.append(line("Ledger:", ledger_path))
    lines.append(line("Network:", "none"))
    lines.append(line("Mainnet:", "not active"))
    lines.append(line("Token created:", "false"))
    lines.append(line("AUNEYA created:", "false"))
    lines.append(line("neya created:", "false"))
    lines.append(line("Real reward created:", "false"))
    lines.append(line("Market value claimed:", "false"))
    lines.append(line("Transferable:", "false"))
    lines.append("")
    lines.append("TOTALS")
    lines.append("-" * 31)
    lines.append(line("Total simulated entries:", ledger["total_simulated_entries"]))
    lines.append(line("Total simulated_neya:", ledger["total_simulated_neya_counted"]))
    lines.append(line("Unit:", "simulated_neya"))
    lines.append("")
    lines.append("LATEST ENTRY")
    lines.append("-" * 31)

    if latest:
        lines.append(line("Entry sequence:", latest["entry_sequence"]))
        lines.append(line("Claim key:", latest["claim_key"]))
        lines.append(line("Claim ID:", latest["claim_id"]))
        lines.append(line("Simulated amount:", str(latest["simulated_amount"]) + " simulated_neya"))
        lines.append(line("Prooflet:", latest["prooflet_id"]))
        lines.append(line("Created at:", latest["created_at"]))
    else:
        lines.append("No local simulated entries recorded yet.")

    lines.append("")
    lines.append("ENTRIES")
    lines.append("-" * 31)

    if entries:
        for entry in entries[-10:]:
            lines.append(
                f"#{entry['entry_sequence']} "
                f"{entry['claim_key']} "
                f"{entry['simulated_amount']} simulated_neya"
            )
    else:
        lines.append("No entries.")

    lines.append("")
    lines.append("BOUNDARY")
    lines.append("-" * 31)
    lines.append("This is local protocol research.")
    lines.append("No token, AUNEYA, neya, real reward, mainnet or market value is created.")
    lines.append("Nothing shown here is transferable.")
    lines.append("Legal review is required before any public token launch, listing, sale, transferability or market-value communication.")

    return "\n".join(str(item) for item in lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="AUNEYA Local Collection Status Display v0.1")
    parser.add_argument("--ledger", default=".auneya/local-collection-ledger.json")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    ledger_path = Path(args.ledger)
    ledger, exists = load_ledger(ledger_path)

    print(render_status(ledger, ledger_path, exists, compact=args.compact))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
