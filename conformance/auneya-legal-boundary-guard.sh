#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import sys

required = {
    "docs/auneya/AUNEYA-LEGAL-BOUNDARY.md": [
        "AUNEYA is non-value protocol research and simulation only",
        "This repository does not provide legal advice",
        "qualified Germany/EU legal review is required",
        "AUNEYA currently creates no token",
        "No-service rule",
        "Hard legal stop",
    ],
    "docs/auneya/AUNEYA-LEGAL-REVIEW-GATES.md": [
        "Prohibited until legal review",
        "No code may implement token, value, wallet, custody",
        "When uncertain, AUNEYA must stay research-only",
    ],
    "docs/auneya/AUNEYA-REGULATED-LANGUAGE.md": [
        "Blocked words may appear only when used as negative boundary language",
        "AUNEYA does not create a token",
        "AUNEYA will launch a token",
    ],
}

for file, phrases in required.items():
    path = Path(file)
    if not path.exists():
        print(f"FAIL: missing required file: {file}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            print(f"FAIL: missing required phrase in {file}: {phrase}")
            sys.exit(1)

forbidden_positive_phrases = [
    "guaranteed return",
    "profit is promised",
    "yield is offered",
    "investment opportunity",
    "token sale is live",
    "airdrop is promised",
    "market value is expected",
    "security is guaranteed",
    "legal compliance is guaranteed",
    "bafin approval is granted",
    "mica compliance is guaranteed",
    "users can earn",
    "users will earn",
    "rewards are paid",
    "staking rewards",
    "launching our token",
    "buy auneya",
    "invest in auneya",
]

negative_markers = [
    "no ",
    "not ",
    "does not",
    "must not",
    "without legal review",
    "blocked",
    "prohibited",
    "non-claim",
    "non-claims",
    "example blocked use",
]

for file in required:
    path = Path(file)
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        lower = line.lower().strip()
        if not lower:
            continue

        for phrase in forbidden_positive_phrases:
            if phrase in lower:
                if any(marker in lower for marker in negative_markers):
                    continue
                print(f"FAIL: forbidden positive legal/value claim found in {file}:{lineno}: {line}")
                sys.exit(1)

print("PASS: AUNEYA legal boundary guard")
PY
