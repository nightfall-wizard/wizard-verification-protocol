
#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/CI-HARDENING.json"
WORKFLOW = ROOT / ".github/workflows/wvp-required-checks.yml"

REQUIRED_FILES = [
    "docs/CI-HARDENING-METHOD.md",
    "docs/REQUIRED-CHECK-GATE-METHOD.md",
    "templates/github/branch-protection-required-checks.json",
    "templates/github/required-checks.md",
]

REQUIRED_WORKFLOW_TERMS = [
    "permissions:",
    "contents: read",
    "persist-credentials: false",
    "timeout-minutes:",
    "concurrency:",
    "python3 -m unittest discover -s tests -v",
    "wvp/nightfall/verifier.py",
    "wvp/nightfall/codepath_binding.py",
    "wvp/nightfall/semantic_regression.py",
    "wvp/nightfall/command_probes.py",
    "wvp/nightfall/release_integrity.py",
    "wvp/nightfall/supply_invariant.py",
    "wvp/nightfall/negative_vectors.py",
    "wvp/nightfall/triage_workflow.py",
    "wvp/nightfall/conformance_score.py",
    "wvp/nightfall/release_pack.py",
    "wvp/nightfall/ci_hardening.py",
]

def main():
    print("WVP CI Hardening Check")

    if not REPORT.exists():
        print("FAIL: CI-HARDENING.json missing")
        return 1

    if not WORKFLOW.exists():
        print("FAIL: required workflow missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    controls = data.get("controls", [])
    passed = data.get("control_pass", 0)
    boundary = data.get("safety_boundary", {})

    print("Controls:", len(controls))
    print("PASS:", passed)

    if len(controls) < 12:
        print("FAIL: expected at least 12 CI hardening controls")
        return 1

    if passed < 12:
        print("FAIL: all CI hardening controls must pass")
        return 1

    required_boundary = [
        "no_real_seed",
        "no_private_key",
        "no_live_funds",
        "no_exploit_payloads",
        "no_write_token_required",
        "non_audit_boundary_required",
    ]

    for key in required_boundary:
        if boundary.get(key) is not True:
            print("FAIL: missing safety boundary:", key)
            return 1

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            print("FAIL: missing required file:", rel)
            return 1

    text = WORKFLOW.read_text(encoding="utf-8", errors="replace")

    for term in REQUIRED_WORKFLOW_TERMS:
        if term not in text:
            print("FAIL: workflow missing term:", term)
            return 1

    forbidden_terms = [
        "secrets.",
        "PRIVATE_KEY",
        "WALLET_SEED",
        "LIVE_FUNDS",
    ]

    for term in forbidden_terms:
        if term in text:
            print("FAIL: workflow contains forbidden secret/live-fund term:", term)
            return 1

    print("PASS: CI hardening and required-check gate complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
