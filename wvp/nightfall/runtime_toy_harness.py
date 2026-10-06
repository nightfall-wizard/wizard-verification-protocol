
#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/RUNTIME-TOY-HARNESS.json"
TOY_ROOT = ROOT / "toy-inputs/nightfall/v1.0.5"

REQUIRED_FILES = [
    "docs/RUNTIME-TOY-HARNESS-METHOD.md",
    "docs/TOY-INPUT-SAFETY-BOUNDARY.md",
    "docs/RUNTIME-HARNESS-LIMITATIONS.md",
    "reports/nightfall/v1.0.5/RUNTIME-TOY-HARNESS.md",
    "templates/runtime/toy-vector-template.json",
    "templates/runtime/toy-harness-result.md",
]

FORBIDDEN_TERMS = [
    "real seed value",
    "private key value",
    "wallet seed value",
    "live wallet file",
    "exploit payload here",
    "weaponized reproduction steps here",
]

def evaluate(item):
    cls = item.get("class")

    if cls in ["supply_neutral_transfer", "supply_inflation_reject"]:
        lhs = item.get("input_sum")
        rhs = item.get("output_sum") + item.get("fee") + item.get("burn")
        return "PASS" if lhs == rhs else "REJECT"

    if cls == "duplicate_input_reject":
        inputs = item.get("inputs", [])
        return "REJECT" if len(inputs) != len(set(inputs)) else "PASS"

    if cls == "canonical_ordering":
        return "PASS" if sorted(item.get("items", [])) == item.get("expected_order") else "REJECT"

    if cls in ["coinbase_maturity_reject", "coinbase_maturity_accept"]:
        age = item.get("spend_height") - item.get("coinbase_height")
        return "PASS" if age >= item.get("maturity") else "REJECT"

    if cls == "release_digest_present":
        digest = item.get("sha256", "")
        return "PASS" if len(digest) == 64 and all(c in "0123456789abcdef" for c in digest.lower()) else "REJECT"

    if cls == "public_report_sanitized":
        text = item.get("public_text", "").lower()
        forbidden = ["private key value", "wallet seed value", "exploit payload", "weaponized reproduction"]
        return "PASS" if not any(x in text for x in forbidden) else "REJECT"

    if cls == "issue_quality_hold":
        return "HOLD" if item.get("contains_sensitive_detail") is True else "PASS"

    if cls == "issue_quality_pass":
        return "PASS" if item.get("contains_sensitive_detail") is False else "HOLD"

    return "WARN"

def main():
    print("WVP Runtime Toy Harness Check")

    if not REPORT.exists():
        print("FAIL: RUNTIME-TOY-HARNESS.json missing")
        return 1

    if not TOY_ROOT.exists():
        print("FAIL: toy input root missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    results = data.get("results", [])
    boundary = data.get("safety_boundary", {})

    print("Toy vectors:", data.get("toy_vector_count"))
    print("PASS:", data.get("toy_vector_pass"))
    print("FAIL:", data.get("toy_vector_fail"))

    if data.get("toy_vector_count", 0) < 10:
        print("FAIL: expected at least 10 toy vectors")
        return 1

    if data.get("toy_vector_fail", 1) != 0:
        print("FAIL: toy vector failures present")
        return 1

    required_boundary = [
        "no_real_seed",
        "no_private_key",
        "no_wallet_file",
        "no_live_funds",
        "no_live_rpc_mutation",
        "no_exploit_payloads",
        "no_weaponized_reproduction",
        "non_audit_boundary_required",
    ]

    for key in required_boundary:
        if boundary.get(key) is not True:
            print("FAIL: missing safety boundary:", key)
            return 1

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            print("FAIL: missing required runtime file:", rel)
            return 1

    vectors = sorted(TOY_ROOT.glob("toy-*.json"))
    if len(vectors) < 10:
        print("FAIL: expected at least 10 toy input files")
        return 1

    result_by_id = {r["id"]: r for r in results}

    for path in vectors:
        raw = path.read_text(encoding="utf-8", errors="replace")
        low = raw.lower()

        for term in FORBIDDEN_TERMS:
            if term in low:
                print("FAIL: forbidden term in toy vector:", path.name, term)
                return 1

        item = json.loads(raw)
        if item.get("safe") is not True:
            print("FAIL: toy vector not marked safe:", path.name)
            return 1

        expected = item.get("expected")
        observed = evaluate(item)

        if observed != expected:
            print("FAIL: toy vector mismatch:", path.name, expected, observed)
            return 1

        rid = item["id"]
        if rid not in result_by_id:
            print("FAIL: toy vector missing from report:", rid)
            return 1

        if result_by_id[rid].get("status") != "PASS":
            print("FAIL: report result is not PASS:", rid)
            return 1

    combined = ""
    for rel in REQUIRED_FILES:
        combined += "\n" + (ROOT / rel).read_text(encoding="utf-8", errors="replace").lower()

    required_phrases = [
        "not an audit",
        "toy",
        "no real seed",
        "no private key",
        "no live funds",
        "no exploit payload",
        "not proof",
    ]

    for phrase in required_phrases:
        if phrase not in combined:
            print("FAIL: missing required phrase:", phrase)
            return 1

    print("PASS: runtime toy harness complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
