
#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/MAINTAINER-HANDOFF.json"
MERGE = ROOT / "reports/nightfall/v1.0.5/MERGE-READINESS.json"

REQUIRED_FILES = [
    "docs/MAINTAINER-HANDOFF.md",
    "docs/MERGE-READINESS-CHECKLIST.md",
    "docs/FINAL-ROADMAP.md",
    "docs/POST-MERGE-OPERATIONS.md",
    "docs/REVIEWER-GUIDE.md",
    "templates/handoff/maintainer-review-checklist.md",
    "templates/handoff/pr-review-comment.md",
    "templates/handoff/release-note.md",
    "reports/nightfall/v1.0.5/MAINTAINER-HANDOFF.md",
    "reports/nightfall/v1.0.5/MERGE-READINESS.md",
]

REQUIRED_PHRASES = [
    "not an audit",
    "not proof",
    "No real seed".lower(),
    "No private key".lower(),
    "No live funds".lower(),
    "No exploit payloads".lower(),
]

def main():
    print("WVP Handoff Readiness Check")

    if not REPORT.exists():
        print("FAIL: MAINTAINER-HANDOFF.json missing")
        return 1

    if not MERGE.exists():
        print("FAIL: MERGE-READINESS.json missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    merge = json.loads(MERGE.read_text(encoding="utf-8"))

    items = data.get("items", [])
    readiness_pass = data.get("readiness_pass", 0)
    boundary = data.get("safety_boundary", {})

    print("Readiness items:", len(items))
    print("PASS:", readiness_pass)

    if len(items) < 10:
        print("FAIL: expected at least 10 readiness items")
        return 1

    if readiness_pass < len(items):
        print("FAIL: not all readiness items passed")
        return 1

    if merge.get("merge_ready_local") is not True:
        print("FAIL: local merge readiness not true")
        return 1

    required_boundary = [
        "no_real_seed",
        "no_private_key",
        "no_live_funds",
        "no_exploit_payloads",
        "public_report_sanitized",
        "non_audit_boundary_required",
    ]

    for key in required_boundary:
        if boundary.get(key) is not True:
            print("FAIL: missing safety boundary:", key)
            return 1

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            print("FAIL: missing required handoff file:", rel)
            return 1

    combined = ""
    for rel in REQUIRED_FILES:
        combined += "\n" + (ROOT / rel).read_text(encoding="utf-8", errors="replace").lower()

    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in combined:
            print("FAIL: missing required phrase:", phrase)
            return 1

    print("PASS: maintainer handoff and merge readiness complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
