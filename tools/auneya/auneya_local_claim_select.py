#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


SUPPORTED_CLAIMS = [
    {
        "key": "release-reality",
        "path": "fixtures/auneya/claims/valid-release-reality.json",
        "label": "Public release reality claim",
    },
    {
        "key": "download-integrity",
        "path": "fixtures/auneya/claims/valid-download-integrity.json",
        "label": "Public download integrity claim",
    },
    {
        "key": "website-claim-reality",
        "path": "fixtures/auneya/claims/valid-website-claim-reality.json",
        "label": "Public website claim reality claim",
    },
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail(f"cannot read claim fixture {path}: {exc}")


def is_lawful_public_claim(claim: dict) -> bool:
    if claim.get("schema_version") != "auneya-claim-v0.1":
        return False

    if not str(claim.get("claim_id", "")).startswith("auneya_claim_"):
        return False

    public_access = claim.get("public_access", {})

    if public_access.get("requires_authentication") is True:
        return False

    if public_access.get("requires_payment") is True:
        return False

    if public_access.get("contains_personal_data") is True:
        return False

    if public_access.get("lawful_basis") not in {
        "publicly_accessible",
        "owner_authorized",
        "publisher_provided",
    }:
        return False

    legal = claim.get("legal_boundary", {})

    for key in [
        "private_data_prohibited",
        "hacked_data_prohibited",
        "paywall_bypass_prohibited",
        "credential_use_prohibited",
        "surveillance_prohibited",
    ]:
        if legal.get(key) is not True:
            return False

    target = claim.get("target", {})
    locator = target.get("locator")

    if not isinstance(locator, str) or len(locator) < 4:
        return False

    return True


def load_supported_claims() -> list:
    loaded = []

    for item in SUPPORTED_CLAIMS:
        path = Path(item["path"])

        if not path.exists():
            fail(f"supported claim fixture is missing: {path}")

        claim = load_json(path)

        if not is_lawful_public_claim(claim):
            fail(f"supported claim fixture is not lawful-public: {path}")

        loaded.append({
            "key": item["key"],
            "path": item["path"],
            "label": item["label"],
            "claim_id": claim["claim_id"],
            "target_locator": claim["target"]["locator"],
        })

    return loaded


def print_list(claims: list) -> None:
    print("AUNEYA LOCAL CLAIM SELECTION v0.1")
    print("Mode: local non-value simulation")
    print("Network: none")
    print("Mainnet: not active")
    print("Token created: false")
    print("Market value claimed: false")
    print("Transferable: false")
    print()
    print("Supported lawful public claim fixtures:")

    for index, claim in enumerate(claims, start=1):
        print(f"{index}. key={claim['key']}")
        print(f"   claim_id={claim['claim_id']}")
        print(f"   path={claim['path']}")
        print(f"   label={claim['label']}")
        print()

    print("Boundary:")
    print("- no token")
    print("- no AUNEYA")
    print("- no neya")
    print("- no real reward")
    print("- no market value")
    print("- no mainnet")
    print("- lawful public or owner-authorized fixtures only")


def select_claim(claims: list, claim_key: str) -> dict:
    for claim in claims:
        if claim["key"] == claim_key:
            return claim

    allowed = ", ".join(claim["key"] for claim in claims)
    fail(f"unsupported claim key: {claim_key}; allowed: {allowed}")


def run_demo(selected: dict, out_dir: str, witness_id: str, start_time: str) -> int:
    env = dict(os.environ)
    env["AUNEYA_DEMO_OUT_DIR"] = out_dir
    env["AUNEYA_WITNESS_ID"] = witness_id
    env["AUNEYA_START_TIME"] = start_time

    print("Selected claim:")
    print(f"key: {selected['key']}")
    print(f"claim_id: {selected['claim_id']}")
    print(f"path: {selected['path']}")
    print()

    return subprocess.run(
        ["./tools/auneya/auneya_one_command_local_demo.sh", selected["path"]],
        env=env,
        check=False,
    ).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="AUNEYA Local Claim Selection v0.1")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--claim-key", default="release-reality")
    parser.add_argument("--print-path", action="store_true")
    parser.add_argument("--run-demo", action="store_true")
    parser.add_argument("--out-dir", default=".tmp/auneya-claim-selection")
    parser.add_argument("--witness-id", default="witness_android_termux_local_001")
    parser.add_argument("--start-time", default="2026-10-06T00:13:00Z")
    args = parser.parse_args()

    claims = load_supported_claims()

    if args.list:
        print_list(claims)
        return 0

    selected = select_claim(claims, args.claim_key)

    if args.print_path:
        print(selected["path"])
        return 0

    if args.run_demo:
        return run_demo(selected, args.out_dir, args.witness_id, args.start_time)

    print("AUNEYA LOCAL CLAIM SELECTED")
    print(f"key: {selected['key']}")
    print(f"claim_id: {selected['claim_id']}")
    print(f"path: {selected['path']}")
    print(f"label: {selected['label']}")
    print("Token created: false")
    print("Market value claimed: false")
    print("Transferable: false")
    print("Mainnet: not active")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
