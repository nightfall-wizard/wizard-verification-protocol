#!/usr/bin/env python3

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PULSE_TYPE_MAP = {
    "http_status": "http_status",
    "content_hash": "content_hash",
    "release_metadata": "release_metadata",
    "page_snapshot_hash": "page_snapshot_hash",
    "dns_record": "dns_record",
    "tls_certificate": "tls_certificate",
    "file_metadata": "file_metadata",
    "publisher_identity": "release_metadata",
    "version_metadata": "release_metadata",
    "commit_reference": "release_metadata",
    "checksum_file": "content_hash",
    "detached_signature": "content_hash",
    "build_metadata": "release_metadata",
    "contract_verification": "page_snapshot_hash",
    "supply_evidence": "page_snapshot_hash",
    "audit_scope": "page_snapshot_hash"
}

def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)

def sha256_json(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def parse_start_time(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception as exc:
        fail(f"invalid --start-time: {value} ({exc})")

def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_claim(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail(f"cannot read claim fixture {path}: {exc}")

def validate_claim_for_local_runner(claim: dict) -> None:
    if claim.get("schema_version") != "auneya-claim-v0.1":
        fail("claim schema_version must be auneya-claim-v0.1")

    if not str(claim.get("claim_id", "")).startswith("auneya_claim_"):
        fail("claim_id must start with auneya_claim_")

    public_access = claim.get("public_access", {})

    if public_access.get("requires_authentication") is True:
        fail("claim requires authentication and is out of scope")

    if public_access.get("requires_payment") is True:
        fail("claim requires payment and is out of scope")

    if public_access.get("contains_personal_data") is True:
        fail("claim contains personal data and is out of scope")

    if public_access.get("lawful_basis") not in {
        "publicly_accessible",
        "owner_authorized",
        "publisher_provided",
    }:
        fail("claim lawful_basis is not allowed")

    legal = claim.get("legal_boundary", {})

    for key in [
        "private_data_prohibited",
        "hacked_data_prohibited",
        "paywall_bypass_prohibited",
        "credential_use_prohibited",
        "surveillance_prohibited",
    ]:
        if legal.get(key) is not True:
            fail(f"claim legal boundary must set {key}=true")

    target = claim.get("target", {})
    locator = target.get("locator")

    if not isinstance(locator, str) or len(locator) < 4:
        fail("claim target locator is missing or invalid")

def build_pulse_types(claim: dict) -> list:
    raw = claim.get("evidence_requirements", [])
    mapped = []

    for item in raw:
        pulse_type = PULSE_TYPE_MAP.get(item)
        if pulse_type and pulse_type not in mapped:
            mapped.append(pulse_type)

    if not mapped:
        mapped = ["http_status"]

    while len(mapped) < 4:
        mapped.append(mapped[len(mapped) % len(mapped)])

    return mapped[:4]

def build_flow(claim: dict, witness_id: str, start_time: datetime) -> dict:
    validate_claim_for_local_runner(claim)

    claim_id = claim["claim_id"]
    target_locator = claim["target"]["locator"]
    claim_hash = sha256_json(claim)
    pulse_types = build_pulse_types(claim)

    pulses = []

    for index, pulse_type in enumerate(pulse_types, start=1):
        pulses.append({
            "pulse_index": index,
            "pulse_type": pulse_type,
            "target_locator": target_locator,
            "observed_status": "observed",
            "evidence_hint": f"local non-value observation for {pulse_type}",
            "observed_at": iso_z(start_time + timedelta(seconds=index - 1)),
        })

    micro_proofs = []

    for number, pulse_indexes in enumerate([[1, 2], [3, 4]], start=1):
        base = {
            "claim_id": claim_id,
            "pulse_indexes": pulse_indexes,
            "target_locator": target_locator,
            "witness_id": witness_id,
        }

        micro_proofs.append({
            "micro_proof_id": f"auneya_micro_proof_local_{number:03d}",
            "pulse_indexes": pulse_indexes,
            "micro_proof_hash": sha256_json(base),
            "observed_status": "observed",
            "created_at": iso_z(start_time + timedelta(seconds=number * 2)),
        })

    prooflet_base = {
        "claim_id": claim_id,
        "micro_proof_ids": [mp["micro_proof_id"] for mp in micro_proofs],
        "witness_id": witness_id,
    }

    prooflet = {
        "prooflet_id": "auneya_prooflet_local_001",
        "claim_id": claim_id,
        "micro_proof_ids": [mp["micro_proof_id"] for mp in micro_proofs],
        "observed_status": "observed",
        "prooflet_hash": sha256_json(prooflet_base),
        "created_at": iso_z(start_time + timedelta(seconds=5)),
    }

    simulated_amount = len(pulses) * 2500 + len(micro_proofs) * 4000 + 420

    return {
        "schema_version": "auneya-pulse-flow-v0.1",
        "flow_id": "auneya_flow_local_runner_001",
        "flow_type": "phone_witness_loop",
        "claim_ref": {
            "claim_id": claim_id,
            "claim_schema_version": "auneya-claim-v0.1",
            "claim_hash": claim_hash,
        },
        "witness": {
            "witness_id": witness_id,
            "device_class": "android_termux",
            "environment_class": "phone_safe",
            "software_name": "wvp",
            "software_version": "local-runner-v0.1",
        },
        "cadence": {
            "pulse_interval_seconds": 1,
            "micro_proof_every_pulses": 2,
            "prooflet_every_micro_proofs": 2,
            "max_duration_seconds": 60,
        },
        "pulses": pulses,
        "micro_proofs": micro_proofs,
        "prooflet": prooflet,
        "lawful_boundary_confirmation": {
            "public_or_authorized_target": True,
            "no_private_data_accessed": True,
            "no_hacked_data_used": True,
            "no_paywall_bypass_used": True,
            "no_credentials_used": True,
            "no_surveillance_performed": True,
            "notes": "Local runner used only lawful public or authorized claim fixture metadata.",
        },
        "simulated_reward_entry": {
            "entry_type": "non_value_simulation",
            "unit": "simulated_neya",
            "amount": simulated_amount,
            "transferable": False,
            "market_value_claimed": False,
            "notes": "Local simulation-only entry with no transferability and no market value.",
        },
        "created_at": iso_z(start_time + timedelta(seconds=6)),
        "non_value_notice": "This local witness report is protocol research and does not create a token, real reward or market value.",
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="AUNEYA Local Witness Runner v0.1")
    parser.add_argument("--claim", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--witness-id", default="witness_android_termux_local_001")
    parser.add_argument("--start-time", default="2026-10-06T00:08:00Z")
    args = parser.parse_args()

    claim = load_claim(Path(args.claim))
    flow = build_flow(claim, args.witness_id, parse_start_time(args.start_time))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(flow, indent=2, sort_keys=False) + "\n")

    print("AUNEYA Local Witness Runner v0.1")
    print(f"claim_id: {flow['claim_ref']['claim_id']}")
    print(f"flow_id: {flow['flow_id']}")
    print(f"pulses: {len(flow['pulses'])}")
    print(f"micro_proofs: {len(flow['micro_proofs'])}")
    print(f"prooflet_id: {flow['prooflet']['prooflet_id']}")
    print(f"simulated_reward_entry: {flow['simulated_reward_entry']['amount']} simulated_neya")
    print("transferable: false")
    print("market_value_claimed: false")
    print(f"written: {out_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
