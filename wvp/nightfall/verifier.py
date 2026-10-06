#!/usr/bin/env python3
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[2]

def read(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def add(out, status, check, detail):
    out.append({
        "status": status,
        "check": check,
        "detail": detail,
    })

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path.home() / "nightfall"))
    ap.add_argument("--profile", default="consensus-v1")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser()
    out = []

    required = [
        "docs/SECURITY-MODEL.md",
        "docs/VERIFICATION-PROFILES.md",
        "reports/nightfall/v1.0.5/SECURITY-REVIEW-PLAN.md",
        "reports/nightfall/v1.0.5/TRACEABILITY.md",
        "reports/nightfall/v1.0.5/FINDINGS.md",
        "reports/nightfall/v1.0.5/LIMITATIONS.md",
        "reports/nightfall/v1.0.5/RUNBOOK.md",
    ]

    for rel in required:
        path = ROOT / rel
        status = "PASS" if path.exists() else "FAIL"
        add(out, status, "WVP file " + rel, str(path))

    fx_dir = ROOT / "fixtures/nightfall/v1.0.5"
    fixtures = list(fx_dir.glob("**/*.json"))
    status = "PASS" if len(fixtures) >= 8 else "FAIL"
    add(out, status, "negative fixtures", str(len(fixtures)))

    spec = repo / "docs/SPEC.md"
    sec = repo / "SECURITY.md"
    text = read(spec) + "\n" + read(sec)

    add(out, "PASS" if repo.exists() else "WARN",
        "Nightfall repo", str(repo))
    add(out, "PASS" if spec.exists() else "WARN",
        "Nightfall SPEC.md", str(spec))
    add(out, "PASS" if sec.exists() else "WARN",
        "Nightfall SECURITY.md", str(sec))

    inv_terms = ["UTXO", "kernel_excess", "minted",
                 "burned", "supply invariant"]
    inv = any(t in text for t in inv_terms)
    add(out, "PASS" if inv else "WARN",
        "supply invariant evidence", "spec/security scan")

    mat_terms = ["coinbase maturity", "1,440", "1440"]
    mat = any(t in text for t in mat_terms)
    add(out, "PASS" if mat else "WARN",
        "coinbase maturity evidence", "spec/security scan")

    wf = repo / ".github/workflows"
    has_wf = wf.exists() and list(wf.glob("*.yml"))
    add(out, "PASS" if has_wf else "WARN",
        "GitHub workflows", str(wf))

    if any(x["status"] == "FAIL" for x in out):
        verdict = "FAIL"
    elif any(x["status"] == "WARN" for x in out):
        verdict = "LIMITED PASS"
    else:
        verdict = "PASS"

    if args.json:
        print(json.dumps({
            "profile": args.profile,
            "verdict": verdict,
            "results": out,
        }, indent=2))
    else:
        print("WVP Nightfall Verification Report")
        print("Profile:", args.profile)
        print()
        for x in out:
            print("[{}] {} - {}".format(
                x["status"],
                x["check"],
                x["detail"],
            ))
        print()
        print("Verdict:", verdict)
        print("Boundary: This is not an audit.")

    return 1 if verdict == "FAIL" else 0

if __name__ == "__main__":
    raise SystemExit(main())
