#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_flow(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail(f"cannot read flow report {path}: {exc}")


def validate_flow(flow: dict) -> None:
    if flow.get("schema_version") != "auneya-pulse-flow-v0.1":
        fail("input is not an AUNEYA pulse-flow v0.1 report")

    if flow.get("flow_type") != "phone_witness_loop":
        fail("flow_type must be phone_witness_loop")

    witness = flow.get("witness", {})

    if witness.get("device_class") != "android_termux":
        fail("device_class must be android_termux")

    if witness.get("environment_class") != "phone_safe":
        fail("environment_class must be phone_safe")

    reward = flow.get("simulated_reward_entry", {})

    if reward.get("entry_type") != "non_value_simulation":
        fail("reward entry must be non_value_simulation")

    if reward.get("unit") != "simulated_neya":
        fail("reward unit must be simulated_neya")

    if reward.get("transferable") is not False:
        fail("simulated reward entry must be non-transferable")

    if reward.get("market_value_claimed") is not False:
        fail("simulated reward entry must not claim market value")

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
            fail(f"lawful boundary failed: {key}")


def status_line(label: str, value) -> str:
    return f"{label:<26} {value}"


def render(flow: dict, compact: bool = False) -> str:
    validate_flow(flow)

    claim = flow["claim_ref"]
    witness = flow["witness"]
    cadence = flow["cadence"]
    reward = flow["simulated_reward_entry"]
    prooflet = flow["prooflet"]

    pulses = flow["pulses"]
    micro_proofs = flow["micro_proofs"]

    pulse_count = len(pulses)
    micro_count = len(micro_proofs)

    observed = sum(1 for p in pulses if p.get("observed_status") == "observed")
    dangerous = sum(1 for p in pulses if p.get("observed_status") == "dangerous")
    stale = sum(1 for p in pulses if p.get("observed_status") == "stale")
    unverifiable = sum(1 for p in pulses if p.get("observed_status") == "unverifiable")

    latest_pulse = pulses[-1] if pulses else {}
    latest_type = latest_pulse.get("pulse_type", "-")
    latest_time = latest_pulse.get("observed_at", "-")

    if compact:
        return "\n".join([
            "AUNEYA LOCAL WITNESS",
            f"claim_id={claim['claim_id']}",
            f"pulses={pulse_count}",
            f"micro_proofs={micro_count}",
            f"prooflet={prooflet['prooflet_id']}",
            f"simulated_neya={reward['amount']}",
            "transferable=false",
            "market_value_claimed=false",
            "mainnet=not_active",
        ])

    lines = []

    lines.append("AUNEYA LOCAL WITNESS")
    lines.append("=" * 22)
    lines.append(status_line("Mode:", "local non-value simulation"))
    lines.append(status_line("Network:", "none"))
    lines.append(status_line("Mainnet:", "not active"))
    lines.append(status_line("Token created:", "false"))
    lines.append(status_line("Market value claimed:", "false"))
    lines.append(status_line("Transferable:", "false"))
    lines.append("")
    lines.append("CLAIM")
    lines.append("-" * 22)
    lines.append(status_line("Claim ID:", claim["claim_id"]))
    lines.append(status_line("Claim schema:", claim["claim_schema_version"]))
    lines.append(status_line("Claim hash:", claim["claim_hash"][:24] + "..."))
    lines.append("")
    lines.append("WITNESS")
    lines.append("-" * 22)
    lines.append(status_line("Witness ID:", witness["witness_id"]))
    lines.append(status_line("Device:", witness["device_class"]))
    lines.append(status_line("Environment:", witness["environment_class"]))
    lines.append(status_line("Software:", witness["software_name"] + " " + witness["software_version"]))
    lines.append("")
    lines.append("FLOW")
    lines.append("-" * 22)
    lines.append(status_line("Pulse interval:", str(cadence["pulse_interval_seconds"]) + "s"))
    lines.append(status_line("Pulses:", pulse_count))
    lines.append(status_line("Observed:", observed))
    lines.append(status_line("Unverifiable:", unverifiable))
    lines.append(status_line("Stale:", stale))
    lines.append(status_line("Dangerous:", dangerous))
    lines.append(status_line("Micro-Proofs:", micro_count))
    lines.append(status_line("Prooflet:", prooflet["prooflet_id"]))
    lines.append(status_line("Latest pulse:", latest_type))
    lines.append(status_line("Latest time:", latest_time))
    lines.append("")
    lines.append("SIMULATED ENTRY")
    lines.append("-" * 22)
    lines.append(status_line("Unit:", reward["unit"]))
    lines.append(status_line("Amount:", reward["amount"]))
    lines.append(status_line("Transferable:", str(reward["transferable"]).lower()))
    lines.append(status_line("Market value:", str(reward["market_value_claimed"]).lower()))
    lines.append("")
    lines.append("BOUNDARY")
    lines.append("-" * 22)
    lines.append(status_line("Private data:", "not accessed"))
    lines.append(status_line("Hacked data:", "not used"))
    lines.append(status_line("Paywall bypass:", "not used"))
    lines.append(status_line("Credentials:", "not used"))
    lines.append(status_line("Surveillance:", "not performed"))
    lines.append("")
    lines.append("NOTICE")
    lines.append("-" * 22)
    lines.append("This is local protocol research.")
    lines.append("No token, real reward, mainnet or market value is created.")
    lines.append("Legal review is required before any public token launch, listing, sale, transferability or market-value communication.")

    return "\n".join(str(line) for line in lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="AUNEYA Local Witness CLI Display v0.1")
    parser.add_argument("--input", required=True)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    flow = load_flow(Path(args.input))
    print(render(flow, compact=args.compact))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
