#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/CONFORMANCE-SCORE.json"
PUBLIC = ROOT / "reports/nightfall/v1.0.5/PUBLIC-REPORT.md"

def main():
    if not REPORT.exists():
        print("FAIL: CONFORMANCE-SCORE.json missing")
        return 1

    if not PUBLIC.exists():
        print("FAIL: PUBLIC-REPORT.md missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))

    score = data.get("score_percent", 0)
    grade = data.get("grade")
    requirements = data.get("requirements", [])
    boundary = data.get("non_audit_boundary")
    sanitized = data.get("public_report_sanitized")

    print("WVP Conformance Score Check")
    print("Score:", score)
    print("Grade:", grade)
    print("Requirements:", len(requirements))

    if len(requirements) < 10:
        print("FAIL: expected at least 10 conformance requirements")
        return 1

    if score < 80:
        print("FAIL: conformance score below required threshold")
        return 1

    if boundary is not True:
        print("FAIL: non-audit boundary missing")
        return 1

    if sanitized is not True:
        print("FAIL: public report sanitation flag missing")
        return 1

    if not all(r.get("status") in ["PASS", "WARN", "FAIL"] for r in requirements):
        print("FAIL: invalid requirement status")
        return 1

    public_text = PUBLIC.read_text(encoding="utf-8", errors="replace").lower()
    required_phrases = [
        "not an audit",
        "no seeds",
        "private keys",
        "weaponized reproduction",
        "not certifications",
    ]

    for phrase in required_phrases:
        if phrase not in public_text:
            print("FAIL: public report missing phrase:", phrase)
            return 1

    print("PASS: conformance scoring and public report complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
