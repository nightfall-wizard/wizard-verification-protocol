#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/NEGATIVE-VECTORS.json"
VECTOR_DIR = ROOT / "negative-vectors/nightfall/v1.0.5"

ALLOWED_RESULTS = {
    "reject",
    "reject_or_warn",
    "reject_without_state_mutation",
    "warn",
    "documented_limitation",
}

def main():
    if not REPORT.exists():
        print("FAIL: NEGATIVE-VECTORS.json missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    vectors = data.get("vectors", [])
    files = list(VECTOR_DIR.glob("*.json"))

    print("WVP Negative Vector Check")
    print("Vectors in report:", len(vectors))
    print("Vector files:", len(files))

    if len(vectors) < 10:
        print("FAIL: expected at least 10 negative vectors")
        return 1

    if len(files) < 10:
        print("FAIL: expected at least 10 vector files")
        return 1

    for f in files:
        item = json.loads(f.read_text(encoding="utf-8"))
        if item.get("contains_secret") is not False:
            print("FAIL: vector may contain secret:", f)
            return 1
        if item.get("contains_live_funds") is not False:
            print("FAIL: vector may contain live funds:", f)
            return 1
        if item.get("expected_result") not in ALLOWED_RESULTS:
            print("FAIL: invalid expected result:", f)
            return 1
        payload = item.get("payload", {})
        if payload.get("kind") != "non_executable_placeholder":
            print("FAIL: vector is not safely abstract:", f)
            return 1

    boundary = data.get("safety_boundary", {})
    required_boundary = [
        "no_real_seed",
        "no_private_key",
        "no_live_funds",
        "no_undisclosed_exploit_detail",
        "no_network_mutation",
        "no_node_state_mutation",
    ]

    for key in required_boundary:
        if boundary.get(key) is not True:
            print("FAIL: missing safety boundary:", key)
            return 1

    print("PASS: negative vector scaffold is safe and complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
